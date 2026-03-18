from datetime import datetime, timedelta

from app import create_app
from app.forms import CateringOrderForm


def test_catering_form_has_fields():
    app = create_app()
    with app.test_request_context("/catering/bestellen"):
        form = CateringOrderForm()
        assert hasattr(form, "customer_name")
        assert hasattr(form, "pickup_date")


def test_pickup_date_in_future_required():
    app = create_app()
    with app.test_request_context("/catering/bestellen", method="POST"):
        form = CateringOrderForm(
            data={
                "customer_name": "Max Mustermann",
                "email": "max@example.com",
                "phone": "01234",
                "pickup_date": datetime.now().date() + timedelta(days=1),
                "pickup_time": datetime.now().time(),
                "bagel_mix_qty": 1,
                "agb_accepted": True,
            }
        )
        assert form.validate() is False
