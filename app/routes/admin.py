import json

from flask import Blueprint, current_app, redirect, render_template, session, url_for

from app.forms import AdminLoginForm
from app.models import CateringOrder


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _is_authenticated() -> bool:
    return bool(session.get("admin_authenticated"))


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    form = AdminLoginForm()
    error = None
    if form.validate_on_submit():
        if form.password.data == current_app.config["ADMIN_PASSWORD"]:
            session["admin_authenticated"] = True
            return redirect(url_for("admin.orders"))
        error = "Ungültiges Passwort."
    return render_template("admin/login.html", page_title="Admin Login", form=form, error=error)


@admin_bp.get("/logout")
def logout():
    session.pop("admin_authenticated", None)
    return redirect(url_for("admin.login"))


@admin_bp.get("/orders")
def orders():
    if not _is_authenticated():
        return redirect(url_for("admin.login"))

    latest_orders = CateringOrder.query.order_by(CateringOrder.created_at.desc()).limit(100).all()
    order_view = []
    for order in latest_orders:
        order_view.append({"order": order, "items": json.loads(order.item_payload)})

    return render_template("admin/orders.html", page_title="Admin Bestellungen", order_view=order_view)


@admin_bp.get("")
def admin_root():
    return redirect(url_for("admin.orders"))
