import json
from datetime import datetime, timedelta

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    EmailField,
    HiddenField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TelField,
    TextAreaField,
    TimeField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)


GERMAN_WEEKDAY = {
    0: "Montag",
    1: "Dienstag",
    2: "Mittwoch",
    3: "Donnerstag",
    4: "Freitag",
    5: "Samstag",
    6: "Sonntag",
}


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email = EmailField("E-Mail", validators=[DataRequired(), Email(), Length(max=255)])
    phone = TelField("Telefon (optional)", validators=[Optional(), Length(max=50)])
    message = TextAreaField("Nachricht", validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField("Nachricht senden")


class AdminLoginForm(FlaskForm):
    password = StringField("Passwort", validators=[DataRequired(), Length(max=255)])
    submit = SubmitField("Einloggen")


class CateringOrderForm(FlaskForm):
    customer_name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    company = StringField("Firma (optional)", validators=[Optional(), Length(max=120)])
    email = EmailField("E-Mail", validators=[DataRequired(), Email(), Length(max=255)])
    phone = TelField("Telefon", validators=[DataRequired(), Length(max=50)])
    pickup_date = DateField("Abholdatum", validators=[InputRequired()], format="%Y-%m-%d")
    pickup_time = TimeField("Abholzeit", validators=[InputRequired()], format="%H:%M")
    special_requests = TextAreaField(
        "Besondere Wünsche / Allergene",
        validators=[Optional(), Length(max=2000)],
    )
    bagel_rows_json = HiddenField("Bagel-Auswahl (JSON)", default="[]")
    zimtschnecke_qty = IntegerField(
        "Zimtschnecken (Anzahl)",
        default=0,
        validators=[NumberRange(min=0, max=200)],
    )
    zimtschnecke_type = StringField(
        "Zimtschnecken-Typ",
        validators=[Optional(), Length(max=120)],
    )
    kuchen_qty = IntegerField(
        "Kuchen (Anzahl Stück)",
        default=0,
        validators=[NumberRange(min=0, max=200)],
    )
    kuchen_type = StringField(
        "Kuchen-Typ",
        validators=[Optional(), Length(max=120)],
    )
    agb_accepted = BooleanField("AGB akzeptiert", validators=[DataRequired()])
    submit = SubmitField("Verbindlich bestellen")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        menu_data = current_app.config.get("MENU_ITEMS", {})
        bagel_names = []
        for category in menu_data.get("categories", []):
            if category.get("title") != "Bagels & Sandwiches":
                continue
            for item in category.get("items", []):
                item_name = item.get("name", "")
                if "Auswahl" in item_name or item_name.startswith("Extra"):
                    continue
                bagel_names.append(item_name)
        self.bagel_choices = [("", "Bitte wählen")] + [
            (name, name) for name in bagel_names
        ]

    def validate_pickup_date(self, field):
        earliest = datetime.now() + timedelta(hours=current_app.config["LEAD_TIME_HOURS"])
        if field.data < earliest.date():
            raise ValidationError(
                f"Bitte mindestens {current_app.config['LEAD_TIME_HOURS']} Stunden im Voraus bestellen."
            )

    def validate(self, extra_validators=None):
        valid = super().validate(extra_validators=extra_validators)
        if not valid:
            return False

        if not self.agb_accepted.data:
            self.agb_accepted.errors.append("Bitte akzeptieren Sie die AGB.")
            return False

        try:
            bagel_rows = json.loads(self.bagel_rows_json.data or "[]")
            if not isinstance(bagel_rows, list):
                raise ValueError
        except (ValueError, TypeError):
            self.bagel_rows_json.errors.append("Ungültige Bagel-Daten.")
            return False

        bagel_total = 0
        for row in bagel_rows:
            qty = int(row.get("qty", 0) or 0)
            if qty <= 0:
                continue
            if not row.get("type"):
                self.bagel_rows_json.errors.append("Bitte einen Bagel-Typ auswählen.")
                return False
            if not row.get("bread"):
                self.bagel_rows_json.errors.append("Bitte eine Bagel-Brotart auswählen.")
                return False
            bagel_total += qty

        zimtschnecke_qty = int(self.zimtschnecke_qty.data or 0)
        kuchen_qty = int(self.kuchen_qty.data or 0)
        total_qty = bagel_total + zimtschnecke_qty + kuchen_qty
        if total_qty <= 0:
            self.submit.errors.append("Bitte wählen Sie mindestens einen Catering-Artikel aus.")
            return False

        if zimtschnecke_qty > 0 and not self.zimtschnecke_type.data:
            self.zimtschnecke_type.errors.append("Bitte den Zimtschnecken-Typ angeben.")
            return False

        if kuchen_qty > 0 and not self.kuchen_type.data:
            self.kuchen_type.errors.append("Bitte den Kuchen-Typ angeben.")
            return False

        pickup_dt = datetime.combine(self.pickup_date.data, self.pickup_time.data)
        earliest = datetime.now() + timedelta(hours=current_app.config["LEAD_TIME_HOURS"])
        if pickup_dt < earliest:
            self.pickup_time.errors.append(
                f"Abholung muss mindestens {current_app.config['LEAD_TIME_HOURS']} Stunden in der Zukunft liegen."
            )
            return False

        hours = current_app.config["BUSINESS_INFO"].get("opening_hours", {})
        weekday_name = GERMAN_WEEKDAY[pickup_dt.weekday()]
        slot = hours.get(weekday_name, "geschlossen")
        if slot == "geschlossen":
            self.pickup_date.errors.append("An diesem Tag ist das Café geschlossen.")
            return False

        try:
            opening, closing = [part.strip() for part in slot.split("-")]
            open_h, open_m = [int(val) for val in opening.split(":")]
            close_h, close_m = [int(val) for val in closing.split(":")]
            open_minutes = open_h * 60 + open_m
            close_minutes = close_h * 60 + close_m
            pickup_minutes = pickup_dt.hour * 60 + pickup_dt.minute
            if pickup_minutes < open_minutes or pickup_minutes > close_minutes:
                self.pickup_time.errors.append(
                    f"Abholung nur innerhalb der Öffnungszeiten möglich ({slot} Uhr)."
                )
                return False
        except ValueError:
            self.pickup_time.errors.append("Öffnungszeiten konnten nicht geprüft werden.")
            return False

        return True
