# DSO Finder 🔭

**Finde Deep-Sky-Objekte für deine nächste Beobachtungsnacht!**

Ein Werkzeug für Amateurastronomen und Astrofotografen zur einfachen Suche, Filterung und Identifizierung von Deep-Sky-Objekten (DSOs) wie Galaxien, Nebeln und Sternhaufen. Plane deine Beobachtungen basierend auf Sichtbarkeit und interessanten Objekten.

---

## Inhaltsverzeichnis

* [Über das Projekt](#über-das-projekt)
* [Features](#features)
* [Technologie-Stack](#technologie-stack)
* [Voraussetzungen](#voraussetzungen)
* [Installation](#installation)
* [Nutzung](#nutzung)
* [Konfiguration](#konfiguration)
* [Mitwirken](#mitwirken)
* [Lizenz](#lizenz)
* [Danksagungen](#danksagungen)
* [Kontakt](#kontakt)

---

## Über das Projekt

Dieses Projekt wurde entwickelt, um die Planung von astronomischen Beobachtungen zu vereinfachen. Anstatt mühsam Kataloge zu durchsuchen und Sichtbarkeiten manuell zu prüfen, bietet der DSO Finder eine zentrale Anlaufstelle, um interessante Objekte für den aktuellen Standort und die gewünschte Zeit zu finden.

**Ziel:** Ein benutzerfreundliches Tool bereitzustellen, das hilft, das Beste aus jeder klaren Nacht herauszuholen.

---

## Features

* 🌌 **Umfangreiche DSO-Datenbank:** Durchsuche Objekte aus gängigen Katalogen (z.B. Messier, NGC, IC).
* 🔦 **Flexible Filter:** Filtere nach Objekttyp (Galaxie, Nebel, Sternhaufen...), Sternbild, visueller Helligkeit (Magnitude), Grösse, Deklination etc.
* 🌍 **Standortbezogene Sichtbarkeit:**
    * Berechnet die aktuelle Höhe und Azimut von Objekten.
    * Zeigt an, welche Objekte zu einer bestimmten Zeit von einem bestimmten Ort (z.B. Schötz, Schweiz) sichtbar sind.
    * Berücksichtigt [optional: atmosphärische Extinktion, Mondphase?].
* ℹ️ **Detaillierte Informationen:** Zeigt relevante Daten für jedes Objekt an (Koordinaten (RA/Dec), Typ, Helligkeit, Grösse, Entfernung, kurze Beschreibung).
* ⭐ **[Optional: Beobachtungslisten]:** Erstelle und verwalte Listen von Objekten, die du beobachten möchtest.
* 🗺️ **[Optional: Sternkarten-Integration]:** Zeige die Position des Objekts auf einer einfachen Sternkarte oder exportiere Koordinaten für andere Programme.
* 🔭 **[Optional: Teleskopsteuerung]:** Schnittstelle zur Steuerung von GoTo-Montierungen (z.B. über ASCOM/INDI).
* **[Füge hier weitere spezifische Features deines Tools hinzu]**


## Technologie-Stack

* **Programmiersprache:** `[z.B. Python 3.9+, JavaScript (Node.js), C++]`
* **Hauptbibliotheken/Frameworks:** `[z.B. Astropy, Skyfield, Flask, React, PyQt, Pandas, NumPy]`
* **Datenbank:** `[z.B. SQLite, PostgreSQL, JSON-Dateien]`
* **Benutzeroberfläche:** `[z.B. Kommandozeile (CLI), Webinterface, Desktop-GUI (Qt/Tkinter)]`
* **[Weitere relevante Technologien auflisten]**

---

## Voraussetzungen

Bevor du beginnst, stelle sicher, dass du Folgendes installiert hast:

* `[z.B. Python 3.9 oder höher]`
* `[z.B. pip (Python package installer)]`
* `[z.B. Node.js und npm]`
* `[Andere Systemabhängigkeiten, z.B. git]`

---

## Installation

1.  **Klone das Repository:**
    ```bash
    git clone https://[Dein-GitHub-Benutzername]/[Dein-Repository-Name].git
    cd [Dein-Repository-Name]
    ```

2.  **Installiere die Abhängigkeiten:**

    * *Für Python-Projekte (häufig):*
        ```bash
        pip install -r requirements.txt
        ```
    * *Für Node.js-Projekte:*
        ```bash
        npm install
        ```
    * *Füge hier spezifische Installationsschritte für dein Projekt hinzu.*

3.  **[Optional: Datenbank-Setup]**
    * *Wenn eine Datenbank initialisiert werden muss:*
        ```bash
        [z.B. python manage.py migrate]
        ```
    * *Wenn Daten importiert werden müssen:*
        ```bash
        [z.B. python import_data.py --catalog=all]
        ```

---

## Nutzung

Beschreibe hier, wie man dein Tool startet und verwendet.

* **Für Kommandozeilen-Tools (Beispiel):**
    ```bash
    # Hilfe anzeigen
    python dso_finder.py --help

    # Finde sichtbare Galaxien heller als Mag 10 in Schötz
    python dso_finder.py --type Galaxy --mag 10 --location "Schötz,CH" --visible

    # Zeige Details für M42 an
    python dso_finder.py --find M42
    ```

* **Für Webanwendungen (Beispiel):**
    1.  Starte den Server:
        ```bash
        [z.B. flask run]
        # oder
        [z.B. python app.py]
        # oder
        [z.B. npm start]
        ```
    2.  Öffne deinen Webbrowser und gehe zu `http://localhost:[Port, z.B. 5000]`.
    3.  Nutze die Weboberfläche, um Objekte zu suchen und zu filtern.

* **Für Desktop-Anwendungen (Beispiel):**
    1.  Führe das Start-Skript aus:
        ```bash
        python main_gui.py
        ```
    2.  Oder starte die kompilierte Anwendung:
        ```bash
        ./dso-finder
        ```

*Füge spezifische Beispiele und Anwendungsfälle hinzu.*

---

## Konfiguration

* **Standort:** Der Beobachtungsstandort kann [z.B. über Kommandozeilenargumente (`--location "Stadt,Land"` oder `--lat LAT --lon LON`), eine Konfigurationsdatei (`config.ini`, `.env`) oder in der Benutzeroberfläche] festgelegt werden. Standardmässig ist [z.B. kein Standort / ein Beispielstandort wie Schötz, Schweiz] eingestellt.
* **Zeit:** Standardmässig wird die aktuelle Systemzeit verwendet. Sie kann [z.B. über `--time "YYYY-MM-DD HH:MM:SS"`] angepasst werden.
* **Kataloge:** [z.B. Standardmässig sind Messier und NGC aktiviert. Dies kann in `config.ini` geändert werden.]
* **[Weitere Konfigurationsoptionen]**

---

## Mitwirken

Beiträge sind herzlich willkommen! Wenn du Ideen für Verbesserungen hast, Fehler findest oder Code beisteuern möchtest, beachte bitte Folgendes:

1.  **Forke das Repository.**
2.  **Erstelle einen neuen Branch:** `git checkout -b feature/DeineNeueFunktion` oder `bugfix/DeinBugfix`.
3.  **Nimm deine Änderungen vor und committe sie:** `git commit -m 'Füge neues Feature hinzu'`.
4.  **Pushe zum Branch:** `git push origin feature/DeineNeueFunktion`.
5.  **Öffne einen Pull Request.**

Bitte melde Fehler oder Feature-Wünsche über die [GitHub Issues](https://github.com/[Dein-GitHub-Benutzername]/[Dein-Repository-Name]/issues) Seite.

---

## Lizenz

Dieses Projekt steht unter der `[Name der Lizenz, z.B. MIT]` Lizenz. Siehe die Datei `LICENSE` für weitere Details.

---

## Danksagungen

* Daten aus den Katalogen [z.B. Messier, NGC, IC].
* Astronomische Berechnungen dank [z.B. Astropy, Skyfield].
* Positionsdaten und Objektinformationen von [z.B. SIMBAD, NASA/IPAC Extragalactic Database (NED)].
* Inspiration durch [z.B. andere Astronomie-Software, Bücher].
* Danke an alle [Contributors](https://github.com/[Dein-GitHub-Benutzername]/[Dein-Repository-Name]/graphs/contributors)!

---

## Kontakt

[Dein Name / Handle] - [Deine E-Mail-Adresse oder Link zum Profil, z.B. GitHub-Profil]

Projektlink: [https://github.com/[Dein-GitHub-Benutzername]/[Dein-Repository-Name]](https://github.com/[Dein-GitHub-Benutzername]/[Dein-Repository-Name])
