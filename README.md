# Don's Café & Bistro

Moderne Flask-Webseite für Don's Café & Bistro (Kiel) mit:

- Informationsseiten (Start, Über uns, Speisekarte, Kontakt)
- Catering-Bereich mit Online-Bestellformular (nur Abholung)
- Speicherung von Bestellungen in SQLite
- E-Mail-Benachrichtigung an Café + Bestätigungs-E-Mail an Kund:innen
- Admin-Ansicht für eingegangene Bestellungen

## Schnellstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Dann öffnen: `http://127.0.0.1:5000`

## Wichtige Routen

- `/` Startseite
- `/ueber-uns`
- `/speisekarte`
- `/catering`
- `/catering/bestellen`
- `/kontakt`
- `/impressum`
- `/datenschutz`
- `/admin/login`
- `/admin/orders`

## Produktion

Lokaler Gunicorn-Start:

```bash
gunicorn -w 2 -b 0.0.0.0:8000 run:app
```

Container:

```bash
docker build -t dons-cafe .
docker run --env-file .env -p 8000:8000 dons-cafe
```

## Rechtliches

Die Seiten `Impressum` und `Datenschutzerklärung` enthalten Platzhalter und sind vor Livegang juristisch prüfen zu lassen.
