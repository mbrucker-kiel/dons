import logging
import os
import re

import requests

logger = logging.getLogger(__name__)

_LLM_TIMEOUT = 30  # seconds

_BASE_SYSTEM_PROMPT = """Du bist ein freundlicher Assistent für Don's Café & Catering.
Du beantwortest Fragen zu unserem Menü, Catering-Angeboten, Öffnungszeiten und Bestellungen.
Antworte immer auf Deutsch, kurz und hilfsbereit."""


def _strip_think_tags(text: str) -> str:
    """Entfernt <think>...</think>-Blöcke aus dem Antworttext (Chain-of-Thought)."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def build_system_prompt(business: dict | None = None, menu: dict | None = None) -> str:
    """Erstellt den System-Prompt inklusive Geschäftsinformationen und Speisekarte."""
    parts = [_BASE_SYSTEM_PROMPT]

    if business:
        hours_lines = "\n".join(
            f"  {day}: {time}" for day, time in (business.get("opening_hours") or {}).items()
        )
        parts.append(
            f"\n## Geschäftsinformationen\n"
            f"Name: {business.get('name', '')}\n"
            f"Adresse: {business.get('address', '')}\n"
            f"Telefon: {business.get('phone', '')}\n"
            f"Beschreibung: {business.get('description', '')}\n"
            f"Öffnungszeiten:\n{hours_lines}"
        )

    if menu:
        menu_lines = ["\n## Speisekarte"]
        for category in menu.get("categories", []):
            menu_lines.append(f"\n### {category['title']}")
            for item in category.get("items", []):
                tags = ", ".join(item.get("tags", []))
                tag_str = f" [{tags}]" if tags else ""
                price = item.get("price", "")
                try:
                    float(price.lstrip("+"))
                    price_str = f"{price}€"
                except (ValueError, AttributeError):
                    price_str = price
                menu_lines.append(
                    f"- {item['name']}: {item.get('description', '')} – {price_str}{tag_str}"
                )
        parts.append("\n".join(menu_lines))

    return "\n".join(parts)


def chat(
    user_message: str,
    business_info: dict | None = None,
    menu_items: dict | None = None,
) -> str:
    """Sendet eine Nachricht an den Ollama-Server und gibt die bereinigte Antwort zurück."""
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    model = os.environ.get("OLLAMA_MODEL", "deepseek-r1:8b")
    url = f"{base_url}/api/chat"
    system_prompt = build_system_prompt(business_info, menu_items)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
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
