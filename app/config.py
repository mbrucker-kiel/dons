import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'dons.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@dons-cafe.de")

    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me")
    STORE_NOTIFICATION_EMAIL = os.getenv("STORE_NOTIFICATION_EMAIL", "[EMAIL]")
    PUBLIC_CONTACT_EMAIL = os.getenv("PUBLIC_CONTACT_EMAIL", "[EMAIL]")

    MIN_ORDER_AMOUNT = float(os.getenv("MIN_ORDER_AMOUNT", "50"))
    LEAD_TIME_HOURS = int(os.getenv("LEAD_TIME_HOURS", "48"))

    BUSINESS_DATA_FILE = BASE_DIR / "data" / "business.yaml"
    MENU_DATA_FILE = BASE_DIR / "data" / "menu.yaml"
    CATERING_DATA_FILE = BASE_DIR / "data" / "catering_menu.yaml"
