from flask import Blueprint, current_app, render_template


menu_bp = Blueprint("menu", __name__, url_prefix="/speisekarte")


@menu_bp.get("")
def menu():
    return render_template(
        "menu.html",
        page_title="Speisekarte",
        menu_data=current_app.config["MENU_ITEMS"],
    )
