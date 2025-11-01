# 🌿 Utopie-in-Real Translator

Ein frei zugängliches Tool, das Texte automatisch übersetzt und im **UiR-Standardlayout** als PDF rendert —  
für Aktivist*innen, Künstler*innen, Forscher*innen und Communities,  
die Hoffnung, Wissen und Solidarität teilen möchten – jenseits von Sprachgrenzen.

---

## 💜 Features

- **Mehrsprachige Ausgabe:** beliebige Eingabesprache, frei wählbare Zielsprachen  
- **Automatische Übersetzung:** via [deep-translator](https://pypi.org/project/deep-translator)  
- **PDF-Erstellung im UiR-Design:** Creme-Hintergrund, Lila Text, Hope-Grün Linien  
- **Inklusive Fonts:**  
  - DejaVu Sans → Lateinische Sprachen  
  - Amiri → Arabisch  
  - Noto Sans CJK SC → Chinesisch / Ostasiatisch  
- **Optionale Personalisierung:** eigenes Logo und Kontaktzeile  
- **ZIP-Export:** mehrere Sprachen in einer Datei  
- **Rechts-nach-links-Schrift:** vollständige Unterstützung für Arabisch  

---

## 🧩 Projektstruktur
Utopie-in-Real-translator/ │ ├── app.py                    # Hauptanwendung (Streamlit) ├── requirements.txt          # Alle benötigten Pakete ├── assets/ │   └── UiR_Logo_standard.png # Standardlogo │ ├── fonts/ │   ├── Amiri-Regular.ttf │   ├── DejaVuSerif.ttf │   └── NotoSansCJKsc-Regular.otf │ └── README.md
Utopie-in-Real-translator/ │ ├── app.py                    # Hauptanwendung (Streamlit) ├── requirements.txt          # Alle benötigten Pakete ├── assets/ │   └── UiR_Logo_standard.png # Standardlogo │ ├── fonts/ │   ├── Amiri-Regular.ttf │   ├── DejaVuSerif.ttf │   └── NotoSansCJKsc-Regular.otf │ └── README.md



---

## ⚙️ Installation

1️⃣ **Repository klonen oder herunterladen:**
```bash
git clone https://github.com/KaRo74/Utopie-in-Real-translator.git
cd Utopie-in-Real-translator


2️⃣ Virtuelle Umgebung aktivieren (optional, aber empfohlen):

python -m venv venv
source venv/bin/activate   # auf macOS / Linux
venv\Scripts\actiUtopie-in-Real-translator


3️⃣ Abhängigkeiten installieren:

pip install -r requirements.txt


4️⃣ App starten:

streamlit run app.py
