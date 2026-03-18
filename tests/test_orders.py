import json
from datetime import date, time

from app import create_app
from app.services.order import build_order_items, calculate_total


def test_build_order_items_and_total():
    app = create_app()
    with app.app_context():
        data = app.config["MENU_ITEMS"]
        items = build_order_items(
            {
                "bagel_rows_json": json.dumps([
                    {"qty": 2, "type": "Cheddar", "bread": "Sesam"},
                ]),
                "zimtschnecke_qty": 1,
                "zimtschnecke_type": "Classic",
            },
            data,
        )
        assert len(items) >= 1
        assert calculate_total(items) > 0
