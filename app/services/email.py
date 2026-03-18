from flask import current_app
from flask_mail import Message

from app.extensions import mail


def _send(subject: str, recipients: list[str], body: str) -> None:
    if not current_app.config["MAIL_USERNAME"]:
        current_app.logger.warning("MAIL_USERNAME nicht gesetzt. E-Mail Versand wird übersprungen.")
        return

    message = Message(subject=subject, recipients=recipients, body=body)
    mail.send(message)


def send_store_notification(body: str) -> None:
    _send(
        subject="Neue Catering-Bestellung bei Don's Café & Bistro",
        recipients=[current_app.config["STORE_NOTIFICATION_EMAIL"]],
        body=body,
    )


def send_customer_confirmation(customer_email: str, body: str) -> None:
    _send(
        subject="Ihre Catering-Bestellung bei Don's Café & Bistro",
        recipients=[customer_email],
        body=body,
    )
