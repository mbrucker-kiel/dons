import time
from collections import defaultdict, deque
from threading import Lock

from flask import Blueprint, jsonify, request, current_app

from app.extensions import csrf
from app.services.chatbot import chat

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/api")

_MAX_MESSAGE_LENGTH = 500
_RATE_LIMIT_REQUESTS = 10
_RATE_LIMIT_WINDOW = 60  # seconds

_rate_lock = Lock()
_rate_store: dict[str, deque] = defaultdict(deque)


def _is_rate_limited(ip: str) -> bool:
    """Returns True if the IP has exceeded the rate limit."""
    now = time.monotonic()
    with _rate_lock:
        timestamps = _rate_store[ip]
        while timestamps and timestamps[0] < now - _RATE_LIMIT_WINDOW:
            timestamps.popleft()
        if len(timestamps) >= _RATE_LIMIT_REQUESTS:
            return True
        timestamps.append(now)
        return False


@chatbot_bp.post("/chat")
@csrf.exempt
def chatbot_endpoint():
    # Only trust X-Forwarded-For from a local reverse proxy to prevent IP spoofing
    remote = request.remote_addr or ""
    if remote in ("127.0.0.1", "::1"):
        ip = request.headers.get("X-Forwarded-For", remote).split(",")[0].strip()
    else:
        ip = remote
    if _is_rate_limited(ip):
        return jsonify({"error": "Zu viele Anfragen. Bitte warte einen Moment."}), 429

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Leere Nachricht"}), 400
    if len(user_message) > _MAX_MESSAGE_LENGTH:
        return jsonify({"error": "Nachricht ist zu lang (max. 500 Zeichen)."}), 400

    reply = chat(
        user_message,
        business_info=current_app.config.get("BUSINESS_INFO"),
        menu_items=current_app.config.get("MENU_ITEMS"),
        base_url=current_app.config["OLLAMA_BASE_URL"],
        model=current_app.config["OLLAMA_MODEL"],
    )
    return jsonify({"reply": reply})
