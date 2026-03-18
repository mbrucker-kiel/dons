import json
from datetime import datetime

from app.extensions import db
from app.models import CateringOrder
from app.services.email import send_customer_confirmation, send_store_notification


def _parse_price(value):
    if value is None:
        return None
    text = str(value).strip().replace("€", "").replace(",", ".").replace("+", "")
    try:
        return float(text)
    except ValueError:
        return None


def _build_price_lookup(menu_data: dict) -> dict[str, str]:
    lookup = {}
    for category in menu_data.get("categories", []):
        for item in category.get("items", []):
            lookup[item.get("name", "")] = item.get("price", "")
    return lookup


def _build_item(name: str, qty: int, unit: str, price_raw: str, option_text: str = "") -> dict:
    unit_price = _parse_price(price_raw)
    if option_text:
        name = f"{name} ({option_text})"
    if unit_price is None:
        return {
            "name": name,
            "qty": qty,
            "unit": unit,
            "unit_price": None,
            "line_total": 0.0,
            "price_label": "Preis auf Anfrage",
        }
    line_total = round(unit_price * qty, 2)
    return {
        "name": name,
        "qty": qty,
        "unit": unit,
        "unit_price": unit_price,
        "line_total": line_total,
        "price_label": f"{line_total:.2f} €",
    }


def build_order_items(form_data: dict, menu_data: dict) -> list[dict]:
    items = []
    price_lookup = _build_price_lookup(menu_data)

    for index in [1, 2, 3]:
        bagel_qty = int(form_data.get(f"bagel_{index}_qty", 0) or 0)
        if bagel_qty <= 0:
            continue
        bagel_type = form_data.get(f"bagel_{index}_type", "Bagel")
        bread = form_data.get(f"bagel_{index}_bread", "")
        option_text = (
            f"Typ: {bagel_type}, Brot: {bread}"
            if bread
            else f"Typ: {bagel_type}"
        )
        bagel_price = price_lookup.get(bagel_type, "")
        items.append(
            _build_item(
                name="Bagel",
                qty=bagel_qty,
                unit="Stück",
                price_raw=bagel_price,
                option_text=option_text,
            )
        )

    zimtschnecke_qty = int(form_data.get("zimtschnecke_qty", 0) or 0)
    if zimtschnecke_qty > 0:
        items.append(
            _build_item(
                name="Zimtschnecke",
                qty=zimtschnecke_qty,
                unit="Stück",
                price_raw=price_lookup.get("Zimtschnecke", ""),
                option_text=f"Typ: {form_data.get('zimtschnecke_type', '')}",
            )
        )

    kuchen_qty = int(form_data.get("kuchen_qty", 0) or 0)
    if kuchen_qty > 0:
        items.append(
            _build_item(
                name="Kuchen",
                qty=kuchen_qty,
                unit="Stück",
                price_raw=price_lookup.get("Stück Kuchen", ""),
                option_text=f"Typ: {form_data.get('kuchen_type', '')}",
            )
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
        if item["unit_price"] is None:
            lines.append(f"- {item['name']}: {item['qty']} x Preis auf Anfrage")
        else:
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
