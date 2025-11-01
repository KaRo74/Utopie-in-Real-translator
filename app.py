import io, zipfile, datetime, base64, textwrap
from pathlib import Path

import streamlit as st

# ---- PDF / Fonts ----
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

# RTL support
try:
    import arabic_reshaper, bidi.algorithm
    HAS_AR = True
except Exception:
    HAS_AR = False

# -------------- UiR CONSTANTS --------------
UIR_BG = HexColor("#FFFDF5")
UIR_LILA = HexColor("#8A2BE2")
UIR_HOPE = HexColor("#00A86B")

PAGE_W, PAGE_H = A4  # 595 x 842 pt

FONTS_DIR = Path("fonts")
# Fonts: put files into ./fonts/
FONT_LATIN = str(FONTS_DIR / "DejaVuSans.ttf")
FONT_AR = str(FONTS_DIR / "Amiri-Regular.ttf")
FONT_CJK = str(FONTS_DIR / "NotoSansCJKsc-Regular.otf")  # Simplified Chinese
# Fallback chain per language
LANG_CFG = {
    "ar": {"rtl": True, "font": FONT_AR, "name": "العربية"},
    "zh": {"rtl": False, "font": FONT_CJK, "name": "中文（简体）"},
    "de": {"rtl": False, "font": FONT_LATIN, "name": "Deutsch"},
    "en": {"rtl": False, "font": FONT_LATIN, "name": "English"},
    "fr": {"rtl": False, "font": FONT_LATIN, "name": "Français"},
    "es": {"rtl": False, "font": FONT_LATIN, "name": "Español"},
    "sw": {"rtl": False, "font": FONT_LATIN, "name": "Kiswahili"},
    "qu": {"rtl": False, "font": FONT_LATIN, "name": "Quechua"},
    "ay": {"rtl": False, "font": FONT_LATIN, "name": "Aymara"},
    "yo": {"rtl": False, "font": FONT_LATIN, "name": "Yorùbá"},
    "ti": {"rtl": False, "font": FONT_LATIN, "name": "Twi / Akan"},
    "ku": {"rtl": False, "font": FONT_LATIN, "name": "Kurdî (Kurmanjî)"},
    "ru": {"rtl": False, "font": FONT_LATIN, "name": "Русский"},
}

# Footers in Dokument-Sprache (fallback: Deutsch)
FOOTERS = {
    "de": ["Hoffnung ist stärker als Angst",
           "Solidarität ist unser Schutz und unsere Verteidigung",
           "Ihr müsst sagen, was ihr wollt.",
           "Freiheit ist die Freiheit der Mitmenschen (frei nach Rosa Luxemburg)"],
    "en": ["Hope is stronger than fear",
           "Solidarity is our protection and our defense",
           "Say clearly what you want.",
           "Freedom is the freedom of others (after Rosa Luxemburg)"],
    "ar": ["الأمل أقوى من الخوف",
           "التضامن هو حمايتنا ودفاعنا",
           "عليكم أن تقولوا ما تريدون.",
           "الحرية هي حرية الآخرين (بتصرف عن روزا لوكسمبورغ)"],
    "fr": ["L’espoir est plus fort que la peur",
           "La solidarité est notre protection et notre défense",
           "Dites clairement ce que vous voulez.",
           "La liberté est la liberté des autres (d’après Rosa Luxemburg)"],
    "es": ["La esperanza es más fuerte que el miedo",
           "La solidaridad es nuestra protección y nuestra defensa",
           "Decid claramente lo que queréis.",
           "La libertad es la libertad de las demás personas (según Rosa Luxemburgo)"],
}

# -------------- helpers --------------
def ensure_font(path: str) -> str:
    p = Path(path)
    if p.exists():
        return str(p)
    # fallback: Latin if missing
    return FONT_LATIN

def rtl_arabic(text: str) -> str:
    if not HAS_AR:
        return text  # graceful fallback
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(text)
    return bidi.algorithm.get_display(reshaped)

def wrap_text(text, width):
    # simple word wrap safe for most scripts
    return textwrap.wrap(text, width=width, replace_whitespace=False,
                         drop_whitespace=False)

def draw_header_footer(c, lang, logo_img, contact_lines, rtl=False):
    # Creme Hintergrund
    c.setFillColor(UIR_BG)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=True, stroke=False)

    # Linien oben/unten (Hope-Grün)
    c.setStrokeColor(UIR_HOPE)
    c.setLineWidth(0.5)
    # obere Linie (0.3 cm ~ 8.5 pt vom Kopfbereich nach unten – wir zeichnen erstmal fixe y)
    top_y = PAGE_H - 72  # ~ 2.54 cm vom Rand, darunter Überschrift
    c.line(0, top_y, PAGE_W, top_y)

    # Fußzeilenlinie
    bottom_y = 110  # ~ 3.8 cm Bereich oben frei für Fußzeile
    c.line(0, bottom_y, PAGE_W, bottom_y)

    # Kopfbereich: Logo und Kontaktblock zueinander gespiegelt bei RTL
    logo_h = 113  # ~4cm
    logo_w = logo_h * 0.75  # grobe Annahme
    margin = 18

    if logo_img:
        if rtl:
            # arabisch: Logo LINKS
            c.drawImage(logo_img, margin, PAGE_H - margin - logo_h,
                        width=logo_w, height=logo_h, mask='auto')
        else:
            # LTR: Logo RECHTS
            c.drawImage(logo_img, PAGE_W - margin - logo_w, PAGE_H - margin - logo_h,
                        width=logo_w, height=logo_h, mask='auto')

    # Kontaktblock (3 Zeilen, 15pt, vertikal an Logo oben/mitte/unten)
    c.setFillColor(UIR_LILA)
    contact_x = PAGE_W - margin - logo_w if rtl else margin
    top_line_y = PAGE_H - margin - 15
    mid_line_y = PAGE_H - margin - (logo_h / 2)
    bot_line_y = PAGE_H - margin - logo_h + 15

    c.setFont("UiRFont", 15)
    if rtl:
        # rechtsbündig
        for i, (y, txt) in enumerate([(top_line_y, contact_lines[0]),
                                      (mid_line_y, contact_lines[1]),
                                      (bot_line_y, contact_lines[2])]):
            draw_text(c, txt, contact_x - 4, y, rtl=True, align="right")
    else:
        for i, (y, txt) in enumerate([(top_line_y, contact_lines[0]),
                                      (mid_line_y, contact_lines[1]),
                                      (bot_line_y, contact_lines[2])]):
            draw_text(c, txt, contact_x + 4, y, rtl=False, align="left")

    return top_y, bottom_y, logo_h

def draw_text(c, txt, x, y, rtl=False, align="left", size=12, leading=14):
    c.setFont("UiRFont", size)
    if rtl and HAS_AR:
        txt = rtl_arabic(txt)
    if align == "center":
        if rtl:
            # ReportLab zentriert von x als Mitte – passt
            c.drawCentredString(x, y, txt)
        else:
            c.drawCentredString(x, y, txt)
    elif align == "right":
        c.drawRightString(x, y, txt)
    else:
        c.drawString(x, y, txt)

def paragraph(c, text, box_x, box_y, box_w, rtl=False, size=10.5, leading=12.5):
    c.setFont("UiRFont", size)
    c.setFillColor(UIR_LILA)
    max_chars = int(box_w / (size * 0.54))  # heuristisch
    lines = []
    for raw_line in text.splitlines():
        wrapped = wrap_text(raw_line, max_chars) if raw_line.strip() else [""]
        lines.extend(wrapped)
    cursor_y = box_y
    for line in lines:
        draw_text(c, line, box_x if not rtl else box_x + box_w, cursor_y,
                  rtl=rtl, align=("right" if rtl else "left"), size=size)
        cursor_y -= leading
    return cursor_y

def render_pdf(logo_bytes, title, body, lang_code, user_contact_extra=None):
    cfg = LANG_CFG.get(lang_code, LANG_CFG["de"])
    rtl = cfg.get("rtl", False)
    font_path = ensure_font(cfg["font"])
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    try:
        pdfmetrics.registerFont(TTFont("UiRFont", font_path))
    except Exception:
        pdfmetrics.registerFont(TTFont("UiRFont", FONT_LATIN))

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    # Hintergrund
    c.setFillColor(UIR_BG); c.rect(0,0,PAGE_W,PAGE_H,fill=True,stroke=False)

    logo_img = ImageReader(io.BytesIO(logo_bytes)) if logo_bytes else None

    # Kontaktblock (3 Zeilen) – aus Vorgabe UiR
    # Reihenfolge fix: Instagram, Ko-fi, CryptPad/Tidal (kannst du im UI anpassen)
    contact = st.session_state.get("contact_block", [
        "Instagram @dr_karo_1312",
        "Ko-fi ko-fi.com/utopieinreal",
        "Tidal is.gd/MusicforUtopieInReal",
    ])
    if user_contact_extra:
        contact[1] = user_contact_extra  # z. B. Nutzerkontakt

    top_line_y, bottom_line_y, logo_h = draw_header_footer(
        c, lang_code, logo_img, contact, rtl=rtl
    )

    # Überschrift (zentriert, 14/16pt)
    c.setFillColor(UIR_LILA)
    c.setFont("UiRFont", 14)
    title_y = top_line_y - 18  # 0.3 cm Abstand
    title_txt = rtl_arabic(title) if rtl and HAS_AR else title
    c.drawCentredString(PAGE_W/2, title_y, title_txt)

    # Haupttext-Box zwischen Linien
    left_margin = 56
    right_margin = 56
    box_w = PAGE_W - left_margin - right_margin
    box_top = title_y - 24
    # genug Platz oberhalb Fußlinie
    box_bottom = bottom_line_y + 24

    paragraph(c, body, left_margin, box_top, box_w, rtl=rtl, size=10.5, leading=12.5)

    # Fußzeile (zentriert, 9pt, 4 Zeilen)
    c.setFont("UiRFont", 9)
    foot = FOOTERS.get(lang_code, FOOTERS["de"])
    fy = bottom_line_y - 22
    for line in foot:
        draw_text(c, rtl_arabic(line) if rtl and HAS_AR else line, PAGE_W/2, fy,
                  rtl=False, align="center", size=9)
        fy -= 12

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()

def make_filename(base_name, lang_code):
    today = datetime.date.today().strftime("%Y%m%d")
    return f"{today}-{base_name}-{lang_code}.pdf"

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="UiR PDF Generator", page_icon="🌿", layout="centered")

st.title("🌿 UiR – Multilingual PDF Generator")
st.caption("UiR-Standardlayout • Creme | Lila | Hope-Grün • Logo optional • ZIP oder Einzel-PDF")

with st.sidebar:
    st.header("Logo & Kontakt")
    logo_file = st.file_uploader("Optionales Logo (PNG/SVG/JPG)", type=["png","jpg","jpeg","svg"])
    contact_custom = st.text_input("Zusätzlicher Kontakt (wird 2. Zeile)", value="")
    out_mode = st.radio("Ausgabe", ["ZIP (alle Sprachen)", "Einzel-PDF je Sprache"], index=0)

# Formular
with st.form("make"):
    file_base = st.text_input("Dateiname (Basis, ohne Endung)", value="WayOfHope")
    title = st.text_input("Überschrift", value="طريق الأمل (Tariq al-Amal)")
    main_text = st.text_area("Haupttext (Deutsch oder Zielsprache)", height=220,
                             placeholder="Deinen Text hier einfügen …")
    st.markdown("**Sprachen wählen**")
    langs = st.multiselect(
        "Zielsprachen",
        options=[("ar","Arabisch"),("de","Deutsch"),("en","Englisch"),("fr","Französisch"),
                 ("es","Spanisch"),("sw","Swahili"),("ti","Twi/Akan"),("ku","Kurdisch (Kurmanjî)"),
                 ("qu","Quechua"),("ay","Aymara"),("yo","Yorùbá"),("zh","Chinesisch (vereinfacht)"),
                 ("ru","Russisch")],
        default=["ar"]
    )
    st.markdown("_Hinweis: automatische Übersetzung ist optional – hier zunächst **ohne** API. Du kannst den Text bereits in Zielsprache einfügen._")
    translate_wish = st.checkbox("Automatisch übersetzen (Hugging Face / optionaler Token)", value=False)
    hf_token = st.text_input("Hugging Face Access Token (optional für Übersetzung)", type="password") if translate_wish else ""
    submitted = st.form_submit_button("PDF(s) erstellen")

# Übersetzung (optional, lightweight)
def translate_text(text, target_lang, hf_token=""):
    """Very simple translator via huggingface pipeline if available; otherwise returns source text."""
    if not translate_wish:
        return text
    try:
        from transformers import pipeline
        model_map = {
            "en":"Helsinki-NLP/opus-mt-de-en",
            "fr":"Helsinki-NLP/opus-mt-de-fr",
            "es":"Helsinki-NLP/opus-mt-de-es",
            "ar":"Helsinki-NLP/opus-mt-de-ar",
            "sw":"Helsinki-NLP/opus-mt-de-sw",
            "ru":"Helsinki-NLP/opus-mt-de-ru",
            # many marginalized langs have weak coverage; fall back to English hop if missing
        }
        model = model_map.get(target_lang, "Helsinki-NLP/opus-mt-de-en")
        task = pipeline("translation", model=model, use_auth_token=(hf_token or None))
        out = task(text, max_length=1024)[0]["translation_text"]
        if target_lang in ("ar",) and HAS_AR:
            out = rtl_arabic(out)
        return out
    except Exception:
        return text  # graceful fallback

if submitted:
    if not langs:
        st.error("Bitte mindestens eine Sprache wählen.")
    else:
        logo_bytes = logo_file.read() if logo_file else None
        pdfs = []
        for code in [c for c,_ in langs]:
            body_txt = translate_text(main_text, code, hf_token)
            pdf_bytes = render_pdf(
                logo_bytes=logo_bytes,
                title=title if code!="ar" else title,  # gib Titel in Zielsprache ein, falls gewünscht
                body=body_txt,
                lang_code=code,
                user_contact_extra=(contact_custom or None),
            )
            fname = make_filename(file_base, code)
            pdfs.append((fname, pdf_bytes))

        if len(pdfs) == 1 or out_mode == "Einzel-PDF je Sprache":
            for fname, data in pdfs:
                st.download_button(f"⬇️ Download {fname}", data=data, file_name=fname, mime="application/pdf")
        else:
            # ZIP
            zbuf = io.BytesIO()
            with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname, data in pdfs:
                    zf.writestr(fname, data)
            zbuf.seek(0)
            zipname = f"{datetime.date.today().strftime('%Y%m%d')}-{file_base}.zip"
            st.download_button("⬇️ ZIP herunterladen", data=zbuf, file_name=zipname, mime="application/zip")

st.markdown("---")
st.caption("Tipp: Lege Schriften in **./fonts/** ab: 1) DejaVuSans.ttf 2) Amiri-Regular.ttf 3) NotoSansCJKsc-Regular.otf")