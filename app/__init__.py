from flask import Flask

from pathlib import Path

from .config import Config
from .extensions import csrf, db, mail
from .routes.admin import admin_bp
from .routes.catering import catering_bp
from .routes.main import main_bp
from .routes.menu import menu_bp
from .utils.data_loader import load_yaml


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    Path(app.root_path).parent.joinpath("instance").mkdir(exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    app.config["BUSINESS_INFO"] = load_yaml(app.config["BUSINESS_DATA_FILE"])
    app.config["MENU_ITEMS"] = load_yaml(app.config["MENU_DATA_FILE"])
    app.config["CATERING_MENU_ITEMS"] = load_yaml(
        app.config["CATERING_DATA_FILE"]
    )

    app.register_blueprint(main_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(catering_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    return app
