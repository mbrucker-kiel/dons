import json
from datetime import datetime

from app.extensions import db
from app.models import CateringOrder
from app.services.email import send_customer_confirmation, send_store_notification


FORM_TO_MENU_SLUG = {
    "bagel_mix_qty": "bagel-platte-gemischt",
    "bagel_veggie_qty": "bagel-platte-vegetarisch",
    "coffee_package_qty": "kaffee-paket",
    "pastry_box_qty": "gebaeckbox",
    "seasonal_option_qty": "saisonale-option",
}


def build_order_items(form_data: dict, catering_items: dict) -> list[dict]:
    by_slug = {item["slug"]: item for item in catering_items["items"]}
    items = []
    for field_name, slug in FORM_TO_MENU_SLUG.items():
        qty = int(form_data.get(field_name, 0) or 0)
        if qty <= 0:
            continue
        menu_item = by_slug[slug]
        unit_price = float(menu_item["price"])
        items.append(
            {
                "slug": slug,
                "name": menu_item["name"],
                "qty": qty,
                "unit": menu_item.get("unit", "Stück"),
                "unit_price": unit_price,
                "line_total": round(unit_price * qty, 2),
            }
        )
    return items


def calculate_total(items: list[dict]) -> float:
    return round(sum(item["line_total"] for item in items), 2)


def create_order(form, items: list[dict], total: float) -> CateringOrder:
    pickup_datetime = datetime.combine(form.pickup_date.data, form.pickup_time.data)
    order = CateringOrder(
        customer_name=form.customer_name.data,
        company=form.company.data,
        email=form.email.data,
        phone=form.phone.data,
        pickup_datetime=pickup_datetime,
        item_payload=json.dumps(items, ensure_ascii=False),
        special_requests=form.special_requests.data,
        total_estimate=total,
        agb_accepted=bool(form.agb_accepted.data),
    )
    db.session.add(order)
    db.session.commit()
    return order


def build_email_summary(order: CateringOrder, items: list[dict], business_name: str) -> str:
    lines = [
        f"Neue Catering-Bestellung bei {business_name}",
        "",
        f"Bestellnummer: {order.id}",
        f"Name: {order.customer_name}",
        f"Firma: {order.company or '-'}",
        f"E-Mail: {order.email}",
        f"Telefon: {order.phone}",
        f"Abholung: {order.pickup_datetime.strftime('%d.%m.%Y %H:%M')} Uhr",
        "",
        "Positionen:",
    ]

    for item in items:
        lines.append(
            f"- {item['name']}: {item['qty']} x {item['unit_price']:.2f} € = {item['line_total']:.2f} €"
        )
    lines += ["", f"Gesamtsumme (geschätzt): {order.total_estimate:.2f} €", ""]
    lines.append(f"Besondere Wünsche: {order.special_requests or '-'}")
    lines.append("Hinweis: Zahlung erfolgt bei Abholung im Café.")

    return "\n".join(lines)


def notify_order(order: CateringOrder, items: list[dict], business_name: str) -> None:
    summary = build_email_summary(order, items, business_name)
    send_store_notification(summary)

    customer_text = (
        f"Vielen Dank für Ihre Bestellung bei {business_name}.\n\n"
        f"Ihre Bestellnummer: {order.id}\n"
        f"Abholung: {order.pickup_datetime.strftime('%d.%m.%Y %H:%M')} Uhr\n"
        f"Gesamtsumme (geschätzt): {order.total_estimate:.2f} €\n\n"
        "Bitte beachten Sie: Nur Abholung vor Ort, keine Lieferung. Zahlung bei Abholung.\n"
    )
    send_customer_confirmation(order.email, customer_text)
