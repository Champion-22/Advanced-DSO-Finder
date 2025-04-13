# -*- coding: utf-8 -*-
# --- Basic Imports ---
from __future__ import annotations # Keep for flexible type hinting
import streamlit as st
import random
from datetime import datetime, date, time, timedelta, timezone
import math
import io
import traceback
import locale # Optional for locale-specific formatting
import os # Needed for file path joining

# --- Page Config (MUST BE FIRST Streamlit command) ---
# Set page config early, title will be set based on default language initially
# The main title widget (st.title) will be static English.
st.set_page_config(page_title="Advanced DSO Finder", layout="wide")

# --- Collect potential import errors ---
import_errors = []

# --- Library Imports (Try after set_page_config) ---
# Astropy Time
try:
    from astropy.time import Time
except ImportError as e:
    import_errors.append(f"Error: Basic Astropy library ('astropy.time') not found. Install: pip install astropy ({e})")
    Time = None

# Main Astronomy Imports
try:
    import numpy as np
    import astropy.units as u
    from astropy.coordinates import EarthLocation, SkyCoord, get_sun, AltAz
    from astroplan.moon import moon_illumination
except ImportError as e:
    import_errors.append(f"Error: Required Astropy/Astroplan library not found. Install: pip install astropy numpy astroplan ({e})")
    np = None
    u = None
    EarthLocation = None
    SkyCoord = None
    get_sun = None
    AltAz = None
    moon_illumination = None

# Additional Libraries
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates # Import for date formatting
    if plt: # Set style only if import succeeded
        plt.style.use('dark_background')
except ImportError as e:
    import_errors.append(f"Error: Required library not found. Install: pip install pandas matplotlib ({e})")
    pd = None
    plt = None
    mdates = None # Define as None if matplotlib fails

# Timezone Library (pytz is still needed for timezone objects)
try:
    import pytz
except ImportError as e:
     import_errors.append(f"Error: Required timezone library not found. Install: pip install pytz ({e})")
     pytz = None

# Geopy für Ortsuche
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
except ImportError as e:
    import_errors.append(f"Error: Required geocoding library not found. Install: pip install geopy ({e})")
    Nominatim = None
    GeocoderTimedOut = None
    GeocoderServiceError = None

# TimezoneFinder für automatische Zeitzone
try:
    from timezonefinder import TimezoneFinder
except ImportError as e:
    import_errors.append(f"Error: Required timezone library not found. Install: pip install timezonefinder ({e})")
    TimezoneFinder = None


# --- Display Import Errors (NOW it's safe to use st.error) ---
if import_errors:
    st.error("### Library Import Errors")
    for error in import_errors:
        st.error(error)
    st.info("Please install the missing libraries and restart the app.")
    st.stop() # Stop execution if imports failed

# --- Check if essential classes/functions were imported ---
essential_imports_ok = all([
    Time, np, u, EarthLocation, SkyCoord, get_sun, AltAz, moon_illumination, pd, plt, pytz, mdates,
    Nominatim, # Geopy
    TimezoneFinder # TimezoneFinder
])
if not essential_imports_ok:
    st.error("Stopping execution due to missing essential libraries.")
    st.stop()

# --- Translations ---
# Added object type glossary strings
translations = {
    'en': {
        'page_title': "Advanced DSO Finder",
        'settings_header': "Settings",
        'language_select_label': "Language / Sprache / Langue",
        'location_expander': "📍 Location",
        'location_select_label': "Select Location Method",
        'location_option_manual': "Enter Manually",
        'location_option_search': "Search by Name",
        'location_search_label': "Enter Location Name:",
        'location_search_submit_button': "Find Coordinates",
        'location_search_placeholder': "e.g., Berlin, Germany or Mount Palomar",
        'location_search_found': "Found: {}",
        'location_search_coords': "Lat: {:.4f}, Lon: {:.4f}",
        'location_search_error_not_found': "Location not found. Try a more specific name.",
        'location_search_error_service': "Geocoding service error: {}",
        'location_lat_label': "Latitude (°N)",
        'location_lon_label': "Longitude (°E)",
        'location_elev_label': "Elevation (Meters)",
        'location_manual_display': "Manual ({:.4f}, {:.4f})",
        'location_search_display': "Searched: {} ({:.4f}, {:.4f})",
        'location_error': "Location Error: {}",
        'location_error_fallback': "ERROR - Using Fallback",
        'location_error_manual_none': "Manual location fields cannot be empty or invalid.",
        'location_error_manual_search': "Cannot search objects: Manual location fields are invalid or empty.",
        'location_error_search_search': "Cannot search objects: Please search for a valid location first.",
        'location_error_undefined': "Cannot search objects: Location is not defined (select Manual or Search).",
        'time_expander': "⏱️ Time & Timezone",
        'time_select_label': "Select Time",
        'time_option_now': "Now (upcoming night)",
        'time_option_specific': "Specific Night",
        'time_date_select_label': "Select Date:",
        'timezone_auto_set_label': "Detected Timezone:",
        'timezone_auto_fail_label': "Timezone:",
        'timezone_auto_fail_msg': "Could not detect timezone, using UTC.",
        'filters_expander': "✨ Filters & Conditions",
        'mag_filter_header': "**Magnitude Filter**",
        'mag_filter_method_label': "Filter Method:",
        'mag_filter_option_bortle': "Bortle Scale",
        'mag_filter_option_manual': "Manual",
        'mag_filter_bortle_label': "Bortle Scale:",
        'mag_filter_bortle_help': "Sky darkness: 1=Excellent Dark, 9=Inner-City Sky",
        'mag_filter_min_mag_label': "Min. Magnitude:",
        'mag_filter_min_mag_help': "Brightest object magnitude to include",
        'mag_filter_max_mag_label': "Max. Magnitude:",
        'mag_filter_max_mag_help': "Faintest object magnitude to include",
        'mag_filter_warning_min_max': "Min. magnitude is greater than Max. magnitude!",
        'min_alt_header': "**Minimum Altitude**",
        'min_alt_label': "Min. Object Altitude (°):",
        'direction_filter_header': "**Peak Direction Filter**",
        'direction_filter_label': "Show objects peaking in direction:",
        'direction_option_all': "All",
        'moon_warning_header': "**Moon Warning**",
        'moon_warning_label': "Warn if Moon > (% Illumination):",
        'object_types_header': "**Object Types**",
        'object_types_error_extract': "Could not extract object types from catalog.",
        'object_types_label': "Filter Types (leave empty for all):",
        'object_type_glossary_title': "Object Type Glossary", # NEU
        'object_type_glossary': { # NEU
            "OCl": "Open Cluster", "GCl": "Globular Cluster", "Cl+N": "Cluster + Nebula",
            "Gal": "Galaxy", "PN": "Planetary Nebula", "SNR": "Supernova Remnant",
            "Neb": "Nebula (general)", "EmN": "Emission Nebula", "RfN": "Reflection Nebula",
            "HII": "HII Region", "AGN": "Active Galactic Nucleus"
         },
        'results_options_expander': "⚙️ Result Options",
        'results_options_max_objects_label': "Max Number of Objects to Display:",
        'results_options_sort_method_label': "Sort Results By:",
        'results_options_sort_duration': "Duration & Altitude",
        'results_options_sort_magnitude': "Brightness",
        'moon_metric_label': "Moon Illumination (approx.)",
        'moon_warning_message': "Warning: Moon is brighter ({:.0f}%) than threshold ({:.0f}%)!",
        'moon_phase_error': "Moon phase calculation error: {}",
        'find_button_label': "🔭 Find Observable Objects",
        'search_params_header': "Search Parameters",
        'search_params_location': "📍 Location: {}",
        'search_params_time': "⏱️ Time: {}",
        'search_params_timezone': "🌍 Timezone: {}",
        'search_params_time_now': "Upcoming night (from {} UTC)",
        'search_params_time_specific': "Night after {}",
        'search_params_filter_mag': "✨ Filter: {}",
        'search_params_filter_mag_bortle': "Bortle {} (<= {:.1f} mag)",
        'search_params_filter_mag_manual': "Manual ({:.1f}-{:.1f} mag)",
        'search_params_filter_alt_types': "🔭 Filter: Min. Alt {}°, Types: {}",
        'search_params_filter_direction': "🧭 Filter: Peak Direction: {}",
        'search_params_types_all': "All",
        'search_params_direction_all': "All",
        'spinner_searching': "Calculating window & searching objects...",
        'spinner_geocoding': "Searching for location...",
        'window_info_template': "{}",
        'error_no_window': "No valid observation window found for the selected date and location.",
        'success_objects_found': "{} matching objects found.",
        'info_showing_list_duration': "Showing {} objects, sorted by visibility duration and peak altitude:",
        'info_showing_list_magnitude': "Showing {} objects, sorted by brightness (brightest first):",
        'error_search_unexpected': "An unexpected error occurred during the search:",
        'results_list_header': "Result List",
        'results_export_name': "Name",
        'results_export_type': "Type",
        'results_export_mag': "Magnitude",
        'results_export_ra': "RA",
        'results_export_dec': "Dec",
        'results_export_max_alt': "Max Altitude (°)",
        'results_export_az_at_max': "Azimuth at Max (°)",
        'results_export_direction_at_max': "Direction at Max",
        'results_export_time_max_utc': "Time at Max (UTC)",
        'results_export_time_max_local': "Time at Max (Local TZ)",
        'results_export_cont_duration': "Max Cont. Duration (h)",
        'results_export_total_duration': "Total Duration (h)",
        'results_expander_title': "{} ({}) - Mag: {:.1f}",
        'results_coords_header': "**Coordinates:**",
        'results_max_alt_header': "**Max. Altitude:**",
        'results_azimuth_label': "(Azimuth: {:.1f}°{})",
        'results_direction_label': ", Direction: {}",
        'results_best_time_header': "**Best Time (Local TZ):**",
        'results_cont_duration_header': "**Max. Cont. Duration:**",
        'results_total_duration_header': "**Total Duration:**",
        'results_duration_value': "{:.1f} hours",
        'results_plot_button': "📈 Altitude Plot",
        'results_spinner_plotting': "Creating plot...",
        'results_plot_error': "Plot Error: {}",
        'results_plot_not_created': "Plot could not be created.",
        'results_close_plot_button': "Close Plot",
        'results_save_csv_button': "💾 Save Result List as CSV",
        'results_csv_filename': "dso_observation_list_{}.csv",
        'results_csv_export_error': "CSV Export Error: {}",
        'warning_no_objects_found': "No objects found matching all criteria for the calculated observation window.",
        'info_initial_prompt': "Welcome! Please **enter coordinates** manually or **search for a location** name to enable the main search.", # Updated prompt
        'plot_time_label_local': "Time ({})",
        'plot_time_label_utc': "Time (UTC)",
        'plot_altitude_label': "Altitude",
        'plot_min_altitude_label': "Min. Altitude ({:.0f}°)",
        'plot_title': "Altitude Profile for {}",
        'plot_ylabel': "Altitude (°)",
        'error_processing_object': "Error processing {}: {}",
        'window_calc_error': "Error calculating observation window: {}\n{}",
        'window_fallback_info': "\nUsing fallback window: {} to {} UTC",
        'window_invalid_calc': "Warning: Invalid darkness window calculated ({} to {}). Using fallback.",
        'window_starts_now': "Observation window starts now ({} UTC) until {} UTC (Astron. Twilight)",
        'window_starts_at': "Observation window starts at {} UTC until {} UTC (Astron. Twilight)",
        'window_for_night': "Observation window for the night of {}: {} to {} UTC (Astron. Twilight)",
        'window_already_passed': "Warning: Today's observation window has already passed. Calculating for tomorrow night.",
        'window_no_darkness': "Warning: Could not find astronomical darkness window for the night of {}. Using fallback.",
        'window_fallback_append': "\nFallback Observation Window: {} to {} UTC",
        'error_loading_catalog': "Error loading catalog file: {}",
        'info_catalog_loaded': "Catalog loaded: {} objects.",
        'warning_catalog_empty': "Catalog file loaded, but no suitable objects found after filtering.",
     },
    'de': {
        'page_title': "Erweiterter DSO Finder",
        'settings_header': "Einstellungen",
        'language_select_label': "Sprache / Language / Langue",
        'location_expander': "📍 Standort",
        'location_select_label': "Standort-Methode wählen",
        'location_option_manual': "Manuell eingeben",
        'location_option_search': "Ort suchen",
        'location_search_label': "Ortsnamen eingeben:",
        'location_search_submit_button': "Koordinaten finden",
        'location_search_placeholder': "z.B. Berlin, Deutschland oder Calar Alto",
        'location_search_found': "Gefunden: {}",
        'location_search_coords': "Breite: {:.4f}, Länge: {:.4f}",
        'location_search_error_not_found': "Ort nicht gefunden. Versuche einen spezifischeren Namen.",
        'location_search_error_service': "Fehler beim Geocoding-Dienst: {}",
        'location_lat_label': "Breitengrad (°N)",
        'location_lon_label': "Längengrad (°E)",
        'location_elev_label': "Höhe (Meter)",
        'location_manual_display': "Manuell ({:.4f}, {:.4f})",
        'location_search_display': "Gesucht: {} ({:.4f}, {:.4f})",
        'location_error': "Standort Fehler: {}",
        'location_error_fallback': "FEHLER - Nutze Fallback",
        'location_error_manual_none': "Manuelle Standortfelder dürfen nicht leer oder ungültig sein.",
        'location_error_manual_search': "Objektsuche nicht möglich: Manuelle Standortfelder sind ungültig oder leer.",
        'location_error_search_search': "Objektsuche nicht möglich: Bitte zuerst einen gültigen Ort suchen.",
        'location_error_undefined': "Objektsuche nicht möglich: Standort ist nicht definiert (wähle Manuell oder Suche).",
        'time_expander': "⏱️ Zeitpunkt & Zeitzone",
        'time_select_label': "Zeitpunkt wählen",
        'time_option_now': "Jetzt (kommende Nacht)",
        'time_option_specific': "Andere Nacht",
        'time_date_select_label': "Datum auswählen:",
        'timezone_auto_set_label': "Ermittelte Zeitzone:",
        'timezone_auto_fail_label': "Zeitzone:",
        'timezone_auto_fail_msg': "Zeitzone konnte nicht ermittelt werden, nutze UTC.",
        'filters_expander': "✨ Filter & Bedingungen",
        'mag_filter_header': "**Helligkeitsfilter**",
        'mag_filter_method_label': "Filtermethode:",
        'mag_filter_option_bortle': "Bortle-Skala",
        'mag_filter_option_manual': "Manuell",
        'mag_filter_bortle_label': "Bortle-Skala:",
        'mag_filter_bortle_help': "Himmelsdunkelheit: 1=Exzellent Dunkel, 9=Innenstadt",
        'mag_filter_min_mag_label': "Min. Magnitude:",
        'mag_filter_min_mag_help': "Hellstes Objekt (Magnitude)",
        'mag_filter_max_mag_label': "Max. Magnitude:",
        'mag_filter_max_mag_help': "Schwächstes Objekt (Magnitude)",
        'mag_filter_warning_min_max': "Min. Magnitude ist größer als Max. Magnitude!",
        'min_alt_header': "**Mindesthöhe**",
        'min_alt_label': "Min. Objekt-Höhe (°):",
        'direction_filter_header': "**Filter Himmelsrichtung (Max. Höhe)**",
        'direction_filter_label': "Zeige Objekte mit Max. Höhe in Richtung:",
        'direction_option_all': "Alle",
        'moon_warning_header': "**Mond Warnung**",
        'moon_warning_label': "Warnen wenn Mond > (% Beleuchtung):",
        'object_types_header': "**Objekttypen**",
        'object_types_error_extract': "Objekttypen konnten nicht aus Katalog extrahiert werden.",
        'object_types_label': "Typen filtern (leer = alle):",
        'object_type_glossary_title': "Objekttyp-Glossar", # NEU
        'object_type_glossary': { # NEU
            "OCl": "Offener Sternhaufen", "GCl": "Kugelsternhaufen", "Cl+N": "Haufen + Nebel",
            "Gal": "Galaxie", "PN": "Planetarischer Nebel", "SNR": "Supernova-Überrest",
            "Neb": "Nebel (allgemein)", "EmN": "Emissionsnebel", "RfN": "Reflexionsnebel",
            "HII": "HII-Region", "AGN": "Aktiver Galaxienkern"
         },
        'results_options_expander': "⚙️ Ergebnis-Optionen",
        'results_options_max_objects_label': "Max. Anzahl Objekte zur Anzeige:",
        'results_options_sort_method_label': "Ergebnisse sortieren nach:",
        'results_options_sort_duration': "Dauer & Höhe",
        'results_options_sort_magnitude': "Helligkeit",
        'moon_metric_label': "Mondhelligkeit (ca.)",
        'moon_warning_message': "Warnung: Mond ist heller ({:.0f}%) als Schwelle ({:.0f}%)!",
        'moon_phase_error': "Mondphasen-Berechnungsfehler: {}",
        'find_button_label': "🔭 Beobachtbare Objekte finden",
        'search_params_header': "Suchparameter",
        'search_params_location': "📍 Standort: {}",
        'search_params_time': "⏱️ Zeitpunkt: {}",
        'search_params_timezone': "🌍 Zeitzone: {}",
        'search_params_time_now': "Kommende Nacht (ab {} UTC)",
        'search_params_time_specific': "Nacht nach dem {}",
        'search_params_filter_mag': "✨ Filter: {}",
        'search_params_filter_mag_bortle': "Bortle {} (<= {:.1f} mag)",
        'search_params_filter_mag_manual': "Manuell ({:.1f}-{:.1f} mag)",
        'search_params_filter_alt_types': "🔭 Filter: Min. Höhe {}°, Typen: {}",
        'search_params_filter_direction': "🧭 Filter: Max. Höhe Richtung: {}",
        'search_params_types_all': "Alle",
        'search_params_direction_all': "Alle",
        'spinner_searching': "Berechne Fenster & suche Objekte...",
        'spinner_geocoding': "Suche nach Ort...",
        'window_info_template': "{}",
        'error_no_window': "Kein gültiges Beobachtungsfenster für gewähltes Datum und Ort gefunden.",
        'success_objects_found': "{} passende Objekte gefunden.",
        'info_showing_list_duration': "Anzeige von {} Objekten, sortiert nach Sichtbarkeitsdauer und max. Höhe:",
        'info_showing_list_magnitude': "Anzeige von {} Objekten, sortiert nach Helligkeit (hellste zuerst):",
        'error_search_unexpected': "Unerwarteter Fehler während der Suche:",
        'results_list_header': "Ergebnisliste",
        'results_export_name': "Name",
        'results_export_type': "Typ",
        'results_export_mag': "Magnitude",
        'results_export_ra': "RA",
        'results_export_dec': "Dec",
        'results_export_max_alt': "Max Höhe (°)",
        'results_export_az_at_max': "Azimut bei Max (°)",
        'results_export_direction_at_max': "Richtung bei Max",
        'results_export_time_max_utc': "Zeit bei Max (UTC)",
        'results_export_time_max_local': "Zeit bei Max (Lokale ZZ)",
        'results_export_cont_duration': "Max. kont. Dauer (h)",
        'results_export_total_duration': "Gesamtdauer (h)",
        'results_expander_title': "{} ({}) - Mag: {:.1f}",
        'results_coords_header': "**Koordinaten:**",
        'results_max_alt_header': "**Max. Höhe:**",
        'results_azimuth_label': "(Azimut: {:.1f}°{})",
        'results_direction_label': ", Richtung: {}",
        'results_best_time_header': "**Beste Zeit (Lokale ZZ):**",
        'results_cont_duration_header': "**Max. kont. Dauer:**",
        'results_total_duration_header': "**Gesamtdauer:**",
        'results_duration_value': "{:.1f} Stunden",
        'results_plot_button': "📈 Höhenverlauf",
        'results_spinner_plotting': "Erstelle Plot...",
        'results_plot_error': "Plot Fehler: {}",
        'results_plot_not_created': "Plot konnte nicht erstellt werden.",
        'results_close_plot_button': "Plot schliessen",
        'results_save_csv_button': "💾 Ergebnisliste als CSV speichern",
        'results_csv_filename': "dso_beobachtungsliste_{}.csv",
        'results_csv_export_error': "CSV Export Fehler: {}",
        'warning_no_objects_found': "Keine Objekte gefunden, die allen Kriterien für das berechnete Beobachtungsfenster entsprechen.",
        'info_initial_prompt': "Willkommen! Bitte **Koordinaten eingeben** oder **Ort suchen**, um die Objektsuche zu aktivieren.", # Updated prompt
        'plot_time_label_local': "Zeit ({})",
        'plot_time_label_utc': "Zeit (UTC)",
        'plot_altitude_label': "Höhe",
        'plot_min_altitude_label': "Mindesthöhe ({:.0f}°)",
        'plot_title': "Höhenverlauf für {}",
        'plot_ylabel': "Höhe (°)",
        'error_processing_object': "Fehler bei Verarbeitung von {}: {}",
        'window_calc_error': "Fehler bei der Berechnung des Beobachtungsfensters: {}\n{}",
        'window_fallback_info': "\nVerwende Fallback-Fenster: {} bis {} UTC",
        'window_invalid_calc': "Warnung: Ungültiges Dunkelheitsfenster berechnet ({} bis {}). Verwende Fallback.",
        'window_starts_now': "Beobachtungsfenster beginnt jetzt ({} UTC) bis {} UTC (Astron. Dämmerung)",
        'window_starts_at': "Beobachtungsfenster beginnt um {} UTC bis {} UTC (Astron. Dämmerung)",
        'window_for_night': "Beobachtungsfenster für die Nacht vom {}: {} bis {} UTC (Astron. Dämmerung)",
        'window_already_passed': "Warnung: Heutiges Beobachtungsfenster ist bereits vorbei. Berechne für morgen Nacht.",
        'window_no_darkness': "Warnung: Konnte kein Fenster für astronomische Dunkelheit für die Nacht vom {} finden. Verwende Fallback.",
        'window_fallback_append': "\nFallback Beobachtungsfenster: {} bis {} UTC",
        'error_loading_catalog': "Fehler beim Laden der Katalogdatei: {}",
        'info_catalog_loaded': "Katalog geladen: {} Objekte.",
        'warning_catalog_empty': "Katalogdatei geladen, aber keine passenden Objekte nach Filterung gefunden.",
     },
     'fr': { # NEU: Französische Übersetzungen
        'page_title': "Chercheur d'objets du ciel profond avancé",
        'settings_header': "Paramètres",
        'language_select_label': "Langue / Language / Sprache",
        'location_expander': "📍 Lieu",
        'location_select_label': "Sélectionner la méthode de localisation",
        'location_option_manual': "Entrer manuellement",
        'location_option_search': "Rechercher par nom",
        'location_search_label': "Entrer le nom du lieu :",
        'location_search_submit_button': "Trouver les coordonnées",
        'location_search_placeholder': "ex: Paris, France ou Mont Palomar",
        'location_search_found': "Trouvé : {}",
        'location_search_coords': "Lat : {:.4f}, Lon : {:.4f}",
        'location_search_error_not_found': "Lieu non trouvé. Essayez un nom plus spécifique.",
        'location_search_error_service': "Erreur du service de géocodage : {}",
        'location_lat_label': "Latitude (°N)",
        'location_lon_label': "Longitude (°E)",
        'location_elev_label': "Altitude (Mètres)",
        'location_manual_display': "Manuel ({:.4f}, {:.4f})",
        'location_search_display': "Recherché : {} ({:.4f}, {:.4f})",
        'location_error': "Erreur de localisation : {}",
        'location_error_fallback': "ERREUR - Utilisation de la solution de repli",
        'location_error_manual_none': "Les champs de localisation manuelle ne peuvent pas être vides ou invalides.",
        'location_error_manual_search': "Recherche d'objets impossible : Les champs de localisation manuelle sont invalides ou vides.",
        'location_error_search_search': "Recherche d'objets impossible : Veuillez d'abord rechercher un lieu valide.",
        'location_error_undefined': "Recherche d'objets impossible : Lieu non défini (sélectionnez Manuel ou Recherche).",
        'time_expander': "⏱️ Heure & Fuseau Horaire",
        'time_select_label': "Sélectionner l'heure",
        'time_option_now': "Maintenant (nuit à venir)",
        'time_option_specific': "Nuit spécifique",
        'time_date_select_label': "Sélectionner la date :",
        'timezone_auto_set_label': "Fuseau horaire détecté :",
        'timezone_auto_fail_label': "Fuseau horaire :",
        'timezone_auto_fail_msg': "Impossible de détecter le fuseau horaire, utilisation de UTC.",
        'filters_expander': "✨ Filtres & Conditions",
        'mag_filter_header': "**Filtre de Magnitude**",
        'mag_filter_method_label': "Méthode de filtrage :",
        'mag_filter_option_bortle': "Échelle de Bortle",
        'mag_filter_option_manual': "Manuel",
        'mag_filter_bortle_label': "Échelle de Bortle :",
        'mag_filter_bortle_help': "Obscurité du ciel : 1=Excellent Noir, 9=Ciel de centre-ville",
        'mag_filter_min_mag_label': "Magnitude Min. :",
        'mag_filter_min_mag_help': "Magnitude de l'objet le plus brillant à inclure",
        'mag_filter_max_mag_label': "Magnitude Max. :",
        'mag_filter_max_mag_help': "Magnitude de l'objet le plus faible à inclure",
        'mag_filter_warning_min_max': "La magnitude Min. est supérieure à la magnitude Max. !",
        'min_alt_header': "**Altitude Minimale**",
        'min_alt_label': "Altitude Min. de l'objet (°) :",
        'direction_filter_header': "**Filtre de Direction au Pic**",
        'direction_filter_label': "Afficher les objets culminant en direction de :",
        'direction_option_all': "Toutes", # Französisch für 'All'
        'moon_warning_header': "**Avertissement Lunaire**",
        'moon_warning_label': "Avertir si Lune > (% Illumination) :",
        'object_types_header': "**Types d'Objets**",
        'object_types_error_extract': "Impossible d'extraire les types d'objets du catalogue.",
        'object_types_label': "Filtrer les types (laisser vide pour tous) :",
        'object_type_glossary_title': "Glossaire des types d'objets", # NEU
        'object_type_glossary': { # NEU
            "OCl": "Amas ouvert", "GCl": "Amas globulaire", "Cl+N": "Amas + Nébuleuse",
            "Gal": "Galaxie", "PN": "Nébuleuse planétaire", "SNR": "Rémanent de supernova",
            "Neb": "Nébuleuse (général)", "EmN": "Nébuleuse en émission", "RfN": "Nébuleuse par réflexion",
            "HII": "Région HII", "AGN": "Noyau actif de galaxie"
         },
        'results_options_expander': "⚙️ Options de Résultat",
        'results_options_max_objects_label': "Nombre max. d'objets à afficher :",
        'results_options_sort_method_label': "Trier les résultats par :",
        'results_options_sort_duration': "Durée & Altitude",
        'results_options_sort_magnitude': "Luminosité",
        'moon_metric_label': "Illumination Lunaire (approx.)",
        'moon_warning_message': "Attention : La Lune est plus brillante ({:.0f}%) que le seuil ({:.0f}%) !",
        'moon_phase_error': "Erreur de calcul de la phase lunaire : {}",
        'find_button_label': "🔭 Trouver les Objets Observables",
        'search_params_header': "Paramètres de Recherche",
        'search_params_location': "📍 Lieu : {}",
        'search_params_time': "⏱️ Heure : {}",
        'search_params_timezone': "🌍 Fuseau horaire : {}",
        'search_params_time_now': "Nuit à venir (à partir de {} UTC)",
        'search_params_time_specific': "Nuit après le {}",
        'search_params_filter_mag': "✨ Filtre : {}",
        'search_params_filter_mag_bortle': "Bortle {} (<= {:.1f} mag)",
        'search_params_filter_mag_manual': "Manuel ({:.1f}-{:.1f} mag)",
        'search_params_filter_alt_types': "🔭 Filtre : Alt Min {}°, Types : {}",
        'search_params_filter_direction': "🧭 Filtre : Direction au Pic : {}",
        'search_params_types_all': "Tous",
        'search_params_direction_all': "Toutes",
        'spinner_searching': "Calcul de la fenêtre & recherche d'objets...",
        'spinner_geocoding': "Recherche du lieu...",
        'window_info_template': "{}",
        'error_no_window': "Aucune fenêtre d'observation valide trouvée pour la date et le lieu sélectionnés.",
        'success_objects_found': "{} objets correspondants trouvés.",
        'info_showing_list_duration': "Affichage de {} objets, triés par durée de visibilité et altitude maximale :",
        'info_showing_list_magnitude': "Affichage de {} objets, triés par luminosité (les plus brillants d'abord) :",
        'error_search_unexpected': "Une erreur inattendue s'est produite lors de la recherche :",
        'results_list_header': "Liste des Résultats",
        'results_export_name': "Nom",
        'results_export_type': "Type",
        'results_export_mag': "Magnitude",
        'results_export_ra': "AD", # Ascension Droite
        'results_export_dec': "Dec", # Déclinaison
        'results_export_max_alt': "Altitude Max (°)",
        'results_export_az_at_max': "Azimut au Max (°)",
        'results_export_direction_at_max': "Direction au Max",
        'results_export_time_max_utc': "Heure au Max (UTC)",
        'results_export_time_max_local': "Heure au Max (FH Local)",
        'results_export_cont_duration': "Durée Cont. Max (h)",
        'results_export_total_duration': "Durée Totale (h)",
        'results_expander_title': "{} ({}) - Mag : {:.1f}",
        'results_coords_header': "**Coordonnées :**",
        'results_max_alt_header': "**Altitude Max. :**",
        'results_azimuth_label': "(Azimut : {:.1f}°{})",
        'results_direction_label': ", Direction : {}",
        'results_best_time_header': "**Meilleure Heure (FH Local) :**",
        'results_cont_duration_header': "**Durée Cont. Max. :**",
        'results_total_duration_header': "**Durée Totale :**",
        'results_duration_value': "{:.1f} heures",
        'results_plot_button': "📈 Graphique d'Altitude",
        'results_spinner_plotting': "Création du graphique...",
        'results_plot_error': "Erreur du graphique : {}",
        'results_plot_not_created': "Le graphique n'a pas pu être créé.",
        'results_close_plot_button': "Fermer le graphique",
        'results_save_csv_button': "💾 Enregistrer la liste en CSV",
        'results_csv_filename': "dso_liste_observation_{}.csv",
        'results_csv_export_error': "Erreur d'exportation CSV : {}",
        'warning_no_objects_found': "Aucun objet trouvé correspondant à tous les critères pour la fenêtre d'observation calculée.",
        'info_initial_prompt': "Bienvenue ! Veuillez **entrer des coordonnées** manuellement ou **rechercher un nom de lieu** pour activer la recherche principale.", # Updated prompt
        'plot_time_label_local': "Heure ({})",
        'plot_time_label_utc': "Heure (UTC)",
        'plot_altitude_label': "Altitude",
        'plot_min_altitude_label': "Altitude Min. ({:.0f}°)",
        'plot_title': "Profil d'Altitude pour {}",
        'plot_ylabel': "Altitude (°)",
        'error_processing_object': "Erreur lors du traitement de {}: {}",
        'window_calc_error': "Erreur lors du calcul de la fenêtre d'observation : {}\n{}",
        'window_fallback_info': "\nUtilisation de la fenêtre de repli : {} à {} UTC",
        'window_invalid_calc': "Attention : Fenêtre d'obscurité invalide calculée ({} à {}). Utilisation de la solution de repli.",
        'window_starts_now': "La fenêtre d'observation commence maintenant ({} UTC) jusqu'à {} UTC (Crépuscule Astron.)",
        'window_starts_at': "La fenêtre d'observation commence à {} UTC jusqu'à {} UTC (Crépuscule Astron.)",
        'window_for_night': "Fenêtre d'observation pour la nuit du {}: {} à {} UTC (Crépuscule Astron.)",
        'window_already_passed': "Attention : La fenêtre d'observation d'aujourd'hui est déjà passée. Calcul pour demain soir.",
        'window_no_darkness': "Attention : Impossible de trouver une fenêtre d'obscurité astronomique pour la nuit du {}. Utilisation de la solution de repli.",
        'window_fallback_append': "\nFenêtre d'observation de repli : {} à {} UTC",
        'error_loading_catalog': "Erreur lors du chargement du fichier catalogue : {}",
        'info_catalog_loaded': "Catalogue chargé : {} objets.",
        'warning_catalog_empty': "Fichier catalogue chargé, mais aucun objet approprié trouvé après filtrage.",
     }
}

# --- Global Configuration & Initial Values ---
INITIAL_LAT = 47.17
INITIAL_LON = 8.01
INITIAL_HEIGHT = 550
INITIAL_TIMEZONE = "Europe/Zurich" # Fallback if auto-detection fails initially

# --- Path to Catalog File ---
# WICHTIG: Die Katalogdatei (z.B. 'ongc.csv') muss sich im selben Verzeichnis
#          wie dieses Python-Skript befinden, damit sie gefunden wird!
try:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    APP_DIR = os.getcwd()
CATALOG_FILENAME = "ongc.csv"
CATALOG_FILEPATH = os.path.join(APP_DIR, CATALOG_FILENAME)


# Define cardinal directions
CARDINAL_DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
# Internal key for 'All' - remains English for consistency in logic
ALL_DIRECTIONS_KEY = 'All'

# --- Initialize TimezoneFinder (cached) ---
@st.cache_resource
def get_timezone_finder():
    """Initializes and returns a TimezoneFinder instance."""
    if TimezoneFinder:
        try:
            # Use try_load=True for potential lazy loading if supported by the library version
            return TimezoneFinder(in_memory=True)
        except Exception as e:
            print(f"Error initializing TimezoneFinder: {e}")
            return None
    return None

tf = get_timezone_finder()

# --- Initialize Session State ---
def initialize_session_state():
    """Initializes all required session state keys if they don't exist."""
    defaults = {
        'language': 'en',
        'plot_object_name': None,
        'show_plot': False,
        'last_results': [],
        'find_button_pressed': False,
        # Location related state
        'location_choice_key': 'Search', # Start with Search mode active
        'manual_lat_val': INITIAL_LAT,
        'manual_lon_val': INITIAL_LON,
        'manual_height_val': INITIAL_HEIGHT,
        'location_search_query': "",
        'searched_location_name': None,
        'location_search_status_msg': "",
        'location_search_success': False,
        # Timezone state
        'selected_timezone': INITIAL_TIMEZONE, # Will be updated automatically
        # Filter states - these should persist across language changes
        'manual_min_mag_slider': 0.0,
        'manual_max_mag_slider': 16.0,
        'object_type_filter_exp': [],
        'mag_filter_mode_exp': 'Bortle Scale',
        'bortle_slider': 5, # Store slider values directly
        'min_alt_slider': 20, # Store slider values directly
        'moon_phase_slider': 35, # Store slider values directly
        'sort_method': 'Duration & Altitude',
        'selected_peak_direction': ALL_DIRECTIONS_KEY, # Internal key ('All', 'N', etc.)
        # Other state
        'expanded_object_name': None,
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# --- Helper Functions ---
def get_magnitude_limit(bortle_scale: int) -> float:
    """Calculates the approximate limiting magnitude based on Bortle scale."""
    limits = {1: 15.5, 2: 15.5, 3: 14.5, 4: 14.5, 5: 13.5, 6: 12.5, 7: 11.5, 8: 10.5, 9: 9.5}
    return limits.get(bortle_scale, 9.5)

def azimuth_to_direction(azimuth_deg: float) -> str:
    """Converts an azimuth angle (degrees) to a cardinal direction string."""
    azimuth_deg = azimuth_deg % 360 # Ensure angle is within 0-360
    index = round(azimuth_deg / 45) % 8
    return CARDINAL_DIRECTIONS[index]

def _get_fallback_window(reference_time: 'Time') -> tuple['Time', 'Time']:
    """Provides a default observation window (e.g., 9 PM to 3 AM local time) in UTC."""
    try:
        local_tz = datetime.now(timezone.utc).astimezone().tzinfo
        dt_ref = reference_time.datetime
        utc_offset_seconds = local_tz.utcoffset(dt_ref).total_seconds() if local_tz and local_tz.utcoffset(dt_ref) is not None else 3600
        utc_offset_hours = utc_offset_seconds / 3600
    except Exception:
        utc_offset_hours = 1 # Fallback offset (e.g., CET)

    start_date = reference_time.datetime.date()
    local_dt_start = datetime.combine(start_date, time(21, 0)) # 9 PM local
    local_dt_end = datetime.combine(start_date + timedelta(days=1), time(3, 0)) # 3 AM local next day
    start_time_utc = Time(local_dt_start - timedelta(hours=utc_offset_hours))
    end_time_utc = Time(local_dt_end - timedelta(hours=utc_offset_hours))
    if end_time_utc < reference_time:
          start_time_utc += timedelta(days=1)
          end_time_utc += timedelta(days=1)
    return start_time_utc, end_time_utc

def get_observable_window(observer_location: 'EarthLocation', reference_time: 'Time', is_now: bool, lang: str) -> tuple['Time' | None, 'Time' | None, str]:
    """Calculates the astronomical twilight window."""
    t = translations[lang]
    status_message = ""
    try:
        reference_date = reference_time.datetime.date()
        midnight_dt = datetime.combine(reference_date + timedelta(days=1), time(0, 0), tzinfo=timezone.utc)
        midnight = Time(midnight_dt)
        time_range = midnight + np.linspace(-12, 12, 100) * u.hour
        # Ensure observer_location is valid before proceeding
        if not isinstance(observer_location, EarthLocation):
             raise ValueError("Invalid observer location provided.")
        sun_altaz = get_sun(time_range).transform_to(AltAz(obstime=time_range, location=observer_location))
        dark_indices = np.where(sun_altaz.alt < -18 * u.deg)[0]

        if len(dark_indices) > 0:
            start_time_calc = time_range[dark_indices[0]]
            end_time_calc = time_range[dark_indices[-1]]
            # Sanity check: window duration should be reasonable for a single night
            calculated_duration_hours = (end_time_calc - start_time_calc).to(u.hour).value
            # Allow slightly longer for high latitudes, but cap extreme values
            if end_time_calc <= start_time_calc or calculated_duration_hours > 18: # Increased cap slightly
                status_message = t['window_invalid_calc'].format(start_time_calc.iso, end_time_calc.iso)
                start_time, end_time = _get_fallback_window(reference_time)
                status_message += t['window_fallback_append'].format(start_time.iso, end_time.iso)
            else:
                start_time = start_time_calc
                end_time = end_time_calc
                current_utc_time = Time.now()
                if is_now and start_time < current_utc_time:
                    start_time = current_utc_time
                if is_now and end_time < current_utc_time:
                    status_message = t['window_already_passed'] + "\n"
                    # Ensure recalculation uses the valid location
                    return get_observable_window(observer_location, current_utc_time + timedelta(days=1), True, lang)

                date_str = (start_time.datetime.date() if not is_now else reference_date).strftime('%Y-%m-%d')
                start_fmt = start_time.to_datetime(timezone.utc).strftime('%H:%M %Z')
                end_fmt = end_time.to_datetime(timezone.utc).strftime('%H:%M %Z')
                if is_now and start_time == current_utc_time:
                     status_message += t['window_starts_now'].format(start_fmt, end_fmt)
                elif is_now and start_time > current_utc_time:
                     status_message += t['window_starts_at'].format(start_fmt, end_fmt)
                else:
                     status_message += t['window_for_night'].format(date_str, start_fmt, end_fmt)
            return start_time, end_time, status_message
        else:
            date_str = reference_date.strftime('%Y-%m-%d')
            status_message = t['window_no_darkness'].format(date_str)
            start_time, end_time = _get_fallback_window(reference_time)
            status_message += t['window_fallback_append'].format(start_time.iso, end_time.iso)
            return start_time, end_time, status_message
    except Exception as e:
        status_message = t['window_calc_error'].format(e, traceback.format_exc())
        start_time, end_time = _get_fallback_window(reference_time)
        status_message += t['window_fallback_info'].format(start_time.iso, end_time.iso)
        return start_time, end_time, status_message

def find_observable_objects(
    location: 'EarthLocation',
    observing_times: 'Time',
    min_altitude_limit: 'u.Quantity',
    magnitude_filter_mode: str,
    bortle_scale: int,
    manual_min_mag: float | None,
    manual_max_mag: float | None,
    selected_object_types: list, # Empty list means all types
    df_catalog: pd.DataFrame,
    lang: str
) -> list:
    """
    Finds DSOs from the catalog DataFrame visible during the observing times.
    Calculates max continuous and total visibility durations.
    """
    t = translations[lang]
    observable_objects = []
    magnitude_limit = None
    MAX_REALISTIC_NIGHT_DURATION = 16.0 # Hours, simple cap for duration display

    # Determine magnitude limit
    if magnitude_filter_mode == 'Bortle Scale':
        magnitude_limit = get_magnitude_limit(bortle_scale)
    elif magnitude_filter_mode == 'Manual':
        is_min_valid = isinstance(manual_min_mag, (int, float))
        is_max_valid = isinstance(manual_max_mag, (int, float))
        if is_min_valid and is_max_valid:
            if manual_min_mag > manual_max_mag:
                manual_min_mag, manual_max_mag = manual_max_mag, manual_min_mag
        else:
             manual_min_mag = None; manual_max_mag = None

    # Pre-calculate AltAz frame
    altaz_frame = AltAz(obstime=observing_times, location=location)
    time_step_duration = (observing_times[1] - observing_times[0]).to(u.hour).value if len(observing_times) > 1 else 0

    for index, row in df_catalog.iterrows():
        name = row['Name']; ra_str = row['RA_str']; dec_str = row['Dec_str']
        mag = row['Mag']; obj_type = row['Type']

        # --- Apply Filters ---
        if selected_object_types and obj_type not in selected_object_types: continue
        if not isinstance(mag, (int, float)): continue
        if magnitude_filter_mode == 'Bortle Scale':
            if magnitude_limit is not None and mag > magnitude_limit: continue
        elif magnitude_filter_mode == 'Manual':
            if manual_min_mag is not None and manual_max_mag is not None:
                if not (manual_min_mag <= mag <= manual_max_mag): continue

        # --- Calculate Observability ---
        try:
            target = SkyCoord(ra=ra_str, dec=dec_str, frame='icrs', unit=(u.hourangle, u.deg))
            target_altaz = target.transform_to(altaz_frame)
            altitudes = target_altaz.alt
            azimuths = target_altaz.az

            # Find indices where object is above minimum altitude during the dark window
            valid_indices = np.where(altitudes >= min_altitude_limit)[0]

            if len(valid_indices) > 0:
                # Find peak altitude within the valid period
                peak_in_window_index = valid_indices[np.argmax(altitudes[valid_indices])]
                peak_alt_val = altitudes[peak_in_window_index].to(u.deg).value
                peak_az_val = azimuths[peak_in_window_index].to(u.deg).value
                peak_direction = azimuth_to_direction(peak_az_val)
                peak_time = observing_times[peak_in_window_index]

                # --- Calculate Durations ---
                max_cont_duration_hours = 0.0
                total_duration_hours = 0.0
                if time_step_duration > 0:
                    diffs = np.diff(valid_indices)
                    splits = np.where(diffs > 1)[0] + 1
                    blocks = np.split(valid_indices, splits)
                    for block in blocks:
                        block_len = len(block)
                        if block_len > 1:
                            # Duration from start of first step to end of last step in block
                            duration = observing_times[block[-1]] - observing_times[block[0]]
                            current_block_duration_hours = duration.to(u.hour).value
                        elif block_len == 1:
                             # Single point visibility, duration is approx one time step
                             current_block_duration_hours = time_step_duration
                        else: # Empty block (shouldn't happen with split logic)
                            current_block_duration_hours = 0.0

                        total_duration_hours += current_block_duration_hours
                        max_cont_duration_hours = max(max_cont_duration_hours, current_block_duration_hours)

                # Apply a cap to prevent unrealistically long durations (e.g., >16h)
                # This is a pragmatic fix for potential edge cases in window calculation
                capped_max_cont_duration = min(max_cont_duration_hours, MAX_REALISTIC_NIGHT_DURATION)
                capped_total_duration = min(total_duration_hours, MAX_REALISTIC_NIGHT_DURATION)

                observable_objects.append({
                    "name": name, "type": obj_type, "magnitude": mag,
                    "ra_str": ra_str, "dec_str": dec_str,
                    "ra": target.ra.to_string(unit=u.hour, sep='hms', precision=1),
                    "dec": target.dec.to_string(unit=u.deg, sep='dms', precision=0),
                    "peak_alt": peak_alt_val, "peak_az": peak_az_val, "peak_direction": peak_direction,
                    "peak_time_utc": peak_time.iso,
                    "cont_duration_hours": capped_max_cont_duration, # Use capped value
                    "total_duration_hours": capped_total_duration,   # Use capped value
                    "times_jd": observing_times.jd, "altitudes": altitudes.to(u.deg).value,
                    "azimuths": azimuths.to(u.deg).value, "min_alt_limit": min_altitude_limit.value
                })
        except ValueError: pass # Skip objects with invalid coordinates
        except Exception as e: st.warning(t['error_processing_object'].format(name, e))
    return observable_objects

def create_moon_phase_svg(illumination_fraction: float, size: int = 80) -> str:
    """Generates an SVG image for moon phase."""
    percentage = illumination_fraction * 100
    radius = size // 2 - 6; cx = cy = size // 2
    stroke_color = "#DDDDDD"; stroke_width = 3; text_fill = "#EEEEEE"
    font_size = size * 0.3
    svg = f"""<svg width="{size}" height="{size}" viewbox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle;">
      <circle cx="{cx}" cy="{cy}" r="{radius}" stroke="{stroke_color}" stroke-width="{stroke_width}" fill="#222222" />
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="{font_size}px" fill="{text_fill}" font-weight="bold">{percentage:.0f}%</text>
    </svg>"""
    return svg

# Plot function - No caching
def plot_altitude(_obj_data: dict, _location_tuple: tuple, lang: str, tz_name: str):
    """Creates a Matplotlib altitude plot."""
    t = translations[lang]
    if plt is None or mdates is None or pytz is None:
        st.error("Plotting libraries (matplotlib, pytz) not available.")
        return None

    fig, ax = plt.subplots()
    try:
        times = Time(_obj_data['times_jd'], format='jd')
        # --- Timezone Conversion for Plot ---
        try:
            selected_tz = pytz.timezone(tz_name)
            times_local = [t_inst.to_datetime(timezone=selected_tz) for t_inst in times]
            xlabel = t['plot_time_label_local'].format(tz_name)
        except Exception as tz_err:
             print(f"Timezone conversion/lookup error in plot for '{tz_name}': {tz_err}. Falling back to UTC.")
             times_local = times.datetime
             xlabel = t['plot_time_label_utc']

        # --- Plotting Data ---
        ax.plot(times_local, _obj_data['altitudes'], label=t['plot_altitude_label'], color='#00C0F0')
        ax.axhline(_obj_data['min_alt_limit'], color='#FF4040', linestyle='--', label=t['plot_min_altitude_label'].format(_obj_data["min_alt_limit"]))
        ax.set_ylim(0, 90)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(t['plot_ylabel'])
        ax.set_title(t['plot_title'].format(_obj_data['name']))
        ax.legend()
        ax.grid(True, linestyle=':', linewidth=0.5, color='#555555')

        # --- Formatting X-axis ---
        xfmt = mdates.DateFormatter('%H:%M')
        ax.xaxis.set_major_formatter(xfmt)
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        plt.tight_layout()

    except Exception as e:
        print(f"Error plotting altitude for {_obj_data.get('name', 'Unknown')}: {e}")
        st.error(t['results_plot_error'].format(e))
        plt.close(fig)
        return None
    return fig

def get_local_time_str(utc_iso_time: str, tz_name: str) -> tuple[str, str]:
    """Converts UTC ISO time string to time string in the specified timezone."""
    try:
        if Time is None or pytz is None: return "N/A", ""
        selected_tz = pytz.timezone(tz_name) # tz_name should be valid here
        dt_peak_utc = Time(utc_iso_time, format='iso', scale='utc').datetime.replace(tzinfo=timezone.utc)
        dt_peak_local = dt_peak_utc.astimezone(selected_tz)
        peak_time_local_str = dt_peak_local.strftime('%Y-%m-%d %H:%M:%S')
        return peak_time_local_str, tz_name
    except Exception as e:
        print(f"Error converting time {utc_iso_time} to timezone {tz_name}: {e}")
        return "N/A", tz_name


# --- Data Loading Function ---
@st.cache_data
def load_ongc_data(catalog_path: str, lang: str) -> pd.DataFrame | None:
    """Loads, filters, and preprocesses data from the OpenNGC CSV file."""
    # Access translations using the provided lang argument
    t_load = translations[lang]
    try:
        if not os.path.exists(catalog_path):
             # Use translated error message
             st.error(f"{t_load['error_loading_catalog'].split(':')[0]}: File not found at {catalog_path}")
             st.info("Please ensure the file 'ongc.csv' is in the same directory as the Python script.")
             return None
        df = pd.read_csv(catalog_path, sep=';', comment='#', low_memory=False)
        dso_types = ['Galaxy', 'Globular Cluster', 'Open Cluster', 'Nebula',
                     'Planetary Nebula', 'Supernova Remnant', 'HII', 'Emission Nebula',
                     'Reflection Nebula', 'Cluster + Nebula', 'Gal', 'GCl', 'Gx', 'OC',
                     'PN', 'SNR', 'Neb', 'EmN', 'RfN', 'C+N', 'Gxy', 'AGN', 'MWSC']
        type_pattern = '|'.join(dso_types)
        if 'Type' not in df.columns:
            st.error("Column 'Type' not found in the catalog file.")
            return None
        df_filtered = df[df['Type'].astype(str).str.contains(type_pattern, case=False, na=False)].copy()
        mag_col = None
        if 'V-Mag' in df_filtered.columns: mag_col = 'V-Mag'
        elif 'B-Mag' in df_filtered.columns: mag_col = 'B-Mag'
        elif 'Mag' in df_filtered.columns: mag_col = 'Mag'
        if mag_col is None:
            st.error(f"Magnitude column ('V-Mag', 'B-Mag' or 'Mag') not found.")
            return None
        df_filtered['Mag'] = pd.to_numeric(df_filtered[mag_col], errors='coerce')
        df_filtered.dropna(subset=['Mag'], inplace=True)
        if 'RA' not in df_filtered.columns or 'Dec' not in df_filtered.columns:
             st.error("RA or Dec column not found.")
             return None
        df_filtered['RA_str'] = df_filtered['RA'].astype(str)
        df_filtered['Dec_str'] = df_filtered['Dec'].astype(str)
        df_filtered.dropna(subset=['RA_str', 'Dec_str'], inplace=True)
        df_filtered = df_filtered[df_filtered['RA_str'].str.strip() != '']
        df_filtered = df_filtered[df_filtered['Dec_str'].str.strip() != '']
        if 'Name' not in df_filtered.columns:
            st.error("'Name' column not found.")
            return None
        df_final = df_filtered[['Name', 'RA_str', 'Dec_str', 'Mag', 'Type']].copy()
        df_final.drop_duplicates(subset=['Name'], inplace=True, keep='first')
        df_final.reset_index(drop=True, inplace=True)
        if not df_final.empty:
            return df_final
        else:
            # Use translated warning
            st.warning(t_load['warning_catalog_empty'])
            return None
    except FileNotFoundError:
        st.error(f"{t_load['error_loading_catalog'].split(':')[0]}: File not found at {catalog_path}")
        st.info("Please ensure the file 'ongc.csv' is in the same directory as the Python script.")
        return None
    except pd.errors.EmptyDataError:
        st.error(f"Catalog file is empty: {catalog_path}")
        return None
    except Exception as e:
         # Use translated error
        st.error(t_load['error_loading_catalog'].format(e))
        if "tokenizing data" in str(e):
             st.info("This often means the wrong separator (delimiter) or inconsistent file structure. The app expects a semicolon (;) separator. Please check your 'ongc.csv' file.")
        else:
             st.info("Please check the file path, filename, and format.")
        st.exception(e)
        return None

# --- Initialize Session State ---
# Call this *before* accessing session state
initialize_session_state()

# --- Get Current Language and Translations ---
# This needs to happen *after* state initialization but *before* UI elements that use translations
lang = st.session_state.language
# Ensure language exists in translations, fallback to 'en'
if lang not in translations:
    lang = 'en'
    st.session_state.language = lang
t = translations[lang]


# --- Load Catalog Data ---
# Load data after language is set, so load_ongc_data gets correct translations
df_catalog_data = load_ongc_data(CATALOG_FILEPATH, lang)


# --- Custom CSS Styling ---
st.markdown("""
<style>
    /* CSS unchanged */
    .main .block-container { background-color: #1E1E1E; color: #EAEAEA; border-radius: 10px; padding: 2rem; }
    div[data-testid="stButton"] > button:not([kind="secondary"]) { background-image: linear-gradient(to right, #007bff, #0056b3); color: white; border: none; padding: 10px 24px; text-align: center; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px; transition-duration: 0.4s; }
    div[data-testid="stButton"] > button:not([kind="secondary"]):hover { background-image: linear-gradient(to right, #0056b3, #003d80); color: white; }
     div[data-testid="stButton"] > button[kind="secondary"] { background-color: #555; color: #eee; }
     div[data-testid="stButton"] > button[kind="secondary"]:hover { background-color: #777; color: white; }
    .streamlit-expanderHeader { background-color: #333333; color: #EAEAEA; border-radius: 5px; }
    div[data-testid="stMetric"] { background-color: #2a2a2a; border-radius: 8px; padding: 10px; }
    div[data-testid="stMetric"] > div[data-testid="stMetricLabel"] { color: #AAAAAA; }
    div[data-testid="stFormSubmitButton"] > button { margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# --- Title ---
# Static English Title
st.title("Advanced DSO Finder")

# --- Sidebar ---
with st.sidebar:
    # Show catalog loaded message here now that translations are ready
    if df_catalog_data is not None and 'catalog_loaded_msg_shown' not in st.session_state:
         st.success(t['info_catalog_loaded'].format(len(df_catalog_data)))
         st.session_state.catalog_loaded_msg_shown = True # Flag to prevent re-showing
    elif df_catalog_data is None and 'catalog_error_msg_shown' not in st.session_state:
        # Optionally show a persistent error if loading failed
        st.error("Catalog loading failed. Check file.")
        st.session_state.catalog_error_msg_shown = True


    st.header(t['settings_header'])

    # --- Language Selector ---
    language_options = {'en': 'English', 'de': 'Deutsch', 'fr': 'Français'} # Added French
    lang_keys = list(language_options.keys())
    try:
        current_lang_index = lang_keys.index(st.session_state.language)
    except ValueError:
        current_lang_index = 0
        st.session_state.language = lang_keys[0] # Reset state to default if invalid

    selected_lang_key = st.radio(
        t['language_select_label'], options=lang_keys,
        format_func=lambda key: language_options[key], key='language_radio',
        index=current_lang_index
    )
    # If language changed, update state and rerun
    if selected_lang_key != st.session_state.language:
        st.session_state.language = selected_lang_key
        # Clear status messages that might be language-specific
        st.session_state.location_search_status_msg = ""
        # Keep search success flag? Maybe reset it too for safety.
        # st.session_state.location_search_success = False
        st.rerun()

    # --- Location Settings ---
    with st.expander(t['location_expander'], expanded=True):
        location_options_map = {
            'Search': t['location_option_search'],
            'Manual': t['location_option_manual']
        }
        current_choice = st.session_state.location_choice_key
        if current_choice not in location_options_map:
            st.session_state.location_choice_key = 'Search'
            current_choice = 'Search'
        st.radio(
            t['location_select_label'], options=list(location_options_map.keys()),
            format_func=lambda key: location_options_map[key], key="location_choice_key"
        )

        # --- Location Input Area ---
        lat_val, lon_val, height_val = None, None, None
        warning_placeholder = st.empty()
        location_valid_for_tz = False

        if st.session_state.location_choice_key == "Manual":
            # Use default values from state for number inputs
            st.number_input(t['location_lat_label'], min_value=-90.0, max_value=90.0, step=0.01, format="%.4f", key="manual_lat_val")
            st.number_input(t['location_lon_label'], min_value=-180.0, max_value=180.0, step=0.01, format="%.4f", key="manual_lon_val")
            st.number_input(t['location_elev_label'], min_value=-500, step=10, format="%d", key="manual_height_val")
            lat_val = st.session_state.manual_lat_val
            lon_val = st.session_state.manual_lon_val
            height_val = st.session_state.manual_height_val
            # Basic validation for manual input
            if isinstance(lat_val, (int, float)) and isinstance(lon_val, (int, float)) and isinstance(height_val, (int, float)):
                location_valid_for_tz = True
                warning_placeholder.empty()
            else:
                warning_placeholder.warning(t['location_error_manual_none'])
                location_valid_for_tz = False

        elif st.session_state.location_choice_key == "Search":
            with st.form("location_search_form"):
                st.text_input(t['location_search_label'], key="location_search_query", placeholder=t['location_search_placeholder'])
                location_search_form_submitted = st.form_submit_button(t['location_search_submit_button'])
            st.number_input(t['location_elev_label'], min_value=-500, step=10, format="%d", key="manual_height_val")
            status_placeholder = st.empty()

            if st.session_state.location_search_status_msg:
                 if "Error" in st.session_state.location_search_status_msg or "Fehler" in st.session_state.location_search_status_msg or "not found" in st.session_state.location_search_status_msg or "non trouvé" in st.session_state.location_search_status_msg:
                      status_placeholder.error(st.session_state.location_search_status_msg)
                 else:
                      status_placeholder.success(st.session_state.location_search_status_msg)

            if location_search_form_submitted and st.session_state.location_search_query:
                with st.spinner(t['spinner_geocoding']):
                    try:
                        geolocator = Nominatim(user_agent=f"dso_finder_app_{random.randint(1000,9999)}_{datetime.now().timestamp()}")
                        query = st.session_state.location_search_query
                        location = geolocator.geocode(query, timeout=10)
                        if location:
                            found_lat = location.latitude; found_lon = location.longitude; found_name = location.address
                            st.session_state.searched_location_name = found_name
                            st.session_state.location_search_success = True
                            st.session_state.manual_lat_val = found_lat
                            st.session_state.manual_lon_val = found_lon
                            coord_str = t['location_search_coords'].format(found_lat, found_lon)
                            st.session_state.location_search_status_msg = f"{t['location_search_found'].format(found_name)}\n({coord_str})"
                            status_placeholder.success(st.session_state.location_search_status_msg)
                            location_valid_for_tz = True
                        else:
                            st.session_state.location_search_success = False; st.session_state.searched_location_name = None
                            st.session_state.location_search_status_msg = t['location_search_error_not_found']
                            status_placeholder.error(st.session_state.location_search_status_msg)
                            location_valid_for_tz = False
                    except (GeocoderTimedOut, GeocoderServiceError, Exception) as e:
                        st.session_state.location_search_success = False
                        error_type = t['location_search_error_service']
                        if isinstance(e, GeocoderTimedOut): error_msg = error_type.format("Request timed out.")
                        else: error_msg = error_type.format(e)
                        st.session_state.location_search_status_msg = error_msg
                        status_placeholder.error(st.session_state.location_search_status_msg)
                        location_valid_for_tz = False

            if st.session_state.location_search_success:
                 lat_val = st.session_state.manual_lat_val
                 lon_val = st.session_state.manual_lon_val
                 height_val = st.session_state.manual_height_val
                 # location_valid_for_tz is set inside search logic


        # --- Determine Final Location and Timezone ---
        current_location_for_run = None
        location_is_valid_for_run = False
        location_display_name_for_run = ""
        auto_timezone_msg = ""

        # Use coordinates from state (either manual or updated by search)
        current_lat = st.session_state.manual_lat_val
        current_lon = st.session_state.manual_lon_val
        current_height = st.session_state.manual_height_val

        # Validate coordinates before creating EarthLocation and finding timezone
        if isinstance(current_lat, (int, float)) and isinstance(current_lon, (int, float)) and isinstance(current_height, (int, float)):
            try:
                current_location_for_run = EarthLocation(lat=current_lat * u.deg, lon=current_lon * u.deg, height=current_height * u.m)
                location_is_valid_for_run = True # Valid EarthLocation created

                # Determine display name
                if st.session_state.location_choice_key == "Manual":
                    location_display_name_for_run = t['location_manual_display'].format(current_lat, current_lon)
                elif st.session_state.location_choice_key == "Search" and st.session_state.location_search_success:
                    name_val = st.session_state.searched_location_name
                    display_name_short = (name_val[:35] + '...') if name_val and len(name_val) > 38 else name_val
                    location_display_name_for_run = t['location_search_display'].format(display_name_short or "Found", current_lat, current_lon)
                else: # Search mode, but no success yet
                    location_display_name_for_run = "Pending Search"
                    location_is_valid_for_run = False # Cannot run main search without successful location search

                # --- Automatic Timezone Detection ---
                if tf and location_is_valid_for_run: # Only run if location is valid
                    try:
                        found_tz = tf.timezone_at(lng=current_lon, lat=current_lat)
                        if found_tz:
                            pytz.timezone(found_tz) # Validate before setting
                            st.session_state.selected_timezone = found_tz
                            auto_timezone_msg = f"{t['timezone_auto_set_label']} **{found_tz}**"
                        else:
                            st.session_state.selected_timezone = 'UTC'
                            auto_timezone_msg = f"{t['timezone_auto_fail_label']} **UTC** ({t['timezone_auto_fail_msg']})"
                    except pytz.UnknownTimeZoneError:
                            st.session_state.selected_timezone = 'UTC'
                            auto_timezone_msg = f"{t['timezone_auto_fail_label']} **UTC** (Invalid TZ '{found_tz}')"
                    except Exception as tz_find_e:
                            print(f"Error finding timezone: {tz_find_e}")
                            st.session_state.selected_timezone = 'UTC'
                            auto_timezone_msg = f"{t['timezone_auto_fail_label']} **UTC** (Error)"

                elif not tf:
                     auto_timezone_msg = "Timezonefinder library not available."
                     st.session_state.selected_timezone = INITIAL_TIMEZONE
                elif not location_is_valid_for_run: # Don't try finding TZ if location isn't valid
                     st.session_state.selected_timezone = INITIAL_TIMEZONE
                     # Don't show a TZ message if location isn't set yet

            except Exception as e: # Error creating EarthLocation
                warning_placeholder.error(t['location_error'].format(e))
                location_display_name_for_run = t['location_error_fallback']
                location_is_valid_for_run = False
                st.session_state.selected_timezone = INITIAL_TIMEZONE

        else: # Coordinates are not valid (e.g., initial state in Manual mode)
            location_is_valid_for_run = False
            if st.session_state.location_choice_key == "Search":
                 location_display_name_for_run = "Please search for a location"
            elif st.session_state.location_choice_key == "Manual":
                 location_display_name_for_run = "Enter valid coordinates"
            st.session_state.selected_timezone = INITIAL_TIMEZONE


    # --- Time & Timezone Settings ---
    with st.expander(t['time_expander'], expanded=True):
        time_options_map = {'Now': t['time_option_now'], 'Specific': t['time_option_specific']}
        time_choice_key = st.radio(
            t['time_select_label'], options=time_options_map.keys(),
            format_func=lambda key: time_options_map[key], key="time_choice_exp"
        )
        is_time_now = (time_choice_key == "Now")
        if is_time_now:
             reference_time = Time.now()
        else:
            selected_date = st.date_input(
                t['time_date_select_label'], date.today(),
                min_value=date.today()-timedelta(days=365*5),
                max_value=date.today()+timedelta(days=365*1)
            )
            reference_time = Time(datetime.combine(selected_date, time(12, 0, tzinfo=timezone.utc)))

        st.markdown("---")
        # Display the automatically determined timezone or fallback
        if auto_timezone_msg:
             st.markdown(auto_timezone_msg, unsafe_allow_html=True)
        else:
             # Show fallback if auto-detection hasn't run or failed silently
             st.markdown(f"{t['timezone_auto_fail_label']} **{st.session_state.selected_timezone}**")


    # --- Filter Settings ---
    with st.expander(t['filters_expander'], expanded=True):
        # Magnitude Filter
        st.markdown(t['mag_filter_header'])
        mag_filter_options_map = {'Bortle Scale': t['mag_filter_option_bortle'], 'Manual': t['mag_filter_option_manual']}
        st.radio(t['mag_filter_method_label'], options=mag_filter_options_map.keys(),
             format_func=lambda key: mag_filter_options_map[key], key="mag_filter_mode_exp", horizontal=True)
        # Use state keys directly for slider values
        bortle_val = st.slider(t['mag_filter_bortle_label'], min_value=1, max_value=9, key='bortle_slider', help=t['mag_filter_bortle_help'])
        if st.session_state.mag_filter_mode_exp == "Manual":
            manual_min_mag_val = st.slider(t['mag_filter_min_mag_label'], min_value=-5.0, max_value=20.0, step=0.5, format="%.1f", help=t['mag_filter_min_mag_help'], key='manual_min_mag_slider')
            manual_max_mag_val = st.slider(t['mag_filter_max_mag_label'], min_value=-5.0, max_value=20.0, step=0.5, format="%.1f", help=t['mag_filter_max_mag_help'], key='manual_max_mag_slider')
            if isinstance(st.session_state.manual_min_mag_slider, (int, float)) and isinstance(st.session_state.manual_max_mag_slider, (int, float)):
                 if st.session_state.manual_min_mag_slider > st.session_state.manual_max_mag_slider:
                       st.warning(t['mag_filter_warning_min_max'])

        # Altitude Filter
        st.markdown("---")
        st.markdown(t['min_alt_header'])
        # Use state key for slider value
        min_altitude_deg = st.slider(t['min_alt_label'], min_value=5, max_value=45, key='min_alt_slider', step=1)
        min_altitude_limit = min_altitude_deg * u.deg

        # Moon Filter
        st.markdown("---")
        st.markdown(t['moon_warning_header'])
        # Use state key for slider value
        moon_phase_threshold = st.slider(t['moon_warning_label'], min_value=0, max_value=100, key='moon_phase_slider', step=5)

        # Object Type Filter
        st.markdown("---")
        st.markdown(t['object_types_header'])
        effective_selected_types = []
        all_types = []
        if df_catalog_data is not None and not df_catalog_data.empty:
            try:
                if 'Type' in df_catalog_data.columns:
                     all_types = sorted(list(df_catalog_data['Type'].dropna().astype(str).unique()))
                else: all_types = []
            except Exception as e:
                st.warning(f"Could not extract object types from loaded data: {e}")
                all_types = []

            if all_types:
                current_selection_in_state = [sel for sel in st.session_state.object_type_filter_exp if sel in all_types]
                if current_selection_in_state != st.session_state.object_type_filter_exp:
                     st.session_state.object_type_filter_exp = current_selection_in_state
                default_for_widget = current_selection_in_state if current_selection_in_state else all_types
                selected_object_types_widget = st.multiselect(
                    t['object_types_label'], options=all_types,
                    default=default_for_widget, key="object_type_filter_exp"
                )
                if not selected_object_types_widget or set(selected_object_types_widget) == set(all_types):
                     effective_selected_types = []
                else:
                    effective_selected_types = selected_object_types_widget
            else: st.info("No object types found in catalog data to filter.")
        else: st.info("Catalog not loaded, cannot filter by type.")


        # Direction Filter
        st.markdown("---")
        st.markdown(t['direction_filter_header'])
        all_directions_str = t['direction_option_all'] # Use translated string for display
        direction_options_display = [all_directions_str] + CARDINAL_DIRECTIONS
        direction_options_internal = [ALL_DIRECTIONS_KEY] + CARDINAL_DIRECTIONS
        try:
            current_direction_internal = st.session_state.selected_peak_direction
            if current_direction_internal not in direction_options_internal:
                 current_direction_internal = ALL_DIRECTIONS_KEY
                 st.session_state.selected_peak_direction = current_direction_internal
            current_direction_index = direction_options_internal.index(current_direction_internal)
        except ValueError:
             st.session_state.selected_peak_direction = ALL_DIRECTIONS_KEY
             current_direction_index = 0
        selected_direction_display = st.selectbox(
             t['direction_filter_label'], options=direction_options_display,
             index=current_direction_index,
        )
        # Map selected display value back to internal value ('All', 'N', ...)
        if selected_direction_display == all_directions_str:
             st.session_state.selected_peak_direction = ALL_DIRECTIONS_KEY
        else:
             st.session_state.selected_peak_direction = selected_direction_display


    # --- Result Options ---
    with st.expander(t['results_options_expander']):
        max_slider_val = len(df_catalog_data) if df_catalog_data is not None and not df_catalog_data.empty else 50
        min_slider_val = 5
        actual_max_slider = max(min_slider_val, max_slider_val)
        default_num_objects = min(20, actual_max_slider)
        slider_disabled = actual_max_slider < min_slider_val
        num_objects_to_suggest = st.slider(
             t['results_options_max_objects_label'], min_value=min_slider_val,
             max_value=actual_max_slider, value=default_num_objects,
             step=1, disabled=slider_disabled
        )
        sort_options_map = {
            'Duration & Altitude': t['results_options_sort_duration'],
            'Brightness': t['results_options_sort_magnitude']
        }
        if st.session_state.sort_method not in sort_options_map:
            st.session_state.sort_method = 'Duration & Altitude'
        st.radio(
            t['results_options_sort_method_label'], options=list(sort_options_map.keys()),
            format_func=lambda key: sort_options_map[key], key='sort_method', horizontal=True
        )


# --- Main Area ---
# Display Moon Phase
if moon_illumination:
    try:
        current_moon_illumination = moon_illumination(reference_time)
        moon_percentage = current_moon_illumination * 100
        moon_col1, moon_col2 = st.columns([1, 4])
        with moon_col1: st.markdown(create_moon_phase_svg(current_moon_illumination, size=80), unsafe_allow_html=True)
        with moon_col2:
            st.metric(label=t['moon_metric_label'], value=f"{moon_percentage:.0f}%")
            if moon_percentage > st.session_state.moon_phase_slider: # Use state key
                 st.error(t['moon_warning_message'].format(moon_percentage, st.session_state.moon_phase_slider))
    except NameError: st.warning("Moon phase calculation requires 'astroplan'. Please install it.")
    except Exception as e: st.error(t['moon_phase_error'].format(e))
else: st.warning("Moon phase calculation disabled: 'astroplan' library not found.")

st.markdown("---")

# --- Main Search Button & Logic ---
find_disabled = not location_is_valid_for_run or df_catalog_data is None or df_catalog_data.empty
if st.button(t['find_button_label'], key="find_button", type="primary", use_container_width=True, disabled=find_disabled):

    st.session_state.expanded_object_name = None
    st.session_state.show_plot = False
    st.session_state.plot_object_name = None

    # Re-check conditions (redundant with disabled state but safe)
    if not location_is_valid_for_run:
         st.error(t[f'location_error_{st.session_state.location_choice_key.lower()}_search'] if st.session_state.location_choice_key != 'Default' else t['location_error_undefined'])
    elif current_location_for_run is None:
         st.error(t['location_error_undefined'])
    elif df_catalog_data is None or df_catalog_data.empty:
         st.error("Cannot search: Catalog data is not loaded or empty.")
    else:
        # --- Start Search Process ---
        st.session_state.find_button_pressed = True
        st.session_state.last_results = []
        with st.container(border=True): # Display Search Parameters
             st.subheader(t['search_params_header'])
             col1, col2, col3 = st.columns(3)
             with col1: st.info(t['search_params_location'].format(location_display_name_for_run))
             with col2:
                 date_str_display = reference_time.datetime.date().strftime('%Y-%m-%d')
                 time_info = t['search_params_time_now'].format(reference_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')) if is_time_now else t['search_params_time_specific'].format(date_str_display)
                 st.info(t['search_params_time'].format(time_info))
                 st.info(t['search_params_timezone'].format(st.session_state.selected_timezone))
             with col3:
                 magnitude_filter_mode_disp = st.session_state.mag_filter_mode_exp
                 min_mag_disp = st.session_state.manual_min_mag_slider
                 max_mag_disp = st.session_state.manual_max_mag_slider
                 bortle_disp = st.session_state.bortle_slider # Use state key
                 if magnitude_filter_mode_disp == "Bortle Scale":
                     mag_limit_display = get_magnitude_limit(bortle_disp)
                     mag_info = t['search_params_filter_mag_bortle'].format(bortle_disp, mag_limit_display)
                 else: # Manual
                     if isinstance(min_mag_disp, (int, float)) and isinstance(max_mag_disp, (int, float)) and min_mag_disp > max_mag_disp:
                          min_mag_disp, max_mag_disp = max_mag_disp, min_mag_disp
                     mag_info = t['search_params_filter_mag_manual'].format(min_mag_disp or 0.0, max_mag_disp or 20.0)
                 st.info(t['search_params_filter_mag'].format(mag_info))
                 types_display = t['search_params_types_all'] if not effective_selected_types else ', '.join(effective_selected_types)
                 min_alt_disp = st.session_state.min_alt_slider # Use state key
                 st.info(t['search_params_filter_alt_types'].format(min_alt_disp, types_display))
                 selected_dir_internal = st.session_state.selected_peak_direction
                 direction_display_map = {ALL_DIRECTIONS_KEY: t['direction_option_all']}
                 direction_display_map.update({k: k for k in CARDINAL_DIRECTIONS})
                 selected_dir_disp = direction_display_map.get(selected_dir_internal, selected_dir_internal)
                 st.info(t['search_params_filter_direction'].format(selected_dir_disp))
        st.markdown("---")

        # --- Perform Calculations ---
        selected_objects = []
        all_found_objects = []
        window_info_placeholder = st.empty()
        try:
            with st.spinner(t['spinner_searching']):
                start_time, end_time, window_msg = get_observable_window(current_location_for_run, reference_time, is_time_now, lang)
                if window_msg:
                    formatted_window_msg = window_msg.replace("\n", "\n\n")
                    if "Warning" in window_msg or "Warnung" in window_msg or "Error" in window_msg or "Fehler" in window_msg or "invalid" in window_msg:
                         window_info_placeholder.warning(formatted_window_msg)
                    else:
                         window_info_placeholder.info(formatted_window_msg)

                if start_time and end_time and start_time < end_time:
                    time_delta_hours = (end_time - start_time).to(u.hour).value
                    num_time_steps = max(30, int(time_delta_hours * 12)) # ~5 min steps
                    observing_times = Time(np.linspace(start_time.jd, end_time.jd, num_time_steps), format='jd', scale='utc')
                    magnitude_filter_mode_calc = st.session_state.mag_filter_mode_exp
                    min_mag_calc = st.session_state.manual_min_mag_slider
                    max_mag_calc = st.session_state.manual_max_mag_slider
                    bortle_calc = st.session_state.bortle_slider # Use state key
                    min_alt_limit_calc = st.session_state.min_alt_slider * u.deg # Use state key

                    all_found_objects = find_observable_objects(
                        current_location_for_run, observing_times, min_alt_limit_calc,
                        magnitude_filter_mode_calc, bortle_calc, min_mag_calc, max_mag_calc,
                        effective_selected_types, df_catalog_data, lang
                    )
                elif not window_msg:
                     st.error(t['error_no_window'])

            # --- Post-Calculation Processing ---
            objects_after_direction_filter = []
            selected_dir_filter_internal = st.session_state.selected_peak_direction
            if selected_dir_filter_internal != ALL_DIRECTIONS_KEY:
                objects_after_direction_filter = [obj for obj in all_found_objects if obj.get('peak_direction') == selected_dir_filter_internal]
            else:
                objects_after_direction_filter = all_found_objects

            if objects_after_direction_filter:
                st.success(t['success_objects_found'].format(len(objects_after_direction_filter)))
                sort_method = st.session_state.sort_method
                if sort_method == 'Duration & Altitude':
                    # Sort primarily by total duration, secondarily by peak altitude
                    objects_after_direction_filter.sort(key=lambda x: (x.get('total_duration_hours', 0), x.get('peak_alt', 0)), reverse=True)
                    info_message = t['info_showing_list_duration']
                elif sort_method == 'Brightness':
                    objects_after_direction_filter.sort(key=lambda x: x['magnitude'])
                    info_message = t['info_showing_list_magnitude']
                else: # Fallback sort
                    objects_after_direction_filter.sort(key=lambda x: (x.get('total_duration_hours', 0), x.get('peak_alt', 0)), reverse=True)
                    info_message = t['info_showing_list_duration']
                selected_objects = objects_after_direction_filter[:num_objects_to_suggest]
                st.write(info_message.format(len(selected_objects)))
                st.session_state.last_results = selected_objects
            else:
                 if all_found_objects and selected_dir_filter_internal != ALL_DIRECTIONS_KEY:
                      direction_display_map = {ALL_DIRECTIONS_KEY: t['direction_option_all']}
                      direction_display_map.update({k: k for k in CARDINAL_DIRECTIONS})
                      selected_dir_disp = direction_display_map.get(selected_dir_filter_internal, selected_dir_filter_internal)
                      st.warning(f"No objects found matching all criteria, including peaking in the selected direction: {selected_dir_disp}")
                 elif start_time and end_time and start_time < end_time:
                     st.warning(t['warning_no_objects_found'])
                 st.session_state.last_results = []
        except Exception as main_e:
            st.error(t['error_search_unexpected'])
            st.exception(main_e)
            st.session_state.last_results = []


# --- Display Results List ---
if st.session_state.last_results:
    st.markdown("---")
    st.subheader(t['results_list_header'])
    export_data = []

    for i, obj in enumerate(st.session_state.last_results):
        peak_time_local_str, tz_display_name = get_local_time_str(obj['peak_time_utc'], st.session_state.selected_timezone)
        export_data.append({
            t['results_export_name']: obj['name'], t['results_export_type']: obj['type'],
            t['results_export_mag']: obj['magnitude'], t['results_export_ra']: obj['ra'],
            t['results_export_dec']: obj['dec'], t['results_export_max_alt']: f"{obj['peak_alt']:.1f}",
            t['results_export_az_at_max']: f"{obj.get('peak_az', 0.0):.1f}",
            t['results_export_direction_at_max']: obj.get('peak_direction', '?'),
            t['results_export_cont_duration']: f"{obj.get('cont_duration_hours', 0):.1f}", # Use new key
            t['results_export_total_duration']: f"{obj.get('total_duration_hours', 0):.1f}", # Use new key
            t['results_export_time_max_utc']: obj['peak_time_utc'],
            t['results_export_time_max_local']: f"{peak_time_local_str} ({tz_display_name})" if peak_time_local_str != "N/A" else "N/A"
        })

        expander_title = t['results_expander_title'].format(obj['name'], obj['type'], obj['magnitude'])
        is_expanded = (st.session_state.expanded_object_name == obj['name'])
        with st.expander(expander_title, expanded=is_expanded):
            # Use columns for better layout of details
            col1, col2, col3 = st.columns([2, 2, 3]) # Adjust ratios
            with col1:
                 st.markdown(t['results_coords_header'])
                 st.markdown(f"RA: {obj['ra']}")
                 st.markdown(f"Dec: {obj['dec']}")
                 st.markdown(f"**Type:** {obj['type']}")
            with col2:
                 st.markdown(t['results_max_alt_header'])
                 st.markdown(f"**{obj['peak_alt']:.1f}°**")
                 st.markdown(t['results_azimuth_label'].format(obj.get('peak_az', 0.0), f" ({obj.get('peak_direction', '?')})"))
                 st.markdown(t['results_best_time_header'])
                 st.markdown(f"**{peak_time_local_str}** ({tz_display_name})")
            with col3:
                 st.markdown(t['results_cont_duration_header']) # Cont Duration
                 st.markdown(f"**{t['results_duration_value'].format(obj.get('cont_duration_hours', 0))}**")
                 st.markdown(t['results_total_duration_header']) # Total Duration
                 st.markdown(f"**{t['results_duration_value'].format(obj.get('total_duration_hours', 0))}**")

            st.markdown("---") # Separator before plot button/plot

            plot_button_key = f"plot_btn_{obj['name']}_{i}"
            close_button_key = f"close_plot_{obj['name']}_{i}"
            if st.button(t['results_plot_button'], key=plot_button_key):
                st.session_state.plot_object_name = obj['name']
                st.session_state.show_plot = True
                st.session_state.expanded_object_name = obj['name']
                st.rerun()

            if st.session_state.show_plot and st.session_state.plot_object_name == obj['name']:
                 if plt and plot_altitude:
                     with st.spinner(t['results_spinner_plotting']):
                         try:
                             location_tuple = None
                             # Check if the location used for the run is valid before plotting
                             if current_location_for_run is not None and isinstance(current_location_for_run, EarthLocation):
                                 location_tuple = (
                                     current_location_for_run.lat.deg,
                                     current_location_for_run.lon.deg,
                                     current_location_for_run.height.value
                                 )

                             # Explicit check for None before plotting
                             if location_tuple is not None:
                                 # Pass the correct timezone from session state
                                 fig = plot_altitude(obj, location_tuple, lang, st.session_state.selected_timezone)
                                 if fig:
                                     st.pyplot(fig)
                                     if st.button(t['results_close_plot_button'], key=close_button_key, type="secondary"):
                                         st.session_state.show_plot = False
                                         st.session_state.plot_object_name = None
                                         st.rerun()
                                 else:
                                     st.warning(t['results_plot_not_created'])
                                     st.session_state.show_plot = False; st.session_state.plot_object_name = None;
                             else:
                                  st.error("Location information missing or invalid for plotting.")
                                  st.session_state.show_plot = False; st.session_state.plot_object_name = None;
                         except Exception as plot_e:
                             st.error(t['results_plot_error'].format(plot_e))
                             st.session_state.show_plot = False; st.session_state.plot_object_name = None;
                 else:
                      st.warning("Plotting skipped: Matplotlib or other required library missing.")
                      st.session_state.show_plot = False; st.session_state.plot_object_name = None;


    # --- CSV Export Button ---
    if export_data and pd:
        st.markdown("---")
        try:
            df_export = pd.DataFrame(export_data)
            # Define column order including new duration columns
            cols = [t['results_export_name'], t['results_export_type'], t['results_export_mag'],
                    t['results_export_cont_duration'], t['results_export_total_duration'], # Added columns
                    t['results_export_max_alt'], t['results_export_az_at_max'], t['results_export_direction_at_max'],
                    t['results_export_time_max_local'], t['results_export_time_max_utc'],
                    t['results_export_ra'], t['results_export_dec']]
            cols_exist = [col for col in cols if col in df_export.columns]
            df_export = df_export[cols_exist]
            csv_buffer = io.StringIO()
            df_export.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8-sig')
            file_date = reference_time.datetime.date().strftime('%Y%m%d')
            st.download_button(
                label=t['results_save_csv_button'], data=csv_buffer.getvalue(),
                file_name=t['results_csv_filename'].format(file_date), mime="text/csv"
            )
        except Exception as csv_e:
            st.error(t['results_csv_export_error'].format(csv_e))

    # --- Object Type Glossary ---
    st.markdown("---")
    with st.expander(t['object_type_glossary_title']):
        glossary_items = t['object_type_glossary']
        glossary_md = ""
        # Create a two-column layout for the glossary
        col1_items = []
        col2_items = []
        items = list(glossary_items.items())
        for i, (abbr, full_name) in enumerate(items):
            md_line = f"- **{abbr}:** {full_name}"
            if i % 2 == 0:
                col1_items.append(md_line)
            else:
                col2_items.append(md_line)

        # Combine columns into markdown string
        max_len = max(len(col1_items), len(col2_items))
        for i in range(max_len):
            col1_entry = col1_items[i] if i < len(col1_items) else ""
            col2_entry = col2_items[i] if i < len(col2_items) else ""
            # Use HTML table for better control over columns, or simple markdown list
            glossary_md += f"{col1_entry}\n{col2_entry}\n" # Simpler list format

        st.markdown(glossary_md)


# Message if search was run but found nothing
elif st.session_state.find_button_pressed and not st.session_state.last_results:
    # Message is already shown in the main search logic block (e.g., warning_no_objects_found)
    # Reset the button press state here *after* attempting to display results
    st.session_state.find_button_pressed = False

# Initial message or if catalog failed to load
elif not st.session_state.find_button_pressed:
    if df_catalog_data is not None:
        # Show initial prompt, guide user based on current location validity
        if not location_is_valid_for_run:
             st.warning(t['info_initial_prompt']) # Use the updated prompt which asks for location first
        # else: # Removed redundant message
             # st.info("Location set. Adjust filters and click 'Find Observable Objects'.")
    else:
         # Error message is already shown by load_ongc_data if loading failed
         st.error("Cannot proceed: Failed to load DSO catalog. Check file and restart.")

