# Advanced DSO Finder 🔭

Ein interaktives Web-Tool für Amateurastronomen zur Planung von Deep-Sky-Beobachtungen, ursprünglich inspiriert durch das Vespera Pro Teleskop, aber generell nützlich.

Diese mit Streamlit erstellte Anwendung hilft dabei, Deep-Sky-Objekte (DSOs) zu finden, die von einem bestimmten Standort zu einer gewählten Zeit unter Berücksichtigung der Himmelsqualität und anderer Faktoren beobachtbar sind.

---

## ✨ Hauptfunktionen

* **Standortwahl:** Standardstandort (Schötz, CH) oder manuelle Eingabe von Längen-, Breitengrad und Höhe.
* **Zeitpunktwahl:** Planung für die kommende Nacht (basierend auf aktueller Zeit) oder Auswahl eines beliebigen Datums.
* **Helligkeitsfilter:**
    * Automatisch basierend auf der Bortle-Skala (1-9).
    * Oder manuelle Eingabe eines Magnitude-Bereichs (Min/Max).
* **Mindesthöhe:** Einstellbare minimale Höhe über dem Horizont, die Objekte erreichen müssen.
* **Objekttyp-Filter:** Auswahl spezifischer DSO-Typen (z.B. Galaxie, Nebel, Sternhaufen).
* **Mondphasen-Anzeige & Warnung:** Zeigt die aktuelle Mondhelligkeit an und warnt (in Rot), wenn ein einstellbarer Schwellenwert überschritten wird.
* **Ergebnis-Optionen:**
    * Einstellbare Anzahl der anzuzeigenden Objekte.
    * Optionale Sortierung nach Helligkeit (hellste zuerst) statt zufälliger Auswahl.
* **Detailansicht:** Ausklappbare Detailinformationen für jedes Objekt (Koordinaten, max. Höhe, beste Beobachtungszeit).
* **Höhenverlauf-Plot:** Möglichkeit, für jedes Ergebnisobjekt einen Graphen des Höhenverlaufs über die Nacht anzuzeigen (benötigt Matplotlib).
* **CSV-Export:** Herunterladen der Ergebnisliste als CSV-Datei.

---

## 🚀 App starten (Lokal)

Um die App auf deinem eigenen Computer auszuführen:

1.  **Repository klonen:**
    ```bash
    # Ersetze DEIN_USERNAME und DEIN_REPO_NAME mit deinen Angaben
    git clone [https://github.com/DEIN_USERNAME/DEIN_REPO_NAME.git](https://github.com/DEIN_USERNAME/DEIN_REPO_NAME.git)
    cd DEIN_REPO_NAME
    ```

2.  **Virtuelle Umgebung erstellen & aktivieren:**
    ```bash
    # Erstellen (nur einmal nötig)
    python -m venv .venv

    # Aktivieren (Windows PowerShell)
    .\.venv\Scripts\Activate.ps1

    # Aktivieren (MacOS/Linux Bash)
    source .venv/bin/activate
    ```
    *Hinweis: Verwende den für dein Betriebssystem und deine Shell passenden Aktivierungsbefehl.*

3.  **Abhängigkeiten installieren:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Stelle sicher, dass die `requirements.txt`-Datei aktuell ist, siehe Anleitung zum Deployment)*

4.  **Streamlit App starten:**
    ```bash
    # Ersetze DeineAppDatei.py mit dem Namen deines Python-Skripts, z.B. dso_app_v14.py
    streamlit run DeineAppDatei.py
    ```

Die App sollte sich nun in deinem Webbrowser öffnen.

---

## 🌐 Live-Version

Eine Live-Version dieser App findest du hier: `[Link zur Live-App einfügen]`

---

## 📚 Abhängigkeiten

Die Hauptbibliotheken, die von dieser Anwendung verwendet werden:

* Streamlit
* Astropy
* Astroplan
* NumPy
* Pandas
* Matplotlib

Die genauen Versionen sind in der `requirements.txt`-Datei aufgeführt.

---

## Lizenz

---

## Kontakt

Email: debrun2005@gmail.com
