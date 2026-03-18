from datetime import datetime

from .extensions import db


class CateringOrder(db.Model):
    __tablename__ = "catering_orders"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    pickup_datetime = db.Column(db.DateTime, nullable=False)
    item_payload = db.Column(db.Text, nullable=False)
    special_requests = db.Column(db.Text, nullable=True)
    total_estimate = db.Column(db.Float, nullable=False, default=0.0)
    agb_accepted = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(30), nullable=False, default="neu")


class ContactInquiry(db.Model):
    __tablename__ = "contact_inquiries"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    message = db.Column(db.Text, nullable=False)
