# Project: Don's Café & Bistro — Online Web Presence & Catering Order System

## 🏪 Business Information

- **Name:** Don's Café & Bistro
- **Address:** Dreieckspl. 10, 24103 Kiel, Germany
- **Phone:** 0178 9303643
- **Instagram:** https://www.instagram.com/dons.cafe.bistro/
- **Type:** Local café and bagel manufacturer in Kiel, Germany

### Opening Hours

| Day       | Hours         |
|-----------|--------------|
| Monday    | Closed        |
| Tuesday   | 10 am – 6 pm |
| Wednesday | 10 am – 6 pm |
| Thursday  | 10 am – 6 pm |
| Friday    | 10 am – 6 pm |
| Saturday  | 11 am – 6 pm |
| Sunday    | 11 am – 6 pm |

---

## 🎯 Project Goals

Build a modern, responsive website for a local café in Kiel, Germany that serves two primary purposes:

1. **Informational presence** — Showcase the café, its story, menu, location, and contact details.
2. **Catering order system** — Allow customers (especially businesses) to browse a catering menu and place pickup orders online. **No delivery service.** All orders are for **in-store pickup only.**

---

## 📄 Pages & Sections

### 1. **Home / Landing Page**
- Hero section with appetizing imagery (placeholder images are fine) and tagline
- Brief welcome message / about snippet
- Opening hours widget
- Call-to-action buttons: "Speisekarte", "Catering bestellen", "So finden Sie uns"
- Instagram feed embed or link to https://www.instagram.com/dons.cafe.bistro/

### 2. **Über uns (About Us)**
- Story of Don's Café & Bistro (use placeholder text, mark as `[OWNER TO FILL IN]`)
- Information about the owner / team (placeholder with `[OWNER TO FILL IN]`)
- Photos section (placeholders)
- The café's philosophy: fresh bagels, local ingredients, community focus

### 3. **Speisekarte (Menu)**
- Display the café's regular menu organized by categories:
  - Bagels & Sandwiches
  - Kaffee & Heißgetränke
  - Kaltgetränke
  - Gebäck & Süßes
  - Specials / Saisonales
- Each item should have: name, short description, price, optional dietary tags (vegan, vegetarisch, glutenfrei)
- Use placeholder menu items that are realistic for a German café/bagel shop
- Menu data should be easily editable (stored in YAML, JSON, or Python data files)

### 4. **Catering Section** ⭐ (Core Feature)
- **Catering landing page** explaining the service:
  - Available for business events, meetings, private parties
  - Pickup only at the store (clearly stated)
  - Minimum order requirements (configurable, e.g., `[MINDESTBESTELLUNG: €50]`)
  - Lead time required (e.g., "Bitte bestellen Sie mindestens 48 Stunden im Voraus")
- **Catering Menu** — separate from the daily menu, with catering-specific items:
  - Bagel-Platten (gemischt, vegetarisch, etc.)
  - Kaffee-/Getränkepakete
  - Gebäckboxen
  - Individuelle / saisonale Optionen
  - Each item: name, description, price (pro Person or pro Stück), photo placeholder
- **Catering Order Form:**
  - Customer info: Name, Firma (optional), E-Mail, Telefon
  - Desired pickup date & time (with validation against opening hours)
  - Item selection with quantities
  - Special requests / dietary notes (free text)
  - Order summary with estimated total
  - Terms & conditions checkbox (AGB)
  - Submit button → sends order via email notification (to the store) and confirmation email (to the customer)
  - **No online payment required** — payment is handled at pickup
  - After submission: confirmation page with order summary and pickup details

### 5. **Kontakt & Anfahrt (Contact & Location)**
- Address with embedded map (Google Maps or OpenStreetMap)
- Phone number (clickable on mobile)
- Email address (placeholder: `[EMAIL]`)
- Instagram link
- Contact form for general inquiries
- Opening hours

### 6. **Legal Pages** (Required for German websites)
- **Impressum** (Legal Notice) — placeholder structure per German TMG/DDG requirements
- **Datenschutzerklärung** (Privacy Policy) — placeholder structure per GDPR/DSGVO
- Mark both as `[MUST BE REVIEWED BY LEGAL COUNSEL]`

---

## 🛠 Technical Requirements

### Stack
- **Backend:** Python 3.11+ with **Flask** (or **FastAPI** if preferred)
- **Templating:** Jinja2 templates
- **Frontend Styling:** Tailwind CSS (via CDN or build step) with a warm, inviting color palette (earth tones, cream, coffee browns)
- **Forms:** WTForms (Flask-WTF) for form handling and CSRF protection
- **Database:** SQLite via **SQLAlchemy** (lightweight, no external DB server needed) for storing catering orders
- **Email:** **Flask-Mail** or `smtplib` for sending order notifications and confirmations (SMTP config via environment variables)
- **Language:** The website should be in **German** as the primary language. Use proper German for all UI text, labels, buttons, and placeholder content.
- **Responsive:** Fully mobile-first responsive design
- **Accessibility:** WCAG 2.1 AA compliant (proper heading hierarchy, alt texts, contrast ratios, keyboard navigation)

### Data Management
- Menu items and catering items stored in **YAML or JSON** data files, loaded at startup
- Opening hours stored in a config file (`config.py` or `data/hours.yaml`)
- Business info (name, address, phone, etc.) in a central `config.py` or `data/business.yaml`
- Catering orders persisted in SQLite database

### Catering Order Handling
- Form validated server-side with WTForms
- On valid submission:
  1. Save order to SQLite database
  2. Send email notification to the store owner
  3. Send confirmation email to the customer with order summary
  4. Redirect to confirmation page
- Admin route (basic, password-protected) to view recent orders: `/admin/orders`

### SEO & Performance
- Proper meta tags, Open Graph tags
- JSON-LD structured data for `LocalBusiness` schema
- Sitemap.xml route and robots.txt
- Optimized static asset serving

### Deployment
- Ready for deployment on **Railway**, **Render**, **Fly.io**, or any Python hosting
- `requirements.txt` and/or `pyproject.toml` with all dependencies
- `.env.example` file documenting required environment variables
- `Dockerfile` for containerized deployment (optional but nice to have)
- **Gunicorn** as production WSGI server

---

## 🎨 Design Guidelines

- **Tone:** Warm, welcoming, artisanal, local — think cozy neighborhood café
- **Typography:** Clean, readable. A mix of a warm serif/display font for headings (e.g., Playfair Display) and a clean sans-serif for body text (e.g., Inter)
- **Colors:** Earth tones — warm browns (#6F4E37), creams (#FFF8F0), olive greens (#606C38), with an accent color (e.g., terracotta #C2703E or mustard #E6A817)
- **Imagery:** Use placeholder images from Unsplash or similar (café, bagels, coffee). Mark as `[REPLACE WITH ACTUAL PHOTOS]`
- **Logo:** Use a text-based placeholder logo: "Don's Café & Bistro"

---

## 📁 Project Structure

```
dons-cafe-bistro/
├── app/
│   ├── __init__.py            # Flask app factory
│   ├── config.py              # App configuration & environment variables
│   ├── models.py              # SQLAlchemy models (CateringOrder, etc.)
│   ├── forms.py               # WTForms form classes
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py            # Home, About, Contact, Legal pages
│   │   ├── menu.py            # Menu page
│   │   ├── catering.py        # Catering info, menu, order form
│   │   └── admin.py           # Basic admin order view
│   ├── services/
│   │   ├── __init__.py
│   │   ├── email.py           # Email sending utility
│   │   └── order.py           # Order processing logic
│   ├── templates/
│   │   ├── base.html          # Base template with header/footer/nav
│   │   ├── index.html         # Home page
│   │   ├── about.html         # Über uns
│   │   ├── menu.html          # Speisekarte
│   │   ├── catering/
│   │   │   ├── index.html     # Catering overview + menu
│   │   │   ├── order.html     # Order form
│   │   │   └── confirmation.html  # Order confirmation
│   │   ├── contact.html       # Kontakt & Anfahrt
│   │   ├── impressum.html     # Legal notice
│   │   ├── datenschutz.html   # Privacy policy
│   │   ├── admin/
│   │   │   └── orders.html    # Admin order list
│   │   └── components/
│   │       ├── hours.html     # Opening hours partial
│   │       ├── map.html       # Embedded map partial
│   │       └── menu_item.html # Menu item card partial
│   └── static/
│       ├── css/
│       │   └── style.css      # Custom styles + Tailwind
│       ├── js/
│       │   └── main.js        # Minimal JS (form validation, interactivity)
│       └── images/            # Placeholder images
├── data/
│   ├── menu.yaml              # Regular menu items
│   ├── catering_menu.yaml     # Catering menu items
│   └── business.yaml          # Store info, hours, contact
├── migrations/                # Flask-Migrate / Alembic (optional)
├── tests/
│   ├── __init__.py
│   ├── test_routes.py
│   ├── test_forms.py
│   └── test_orders.py
├── .env.example               # Environment variable template
├── .gitignore
├── Dockerfile                 # Container deployment
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project metadata
├── run.py                     # Entry point: python run.py
└── README.md                  # Setup & deployment instructions
```

---

## ✅ Summary of Key Constraints

- 🇩🇪 **German language** UI and content
- 🐍 **Python/Flask** backend with Jinja2 templates
- 🏬 **Pickup only** — no delivery, clearly communicated
- 💳 **No online payment** — payment at pickup
- 📧 **Email-based order notifications** + SQLite order storage
- 🔐 **Basic admin view** for orders (password-protected)
- ⚖️ **German legal compliance** — Impressum & Datenschutz pages (placeholder)
- 📱 **Mobile-first** responsive design
- 🔧 **Easy content editing** — menu/prices in YAML data files, not hardcoded in templates

Please generate the complete codebase for this project, starting with the project setup, configuration files, data files, models, then all routes, templates, and static assets.