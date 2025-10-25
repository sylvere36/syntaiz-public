

import json
from scanned_text.helpers.ai_utils import _OPENAI_MODEL, initOpenAI


def generate_exercise_steps(processed_text: str, age: int, classe: str) -> dict:
    """
    Utilise GPT pour générer les étapes de résolution de l'exercice fourni dans `processed_text`.

    Retour :
        {
            "steps": {
                0: "Lire attentivement l'énoncé",
                1: "Identifier les données connues",
                ...
            },
        }
    """
    _openai_client = initOpenAI()
    _OPENAI_ENABLED = _openai_client is not None

    def _fallback_steps(text: str) -> dict:
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        base_steps = [
            "Lire attentivement l'énoncé",
            "Identifier les données connues et la question",
            "Choisir la méthode adaptée",
            "On ne doit pas donner la réponse juste les étapes",
        ]
        steps = {str(i): step for i, step in enumerate(base_steps[: max(3, min(5, len(base_steps)))])}
        return {"steps": steps}

    if not _OPENAI_ENABLED or not _openai_client:
        return _fallback_steps(processed_text)

    response = _openai_client.chat.completions.create(
        model=_OPENAI_MODEL,
        max_completion_tokens=800,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un excellent professeur qui aide les élèves à comprendre comment résoudre un exercice. "
                    "Tu expliques étape par étape la démarche à suivre, en t’adaptant à leur niveau. "
                    "Réponds STRICTEMENT en JSON, sans texte autour, sans bloc de code."
                    "On ne doit pas donner la réponse juste les étapes"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Exercice à analyser :\n{processed_text}\n\n"
                    f"Âge de l'élève : {age} | Classe : {classe}.\n"
                    "Retourne UNIQUEMENT un JSON de la forme suivante :\n"
                    "{\n"
                    '  "0": "Lire attentivement l\'énoncé",\n'
                    '  "1": "Identifier les données et la question",\n'
                    '  "2": "Choisir la méthode et appliquer",\n'
                    '  "3": "Vérifier et rédiger la réponse"\n'
                    "}\n"
                    "- Chaque clé DOIT être une chaîne (\"0\", \"1\", ...).\n"
                    "- Chaque valeur DOIT être une phrase claire et concise.\n"
                    "- Pas de commentaires, pas de texte hors JSON."
                ),
            },
        ],
    )

    # Extraire le contenu indépendamment du type de réponse (objets vs dict-like)
    content = None
    try:
        content = response.choices[0].message.content
        print("OpenAI response content:", content)
    except Exception:
        try:
            content = response.choices[0].message.content
        except Exception:
            content = ""

    # Tentative de parsing direct
    def _try_parse_json(txt: str):
        try:
            return json.loads(txt)
        except Exception:
            return None

    steps_json = _try_parse_json(content)
    if steps_json is None:
        # Essayer d'extraire un éventuel bloc JSON dans des backticks
        if "```" in content:
            parts = content.split("```")
            # chercher un bloc qui ressemble à du JSON
            for i in range(len(parts)):
                candidate = parts[i].strip()
                if candidate.startswith("{") and candidate.endswith("}"):
                    parsed = _try_parse_json(candidate)
                    if parsed is not None:
                        steps_json = parsed
                        break

    if steps_json is None:
        # Fallback texte -> liste d'étapes
        lines = [line.strip("- •\t ") for line in content.split("\n") if line.strip()]
        steps_json = {i: line for i, line in enumerate(lines) if line}

    # S'assurer que les clés sont bien des chaînes
    normalized = {str(k): v for k, v in steps_json.items()}
    return {"steps": normalized}
