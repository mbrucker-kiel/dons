from flask import Blueprint, Response, current_app, render_template, request

from app.extensions import db
from app.forms import ContactForm
from app.models import ContactInquiry


main_bp = Blueprint("main", __name__)


@main_bp.app_context_processor
def inject_business_info():
    return {
        "business": current_app.config["BUSINESS_INFO"],
        "public_contact_email": current_app.config["PUBLIC_CONTACT_EMAIL"],
    }


@main_bp.get("/")
def index():
    return render_template("index.html", page_title="Startseite")


@main_bp.get("/ueber-uns")
def about():
    return render_template("about.html", page_title="Über uns")


@main_bp.route("/kontakt", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    success = False

    if form.validate_on_submit():
        inquiry = ContactInquiry(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            message=form.message.data,
        )
        db.session.add(inquiry)
        db.session.commit()
        success = True
        form = ContactForm(formdata=None)

    return render_template("contact.html", page_title="Kontakt & Anfahrt", form=form, success=success)


@main_bp.get("/impressum")
def impressum():
    return render_template("impressum.html", page_title="Impressum")


@main_bp.get("/datenschutz")
def datenschutz():
    return render_template("datenschutz.html", page_title="Datenschutz")


@main_bp.get("/robots.txt")
def robots():
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.url_root.rstrip('/')}/sitemap.xml",
    ]
    return Response("\n".join(lines), mimetype="text/plain")


@main_bp.get("/sitemap.xml")
def sitemap():
    pages = [
        ("main.index", {}),
        ("main.about", {}),
        ("menu.menu", {}),
        ("catering.catering", {}),
        ("catering.order", {}),
        ("main.contact", {}),
        ("main.impressum", {}),
        ("main.datenschutz", {}),
    ]
    return render_template("sitemap.xml", pages=pages), 200, {"Content-Type": "application/xml"}
