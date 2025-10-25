

from scanned_text.helpers.ai_utils import _OPENAI_MODEL, initOpenAI


def generate_text_explanation(processed_text: str, age: int, classe: str) -> dict:
    """
    Envoie le texte scanné à GPT pour générer une explication adaptée à l'âge et à la classe de l'utilisateur.

    Retourne :
        {
            "explanation": "explication adaptée",
            "tokens_used": 123,
        }
    """

    _openai_client = initOpenAI()
    _OPENAI_ENABLED = _openai_client is not None

    def _fallback_explanation(txt: str) -> str:
        try:
            sentences = [s.strip() for s in txt.replace("\r", " ").split(".") if s.strip()]
            take = max(2, min(5, len(sentences)))
            snippet = ". ".join(sentences[:take]).strip()
            if not snippet:
                snippet = txt.strip()
        except Exception:
            snippet = (txt or "").strip()
        if len(snippet) > 600:
            snippet = snippet[:600] + "..."
        return (
            "Voici une explication concise et accessible basée sur le texte fourni: "
            + snippet
        )

    if not _OPENAI_ENABLED or not _openai_client:
        return {"explanation": _fallback_explanation(processed_text), "tokens_used": 0}

    try:
        response = _openai_client.chat.completions.create(
            model=_OPENAI_MODEL,
            temperature=0.3,
            max_completion_tokens=600,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un excellent pédagogue. Explique le texte de manière claire, simple, et adaptée à l'âge et à la classe. "
                        "Utilise un ton bienveillant, accessible, et évite le jargon. Réponds en français en 5 à 7 phrases maximum. "
                        "N'utilise pas de liste, pas de code, pas de balises."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Texte à expliquer :\n\n{processed_text}\n\n"
                        f"Contexte élève → Âge: {age} | Classe: {classe}.\n"
                        "Fournis une explication claire et adaptée."
                    ),
                },
            ],
        )

        # Content extraction (defensive)
        try:
            content = response.choices[0].message.content
        except Exception:
            try:
                content = response.choices[0].message["content"]
            except Exception:
                content = ""
        content = (content or "").strip()
        if not content:
            content = _fallback_explanation(processed_text)

        # Token usage extraction (defensive)
        usage = getattr(response, "usage", None)
        tokens_used = 0
        if usage is not None:
            # usage may be an object with attributes or a dict
            tokens_used = getattr(usage, "total_tokens", None) or (
                usage.get("total_tokens") if isinstance(usage, dict) else 0
            )

        return {"explanation": content, "tokens_used": tokens_used or 0}
    except Exception:
        # Any error → safe fallback
        return {"explanation": _fallback_explanation(processed_text), "tokens_used": 0}
