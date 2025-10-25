

import json
from scanned_text.helpers.ai_utils import _OPENAI_MODEL, initOpenAI


def process_ocr_text_with_openai(text: str, max_chars: int = 400) -> dict:
    """Return a concise summary of the input text using OpenAI if configured.

    Fallback: returns the first N characters when OpenAI is not enabled.
    """
    _openai_client = initOpenAI()
    _OPENAI_ENABLED = _openai_client is not None

    if not _OPENAI_ENABLED or not _openai_client:
        print("OpenAI not enabled, using fallback processing.")
        return {"processed_text": (text[:max_chars] + "...") if len(text) > max_chars else text, "detected_type": None}

    response = _openai_client.chat.completions.create(
        model=_OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un agent intelligent qui analyse un texte scanné par OCR. "
                    "Tu dois déterminer s'il s'agit d'un **exercice** ou d'un **cours** (le champ `detected_type`), "
                    "et reformater proprement le contenu dans `processed_text` (sans fautes, sans retours à la ligne inutiles). "
                    "Réponds STRICTEMENT en JSON, sans texte autour, sans bloc de code."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Voici un texte brut scanné :\n\n{text}\n\n"
                    "Analyse le texte ci-dessus et retourne UNIQUEMENT un JSON strictement de la forme :\n"
                    "{\n"
                    '  "processed_text": "Texte nettoyé et lisible...",\n'
                    '  "detected_type": "cours"\n'
                    "}\n"
                    "- La valeur de 'detected_type' doit être 'cours' ou 'exercice'.\n"
                    "- Pas de commentaires ou de texte hors JSON.\n"
                    "Fais attention à garder la structure utile du contenu. Ne change pas la nature du texte."
                )
            }
        ],
        max_completion_tokens=1000
    )

    raw_content = None
    try:
        raw_content = response.choices[0].message.content
    except Exception:
        try:
            raw_content = response.choices[0].message["content"]
        except Exception:
            raw_content = ""

    # Helper: try parse JSON directly
    def _try_parse_json(txt: str):
        try:
            return json.loads(txt)
        except Exception:
            return None

    # 1) Direct parse
    parsed = _try_parse_json(raw_content)

    # 2) If failed, try to extract a JSON block from code fences
    if parsed is None and raw_content:
        if "```" in raw_content:
            parts = raw_content.split("```")
            for part in parts:
                candidate = part.strip()
                if candidate.lower().startswith("json\n"):
                    candidate = candidate[5:].strip()
                if candidate.startswith("{") and candidate.endswith("}"):
                    parsed = _try_parse_json(candidate)
                    if parsed is not None:
                        break

    # 3) If still failed, try to extract braces region heuristically
    if parsed is None and raw_content:
        start = raw_content.find("{")
        end = raw_content.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = raw_content[start : end + 1]
            parsed = _try_parse_json(candidate)

    # 4) Final fallback: return a minimal structure using truncated text
    if parsed is None or not isinstance(parsed, dict):
        return {
            "processed_text": (text[:max_chars] + "...") if len(text) > max_chars else text,
            "detected_type": None,
        }

    # Ensure required keys exist and are strings
    processed = parsed.get("processed_text")
    if not isinstance(processed, str) or not processed:
        processed = (text[:max_chars] + "...") if len(text) > max_chars else text

    detected = parsed.get("detected_type")
    if detected not in {"cours", "exercice"}:
        detected = None

    return {"processed_text": processed, "detected_type": detected}
