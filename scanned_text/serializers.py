from rest_framework import serializers

from account.serializers import UserSerializer
from .models import ScannedText


class ScannedTextSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ScannedText
        fields = [
            'id', 'user', 'original_text', 'processed_text', 'detected_type', 'createdAt', 'updatedAt'
        ]
        read_only_fields = ['user', 'processed_text', 'detected_type', 'createdAt', 'updatedAt']

class DifficultWordsResponseSerializer(serializers.Serializer):
    """Structure de réponse: mapping position -> définition simple.

    Exemple:
    {
        "3": "Définition simple",
        "7": "Explication facile"
    }
    """

    words = serializers.DictField(
        child=serializers.CharField(),
        help_text="Dictionnaire: clé=position du mot (index), valeur=définition adaptée."
    )


class TextExplanationSerializer(serializers.Serializer):
    explanation = serializers.CharField(help_text="Explication du texte adaptée à l'âge et la classe.")


class ExerciseStepsResponseSerializer(serializers.Serializer):
    steps = serializers.DictField(
        child=serializers.CharField(),
        help_text="Dictionnaire: clé=étape (index), valeur=description de l'étape."
    )

class QuizQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(help_text="Texte de la question.")
    options = serializers.ListField(
        child=serializers.CharField(),
        help_text="Liste des options de réponse."
    )
    answer = serializers.CharField(help_text="Réponse correcte.")   
    explanation = serializers.CharField(help_text="Explication de la réponse correcte.")