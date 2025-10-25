

import json
from scanned_text.helpers.ai_utils import _OPENAI_MODEL, initOpenAI

def get_difficult_words_with_meanings(processed_text: str, age: int, classe: str) -> dict:
    """Retourne un mapping index->définition simple des mots difficiles.

    - Utilise OpenAI si disponible et tente de parser un JSON strict.
    - En absence d'OpenAI (ou si parsing échoue), renvoie un fallback heuristique.
    - Toujours retourner un dict avec des clés chaîne ("0", "1", ...).
    """
    _openai_client = initOpenAI()
    _OPENAI_ENABLED = _openai_client is not None

    def _fallback_mapping(text: str) -> dict:
        words = (text or "").split()
        difficult_indices = []
        for idx, w in enumerate(words):
            token = w.strip(",.;:!?()[]{}\"'«»“”–-_")
            if len(token) >= 9 and token.isalpha():
                difficult_indices.append(idx)
            if len(difficult_indices) >= 5:
                break
        mapping = {}
        for i in difficult_indices:
            mapping[str(i)] = (
                f"Mot potentiellement difficile pour {classe} ({age} ans). Explication simple: définition courte et accessible."
            )
        return mapping

    if not _OPENAI_ENABLED or not _openai_client:
        return _fallback_mapping(processed_text)

    response = _openai_client.chat.completions.create(
        model=_OPENAI_MODEL,
        temperature=0.2,
        max_completion_tokens=800,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un assistant pédagogique spécialisé dans la simplification de texte. "
                    "Identifie les mots qui pourraient être compliqués pour un élève selon son âge et sa classe.\n\n"
                    "Consignes de sortie:\n"
                    "- Retourne UNIQUEMENT un JSON, sans texte autour ni bloc de code.\n"
                    "- Les clés DOIVENT être des chaînes (\"0\", \"1\", ...).\n"
                    "- La valeur est une définition simple et adaptée à l'âge indiqué.\n"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Texte à analyser :\n{processed_text}\n\n"
                    f"Contexte élève → Âge: {age} | Classe: {classe}.\n"
                    "Retourne un JSON de la forme :\n"
                    "{\n"
                    '  "3": "Définition simple",\n'
                    '  "7": "Explication facile"\n'
                    "}\n"
                    "- Pas de commentaires, pas de texte hors JSON."
                ),
            },
        ],
    )

    # Extraction et parsing robustes
    try:
        content = response.choices[0].message.content
    except Exception:
        try:
            content = response.choices[0].message["content"]
        except Exception:
            content = ""

    def _try_parse_json(txt: str):
        try:
            return json.loads(txt)
        except Exception:
            return None

    result = _try_parse_json(content)
    if result is None and content:
        if "```" in content:
            parts = content.split("```")
            for part in parts:
                candidate = part.strip()
                if candidate.lower().startswith("json\n"):
                    candidate = candidate[5:].strip()
                if candidate.startswith("{") and candidate.endswith("}"):
                    parsed = _try_parse_json(candidate)
                    if parsed is not None:
                        result = parsed
                        break

    if result is None and content:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = content[start : end + 1]
            result = _try_parse_json(candidate)

    if not isinstance(result, dict):
        return _fallback_mapping(processed_text)

    normalized = {str(k): v for k, v in result.items()}
    return normalized

    """Retourne un mapping index->définition simplifiée des mots difficiles.

    - Utilise OpenAI si disponible, sinon applique un fallback heuristique.
    - Tente de parser la réponse en JSON même si elle contient des blocs de code.
    - Si le JSON est vide ou invalide, applique un fallback heuristique.
    """
    _openai_client = initOpenAI()
    _OPENAI_ENABLED = _openai_client is not None

    def _heuristic_mapping(text: str) -> dict:
        words = text.replace("\n", " ").split()
        seen = set()
        candidates = []
        for idx, w in enumerate(words):
            token = "".join(ch for ch in w if ch.isalpha())
            lw = token.lower()
            if len(token) >= 9 and lw not in seen:
                seen.add(lw)
                candidates.append((idx, token))
            if len(candidates) >= 4:
                break
        if not candidates:
            # fallback: plus longs mots > 6
            words_clean = [(i, "".join(ch for ch in w if ch.isalpha())) for i, w in enumerate(words)]
            words_clean = [(i, w) for i, w in words_clean if len(w) >= 7]
            words_clean.sort(key=lambda t: len(t[1]), reverse=True)
            candidates = words_clean[:3]
        return {
            str(i): f"Définition simplifiée du mot '{w}' adaptée à {age} ans (classe {classe})."
            for i, w in candidates
        }

    if not _OPENAI_ENABLED or not _openai_client:
        # Ne pas renvoyer une map vide: fournir un résultat heuristique minimal
        return _heuristic_mapping(processed_text)

    response = _openai_client.chat.completions.create(
        model=_OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un assistant pédagogique spécialisé dans la simplification de texte. "
                    "Tu dois identifier les mots qui pourraient être compliqués pour un élève selon son âge et son niveau scolaire.\n\n"
                    "Consignes strictes de sortie :\n"
                    "- Réponds UNIQUEMENT en JSON valide, sans bloc de code, sans texte autour.\n"
                    "- Retourne entre 1 et 8 éléments.\n"
                    "- Les clés DOIVENT être des chaînes représentant l'index du mot (`\"0\"`, `\"7\"`, ...).\n"
                    "- Les valeurs DOIVENT être des définitions simples adaptées à {age} ans (classe {classe})."
                ).format(age=age, classe=classe)
            },
            {
                "role": "user",
                "content": (
                    f"Voici le texte à analyser :\n\n{processed_text}\n\n"
                    "Retourne UNIQUEMENT un JSON de ce type :\n"
                    "{\n"
                    '  "3": "Définition simple",\n'
                    '  "7": "Explication facile"\n'
                    "}\n"
                    "Chaque clé correspond à la position du mot dans le texte (split par espace) en partant de 0."
                )
            }
        ],
        temperature=0.2,
        max_completion_tokens=800,
    )

    raw = None
    try:
        raw = response.choices[0].message.content
    except Exception:
        try:
            raw = response.choices[0].message["content"]
        except Exception:
            raw = ""

    def _try_parse_json(txt: str):
        try:
            return json.loads(txt)
        except Exception:
            return None

    parsed = _try_parse_json(raw)
    if parsed is None and raw:
        if "```" in raw:
            parts = raw.split("```")
            for part in parts:
                candidate = part.strip()
                if candidate.lower().startswith("json\n"):
                    candidate = candidate[5:].strip()
                if candidate.startswith("{") and candidate.endswith("}"):
                    parsed = _try_parse_json(candidate)
                    if parsed is not None:
                        break

    if parsed is None and raw:
        s = raw.find("{")
        e = raw.rfind("}")
        if s != -1 and e != -1 and e > s:
            parsed = _try_parse_json(raw[s : e + 1])

    if not isinstance(parsed, dict) or len(parsed) == 0:
        # Fallback heuristique si JSON vide/invalide
        return _heuristic_mapping(processed_text)

    # Normalisation: clés en chaînes, valeurs en chaînes non vides
    normalized = {}
    for k, v in parsed.items():
        sk = str(k)
        if isinstance(v, str) and v.strip():
            normalized[sk] = v.strip()

    if not normalized:
        normalized = _heuristic_mapping(processed_text)

    return normalized