
from scanned_text.helpers.ai_utils import _OPENAI_MODEL, initOpenAI


def generate_quiz_from_text(processed_text: str, age: int, classe: str) -> dict:
    """
    Utilise GPT pour générer une liste de questions à choix multiple à partir du texte scanné,
    adaptée à l'âge et au niveau scolaire de l'utilisateur.
    
    Structure des éléments retournés :
    [
        {
            "question": "Quel est le sujet principal du texte ?",
            "options": ["La pollution", "Le sport", "L'école", "La santé"],
            "answer": "La pollution",
            "explanation": "Le texte parle principalement de la pollution et de ses effets."
        },
        ...
    ]
    """
    _openai_client = initOpenAI()
    _OPENAI_ENABLED = _openai_client is not None

    if not _OPENAI_ENABLED or not _openai_client:
        return {}

    response = _openai_client.chat.completions.create(
        model=_OPENAI_MODEL,  # ou "gpt-5-nano" si activé
        temperature=0.3,
        max_completion_tokens=900,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un assistant pédagogique qui crée des quiz adaptés à l'âge et au niveau scolaire de l'élève. "
                    "Tu dois générer un quiz à partir du texte fourni. Chaque question doit avoir : "
                    "le texte de la question, une liste d'options (3 à 5), la bonne réponse, et une explication. "
                    "La réponse doit être exactement l'un des éléments dans options."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Texte à analyser :\n{processed_text}\n\n"
                    f"Âge de l’élève : {age}\n"
                    f"Classe : {classe}\n\n"
                    "Génère une liste JSON de quiz au format suivant :\n"
                    "[\n"
                    "  {\n"
                    '    "question": "Quel est le sujet principal du texte ?",\n'
                    '    "options": ["A", "B", "C", "D"],\n'
                    '    "answer": "A",\n'
                    '    "explanation": "Parce que le texte parle de cela."\n'
                    "  },\n"
                    "  ...\n"
                    "]\n"
                    "Retourne uniquement du JSON sans texte autour."
                )
            }
        ]
    )

    raw = response.choices[0].message.content

    try:
        import json
        quiz_data = json.loads(raw)
    except Exception:
        quiz_data = {"error": "Échec du parsing JSON", "raw": raw}

    return {
        "questions": quiz_data
    }