from rest_framework import viewsets, status, exceptions
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample

from .models import ScannedText
from .serializers import (
    QuizQuestionSerializer,
    ScannedTextSerializer,
    DifficultWordsResponseSerializer,
    TextExplanationSerializer,
    ExerciseStepsResponseSerializer
)
from .helpers.ai import (
    generate_exercise_steps,
    generate_text_explanation, 
    get_difficult_words_with_meanings,
    generate_quiz_from_text, 
    process_ocr_text_with_openai)
from decouple import config

class ScannedTextViewSet(viewsets.ModelViewSet):
    queryset = ScannedText.objects.all().order_by('-createdAt')
    serializer_class = ScannedTextSerializer
    http_method_names = ['post', 'get']
    pagination_class = None  # Désactive la pagination pour cette vue.


    @extend_schema(
        operation_id="createScannedText",
        summary="Créer un texte scanné",
        description="Crée un enregistrement à partir d'un texte brut et applique un traitement (mock ou OpenAI).",
        responses={201: ScannedTextSerializer},
    )
    def create(self, request, *args, **kwargs):
        original_text = request.data.get("original_text", "")
        if not original_text.strip():
            return Response({"error": "Le champ original_text est requis."}, status=status.HTTP_400_BAD_REQUEST)

        # Traitement IA simulé
        if config('ENV') == 'production':
            print("Utilisation d'OpenAI pour le traitement du texte.")
            
            ai_result = process_ocr_text_with_openai.process_ocr_text_with_openai(original_text)
            processed = ai_result.get("processed_text")
            detected_type = ai_result.get("detected_type") or ai_utils.mock_detect_type(processed)

            if not processed:
                raise exceptions.APIException("Erreur lors du traitement du texte avec OpenAI.")
        else:
            from .helpers import ai_utils
            processed = ai_utils.mock_process_text(original_text)
            detected_type = ai_utils.mock_detect_type(processed)
        

        scanned = ScannedText.objects.create(
            user=request.user,
            original_text=original_text,
            processed_text=processed,
            detected_type=detected_type
        )

        serializer = self.get_serializer(scanned)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="getWordsExplanation",
        summary="Identifier les mots difficiles",
        description=(
            "Analyse un texte (fourni directement ou via l'ID d'un ScannedText existant) et "
            "retourne un dictionnaire des mots potentiellement difficiles pour l'élève, "
            "avec des définitions adaptées à son âge et sa classe. Nécessite OpenAI pour une réponse enrichie; "
            "sinon retour vide ou réduit."
        ),
        responses={200: DifficultWordsResponseSerializer},
    )
    @action(methods=["get"], detail=True, url_path="words-explanation")
    def words_explanation(self, request, *args, **kwargs):
        obj = self.get_object()  # type: ScannedText
        if not obj.processed_text:
            return Response({"detail": "Le texte scanné n'a pas de processed_text."}, status=400)
        
        scannedText = ScannedText.objects.get(id=obj.id)

        try:
            raw_result = get_difficult_words_with_meanings.get_difficult_words_with_meanings(
                processed_text=scannedText.processed_text,
                age=scannedText.user.age,
                classe=scannedText.user.classe,
            )
        except Exception as e:  # pragma: no cover
            return Response({"detail": f"Erreur IA: {e}"}, status=500)

        # La fonction renvoie du JSON texte; essayer de parser.
        words_mapping = {}
        if isinstance(raw_result, dict):
            words_mapping = raw_result
        else:
            import json
            try:
                words_mapping = json.loads(raw_result)
            except Exception:
                # Fallback simple: retour vide
                words_mapping = {}

        response_payload = {"words": {str(k): v for k, v in words_mapping.items()}}
        out_ser = DifficultWordsResponseSerializer(data=response_payload)
        out_ser.is_valid(raise_exception=True)
        return Response(out_ser.data)
    
    @extend_schema(
        operation_id="getTextExplanation",
        summary="Obtenir une explication du texte",
        description=(
            "Génère une explication claire et adaptée à l'âge et la classe de l'utilisateur "
            "pour un texte scanné existant. Nécessite OpenAI."
        ),
        responses={200: TextExplanationSerializer},
        examples=[
            OpenApiExample(
                "Exemple de réponse",
                summary="Exemple",
                description="Exemple d'explication générée pour un texte scanné.",
                value={ "explanation": "Cette explication est adaptée à l'âge et la classe de l'utilisateur." },
                response_only=True,
            )
        ]
    )
    @action(methods=["get"], detail=True, url_path="text-explanation")
    def text_explanation(self, request, *args, **kwargs):
        obj = self.get_object()  # type: ScannedText

        if not obj.processed_text:
            return Response({"detail": "Le texte scanné n'a pas de processed_text."}, status=400)
        
        scannedText = ScannedText.objects.get(id=obj.id)

        try:
            raw_result = generate_text_explanation.generate_text_explanation(
                processed_text=scannedText.processed_text,
                age=scannedText.user.age,
                classe=scannedText.user.classe,
            )
        except Exception as e:  # pragma: no cover
            return Response({"detail": f"Erreur IA: {e}"}, status=500)

        response_payload = {"explanation": raw_result.get("explanation", "")}

        out_ser = TextExplanationSerializer(data=response_payload)
        out_ser.is_valid(raise_exception=True)
        return Response(out_ser.data)

    @extend_schema(
        operation_id="getExerciseSteps",
        summary="Obtenir les étapes pour un exercice",
        description=(
            "Génère les étapes détaillées pour résoudre un exercice contenu dans un texte scanné existant. "
            "Nécessite OpenAI. Le texte doit être de type 'exercice'."
        ),
        responses={200: ExerciseStepsResponseSerializer},
    )
    @action(methods=["get"], detail=True, url_path="exercise-steps")
    def exercise_steps(self, request, *args, **kwargs):
        obj = self.get_object()  # type: ScannedText

        scannedText = ScannedText.objects.get(id=obj.id)

        if not scannedText.processed_text:
            return Response({"detail": "Le texte scanné n'a pas de processed_text."}, status=400)
        
        if scannedText.detected_type != "exercice":
            return Response({"detail": "Le texte scanné n'est pas de type 'exercice'."}, status=400)

        try:
            raw_result = generate_exercise_steps.generate_exercise_steps(
                processed_text=scannedText.processed_text,
                age=scannedText.user.age,
                classe=scannedText.user.classe,
            )
        except Exception as e:  # pragma: no cover
            return Response({"detail": f"Erreur IA: {e}"}, status=500)

        out_ser = ExerciseStepsResponseSerializer(data={"steps": raw_result.get("steps", {})})
        out_ser.is_valid(raise_exception=True)
        return Response(out_ser.data)
    

    @extend_schema(
        operation_id="getQuizFromText",
        summary="Générer un quiz à partir du texte",
        description=(
            "Génère un quiz à choix multiple basé sur le texte scanné existant, adapté à l'âge et la classe de l'utilisateur. "
            "Nécessite OpenAI."
        ),
        responses={200: QuizQuestionSerializer(many=True)},
    )
    @action(methods=["get"], detail=True, url_path="quiz-from-text")
    def quiz_from_text(self, request, *args, **kwargs):
        obj = self.get_object()  # type: ScannedText

        scannedText = ScannedText.objects.get(id=obj.id)

        if not scannedText.processed_text:
            return Response({"detail": "Le texte scanné n'a pas de processed_text."}, status=400)

        try:
            raw_result = generate_quiz_from_text.generate_quiz_from_text(
                processed_text=scannedText.processed_text,
                age=scannedText.user.age,
                classe=scannedText.user.classe,
            )
        except Exception as e:  # pragma: no cover
            return Response({"detail": f"Erreur IA: {e}"}, status=500)

        out_ser = QuizQuestionSerializer(data=raw_result.get("questions", []), many=True)
        out_ser.is_valid(raise_exception=True)
        return Response(out_ser.data)