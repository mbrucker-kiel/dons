import json
from datetime import date, time

from app import create_app
from app.services.order import build_order_items, calculate_total


def test_build_order_items_and_total():
    app = create_app()
    with app.app_context():
        data = app.config["CATERING_MENU_ITEMS"]
        items = build_order_items({"bagel_mix_qty": 2, "coffee_package_qty": 1}, data)
        assert len(items) == 2
        assert calculate_total(items) > 0
