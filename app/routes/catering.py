import json

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for

from app.forms import CateringOrderForm
from app.models import CateringOrder
from app.services.order import build_order_items, calculate_total, create_order, notify_order


catering_bp = Blueprint("catering", __name__, url_prefix="/catering")


def _parse_price(value):
    if value is None:
        return None
    text = str(value).strip().replace("€", "").replace(",", ".").replace("+", "")
    try:
        return float(text)
    except ValueError:
        return None


def _bagel_price_map(menu_data: dict) -> dict[str, float]:
    prices: dict[str, float] = {}
    for category in menu_data.get("categories", []):
        if category.get("title") != "Bagels & Sandwiches":
            continue
        for item in category.get("items", []):
            name = item.get("name", "")
            if "Auswahl" in name or name.startswith("Extra"):
                continue
            parsed = _parse_price(item.get("price"))
            if parsed is not None:
                prices[name] = parsed
    return prices


@catering_bp.get("")
def catering():
    return render_template(
        "catering/index.html",
        page_title="Catering",
        min_order=current_app.config["MIN_ORDER_AMOUNT"],
        lead_time=current_app.config["LEAD_TIME_HOURS"],
    )


@catering_bp.route("/bestellen", methods=["GET", "POST"])
def order():
    form = CateringOrderForm()
    menu_data = current_app.config["MENU_ITEMS"]
    bagel_prices = _bagel_price_map(menu_data)

    preview_items = build_order_items(form.data, menu_data)
    preview_total = calculate_total(preview_items)

    if form.validate_on_submit():
        items = build_order_items(form.data, menu_data)
        total = calculate_total(items)

        if 0 < total < current_app.config["MIN_ORDER_AMOUNT"]:
            flash(
                f"Der Mindestbestellwert beträgt {current_app.config['MIN_ORDER_AMOUNT']:.2f} €.",
                "error",
            )
            return render_template(
                "catering/order.html",
                page_title="Catering bestellen",
                form=form,
                preview_items=items,
                preview_total=total,
                bagel_prices=bagel_prices,
            )

        order_obj = create_order(form, items, total)
        notify_order(order_obj, items, current_app.config["BUSINESS_INFO"]["name"])
        session["last_order_items"] = json.dumps(items, ensure_ascii=False)
        return redirect(url_for("catering.confirmation", order_id=order_obj.id))

    return render_template(
        "catering/order.html",
        page_title="Catering bestellen",
        form=form,
        preview_items=preview_items,
        preview_total=preview_total,
        bagel_prices=bagel_prices,
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
