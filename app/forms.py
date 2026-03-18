from datetime import datetime, timedelta

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    EmailField,
    IntegerField,
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
    special_requests = TextAreaField("Besondere Wünsche / Allergene", validators=[Optional(), Length(max=2000)])
    bagel_mix_qty = IntegerField("Bagel-Platte Gemischt", default=0, validators=[NumberRange(min=0, max=200)])
    bagel_veggie_qty = IntegerField("Bagel-Platte Vegetarisch", default=0, validators=[NumberRange(min=0, max=200)])
    coffee_package_qty = IntegerField("Kaffee-Paket", default=0, validators=[NumberRange(min=0, max=200)])
    pastry_box_qty = IntegerField("Gebäckbox", default=0, validators=[NumberRange(min=0, max=200)])
    seasonal_option_qty = IntegerField("Saisonale Option", default=0, validators=[NumberRange(min=0, max=200)])
    agb_accepted = BooleanField("AGB akzeptiert", validators=[DataRequired()])
    submit = SubmitField("Verbindlich bestellen")

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

        total_qty = sum(
            q or 0
            for q in [
                self.bagel_mix_qty.data,
                self.bagel_veggie_qty.data,
                self.coffee_package_qty.data,
                self.pastry_box_qty.data,
                self.seasonal_option_qty.data,
            ]
        )
        if total_qty <= 0:
            self.submit.errors.append("Bitte wählen Sie mindestens einen Catering-Artikel aus.")
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
