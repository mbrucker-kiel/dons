import logging
import os
import re

import requests

logger = logging.getLogger(__name__)

_LLM_TIMEOUT = 30  # seconds

SYSTEM_PROMPT = """Du bist ein freundlicher Assistent für Don's Café & Catering.
Du beantwortest Fragen zu unserem Menü, Catering-Angeboten, Öffnungszeiten und Bestellungen.
Antworte immer auf Deutsch, kurz und hilfsbereit."""


def _strip_think_tags(text: str) -> str:
    """Entfernt <think>...</think>-Blöcke aus dem Antworttext (Chain-of-Thought)."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def chat(user_message: str) -> str:
    """Sendet eine Nachricht an den Ollama-Server und gibt die bereinigte Antwort zurück."""
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.environ.get("OLLAMA_MODEL", "deepseek-r1:8b")
    url = f"{base_url}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "stream": False,
    }
    try:
        resp = requests.post(url, json=payload, timeout=_LLM_TIMEOUT)
        resp.raise_for_status()
        content = resp.json()["message"]["content"]
        return _strip_think_tags(content)
    except requests.exceptions.ConnectionError as exc:
        logger.warning(
            "LLM server unreachable at %s (model=%s): %s",
            url,
            model,
            exc,
        )
        return "Der Chatbot ist gerade nicht verfügbar (LLM-Server nicht erreichbar)."
    except requests.exceptions.Timeout as exc:
        logger.warning(
            "LLM request timed out after %d s (url=%s, model=%s): %s",
            _LLM_TIMEOUT,
            url,
            model,
            exc,
        )
        return "Der Chatbot antwortet gerade nicht (Timeout). Bitte versuche es später erneut."
    except requests.exceptions.HTTPError as exc:
        logger.error(
            "LLM server returned HTTP %s (url=%s, model=%s): %s",
            exc.response.status_code if exc.response is not None else "unknown",
            url,
            model,
            exc,
        )
        return "Es ist ein Fehler aufgetreten. Bitte versuche es später erneut."
    except Exception:
        logger.exception(
            "Unexpected error while calling LLM (url=%s, model=%s)",
            url,
            model,
        )
        return "Es ist ein Fehler aufgetreten. Bitte versuche es später erneut."
