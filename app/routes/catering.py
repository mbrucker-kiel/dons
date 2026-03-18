import json

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for

from app.forms import CateringOrderForm
from app.models import CateringOrder
from app.services.order import build_order_items, calculate_total, create_order, notify_order


catering_bp = Blueprint("catering", __name__, url_prefix="/catering")


@catering_bp.get("")
def catering():
    return render_template(
        "catering/index.html",
        page_title="Catering",
        catering_data=current_app.config["CATERING_MENU_ITEMS"],
        min_order=current_app.config["MIN_ORDER_AMOUNT"],
        lead_time=current_app.config["LEAD_TIME_HOURS"],
    )


@catering_bp.route("/bestellen", methods=["GET", "POST"])
def order():
    form = CateringOrderForm()
    catering_data = current_app.config["CATERING_MENU_ITEMS"]

    preview_items = build_order_items(form.data, catering_data)
    preview_total = calculate_total(preview_items)

    if form.validate_on_submit():
        items = build_order_items(form.data, catering_data)
        total = calculate_total(items)

        if total < current_app.config["MIN_ORDER_AMOUNT"]:
            flash(
                f"Der Mindestbestellwert beträgt {current_app.config['MIN_ORDER_AMOUNT']:.2f} €.",
                "error",
            )
            return render_template(
                "catering/order.html",
                page_title="Catering bestellen",
                form=form,
                catering_data=catering_data,
                preview_items=items,
                preview_total=total,
            )

        order_obj = create_order(form, items, total)
        notify_order(order_obj, items, current_app.config["BUSINESS_INFO"]["name"])
        session["last_order_items"] = json.dumps(items, ensure_ascii=False)
        return redirect(url_for("catering.confirmation", order_id=order_obj.id))

    return render_template(
        "catering/order.html",
        page_title="Catering bestellen",
        form=form,
        catering_data=catering_data,
        preview_items=preview_items,
        preview_total=preview_total,
    )


@catering_bp.get("/bestaetigung/<int:order_id>")
def confirmation(order_id: int):
    order_obj = CateringOrder.query.get_or_404(order_id)
    items = json.loads(order_obj.item_payload)
    return render_template(
        "catering/confirmation.html",
        page_title="Bestätigung",
        order=order_obj,
        items=items,
    )
