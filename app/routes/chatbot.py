from flask import Blueprint, jsonify, request, current_app

from app.extensions import csrf
from app.services.chatbot import chat

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/api")


@chatbot_bp.post("/chat")
@csrf.exempt
def chatbot_endpoint():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Leere Nachricht"}), 400
    reply = chat(
        user_message,
        business_info=current_app.config.get("BUSINESS_INFO"),
        menu_items=current_app.config.get("MENU_ITEMS"),
    )
    return jsonify({"reply": reply})
