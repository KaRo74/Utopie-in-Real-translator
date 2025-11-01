# UiR – Multilingual PDF Generator

Web-App, die Texte ins UiR-Standardlayout rendert (Creme/Lila/Hope-Grün), optional übersetzt und als PDF (oder ZIP) ausgibt. Arabisch = RTL, Logo links, Kontaktblock rechts.

## Start (lokal)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

## Schriften
Lege in `./fonts/` ab:
- DejaVuSans.ttf
- Amiri-Regular.ttf
- NotoSansCJKsc-Regular.otf

## Deploy
- Hugging Face Spaces (Streamlit)
- Replit / Codespaces

## Hinweis Übersetzung
Optional via Hugging Face `transformers`. Ohne Token läuft ggf. langsamer/limitiert. Für marginalisierte Sprachen ggf. Text direkt in Zielsprache einfügen.