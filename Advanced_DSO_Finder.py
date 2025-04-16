# -*- coding: utf-8 -*-
# --- Basic Imports ---
from __future__ import annotations
import streamlit as st
import random
from datetime import datetime, date, time, timedelta, timezone
import io
import traceback
import os  # Needed for file path joining
import urllib.parse # Needed for robust URL encoding
import pandas as pd

# --- Library Imports (Try after set_page_config) ---
try:
    from astropy.time import Time
    import numpy as np
    import astropy.units as u
    from astropy.coordinates import EarthLocation, SkyCoord, get_sun, AltAz, get_constellation
    from astroplan import Observer
    # from astroplan.constraints import AtNightConstraint # Not strictly needed for current logic
    from astroplan.moon import moon_illumination
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import pytz
    from timezonefinder import TimezoneFinder
    from geopy.geocoders import Nominatim, ArcGIS, Photon
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError
except ImportError as e:
    st.error(f"Error: Missing libraries. Please install the required packages. ({e})")
    st.stop()

# --- Page Config (MUST BE FIRST Streamlit command) ---
st.set_page_config(page_title="Advanced DSO Finder", layout="wide")

# --- Global Configuration & Initial Values ---
INITIAL_LAT = 47.17
INITIAL_LON = 8.01
INITIAL_HEIGHT = 550
INITIAL_TIMEZONE = "Europe/Zurich"
APP_VERSION = "v7.10-lang_optim" # Updated internal version

# --- Path to Catalog File ---
try:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback for environments where __file__ is not defined (e.g., interactive)
    APP_DIR = os.getcwd()
CATALOG_FILENAME = "ongc.csv"
CATALOG_FILEPATH = os.path.join(APP_DIR, CATALOG_FILENAME)


# Define cardinal directions
CARDINAL_DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
ALL_DIRECTIONS_KEY = 'All' # Internal key for 'All' option

# --- Translations (Ensure all keys exist for all languages) ---
translations = {
    'de': {
        # 'page_title': "Erweiterter DSO Finder", # Removed, title is now fixed
        'settings_header': "Einstellungen",
        'language_select_label': "Sprache",
        'location_expander': "📍 Standort",
        'location_select_label': "Standort-Methode wählen",
        'location_option_manual': "Manuell eingeben",
        'location_option_search': "Nach Name suchen",
        'location_search_label': "Ortsnamen eingeben:",
        'location_search_submit_button': "Koordinaten finden",
        'location_search_placeholder': "z.B. Berlin, Deutschland",
        'location_search_found': "Gefunden (Nominatim): {}",
        'location_search_found_fallback': "Gefunden via Fallback (ArcGIS): {}",
        'location_search_found_fallback2': "Gefunden via 2. Fallback (Photon): {}",
        'location_search_coords': "Lat: {:.4f}, Lon: {:.4f}",
        'location_search_error_not_found': "Ort nicht gefunden.",
        'location_search_error_service': "Geocoding-Dienst Fehler: {}",
        'location_search_error_timeout': "Geocoding-Dienst Zeitüberschreitung.",
        'location_search_error_refused': "Geocoding Verbindung abgelehnt.",
        'location_search_info_fallback': "Nominatim fehlgeschlagen, versuche Fallback-Dienst (ArcGIS)...",
        'location_search_info_fallback2': "ArcGIS fehlgeschlagen, versuche 2. Fallback-Dienst (Photon)...",
        'location_search_error_fallback_failed': "Primär (Nominatim) und Fallback (ArcGIS) fehlgeschlagen: {}",
        'location_search_error_fallback2_failed': "Alle Geocoding-Dienste (Nominatim, ArcGIS, Photon) fehlgeschlagen: {}",
        'location_lat_label': "Breitengrad (°N)",
        'location_lon_label': "Längengrad (°E)",
        'location_elev_label': "Höhe (Meter)",
        'location_manual_display': "Manuell ({:.4f}, {:.4f})",
        'location_search_display': "Gesucht: {} ({:.4f}, {:.4f})",
        'location_error': "Standortfehler: {}",
        'location_error_fallback': "FEHLER - Fallback wird verwendet",
        'location_error_manual_none': "Manuelle Standortfelder dürfen nicht leer oder ungültig sein.",
        'time_expander': "⏱️ Zeit & Zeitzone",
        'time_select_label': "Zeit wählen",
        'time_option_now': "Jetzt (kommende Nacht)",
        'time_option_specific': "Spezifische Nacht",
        'time_date_select_label': "Datum auswählen:",
        'timezone_auto_set_label': "Erkannte Zeitzone:",
        'timezone_auto_fail_label': "Zeitzone:",
        'timezone_auto_fail_msg': "Zeitzone konnte nicht erkannt werden, UTC wird verwendet.",
        'filters_expander': "✨ Filter & Bedingungen",
        'mag_filter_header': "**Magnitude Filter**",
        'mag_filter_method_label': "Filter Methode:",
        'mag_filter_option_bortle': "Bortle Skala",
        'mag_filter_option_manual': "Manuell",
        'mag_filter_bortle_label': "Bortle Skala:",
        'mag_filter_bortle_help': "Himmelsdunkelheit: 1=Exzellent Dunkel, 9=Innenstadt-Himmel",
        'mag_filter_min_mag_label': "Min. Magnitude:",
        'mag_filter_min_mag_help': "Hellste Objektmagnitude, die eingeschlossen wird",
        'mag_filter_max_mag_label': "Max. Magnitude:",
        'mag_filter_max_mag_help': "Schwächste Objektmagnitude, die eingeschlossen wird",
        'mag_filter_warning_min_max': "Min. Magnitude ist größer als Max. Magnitude!",
        'min_alt_header': "**Objekthöhe über Horizont**",
        'min_alt_label': "Min. Objekthöhe (°):",
        'max_alt_label': "Max. Objekthöhe (°):",
        'moon_warning_header': "**Mond Warnung**",
        'moon_warning_label': "Warnen wenn Mond > (% Beleuchtung):",
        'object_types_header': "**Objekttypen**",
        'object_types_error_extract': "Objekttypen konnten nicht aus dem Katalog extrahiert werden.",
        'object_types_label': "Typen filtern (leer lassen für alle):",
        'size_filter_header': "**Winkelgrößen Filter**",
        'size_filter_label': "Objektgröße (Bogenminuten):",
        'size_filter_help': "Objekte nach ihrer scheinbaren Größe filtern (Hauptachse). 1 Bogenminute = 1/60 Grad.",
        'direction_filter_header': "**Filter nach Himmelsrichtung**",
        'direction_filter_label': "Zeige Objekte mit höchstem Stand in Richtung:",
        'direction_option_all': "Alle",
        'object_type_glossary_title': "Objekttyp Glossar",
        'object_type_glossary': {
            "OCl": "Offener Haufen", "GCl": "Kugelsternhaufen", "Cl+N": "Haufen + Nebel",
            "Gal": "Galaxie", "PN": "Planetarischer Nebel", "SNR": "Supernova-Überrest",
            "Neb": "Nebel (allgemein)", "EmN": "Emissionsnebel", "RfN": "Reflexionsnebel",
            "HII": "HII-Region", "AGN": "Aktiver Galaxienkern"
        },
        'results_options_expander': "⚙️ Ergebnisoptionen",
        'results_options_max_objects_label': "Max. Anzahl anzuzeigender Objekte:",
        'results_options_sort_method_label': "Ergebnisse sortieren nach:",
        'results_options_sort_duration': "Dauer & Höhe",
        'results_options_sort_magnitude': "Helligkeit",
        'moon_metric_label': "Mondbeleuchtung (ca.)",
        'moon_warning_message': "Warnung: Mond ist heller ({:.0f}%) als Schwellenwert ({:.0f}%)!",
        'moon_phase_error': "Fehler bei Mondphasenberechnung: {}",
        'find_button_label': "🔭 Beobachtbare Objekte finden",
        'search_params_header': "Suchparameter",
        'search_params_location': "📍 Standort: {}",
        'search_params_time': "⏱️ Zeit: {}",
        'search_params_timezone': "🌍 Zeitzone: {}", # Removed from main display
        'search_params_time_now': "Kommende Nacht (ab {} UTC)",
        'search_params_time_specific': "Nacht nach {}",
        'search_params_filter_mag': "✨ Filter: {}",
        'search_params_filter_mag_bortle': "Bortle {} (<= {:.1f} mag)",
        'search_params_filter_mag_manual': "Manuell ({:.1f}-{:.1f} mag)",
        'search_params_filter_alt_types': "🔭 Filter: Höhe {}-{}°, Typen: {}",
        'search_params_filter_size': "📐 Filter: Größe {:.1f} - {:.1f} arcmin",
        'search_params_filter_direction': "🧭 Filter: Himmelsrichtung bei Max: {}",
        'search_params_types_all': "Alle",
        'search_params_direction_all': "Alle",
        'spinner_searching': "Berechne Fenster & suche Objekte...",
        'spinner_geocoding': "Suche nach Standort...",
        'window_info_template': "Beobachtungsfenster: {} bis {} UTC (Astronomische Dämmerung)",
        'window_already_passed': "Berechnetes Nachtfenster für 'Jetzt' ist bereits vorbei. Berechne für nächste Nacht.",
        'error_no_window': "Kein gültiges astronomisches Dunkelheitsfenster für das gewählte Datum und den Standort gefunden.",
        'error_polar_night': "Astronomische Dunkelheit dauert >24h an (Polarnacht?). Fallback-Fenster wird verwendet.",
        'error_polar_day': "Keine astronomische Dunkelheit tritt ein (Polartag?). Fallback-Fenster wird verwendet.",
        'success_objects_found': "{} passende Objekte gefunden.",
        'info_showing_list_duration': "Zeige {} Objekte, sortiert nach Sichtbarkeitsdauer und Kulminationshöhe:",
        'info_showing_list_magnitude': "Zeige {} Objekte, sortiert nach Helligkeit (hellstes zuerst):",
        'error_search_unexpected': "Ein unerwarteter Fehler ist während der Suche aufgetreten:",
        'results_list_header': "Ergebnisliste",
        'results_export_name': "Name",
        'results_export_type': "Typ",
        'results_export_constellation': "Sternbild",
        'results_export_mag': "Magnitude",
        'results_export_size': "Größe (arcmin)",
        'results_export_ra': "RA",
        'results_export_dec': "Dec",
        'results_export_max_alt': "Max Höhe (°)",
        'results_export_az_at_max': "Azimut bei Max (°)",
        'results_export_direction_at_max': "Richtung bei Max",
        'results_export_time_max_utc': "Zeit bei Max (UTC)",
        'results_export_time_max_local': "Zeit bei Max (Lokale TZ)",
        'results_export_cont_duration': "Max Kont Dauer (h)",
        'results_expander_title': "{} ({}) - Mag: {:.1f}",
        'google_link_text': "Google",
        'simbad_link_text': "SIMBAD",
        'results_coords_header': "**Details:**",
        'results_constellation_label': "Sternbild:",
        'results_size_label': "Größe (Hauptachse):",
        'results_size_value': "{:.1f} arcmin",
        'results_max_alt_header': "**Max. Höhe:**",
        'results_azimuth_label': "(Azimut: {:.1f}°{})",
        'results_direction_label': ", Richtung: {}",
        'results_best_time_header': "**Beste Zeit (Lokale TZ):**",
        'results_cont_duration_header': "**Max. Kont. Dauer:**",
        'results_duration_value': "{:.1f} Stunden",
        'graph_type_label': "Grafiktyp (für alle Grafiken):",
        'graph_type_sky_path': "Himmelsbahn (Az/Alt)",
        'graph_type_alt_time': "Höhenverlauf (Alt/Zeit)",
        'results_graph_button': "📈 Grafik anzeigen",
        'results_spinner_plotting': "Erstelle Grafik...",
        'results_graph_error': "Grafik Fehler: {}",
        'results_graph_not_created': "Grafik konnte nicht erstellt werden.",
        'results_close_graph_button': "Grafik schliessen",
        'results_save_csv_button': "💾 Ergebnisliste als CSV speichern",
        'results_csv_filename': "dso_beobachtungsliste_{}.csv",
        'results_csv_export_error': "CSV Export Fehler: {}",
        'warning_no_objects_found': "Keine Objekte gefunden, die allen Kriterien für das berechnete Beobachtungsfenster entsprechen.",
        'info_initial_prompt': "Willkommen! Bitte **Koordinaten eingeben** oder **Ort suchen**, um die Objektsuche zu aktivieren.",
        'graph_altitude_label': "Höhe (°)",
        'graph_azimuth_label': "Azimut (°)",
        'graph_min_altitude_label': "Mindesthöhe ({:.0f}°)",
        'graph_max_altitude_label': "Maximalhöhe ({:.0f}°)",
        'graph_title_sky_path': "Himmelsbahn für {}",
        'graph_title_alt_time': "Höhenverlauf für {}",
        'graph_ylabel': "Höhe (°)",
        'custom_target_expander': "Eigenes Ziel grafisch darstellen",
        'custom_target_ra_label': "Rektaszension (RA):",
        'custom_target_dec_label': "Deklination (Dec):",
        'custom_target_name_label': "Ziel-Name (Optional):",
        'custom_target_ra_placeholder': "z.B. 10:45:03.6 oder 161.265",
        'custom_target_dec_placeholder': "z.B. -16:42:58 oder -16.716",
        'custom_target_button': "Eigene Grafik erstellen",
        'custom_target_error_coords': "Ungültiges RA/Dec Format. Verwende HH:MM:SS.s / DD:MM:SS oder Dezimalgrad.",
        'custom_target_error_window': "Grafik kann nicht erstellt werden. Stelle sicher, dass Ort und Zeitfenster gültig sind (ggf. zuerst 'Beobachtbare Objekte finden' klicken).",
        'error_processing_object': "Fehler bei der Verarbeitung von {}: {}",
        'window_calc_error': "Fehler bei der Berechnung des Beobachtungsfensters: {}\n{}",
        'window_fallback_info': "\nFallback-Fenster wird verwendet: {} bis {} UTC",
        'error_loading_catalog': "Fehler beim Laden der Katalogdatei: {}",
        'info_catalog_loaded': "Katalog geladen: {} Objekte.",
        'warning_catalog_empty': "Katalogdatei geladen, aber keine passenden Objekte nach Filterung gefunden.",
        'donation_text': "Gefällt dir die App? [Unterstütze die Entwicklung auf Ko-fi ☕](https://ko-fi.com/advanceddsofinder)"
    },
    'en': {
        'settings_header': "Settings",
        'language_select_label': "Language",
        'location_expander': "📍 Location",
        'location_select_label': "Select Location Method",
        'location_option_manual': "Enter Manually",
        'location_option_search': "Search by Name",
        'location_search_label': "Enter location name:",
        'location_search_submit_button': "Find Coordinates",
        'location_search_placeholder': "e.g. London, UK",
        'location_search_found': "Found (Nominatim): {}",
        'location_search_found_fallback': "Found via Fallback (ArcGIS): {}",
        'location_search_found_fallback2': "Found via 2nd Fallback (Photon): {}",
        'location_search_coords': "Lat: {:.4f}, Lon: {:.4f}",
        'location_search_error_not_found': "Location not found.",
        'location_search_error_service': "Geocoding Service Error: {}",
        'location_search_error_timeout': "Geocoding Service Timeout.",
        'location_search_error_refused': "Geocoding connection refused.",
        'location_search_info_fallback': "Nominatim failed, trying fallback service (ArcGIS)...",
        'location_search_info_fallback2': "ArcGIS failed, trying 2nd fallback service (Photon)...",
        'location_search_error_fallback_failed': "Primary (Nominatim) and Fallback (ArcGIS) failed: {}",
        'location_search_error_fallback2_failed': "All geocoding services (Nominatim, ArcGIS, Photon) failed: {}",
        'location_lat_label': "Latitude (°N)",
        'location_lon_label': "Longitude (°E)",
        'location_elev_label': "Elevation (meters)",
        'location_manual_display': "Manual ({:.4f}, {:.4f})",
        'location_search_display': "Search: {} ({:.4f}, {:.4f})",
        'location_error': "Location Error: {}",
        'location_error_fallback': "ERROR - Using fallback",
        'location_error_manual_none': "Manual location fields cannot be empty or invalid.",
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
        'mag_filter_bortle_help': "Sky Darkness: 1=Excellent Dark, 9=Inner-city Sky",
        'mag_filter_min_mag_label': "Min. Magnitude:",
        'mag_filter_min_mag_help': "Brightest object magnitude to include",
        'mag_filter_max_mag_label': "Max. Magnitude:",
        'mag_filter_max_mag_help': "Faintest object magnitude to include",
        'mag_filter_warning_min_max': "Min. Magnitude is greater than Max. Magnitude!",
        'min_alt_header': "**Object Altitude Above Horizon**",
        'min_alt_label': "Min. Object Altitude (°):",
        'max_alt_label': "Max. Object Altitude (°):",
        'moon_warning_header': "**Moon Warning**",
        'moon_warning_label': "Warn if Moon > (% illumination):",
        'object_types_header': "**Object Types**",
        'object_types_error_extract': "Could not extract object types from catalog.",
        'object_types_label': "Filter Types (leave empty for all):",
        'size_filter_header': "**Angular Size Filter**",
        'size_filter_label': "Object Size (arcminutes):",
        'size_filter_help': "Filter objects by their apparent size (major axis). 1 arcminute = 1/60 degree.",
        'direction_filter_header': "**Filter by Sky Direction**",
        'direction_filter_label': "Show objects peaking in direction:",
        'direction_option_all': "All",
        'object_type_glossary_title': "Object Type Glossary",
        'object_type_glossary': {
            "OCl": "Open Cluster", "GCl": "Globular Cluster", "Cl+N": "Cluster + Nebula",
            "Gal": "Galaxy", "PN": "Planetary Nebula", "SNR": "Supernova Remnant",
            "Neb": "Nebula (general)", "EmN": "Emission Nebula", "RfN": "Reflection Nebula",
            "HII": "HII Region", "AGN": "Active Galactic Nucleus"
        },
        'results_options_expander': "⚙️ Result Options",
        'results_options_max_objects_label': "Max. Number of Objects to Display:",
        'results_options_sort_method_label': "Sort Results By:",
        'results_options_sort_duration': "Duration & Altitude",
        'results_options_sort_magnitude': "Brightness",
        'moon_metric_label': "Moon Illumination (approx.)",
        'moon_warning_message': "Warning: Moon is brighter ({:.0f}%) than threshold ({:.0f}%)!",
        'moon_phase_error': "Error calculating moon phase: {}",
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
        'search_params_filter_alt_types': "🔭 Filter: Altitude {}-{}°, Types: {}",
        'search_params_filter_size': "📐 Filter: Size {:.1f} - {:.1f} arcmin",
        'search_params_filter_direction': "🧭 Filter: Direction at Max: {}",
        'search_params_types_all': "All",
        'search_params_direction_all': "All",
        'spinner_searching': "Calculating window & searching objects...",
        'spinner_geocoding': "Searching for location...",
        'window_info_template': "Observation Window: {} to {} UTC (Astronomical Twilight)",
        'window_already_passed': "Calculated night window for 'Now' has already passed. Calculating for next night.",
        'error_no_window': "No valid astronomical darkness window found for the selected date and location.",
        'error_polar_night': "Astronomical darkness lasts >24h (Polar night?). Using fallback window.",
        'error_polar_day': "No astronomical darkness occurs (Polar day?). Using fallback window.",
        'success_objects_found': "{} matching objects found.",
        'info_showing_list_duration': "Showing {} objects, sorted by visibility duration and culmination altitude:",
        'info_showing_list_magnitude': "Showing {} objects, sorted by brightness (brightest first):",
        'error_search_unexpected': "An unexpected error occurred during the search:",
        'results_list_header': "Result List",
        'results_export_name': "Name",
        'results_export_type': "Type",
        'results_export_constellation': "Constellation",
        'results_export_mag': "Magnitude",
        'results_export_size': "Size (arcmin)",
        'results_export_ra': "RA",
        'results_export_dec': "Dec",
        'results_export_max_alt': "Max Altitude (°)",
        'results_export_az_at_max': "Azimuth at Max (°)",
        'results_export_direction_at_max': "Direction at Max",
        'results_export_time_max_utc': "Time at Max (UTC)",
        'results_export_time_max_local': "Time at Max (Local TZ)",
        'results_export_cont_duration': "Max Cont. Duration (h)",
        'results_expander_title': "{} ({}) - Mag: {:.1f}",
        'google_link_text': "Google",
        'simbad_link_text': "SIMBAD",
        'results_coords_header': "**Details:**",
        'results_constellation_label': "Constellation:",
        'results_size_label': "Size (Major Axis):",
        'results_size_value': "{:.1f} arcmin",
        'results_max_alt_header': "**Max. Altitude:**",
        'results_azimuth_label': "(Azimuth: {:.1f}°{})",
        'results_direction_label': ", Direction: {}",
        'results_best_time_header': "**Best Time (Local TZ):**",
        'results_cont_duration_header': "**Max. Cont. Duration:**",
        'results_duration_value': "{:.1f} hours",
        'graph_type_label': "Graph Type (for all plots):",
        'graph_type_sky_path': "Sky Path (Az/Alt)",
        'graph_type_alt_time': "Altitude Plot (Alt/Time)",
        'results_graph_button': "📈 Show Plot",
        'results_spinner_plotting': "Creating plot...",
        'results_graph_error': "Plot Error: {}",
        'results_graph_not_created': "Could not create plot.",
        'results_close_graph_button': "Close Plot",
        'results_save_csv_button': "💾 Save Result List as CSV",
        'results_csv_filename': "dso_observing_list_{}.csv",
        'results_csv_export_error': "CSV Export Error: {}",
        'warning_no_objects_found': "No objects found matching all criteria for the calculated observation window.",
        'info_initial_prompt': "Welcome! Please **enter coordinates** or **search for a location** to enable object search.",
        'graph_altitude_label': "Altitude (°)",
        'graph_azimuth_label': "Azimuth (°)",
        'graph_min_altitude_label': "Min Altitude ({:.0f}°)",
        'graph_max_altitude_label': "Max Altitude ({:.0f}°)",
        'graph_title_sky_path': "Sky Path for {}",
        'graph_title_alt_time': "Altitude Plot for {}",
        'graph_ylabel': "Altitude (°)",
        'custom_target_expander': "Plot Custom Target",
        'custom_target_ra_label': "Right Ascension (RA):",
        'custom_target_dec_label': "Declination (Dec):",
        'custom_target_name_label': "Target Name (Optional):",
        'custom_target_ra_placeholder': "e.g. 10:45:03.6 or 161.265",
        'custom_target_dec_placeholder': "e.g. -16:42:58 or -16.716",
        'custom_target_button': "Create Custom Plot",
        'custom_target_error_coords': "Invalid RA/Dec format. Use HH:MM:SS.s / DD:MM:SS or decimal degrees.",
        'custom_target_error_window': "Cannot create plot. Ensure location and time window are valid (you may need to click 'Find Observable Objects' first).",
        'error_processing_object': "Error processing {}: {}",
        'window_calc_error': "Error calculating observation window: {}\n{}",
        'window_fallback_info': "\nUsing fallback window: {} to {} UTC",
        'error_loading_catalog': "Error loading catalog file: {}",
        'info_catalog_loaded': "Catalog loaded: {} objects.",
        'warning_catalog_empty': "Catalog file loaded, but no matching objects found after filtering.",
        'donation_text': "Like the app? [Support the development on Ko-fi ☕](https://ko-fi.com/advanceddsofinder)"
    },
    'fr': {
        'settings_header': "Paramètres",
        'language_select_label': "Langue",
        'location_expander': "📍 Emplacement",
        'location_select_label': "Choisir la méthode de localisation",
        'location_option_manual': "Entrer manuellement",
        'location_option_search': "Rechercher par nom",
        'location_search_label': "Entrez le nom du lieu :",
        'location_search_submit_button': "Trouver les coordonnées",
        'location_search_placeholder': "ex. Paris, France",
        'location_search_found': "Trouvé (Nominatim) : {}",
        'location_search_found_fallback': "Trouvé via le service alternatif (ArcGIS) : {}",
        'location_search_found_fallback2': "Trouvé via le 2ème service alternatif (Photon) : {}",
        'location_search_coords': "Lat : {:.4f}, Lon : {:.4f}",
        'location_search_error_not_found': "Lieu non trouvé.",
        'location_search_error_service': "Erreur du service de géocodage : {}",
        'location_search_error_timeout': "Délai d'attente du service de géocodage dépassé.",
        'location_search_error_refused': "Connexion de géocodage refusée.",
        'location_search_info_fallback': "Nominatim a échoué, tentative avec le service alternatif (ArcGIS)...",
        'location_search_info_fallback2': "ArcGIS a échoué, tentative avec le 2ème service alternatif (Photon)...",
        'location_search_error_fallback_failed': "Échec du service principal (Nominatim) et alternatif (ArcGIS) : {}",
        'location_search_error_fallback2_failed': "Échec de tous les services de géocodage (Nominatim, ArcGIS, Photon) : {}",
        'location_lat_label': "Latitude (°N)",
        'location_lon_label': "Longitude (°E)",
        'location_elev_label': "Altitude (mètres)",
        'location_manual_display': "Manuel ({:.4f}, {:.4f})",
        'location_search_display': "Recherche : {} ({:.4f}, {:.4f})",
        'location_error': "Erreur de localisation : {}",
        'location_error_fallback': "ERREUR - Utilisation de la solution de repli",
        'location_error_manual_none': "Les champs de localisation manuels ne peuvent pas être vides ou invalides.",
        'time_expander': "⏱️ Heure & Fuseau horaire",
        'time_select_label': "Choisir l'heure",
        'time_option_now': "Maintenant (nuit à venir)",
        'time_option_specific': "Nuit spécifique",
        'time_date_select_label': "Choisir la date :",
        'timezone_auto_set_label': "Fuseau horaire détecté :",
        'timezone_auto_fail_label': "Fuseau horaire :",
        'timezone_auto_fail_msg': "Impossible de détecter le fuseau horaire, UTC est utilisé.",
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
        'mag_filter_warning_min_max': "Magnitude Min. est supérieure à la Magnitude Max. !",
        'min_alt_header': "**Altitude de l'objet au-dessus de l'horizon**",
        'min_alt_label': "Altitude Min. de l'objet (°):",
        'max_alt_label': "Altitude Max. de l'objet (°):",
        'moon_warning_header': "**Avertissement Lune**",
        'moon_warning_label': "Avertir si Lune > (% illumination) :",
        'object_types_header': "**Types d'objets**",
        'object_types_error_extract': "Impossible d'extraire les types d'objets du catalogue.",
        'object_types_label': "Filtrer les types (laisser vide pour tous) :",
        'size_filter_header': "**Filtre de Taille Angulaire**",
        'size_filter_label': "Taille de l'objet (arcminutes) :",
        'size_filter_help': "Filtrer les objets par leur taille apparente (axe majeur). 1 arcminute = 1/60 degré.",
        'direction_filter_header': "**Filtre par Direction Céleste**",
        'direction_filter_label': "Afficher les objets culminant en direction de :",
        'direction_option_all': "Toutes",
        'object_type_glossary_title': "Glossaire des types d'objets",
        'object_type_glossary': {
            "OCl": "Amas Ouvert", "GCl": "Amas Globulaire", "Cl+N": "Amas + Nébuleuse",
            "Gal": "Galaxie", "PN": "Nébuleuse Planétaire", "SNR": "Rémanent de Supernova",
            "Neb": "Nébuleuse (général)", "EmN": "Nébuleuse en Émission", "RfN": "Nébuleuse par Réflexion",
            "HII": "Région HII", "AGN": "Noyau Actif de Galaxie"
        },
        'results_options_expander': "⚙️ Options de Résultat",
        'results_options_max_objects_label': "Nombre Max. d'Objets à Afficher :",
        'results_options_sort_method_label': "Trier les Résultats Par :",
        'results_options_sort_duration': "Durée & Altitude",
        'results_options_sort_magnitude': "Luminosité",
        'moon_metric_label': "Illumination Lunaire (approx.)",
        'moon_warning_message': "Attention : La Lune est plus lumineuse ({:.0f}%) que le seuil ({:.0f}%) !",
        'moon_phase_error': "Erreur de calcul de la phase lunaire : {}",
        'find_button_label': "🔭 Trouver les Objets Observables",
        'search_params_header': "Paramètres de Recherche",
        'search_params_location': "📍 Lieu : {}",
        'search_params_time': "⏱️ Heure : {}",
        'search_params_timezone': "🌍 Fuseau horaire : {}",
        'search_params_time_now': "Nuit prochaine (à partir de {} UTC)",
        'search_params_time_specific': "Nuit après {}",
        'search_params_filter_mag': "✨ Filtre : {}",
        'search_params_filter_mag_bortle': "Bortle {} (<= {:.1f} mag)",
        'search_params_filter_mag_manual': "Manuel ({:.1f}-{:.1f} mag)",
        'search_params_filter_alt_types': "🔭 Filtre : Altitude {}-{}°, Types : {}",
        'search_params_filter_size': "📐 Filtre : Taille {:.1f} - {:.1f} arcmin",
        'search_params_filter_direction': "🧭 Filtre : Direction au Max : {}",
        'search_params_types_all': "Tous",
        'search_params_direction_all': "Toutes",
        'spinner_searching': "Calcul de la fenêtre & recherche des objets...",
        'spinner_geocoding': "Recherche de l'emplacement...",
        'window_info_template': "Fenêtre d'Observation : {} à {} UTC (Crépuscule Astronomique)",
        'window_already_passed': "La fenêtre nocturne calculée pour 'Maintenant' est déjà passée. Calcul pour la nuit suivante.",
        'error_no_window': "Aucune fenêtre de noirceur astronomique valide trouvée pour la date et le lieu sélectionnés.",
        'error_polar_night': "La noirceur astronomique dure >24h (Nuit polaire ?). Utilisation de la fenêtre de secours.",
        'error_polar_day': "Aucune noirceur astronomique ne se produit (Jour polaire ?). Utilisation de la fenêtre de secours.",
        'success_objects_found': "{} objets correspondants trouvés.",
        'info_showing_list_duration': "Affichage de {} objets, triés par durée de visibilité et altitude de culmination :",
        'info_showing_list_magnitude': "Affichage de {} objets, triés par luminosité (le plus brillant en premier) :",
        'error_search_unexpected': "Une erreur inattendue s'est produite lors de la recherche :",
        'results_list_header': "Liste des Résultats",
        'results_export_name': "Nom",
        'results_export_type': "Type",
        'results_export_constellation': "Constellation",
        'results_export_mag': "Magnitude",
        'results_export_size': "Taille (arcmin)",
        'results_export_ra': "AD",
        'results_export_dec': "Dec",
        'results_export_max_alt': "Altitude Max (°)",
        'results_export_az_at_max': "Azimut au Max (°)",
        'results_export_direction_at_max': "Direction au Max",
        'results_export_time_max_utc': "Heure au Max (UTC)",
        'results_export_time_max_local': "Heure au Max (Fuseau Local)",
        'results_export_cont_duration': "Durée Cont. Max (h)",
        'results_expander_title': "{} ({}) - Mag : {:.1f}",
        'google_link_text': "Google",
        'simbad_link_text': "SIMBAD",
        'results_coords_header': "**Détails :**",
        'results_constellation_label': "Constellation :",
        'results_size_label': "Taille (Axe Majeur) :",
        'results_size_value': "{:.1f} arcmin",
        'results_max_alt_header': "**Altitude Max. :**",
        'results_azimuth_label': "(Azimut : {:.1f}°{})",
        'results_direction_label': ", Direction : {}",
        'results_best_time_header': "**Meilleure Heure (Fuseau Local) :**",
        'results_cont_duration_header': "**Durée Cont. Max. :**",
        'results_duration_value': "{:.1f} heures",
        'graph_type_label': "Type de Graphique (pour tous les graph.) :",
        'graph_type_sky_path': "Trajectoire Céleste (Az/Alt)",
        'graph_type_alt_time': "Courbe d'Altitude (Alt/Temps)",
        'results_graph_button': "📈 Afficher le Graphique",
        'results_spinner_plotting': "Création du graphique...",
        'results_graph_error': "Erreur Graphique : {}",
        'results_graph_not_created': "Impossible de créer le graphique.",
        'results_close_graph_button': "Fermer le Graphique",
        'results_save_csv_button': "💾 Enregistrer la Liste comme CSV",
        'results_csv_filename': "liste_observation_dso_{}.csv",
        'results_csv_export_error': "Erreur Export CSV : {}",
        'warning_no_objects_found': "Aucun objet trouvé correspondant à tous les critères pour la fenêtre d'observation calculée.",
        'info_initial_prompt': "Bienvenue ! Veuillez **entrer les coordonnées** ou **rechercher un lieu** pour activer la recherche d'objets.",
        'graph_altitude_label': "Altitude (°)",
        'graph_azimuth_label': "Azimut (°)",
        'graph_min_altitude_label': "Altitude Min ({:.0f}°)",
        'graph_max_altitude_label': "Altitude Max ({:.0f}°)",
        'graph_title_sky_path': "Trajectoire céleste pour {}",
        'graph_title_alt_time': "Courbe d'altitude pour {}",
        'graph_ylabel': "Altitude (°)",
        'custom_target_expander': "Graphique Cible Personnalisée",
        'custom_target_ra_label': "Ascension Droite (AD) :",
        'custom_target_dec_label': "Déclinaison (Dec) :",
        'custom_target_name_label': "Nom de la Cible (Optionnel) :",
        'custom_target_ra_placeholder': "ex. 10:45:03.6 ou 161.265",
        'custom_target_dec_placeholder': "ex. -16:42:58 ou -16.716",
        'custom_target_button': "Créer Graphique Personnalisé",
        'custom_target_error_coords': "Format AD/Dec invalide. Utilisez HH:MM:SS.s / DD:MM:SS ou degrés décimaux.",
        'custom_target_error_window': "Impossible de créer le graphique. Assurez-vous que le lieu et la fenêtre temporelle sont valides (vous devrez peut-être cliquer d'abord sur 'Trouver les Objets Observables').",
        'error_processing_object': "Erreur lors du traitement de {}: {}",
        'window_calc_error': "Erreur lors du calcul de la fenêtre d'observation : {}\n{}",
        'window_fallback_info': "\nFenêtre de secours utilisée : {} à {} UTC",
        'error_loading_catalog': "Erreur lors du chargement du fichier catalogue : {}",
        'info_catalog_loaded': "Catalogue chargé : {} objets.",
        'warning_catalog_empty': "Fichier catalogue chargé, mais aucun objet correspondant trouvé après filtrage.",
        'donation_text': "Vous aimez l'application ? [Soutenez le développement sur Ko-fi ☕](https://ko-fi.com/advanceddsofinder)"
    }
}


# --- Initialize TimezoneFinder (cached) ---
@st.cache_resource
def get_timezone_finder():
    """Initializes and returns a TimezoneFinder instance."""
    if TimezoneFinder:
        try:
            return TimezoneFinder(in_memory=True)
        except Exception as e:
            print(f"Error initializing TimezoneFinder: {e}")
            st.warning(f"TimezoneFinder init failed: {e}. Automatic timezone detection disabled.")
            return None
    return None

tf = get_timezone_finder()

# --- Initialize Session State ---
def initialize_session_state():
    """Initializes all required session state keys if they don't exist."""
    defaults = {
        'language': 'de', # Default to German
        'plot_object_name': None,
        'show_plot': False,
        'active_result_plot_data': None,
        'last_results': [],
        'find_button_pressed': False,
        'location_choice_key': 'Search',
        'manual_lat_val': INITIAL_LAT,
        'manual_lon_val': INITIAL_LON,
        'manual_height_val': INITIAL_HEIGHT,
        'location_search_query': "",
        'searched_location_name': None,
        'location_search_status_msg': "",
        'location_search_success': False,
        'selected_timezone': INITIAL_TIMEZONE,
        'manual_min_mag_slider': 0.0,
        'manual_max_mag_slider': 16.0,
        'object_type_filter_exp': [],
        'mag_filter_mode_exp': 'Bortle Scale', # Matches key in translations['de']
        'bortle_slider': 5,
        'min_alt_slider': 20,
        'max_alt_slider': 90, # Added max altitude default
        'moon_phase_slider': 35,
        'size_arcmin_range': [1.0, 120.0],
        'sort_method': 'Duration & Altitude', # Matches key in translations['de']
        'selected_peak_direction': ALL_DIRECTIONS_KEY,
        'plot_type_selection': 'Sky Path', # Matches key in translations['de']
        'custom_target_ra': "",
        'custom_target_dec': "",
        'custom_target_name': "",
        'custom_target_error': "",
        'custom_target_plot_data': None,
        'show_custom_plot': False,
        'expanded_object_name': None,
        'location_is_valid_for_run': False, # Added location validity state
        'time_choice_exp': 'Now',
        'window_start_time': None,
        'window_end_time': None,
        'selected_date_widget': date.today(),
        'catalog_status_msg': "" # Initialize catalog status message
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
    azimuth_deg = azimuth_deg % 360
    index = round((azimuth_deg + 22.5) / 45) % 8
    index = max(0, min(index, len(CARDINAL_DIRECTIONS) - 1))
    return CARDINAL_DIRECTIONS[index]

# --- Moon Phase SVG ---
def create_moon_phase_svg(illumination: float, size: int = 100) -> str:
    """Creates an SVG representation of the moon phase."""
    if not 0 <= illumination <= 1:
        print(f"Warning: Invalid moon illumination value ({illumination}). Clamping to [0, 1].")
        illumination = max(0.0, min(1.0, illumination))
    radius = size / 2
    cx = cy = radius
    light_color = "var(--text-color, #e0e0e0)"
    dark_color = "var(--secondary-background-color, #333333)"
    svg = f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
    svg += f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{dark_color}"/>'
    if illumination < 0.01: pass
    elif illumination > 0.99: svg += f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{light_color}"/>'
    else:
        x_terminator_center = radius * (illumination * 2 - 1)
        rx_terminator = abs(x_terminator_center)
        if illumination <= 0.5:
            large_arc_flag_ellipse, sweep_flag_ellipse = 0, 1
            large_arc_flag_circle, sweep_flag_circle = 0, 1
            d = (f"M {cx},{cy - radius} "
                 f"A {rx_terminator},{radius} 0 {large_arc_flag_ellipse},{sweep_flag_ellipse} {cx},{cy + radius} "
                 f"A {radius},{radius} 0 {large_arc_flag_circle},{sweep_flag_circle} {cx},{cy - radius} Z")
        else:
            large_arc_flag_circle, sweep_flag_circle = 1, 1
            large_arc_flag_ellipse, sweep_flag_ellipse = 1, 1
            d = (f"M {cx},{cy - radius} "
                 f"A {radius},{radius} 0 {large_arc_flag_circle},{sweep_flag_circle} {cx},{cy + radius} "
                 f"A {rx_terminator},{radius} 0 {large_arc_flag_ellipse},{sweep_flag_ellipse} {cx},{cy - radius} Z")
        svg += f'<path d="{d}" fill="{light_color}"/>'
    svg += '</svg>'
    return svg

# --- Catalog Loading (Optimized Caching) ---
# This function performs the actual data loading and processing. It's cached.
@st.cache_data(show_spinner=False) # Cache the result of this function
def load_and_process_ongc_data(catalog_path: str) -> pd.DataFrame | str:
    """Loads and processes the ONGC data from the CSV file.
       Returns DataFrame on success, or an error message string on failure."""
    print(f"Cache miss or invalidation: Loading and processing ONGC data from {catalog_path}")
    required_cols = ['Name', 'RA', 'Dec', 'Type']
    mag_cols = ['V-Mag', 'B-Mag', 'Mag']
    size_col = 'MajAx'

    try:
        if not os.path.exists(catalog_path):
             return f"error:file_not_found:{catalog_path}" # Return error code

        df = pd.read_csv(catalog_path, sep=';', comment='#', low_memory=False)

        # --- Validation ---
        missing_req_cols = [col for col in required_cols if col not in df.columns]
        if missing_req_cols:
            return f"error:missing_cols:{','.join(missing_req_cols)}"

        # --- Processing (as before) ---
        df['RA_str'] = df['RA'].astype(str).str.strip()
        df['Dec_str'] = df['Dec'].astype(str).str.strip()
        df.dropna(subset=['RA_str', 'Dec_str'], inplace=True)
        df = df[(df['RA_str'] != '') & (df['Dec_str'] != '')]

        mag_col_found = None
        for col in mag_cols:
            if col in df.columns:
                numeric_mags = pd.to_numeric(df[col], errors='coerce')
                if numeric_mags.notna().any():
                    mag_col_found = col
                    break
        if mag_col_found is None:
            return f"error:no_mag_col:{','.join(mag_cols)}"
        df['Mag'] = pd.to_numeric(df[mag_col_found], errors='coerce')
        df.dropna(subset=['Mag'], inplace=True)

        if size_col not in df.columns:
            df[size_col] = np.nan
        else:
            df[size_col] = pd.to_numeric(df[size_col], errors='coerce')
            if not df[size_col].notna().any():
                df[size_col] = np.nan # Ensure column exists but is all NaN if no valid data

        dso_types_provided = ['Galaxy', 'Globular Cluster', 'Open Cluster', 'Nebula',
                              'Planetary Nebula', 'Supernova Remnant', 'HII', 'Emission Nebula',
                              'Reflection Nebula', 'Cluster + Nebula', 'Gal', 'GCl', 'Gx', 'OC',
                              'PN', 'SNR', 'Neb', 'EmN', 'RfN', 'C+N', 'Gxy', 'AGN', 'MWSC', 'OCl']
        type_pattern = '|'.join(dso_types_provided)
        if 'Type' in df.columns:
            df_filtered = df[df['Type'].astype(str).str.contains(type_pattern, case=False, na=False)].copy()
        else:
             return "error:missing_type_col" # Should be caught earlier, but safe check

        final_cols = ['Name', 'RA_str', 'Dec_str', 'Mag', 'Type', size_col]
        final_cols_exist = [col for col in final_cols if col in df_filtered.columns]
        df_final = df_filtered[final_cols_exist].copy()
        df_final.drop_duplicates(subset=['Name'], inplace=True, keep='first')
        df_final.reset_index(drop=True, inplace=True)

        if df_final.empty:
            return "warning:catalog_empty"

        print(f"Catalog processed successfully: {len(df_final)} objects.")
        return df_final

    except FileNotFoundError: # Should be caught by os.path.exists, but keep for safety
         return f"error:file_not_found:{catalog_path}"
    except pd.errors.ParserError as e:
        return f"error:parser_error:{e}"
    except Exception as e:
        # Log the full traceback for debugging
        print(f"Unexpected error loading catalog: {e}")
        traceback.print_exc()
        return f"error:unexpected:{e}"

# --- Wrapper function to handle cached loading and display messages ---
def get_catalog_data(catalog_path: str, lang: str) -> pd.DataFrame | None:
    """Gets catalog data using cache and displays status messages in the correct language."""
    t = translations.get(lang, translations['en']) # Get translations for messages
    result = load_and_process_ongc_data(catalog_path) # Call the cached function

    status_message = ""
    df_catalog = None

    if isinstance(result, pd.DataFrame):
        df_catalog = result
        status_message = t['info_catalog_loaded'].format(len(df_catalog))
        st.session_state.catalog_status_msg = status_message # Store for display in sidebar
        print("Catalog loaded from cache or processed successfully.")
    elif isinstance(result, str):
        error_parts = result.split(':', 2)
        error_type = error_parts[0]
        error_code = error_parts[1]
        error_detail = error_parts[2] if len(error_parts) > 2 else ""

        if error_type == "error":
            if error_code == "file_not_found":
                 status_message = f"{t['error_loading_catalog'].split(':')[0]}: File not found at {error_detail}"
                 st.sidebar.error(status_message)
                 st.sidebar.info(f"Please ensure the file '{CATALOG_FILENAME}' is in the directory: {APP_DIR}")
            elif error_code == "missing_cols":
                 status_message = f"Missing required columns in catalog: {error_detail}"
                 st.sidebar.error(status_message)
            elif error_code == "no_mag_col":
                 status_message = f"No usable magnitude column found: {error_detail}"
                 st.sidebar.error(status_message)
            elif error_code == "missing_type_col":
                 status_message = "Catalog is missing the required 'Type' column."
                 st.sidebar.error(status_message)
            elif error_code == "parser_error":
                 status_message = f"Error parsing catalog file: {error_detail}"
                 st.sidebar.error(status_message)
                 st.sidebar.info("Please ensure the file is a valid CSV with ';' separator.")
            else: # Unexpected error
                 status_message = f"{t['error_loading_catalog']}: {error_detail}"
                 st.sidebar.error(status_message)
        elif error_type == "warning":
            if error_code == "catalog_empty":
                 status_message = t['warning_catalog_empty']
                 st.sidebar.warning(status_message) # Show warning if empty after processing

        st.session_state.catalog_status_msg = status_message # Store error/warning message
        df_catalog = None # Ensure None is returned on error/warning
    else:
        # Should not happen, but handle unexpected return type
        status_message = "Unknown error loading catalog."
        st.sidebar.error(status_message)
        st.session_state.catalog_status_msg = status_message
        df_catalog = None

    return df_catalog


# --- Fallback Window ---
def _get_fallback_window(reference_time: Time) -> tuple[Time, Time]:
    """Provides a simple fallback observation window (e.g., 6 PM to 6 AM UTC)."""
    ref_dt_utc = reference_time.to_datetime(timezone.utc)
    ref_date = ref_dt_utc.date()
    fallback_start_dt = datetime.combine(ref_date, time(18, 0), tzinfo=timezone.utc)
    fallback_end_dt = datetime.combine(ref_date + timedelta(days=1), time(6, 0), tzinfo=timezone.utc)
    fallback_start_time = Time(fallback_start_dt, scale='utc')
    fallback_end_time = Time(fallback_end_dt, scale='utc')
    print(f"Using fallback window: {fallback_start_time.iso} to {fallback_end_time.iso}")
    return fallback_start_time, fallback_end_time

# --- Observation Window Calculation ---
def get_observable_window(observer: Observer, reference_time: Time, is_now: bool, lang: str) -> tuple[Time | None, Time | None, str]:
    """Calculates the astronomical darkness window for observation."""
    t = translations.get(lang, translations['en'])
    status_message = ""
    start_time, end_time = None, None
    current_utc_time = Time.now()

    # Determine calculation base time
    calc_base_time = reference_time
    if is_now:
        current_dt_utc = current_utc_time.to_datetime(timezone.utc)
        noon_today_utc = datetime.combine(current_dt_utc.date(), time(12, 0), tzinfo=timezone.utc)
        calc_base_time = Time(noon_today_utc - timedelta(days=1)) if current_dt_utc < noon_today_utc else Time(noon_today_utc)
        print(f"Calculating 'Now' window based on UTC noon: {calc_base_time.iso}")
    else:
        selected_date_noon_utc = datetime.combine(reference_time.to_datetime(timezone.utc).date(), time(12, 0), tzinfo=timezone.utc)
        calc_base_time = Time(selected_date_noon_utc, scale='utc')
        print(f"Calculating specific night window based on UTC noon: {calc_base_time.iso}")

    try:
        if not isinstance(observer, Observer): raise TypeError(f"Internal Error: Expected astroplan.Observer, got {type(observer)}")

        astro_set = observer.twilight_evening_astronomical(calc_base_time, which='next')
        astro_rise = observer.twilight_morning_astronomical(astro_set if astro_set else calc_base_time, which='next')

        if astro_set is None or astro_rise is None: raise ValueError("Could not determine one or both astronomical twilight times.")
        if astro_rise <= astro_set:
            try: # Check for polar conditions
                sun_alt_ref = observer.sun_altaz(calc_base_time).alt
                sun_alt_12h_later = observer.sun_altaz(calc_base_time + 12*u.hour).alt
                if sun_alt_ref < -18*u.deg and sun_alt_12h_later < -18*u.deg:
                    status_message = t['error_polar_night']
                    start_time, end_time = _get_fallback_window(calc_base_time)
                    status_message += t['window_fallback_info'].format(start_time.iso, end_time.iso)
                    return start_time, end_time, status_message
                elif sun_alt_ref > -18*u.deg:
                    times_check = calc_base_time + np.linspace(0, 24, 49)*u.hour
                    sun_alts_check = observer.sun_altaz(times_check).alt
                    if np.min(sun_alts_check) > -18*u.deg:
                        status_message = t['error_polar_day']
                        start_time, end_time = _get_fallback_window(calc_base_time)
                        status_message += t['window_fallback_info'].format(start_time.iso, end_time.iso)
                        return start_time, end_time, status_message
            except Exception as check_e: print(f"Error during polar check: {check_e}")
            raise ValueError("Calculated morning twilight is not after evening twilight.")

        start_time, end_time = astro_set, astro_rise

        if is_now:
            if end_time < current_utc_time:
                status_message = t['window_already_passed'] + "\n"
                next_noon_utc = datetime.combine(current_utc_time.to_datetime(timezone.utc).date() + timedelta(days=1), time(12, 0), tzinfo=timezone.utc)
                astro_set_next = observer.twilight_evening_astronomical(Time(next_noon_utc), which='next')
                astro_rise_next = observer.twilight_morning_astronomical(astro_set_next if astro_set_next else Time(next_noon_utc), which='next')
                if astro_set_next is None or astro_rise_next is None or astro_rise_next <= astro_set_next:
                    raise ValueError("Could not determine valid twilight times for the *next* night.")
                start_time, end_time = astro_set_next, astro_rise_next
            elif start_time < current_utc_time:
                print(f"Adjusting window start from {start_time.iso} to current time {current_utc_time.iso}")
                start_time = current_utc_time

        start_fmt = start_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')
        end_fmt = end_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')
        status_message += t['window_info_template'].format(start_fmt, end_fmt)

    except ValueError as ve:
        error_detail = f"{ve}"
        print(f"Astroplan ValueError calculating window: {error_detail}")
        if 'polar' not in status_message:
            try: # Check polar conditions again on error
                sun_alt_ref = observer.sun_altaz(calc_base_time).alt
                sun_alt_12h_later = observer.sun_altaz(calc_base_time + 12*u.hour).alt
                if sun_alt_ref < -18*u.deg and sun_alt_12h_later < -18*u.deg: status_message = t['error_polar_night']
                elif sun_alt_ref > -18*u.deg:
                    times_check = calc_base_time + np.linspace(0, 24, 49)*u.hour
                    sun_alts_check = observer.sun_altaz(times_check).alt
                    if np.min(sun_alts_check) > -18*u.deg: status_message = t['error_polar_day']
                    else: status_message = t['window_calc_error'].format(error_detail, " (Check location/time)")
                else: status_message = t['window_calc_error'].format(error_detail, traceback.format_exc())
            except Exception as check_e:
                print(f"Error checking sun altitude for polar conditions: {check_e}")
                status_message = t['window_calc_error'].format(error_detail, traceback.format_exc())
        start_time, end_time = _get_fallback_window(calc_base_time)
        status_message += t['window_fallback_info'].format(start_time.iso, end_time.iso)

    except Exception as e:
        status_message = t['window_calc_error'].format(e, traceback.format_exc())
        print(f"Unexpected error calculating window: {e}")
        start_time, end_time = _get_fallback_window(calc_base_time)
        status_message += t['window_fallback_info'].format(start_time.iso, end_time.iso)

    # Final check and fallback
    if start_time is None or end_time is None or end_time <= start_time:
        if not status_message or ("Error" not in status_message and "Fallback" not in status_message):
             status_message += ("\n" if status_message else "") + t['error_no_window']
        start_time_fb, end_time_fb = _get_fallback_window(calc_base_time)
        if t['window_fallback_info'].format(start_time_fb.iso, end_time_fb.iso) not in status_message:
             status_message += t['window_fallback_info'].format(start_time_fb.iso, end_time_fb.iso)
        start_time, end_time = start_time_fb, end_time_fb

    return start_time, end_time, status_message


# --- Object Finding Logic ---
def find_observable_objects(observer_location: EarthLocation,
                            observing_times: Time,
                            min_altitude_limit: u.Quantity,
                            catalog_df: pd.DataFrame,
                            lang: str) -> list[dict]:
    """Finds observable Deep Sky Objects."""
    t = translations.get(lang, translations['en'])
    observable_objects = []

    # --- Input Validation ---
    if not isinstance(observer_location, EarthLocation): st.error(f"Internal Error: observer_location type {type(observer_location)}"); return []
    if not isinstance(observing_times, Time) or not observing_times.shape: st.error(f"Internal Error: observing_times type {type(observing_times)}"); return []
    if not isinstance(min_altitude_limit, u.Quantity) or not min_altitude_limit.unit.is_equivalent(u.deg): st.error(f"Internal Error: min_altitude_limit type {type(min_altitude_limit)}"); return []
    if not isinstance(catalog_df, pd.DataFrame): st.error(f"Internal Error: catalog_df type {type(catalog_df)}"); return []
    if catalog_df.empty: print("Input catalog_df is empty."); return []
    if len(observing_times) < 2: st.warning("Observing window too short.")

    altaz_frame = AltAz(obstime=observing_times, location=observer_location)
    min_alt_deg = min_altitude_limit.to(u.deg).value
    time_step_hours = (observing_times[1] - observing_times[0]).sec / 3600.0 if len(observing_times) > 1 else 0

    for index, obj in catalog_df.iterrows():
        try:
            ra_str, dec_str = obj.get('RA_str'), obj.get('Dec_str')
            dso_name = obj.get('Name', f"Unnamed {index}")
            if not ra_str or not dec_str: continue
            try: dso_coord = SkyCoord(ra=ra_str, dec=dec_str, unit=(u.hourangle, u.deg))
            except ValueError as coord_err: print(f"Skipping '{dso_name}': Invalid coords ('{ra_str}', '{dec_str}'). Err: {coord_err}"); continue

            dso_altazs = dso_coord.transform_to(altaz_frame)
            dso_alts = dso_altazs.alt.to(u.deg).value
            dso_azs = dso_altazs.az.to(u.deg).value

            if np.max(dso_alts) >= min_alt_deg:
                peak_alt_index = np.argmax(dso_alts)
                peak_alt = dso_alts[peak_alt_index]
                peak_time_utc = observing_times[peak_alt_index]
                peak_az = dso_azs[peak_alt_index]
                peak_direction = azimuth_to_direction(peak_az)
                try: constellation = get_constellation(dso_coord)
                except Exception as const_err: print(f"Warn: Constellation failed for {dso_name}: {const_err}"); constellation = "N/A"

                above_min_alt = dso_alts >= min_alt_deg
                continuous_duration_hours = 0
                if time_step_hours > 0 and np.any(above_min_alt):
                    runs = np.split(np.arange(len(above_min_alt)), np.where(np.diff(above_min_alt))[0]+1)
                    max_duration_indices = max((len(run) for run in runs if above_min_alt[run[0]]), default=0)
                    continuous_duration_hours = max_duration_indices * time_step_hours

                observable_objects.append({
                    'Name': dso_name, 'Type': obj.get('Type', "Unknown"), 'Constellation': constellation,
                    'Magnitude': obj.get('Mag'), 'Size (arcmin)': obj.get('MajAx'),
                    'RA': ra_str, 'Dec': dec_str, 'Max Altitude (°)': peak_alt,
                    'Azimuth at Max (°)': peak_az, 'Direction at Max': peak_direction,
                    'Time at Max (UTC)': peak_time_utc, 'Max Cont. Duration (h)': continuous_duration_hours,
                    'skycoord': dso_coord, 'altitudes': dso_alts, 'azimuths': dso_azs, 'times': observing_times
                })
        except Exception as obj_proc_e:
            error_msg = t.get('error_processing_object', "Error processing {}: {}").format(obj.get('Name', f'Index {index}'), obj_proc_e)
            print(error_msg)

    return observable_objects

# --- Time Formatting ---
def get_local_time_str(utc_time: Time | None, timezone_str: str) -> tuple[str, str]:
    """Converts UTC Time to localized string, returns 'N/A' on error."""
    if not isinstance(utc_time, Time): return "N/A", "N/A"
    if not isinstance(timezone_str, str) or not timezone_str: return "N/A", "N/A"
    try:
        local_tz = pytz.timezone(timezone_str)
        utc_dt = utc_time.to_datetime(timezone.utc)
        local_dt = utc_dt.astimezone(local_tz)
        local_time_str = local_dt.strftime('%Y-%m-%d %H:%M:%S')
        tz_display_name = local_dt.tzname() or local_tz.zone
        return local_time_str, tz_display_name
    except pytz.exceptions.UnknownTimeZoneError:
        print(f"Error: Unknown timezone '{timezone_str}'.")
        return utc_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), "UTC (TZ Error)"
    except Exception as e:
        print(f"Error converting time to local timezone '{timezone_str}': {e}")
        # traceback.print_exc() # Uncomment for debug
        return utc_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), "UTC (Conv. Error)"


# --- Main App ---
def main():
    """Main function to run the Streamlit application."""
    initialize_session_state()

    # --- Language Selection ---
    # This needs to happen *before* loading data or setting up UI elements that depend on translations
    lang_options_map = {'de': 'Deutsch', 'en': 'English', 'fr': 'Français'}
    lang_keys = list(lang_options_map.keys())
    current_lang_key = st.session_state.language
    if current_lang_key not in lang_keys:
        current_lang_key = 'de' # Default to German if invalid
        st.session_state.language = current_lang_key
    try:
        current_lang_index = lang_keys.index(current_lang_key)
    except ValueError:
        current_lang_index = 0 # Default to first index if key not found
        st.session_state.language = lang_keys[0]

    # Display radio button in the sidebar
    with st.sidebar:
        st.header(translations[current_lang_key]['settings_header']) # Use current lang for header *before* potential change
        selected_lang_key = st.radio(
            translations[current_lang_key]['language_select_label'], # Label in current lang
            options=lang_keys,
            format_func=lambda key: lang_options_map[key], # Display names
            key='language_radio', # Use a stable key
            index=current_lang_index,
            horizontal=True
        )

    # Update language state *if* changed, this triggers rerun automatically
    if selected_lang_key != st.session_state.language:
        st.session_state.language = selected_lang_key
        st.session_state.location_search_status_msg = "" # Reset location msg on lang change
        # --- OPTIMIZATION: Removed explicit st.rerun() ---
        # Streamlit handles rerun automatically on widget change
        # st.rerun()

    # --- Get Current Language and Translations (AFTER potential update) ---
    lang = st.session_state.language
    t = translations[lang] # Use the potentially updated language

    # --- Load Catalog Data (using optimized caching) ---
    # This now uses the wrapper function which handles caching and messages
    df_catalog_data = get_catalog_data(CATALOG_FILEPATH, lang)

    # --- Display Catalog Status in Sidebar ---
    with st.sidebar:
        # Display the status message set by get_catalog_data
        if st.session_state.catalog_status_msg:
             # Check the message content to decide if success, warning or error
             if "Error" in st.session_state.catalog_status_msg or "Fehler" in st.session_state.catalog_status_msg:
                 st.error(st.session_state.catalog_status_msg)
             elif "Warning" in st.session_state.catalog_status_msg or "Warnung" in st.session_state.catalog_status_msg or "empty" in st.session_state.catalog_status_msg or "leer" in st.session_state.catalog_status_msg:
                 st.warning(st.session_state.catalog_status_msg)
             else:
                 st.success(st.session_state.catalog_status_msg)


    # --- Title and Glossary (Main Area) ---
    st.title("Advanced DSO Finder")
    with st.expander(t['object_type_glossary_title']):
        glossary_items = t.get('object_type_glossary', {})
        if glossary_items:
            col1, col2 = st.columns(2)
            col_index = 0
            sorted_items = sorted(glossary_items.items())
            for abbr, full_name in sorted_items:
                target_col = col1 if col_index % 2 == 0 else col2
                target_col.markdown(f"**{abbr}:** {full_name}")
                col_index += 1
        else: st.info("Glossary not available.")
    st.markdown("---")


    # --- Sidebar Settings (Continued) ---
    with st.sidebar:
        # --- Location Settings ---
        with st.expander(t['location_expander'], expanded=True):
            location_options_map_ui = {
                'Search': t['location_option_search'],
                'Manual': t['location_option_manual']
            }
            st.radio(
                t['location_select_label'], options=list(location_options_map_ui.keys()),
                format_func=lambda key: location_options_map_ui[key],
                key="location_choice_key", horizontal=True
            )

            lat_val, lon_val, height_val = None, None, None
            location_valid_for_tz = False
            current_location_valid = False # Renamed from location_is_valid_for_run for clarity

            if st.session_state.location_choice_key == "Manual":
                st.number_input(t['location_lat_label'], min_value=-90.0, max_value=90.0, step=0.01, format="%.4f", key="manual_lat_val")
                st.number_input(t['location_lon_label'], min_value=-180.0, max_value=180.0, step=0.01, format="%.4f", key="manual_lon_val")
                st.number_input(t['location_elev_label'], min_value=-500, step=10, format="%d", key="manual_height_val")
                lat_val, lon_val, height_val = st.session_state.manual_lat_val, st.session_state.manual_lon_val, st.session_state.manual_height_val
                if isinstance(lat_val, (int, float)) and isinstance(lon_val, (int, float)) and isinstance(height_val, (int, float)):
                    location_valid_for_tz, current_location_valid = True, True
                    st.session_state.location_search_success = False # Reset search state
                    st.session_state.searched_location_name = None
                    st.session_state.location_search_status_msg = ""
                else:
                    st.warning(t['location_error_manual_none'])
                    current_location_valid = False

            elif st.session_state.location_choice_key == "Search":
                with st.form("location_search_form"):
                    st.text_input(t['location_search_label'], key="location_search_query", placeholder=t['location_search_placeholder'])
                    st.number_input(t['location_elev_label'], min_value=-500, step=10, format="%d", key="manual_height_val")
                    location_search_form_submitted = st.form_submit_button(t['location_search_submit_button'])

                status_placeholder = st.empty() # Placeholder for status messages
                # Display previous status if exists
                if st.session_state.location_search_status_msg:
                    if st.session_state.location_search_success: status_placeholder.success(st.session_state.location_search_status_msg)
                    else: status_placeholder.error(st.session_state.location_search_status_msg)

                if location_search_form_submitted and st.session_state.location_search_query:
                    location, service_used, final_error = None, None, None
                    query = st.session_state.location_search_query
                    user_agent = f"AdvDSOFinder/{random.randint(1000,9999)}"

                    with st.spinner(t['spinner_geocoding']):
                        # Try Nominatim -> ArcGIS -> Photon
                        for service_name, geocoder_cls, geolocator_args in [
                            ("Nominatim", Nominatim, {'user_agent': user_agent, 'timeout': 10}),
                            ("ArcGIS", ArcGIS, {'timeout': 15}),
                            ("Photon", Photon, {'user_agent': user_agent, 'timeout': 15})
                        ]:
                            if location: break # Stop if found
                            print(f"Trying {service_name}...")
                            if service_name != "Nominatim": status_placeholder.info(t[f'location_search_info_{"fallback" if service_name=="ArcGIS" else "fallback2"}'])
                            try:
                                geolocator = geocoder_cls(**geolocator_args)
                                location = geolocator.geocode(query)
                                if location: service_used = service_name; print(f"{service_name} success."); break
                                else: print(f"{service_name} returned None.")
                            except (GeocoderTimedOut, GeocoderServiceError) as e_geo:
                                print(f"{service_name} failed: {e_geo}")
                                if not final_error: final_error = e_geo
                            except Exception as e_gen:
                                print(f"{service_name} failed unexpectedly: {e_gen}")
                                if not final_error: final_error = e_gen

                    # Process result
                    if location and service_used:
                        found_lat, found_lon, found_name = location.latitude, location.longitude, location.address
                        st.session_state.update({
                            'searched_location_name': found_name, 'location_search_success': True,
                            'manual_lat_val': found_lat, 'manual_lon_val': found_lon
                        })
                        coord_str = t['location_search_coords'].format(found_lat, found_lon)
                        msg_key = 'location_search_found' if service_used=="Nominatim" else f'location_search_found_{"fallback" if service_used=="ArcGIS" else "fallback2"}'
                        st.session_state.location_search_status_msg = f"{t[msg_key].format(found_name)}\n({coord_str})"
                        status_placeholder.success(st.session_state.location_search_status_msg) # Show success
                        lat_val, lon_val, height_val = found_lat, found_lon, st.session_state.manual_height_val
                        location_valid_for_tz, current_location_valid = True, True
                    else: # Geocoding failed
                        st.session_state.update({'location_search_success': False, 'searched_location_name': None})
                        if final_error:
                            if isinstance(final_error, GeocoderTimedOut): msg = t['location_search_error_timeout']
                            elif isinstance(final_error, GeocoderServiceError): msg = t['location_search_error_service'].format(final_error)
                            else: msg = t['location_search_error_fallback2_failed'].format(final_error)
                        else: msg = t['location_search_error_not_found']
                        st.session_state.location_search_status_msg = msg
                        status_placeholder.error(msg) # Show error
                        current_location_valid = False

                # If search was previously successful, use stored values
                elif st.session_state.location_search_success:
                    lat_val, lon_val, height_val = st.session_state.manual_lat_val, st.session_state.manual_lon_val, st.session_state.manual_height_val
                    location_valid_for_tz, current_location_valid = True, True
                    status_placeholder.success(st.session_state.location_search_status_msg) # Re-display success message

            # Update overall location validity state
            st.session_state.location_is_valid_for_run = current_location_valid

            # --- Automatic Timezone Detection ---
            st.markdown("---")
            auto_timezone_msg = ""
            if location_valid_for_tz and lat_val is not None and lon_val is not None:
                if tf:
                    try:
                        found_tz = tf.timezone_at(lng=lon_val, lat=lat_val)
                        if found_tz:
                            pytz.timezone(found_tz); st.session_state.selected_timezone = found_tz
                            auto_timezone_msg = f"{t['timezone_auto_set_label']} **{found_tz}**"
                        else: st.session_state.selected_timezone = 'UTC'; auto_timezone_msg = f"{t['timezone_auto_fail_label']} **UTC** ({t['timezone_auto_fail_msg']})"
                    except pytz.UnknownTimeZoneError: st.session_state.selected_timezone = 'UTC'; auto_timezone_msg = f"{t['timezone_auto_fail_label']} **UTC** (Invalid TZ: '{found_tz}')"
                    except Exception as tz_find_e: print(f"TZ find error: {tz_find_e}"); st.session_state.selected_timezone = 'UTC'; auto_timezone_msg = f"{t['timezone_auto_fail_label']} **UTC** (Error)"
                else: auto_timezone_msg = f"{t['timezone_auto_fail_label']} **{INITIAL_TIMEZONE}** (Auto-detect N/A)"; st.session_state.selected_timezone = INITIAL_TIMEZONE
            else: auto_timezone_msg = f"{t['timezone_auto_fail_label']} **{INITIAL_TIMEZONE}** (Location Invalid)"; st.session_state.selected_timezone = INITIAL_TIMEZONE
            st.markdown(auto_timezone_msg, unsafe_allow_html=True)


        # --- Time Settings ---
        with st.expander(t['time_expander'], expanded=False):
            time_options_map_ui = {'Now': t['time_option_now'], 'Specific': t['time_option_specific']}
            time_choice_key_exp = st.radio(
                t['time_select_label'], options=list(time_options_map_ui.keys()),
                format_func=lambda key: time_options_map_ui[key],
                key="time_choice_exp", horizontal=True
            )
            is_time_now_exp = (time_choice_key_exp == "Now")
            if is_time_now_exp: st.caption(f"Current UTC: {Time.now().iso}")
            else:
                st.date_input(
                    t['time_date_select_label'], value=st.session_state.selected_date_widget,
                    min_value=date.today()-timedelta(days=365*10), max_value=date.today()+timedelta(days=365*2),
                    key='selected_date_widget'
                )

        # --- Filter Settings ---
        with st.expander(t['filters_expander'], expanded=False):
            # Magnitude Filter
            st.markdown(t['mag_filter_header'])
            mag_filter_options_map_ui = {'Bortle Scale': t['mag_filter_option_bortle'], 'Manual': t['mag_filter_option_manual']}
            st.radio(t['mag_filter_method_label'], options=list(mag_filter_options_map_ui.keys()),
                     format_func=lambda key: mag_filter_options_map_ui[key], key="mag_filter_mode_exp", horizontal=True)
            st.slider(t['mag_filter_bortle_label'], 1, 9, key='bortle_slider', help=t['mag_filter_bortle_help'])
            if st.session_state.mag_filter_mode_exp == "Manual":
                st.slider(t['mag_filter_min_mag_label'], -5.0, 20.0, step=0.5, format="%.1f", help=t['mag_filter_min_mag_help'], key='manual_min_mag_slider')
                st.slider(t['mag_filter_max_mag_label'], -5.0, 20.0, step=0.5, format="%.1f", help=t['mag_filter_max_mag_help'], key='manual_max_mag_slider')
                if st.session_state.manual_min_mag_slider > st.session_state.manual_max_mag_slider: st.warning(t['mag_filter_warning_min_max'])

            # Altitude Filter
            st.markdown("---"); st.markdown(t['min_alt_header'])
            st.slider(t['min_alt_label'], 0, 90, key='min_alt_slider', step=1)
            st.slider(t['max_alt_label'], 0, 90, key='max_alt_slider', step=1)
            if st.session_state.min_alt_slider > st.session_state.max_alt_slider: st.warning("Min. Höhe > Max. Höhe!")

            # Moon Filter
            st.markdown("---"); st.markdown(t['moon_warning_header'])
            st.slider(t['moon_warning_label'], 0, 100, key='moon_phase_slider', step=5)

            # Object Type Filter
            st.markdown("---"); st.markdown(t['object_types_header'])
            all_types = []
            if df_catalog_data is not None and not df_catalog_data.empty and 'Type' in df_catalog_data.columns:
                try: all_types = sorted(list(df_catalog_data['Type'].dropna().astype(str).unique()))
                except Exception as e: st.warning(f"{t['object_types_error_extract']}: {e}")
            if all_types:
                st.multiselect(t['object_types_label'], options=all_types, key="object_type_filter_exp")
            else: st.info("Object types unavailable. Filter disabled."); st.session_state.object_type_filter_exp = []

            # Angular Size Filter
            st.markdown("---"); st.markdown(t['size_filter_header'])
            size_col_exists = df_catalog_data is not None and 'MajAx' in df_catalog_data.columns and df_catalog_data['MajAx'].notna().any()
            size_slider_disabled = not size_col_exists
            if size_col_exists:
                try:
                    valid_sizes = df_catalog_data['MajAx'].dropna()
                    min_sz, max_sz = max(0.1, float(valid_sizes.min())), float(valid_sizes.max())
                    c_min, c_max = st.session_state.size_arcmin_range
                    val = (max(min_sz, min(c_min, max_sz)), min(max_sz, max(c_max, min_sz)))
                    if val[0] > val[1]: val = (val[1], val[1]) # Ensure min <= max
                    step = 0.1 if max_sz <= 20 else (0.5 if max_sz <= 100 else 1.0)
                    st.slider(t['size_filter_label'], min_sz, max_sz, value=val, step=step, format="%.1f arcmin", key='size_arcmin_range', help=t['size_filter_help'])
                except Exception as size_e: st.error(f"Size slider error: {size_e}"); size_slider_disabled = True
            if size_slider_disabled:
                st.info("Angular size data ('MajAx') not found or invalid. Filter disabled.")
                st.slider(t['size_filter_label'], 0.0, 1.0, value=(0.0, 1.0), key='size_arcmin_range', disabled=True)

            # Direction Filter
            st.markdown("---"); st.markdown(t['direction_filter_header'])
            all_dir_str = t['direction_option_all']
            dir_opts_disp = [all_dir_str] + CARDINAL_DIRECTIONS
            dir_opts_int = [ALL_DIRECTIONS_KEY] + CARDINAL_DIRECTIONS
            curr_dir_int = st.session_state.selected_peak_direction
            if curr_dir_int not in dir_opts_int: curr_dir_int = ALL_DIRECTIONS_KEY; st.session_state.selected_peak_direction = curr_dir_int
            try: curr_dir_idx = dir_opts_int.index(curr_dir_int)
            except ValueError: curr_dir_idx = 0
            sel_dir_disp = st.selectbox(t['direction_filter_label'], options=dir_opts_disp, index=curr_dir_idx, key='direction_selectbox')
            st.session_state.selected_peak_direction = ALL_DIRECTIONS_KEY if sel_dir_disp == all_dir_str else dir_opts_int[dir_opts_disp.index(sel_dir_disp)]


        # --- Result Options ---
        with st.expander(t['results_options_expander'], expanded=False):
            max_objs = len(df_catalog_data) if df_catalog_data is not None else 50
            max_slider = max(5, max_objs); slider_dis = max_slider <= 5
            default_num = st.session_state.get('num_objects_slider', 20)
            clamped_def = max(5, min(default_num, max_slider))
            st.slider(t['results_options_max_objects_label'], 5, max_slider, value=clamped_def, step=1, key='num_objects_slider', disabled=slider_dis)

            sort_options_map_ui = {'Duration & Altitude': t['results_options_sort_duration'], 'Brightness': t['results_options_sort_magnitude']}
            st.radio(t['results_options_sort_method_label'], options=list(sort_options_map_ui.keys()),
                     format_func=lambda key: sort_options_map_ui[key], key='sort_method', horizontal=True)

    # --- Main Area ---

    # Display Search Parameters (using current language 't')
    st.subheader(t['search_params_header'])
    param_col1, param_col2 = st.columns(2)

    # Location Display
    location_display_main = t['location_error'].format("Not Set")
    observer_for_run_main = None # Define here for clarity
    if st.session_state.location_is_valid_for_run: # Use the state set in sidebar
        lat_main, lon_main, height_main = st.session_state.manual_lat_val, st.session_state.manual_lon_val, st.session_state.manual_height_val
        tz_str_main = st.session_state.selected_timezone
        try:
            observer_for_run_main = Observer(latitude=lat_main*u.deg, longitude=lon_main*u.deg, elevation=height_main*u.m, timezone=tz_str_main)
            if st.session_state.location_choice_key == "Manual": location_display_main = t['location_manual_display'].format(lat_main, lon_main)
            elif st.session_state.searched_location_name: location_display_main = t['location_search_display'].format(st.session_state.searched_location_name, lat_main, lon_main)
            else: location_display_main = f"Lat: {lat_main:.4f}, Lon: {lon_main:.4f}" # Fallback if search name missing
        except Exception as obs_e_main: location_display_main = t['location_error'].format(f"Observer creation failed: {obs_e_main}"); st.session_state.location_is_valid_for_run = False # Invalidate if observer fails
    param_col1.markdown(t['search_params_location'].format(location_display_main))

    # Time Display
    is_time_now_main_disp = (st.session_state.time_choice_exp == "Now")
    if is_time_now_main_disp:
        ref_time_main_disp = Time.now()
        try: local_now_str_disp, local_tz_now_disp = get_local_time_str(ref_time_main_disp, st.session_state.selected_timezone); time_display_main = t['search_params_time_now'].format(f"{local_now_str_disp} {local_tz_now_disp}")
        except: time_display_main = t['search_params_time_now'].format(f"{ref_time_main_disp.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    else:
        selected_date_main_disp = st.session_state.selected_date_widget
        ref_time_main_disp = Time(datetime.combine(selected_date_main_disp, time(12, 0)), scale='utc') # Define ref time for specific date
        time_display_main = t['search_params_time_specific'].format(selected_date_main_disp.strftime('%Y-%m-%d'))
    param_col1.markdown(t['search_params_time'].format(time_display_main))

    # Magnitude Filter Display
    min_mag_filter_disp, max_mag_filter_disp = -np.inf, np.inf
    if st.session_state.mag_filter_mode_exp == "Bortle Scale":
        max_mag_filter_disp = get_magnitude_limit(st.session_state.bortle_slider)
        mag_filter_display_main = t['search_params_filter_mag_bortle'].format(st.session_state.bortle_slider, max_mag_filter_disp)
    else:
        min_mag_filter_disp = st.session_state.manual_min_mag_slider
        max_mag_filter_disp = st.session_state.manual_max_mag_slider
        mag_filter_display_main = t['search_params_filter_mag_manual'].format(min_mag_filter_disp, max_mag_filter_disp)
    param_col2.markdown(t['search_params_filter_mag'].format(mag_filter_display_main))

    # Altitude and Type Filter Display
    min_alt_disp_main, max_alt_disp_main = st.session_state.min_alt_slider, st.session_state.max_alt_slider
    selected_types_disp_main = st.session_state.object_type_filter_exp
    types_str_main = ', '.join(selected_types_disp_main) if selected_types_disp_main else t['search_params_types_all']
    param_col2.markdown(t['search_params_filter_alt_types'].format(min_alt_disp_main, max_alt_disp_main, types_str_main))

    # Size Filter Display
    size_min_disp_main, size_max_disp_main = st.session_state.size_arcmin_range
    param_col2.markdown(t['search_params_filter_size'].format(size_min_disp_main, size_max_disp_main))

    # Direction Filter Display
    direction_disp_main = st.session_state.selected_peak_direction
    if direction_disp_main == ALL_DIRECTIONS_KEY: direction_disp_main = t['search_params_direction_all']
    param_col2.markdown(t['search_params_filter_direction'].format(direction_disp_main))


    # --- Find Objects Button ---
    st.markdown("---")
    find_button_clicked = st.button(t['find_button_label'], key="find_button", disabled=(df_catalog_data is None or not st.session_state.location_is_valid_for_run))
    if not st.session_state.location_is_valid_for_run and df_catalog_data is not None: st.warning(t['info_initial_prompt'])

    # --- Results Area ---
    results_placeholder = st.container()

    # --- Processing Logic ---
    if find_button_clicked:
        st.session_state.find_button_pressed = True
        # Reset plot states and results
        st.session_state.update({'show_plot': False, 'show_custom_plot': False, 'active_result_plot_data': None,
                                 'custom_target_plot_data': None, 'last_results': [], 'window_start_time': None, 'window_end_time': None})

        if observer_for_run_main and df_catalog_data is not None: # Use observer created for main area
            with st.spinner(t['spinner_searching']):
                try:
                    # 1. Calculate Window (use ref_time_main_disp calculated for display)
                    start_time_calc, end_time_calc, window_status = get_observable_window(observer_for_run_main, ref_time_main_disp, is_time_now_main_disp, lang)
                    results_placeholder.info(window_status)
                    st.session_state.window_start_time, st.session_state.window_end_time = start_time_calc, end_time_calc

                    if start_time_calc and end_time_calc and start_time_calc < end_time_calc:
                        time_res = 5 * u.minute
                        obs_times = Time(np.arange(start_time_calc.jd, end_time_calc.jd, time_res.to(u.day).value), format='jd', scale='utc')
                        if len(obs_times) < 2: results_placeholder.warning("Warning: Observation window too short.")

                        # 2. Filter Catalog (use filters from display section)
                        filtered_df = df_catalog_data[
                            (df_catalog_data['Mag'] >= min_mag_filter_disp) & (df_catalog_data['Mag'] <= max_mag_filter_disp)
                        ]
                        if selected_types_disp_main: filtered_df = filtered_df[filtered_df['Type'].isin(selected_types_disp_main)]
                        size_col_exists_run = 'MajAx' in filtered_df.columns and filtered_df['MajAx'].notna().any()
                        if size_col_exists_run:
                            filtered_df = filtered_df.dropna(subset=['MajAx'])
                            filtered_df = filtered_df[(filtered_df['MajAx'] >= size_min_disp_main) & (filtered_df['MajAx'] <= size_max_disp_main)]

                        if filtered_df.empty:
                            results_placeholder.warning(t['warning_no_objects_found'] + " (after initial filtering)")
                        else:
                            # 3. Find Observable Objects
                            min_alt_search = min_alt_disp_main * u.deg
                            found_objs = find_observable_objects(observer_for_run_main.location, obs_times, min_alt_search, filtered_df, lang)

                            # 4. Apply Max Alt & Direction Filters
                            final_objs = []
                            sel_dir_run = st.session_state.selected_peak_direction # Use state directly
                            max_alt_filter_run = max_alt_disp_main # Use value from display
                            for obj in found_objs:
                                if obj.get('Max Altitude (°)', -999) > max_alt_filter_run: continue
                                if sel_dir_run != ALL_DIRECTIONS_KEY and obj.get('Direction at Max') != sel_dir_run: continue
                                final_objs.append(obj)

                            # 5. Sort
                            sort_key_run = st.session_state.sort_method
                            if sort_key_run == 'Brightness': final_objs.sort(key=lambda x: x.get('Magnitude', float('inf')) if x.get('Magnitude') is not None else float('inf'))
                            else: final_objs.sort(key=lambda x: (x.get('Max Cont. Duration (h)', 0), x.get('Max Altitude (°)', 0)), reverse=True)

                            # 6. Limit & Store
                            num_to_show_run = st.session_state.num_objects_slider
                            st.session_state.last_results = final_objs[:num_to_show_run]

                            # Display Summary
                            if not final_objs: results_placeholder.warning(t['warning_no_objects_found'])
                            else:
                                results_placeholder.success(t['success_objects_found'].format(len(final_objs)))
                                sort_msg_key = 'info_showing_list_duration' if sort_key_run != 'Brightness' else 'info_showing_list_magnitude'
                                results_placeholder.info(t[sort_msg_key].format(len(st.session_state.last_results)))
                    else: # Window calc failed
                        results_placeholder.error(t['error_no_window'] + " Cannot proceed.")
                        st.session_state.window_start_time, st.session_state.window_end_time = None, None # Ensure reset
                except Exception as search_e:
                    results_placeholder.error(t['error_search_unexpected'] + f"\n```\n{search_e}\n```")
                    traceback.print_exc()
                    st.session_state.last_results = [] # Clear results on error
                    st.session_state.window_start_time, st.session_state.window_end_time = None, None # Ensure reset
        else: # Observer or catalog invalid
             if df_catalog_data is None: results_placeholder.error("Cannot search: Catalog data not loaded.")
             if not observer_for_run_main: results_placeholder.error("Cannot search: Location is not valid.")
             st.session_state.last_results = []
             st.session_state.window_start_time, st.session_state.window_end_time = None, None


    # --- Display Results Block ---
    if st.session_state.last_results:
        results_data_disp = st.session_state.last_results
        results_placeholder.subheader(t['results_list_header'])

        # Moon Phase Display
        window_start_disp = st.session_state.get('window_start_time')
        window_end_disp = st.session_state.get('window_end_time')
        if observer_for_run_main and isinstance(window_start_disp, Time) and isinstance(window_end_disp, Time):
            mid_time_disp = window_start_disp + (window_end_disp - window_start_disp) / 2
            try:
                illum_disp = moon_illumination(mid_time_disp) * 100
                moon_svg_disp = create_moon_phase_svg(illum_disp / 100, size=50)
                moon_col1, moon_col2 = results_placeholder.columns([1, 3])
                with moon_col1: st.markdown(moon_svg_disp, unsafe_allow_html=True)
                with moon_col2:
                    st.metric(label=t['moon_metric_label'], value=f"{illum_disp:.0f}%")
                    if illum_disp > st.session_state.moon_phase_slider: st.warning(t['moon_warning_message'].format(illum_disp, st.session_state.moon_phase_slider))
            except Exception as moon_e_disp: results_placeholder.warning(t['moon_phase_error'].format(moon_e_disp))
        elif st.session_state.find_button_pressed: results_placeholder.info("Moon phase cannot be calculated (invalid window).")

        # Plot Type Selection
        plot_options_map_ui = {'Sky Path': t['graph_type_sky_path'], 'Altitude Plot': t['graph_type_alt_time']}
        results_placeholder.radio(t['graph_type_label'], options=list(plot_options_map_ui.keys()), format_func=lambda key: plot_options_map_ui[key], key='plot_type_selection', horizontal=True)

        # Display Individual Objects
        for i, obj_data_disp in enumerate(results_data_disp):
            obj_name_disp = obj_data_disp.get('Name', 'N/A')
            obj_type_disp = obj_data_disp.get('Type', 'N/A')
            obj_mag_disp = obj_data_disp.get('Magnitude')
            exp_title = t['results_expander_title'].format(obj_name_disp, obj_type_disp, obj_mag_disp if obj_mag_disp is not None else 99)
            is_exp = (st.session_state.expanded_object_name == obj_name_disp)
            obj_cont = results_placeholder.container() # Use main results placeholder

            with obj_cont.expander(exp_title, expanded=is_exp):
                col1, col2, col3 = st.columns([2,2,1])
                # Col 1: Details
                col1.markdown(t['results_coords_header'])
                col1.markdown(f"**{t['results_export_constellation']}:** {obj_data_disp.get('Constellation', 'N/A')}")
                size_disp = obj_data_disp.get('Size (arcmin)')
                col1.markdown(f"**{t['results_size_label']}** {t['results_size_value'].format(size_disp) if size_disp is not None else 'N/A'}")
                col1.markdown(f"**RA:** {obj_data_disp.get('RA', 'N/A')}")
                col1.markdown(f"**Dec:** {obj_data_disp.get('Dec', 'N/A')}")
                # Col 2: Visibility
                col2.markdown(t['results_max_alt_header'])
                max_alt_disp = obj_data_disp.get('Max Altitude (°)', 0)
                az_max_disp = obj_data_disp.get('Azimuth at Max (°)', 0)
                dir_max_disp = obj_data_disp.get('Direction at Max', 'N/A')
                az_fmt = t['results_azimuth_label'].format(az_max_disp, "")
                dir_fmt = t['results_direction_label'].format(dir_max_disp)
                col2.markdown(f"**{max_alt_disp:.1f}°** {az_fmt}{dir_fmt}")
                col2.markdown(t['results_best_time_header'])
                peak_utc_disp = obj_data_disp.get('Time at Max (UTC)')
                loc_time_str, loc_tz_name = get_local_time_str(peak_utc_disp, st.session_state.selected_timezone)
                col2.markdown(f"{loc_time_str} ({loc_tz_name})")
                col2.markdown(t['results_cont_duration_header'])
                dur_h_disp = obj_data_disp.get('Max Cont. Duration (h)', 0)
                col2.markdown(t['results_duration_value'].format(dur_h_disp))
                # Col 3: Links & Actions
                g_query = urllib.parse.quote_plus(f"{obj_name_disp} astronomy"); g_url = f"https://www.google.com/search?q={g_query}"
                col3.markdown(f"[{t['google_link_text']}]({g_url})", unsafe_allow_html=True)
                s_query = urllib.parse.quote_plus(obj_name_disp); s_url = f"http://simbad.u-strasbg.fr/simbad/sim-basic?Ident={s_query}"
                col3.markdown(f"[{t['simbad_link_text']}]({s_url})", unsafe_allow_html=True)

                plot_btn_key = f"plot_{obj_name_disp}_{i}"
                if st.button(t['results_graph_button'], key=plot_btn_key):
                    st.session_state.update({'plot_object_name': obj_name_disp, 'active_result_plot_data': obj_data_disp,
                                             'show_plot': True, 'show_custom_plot': False, 'expanded_object_name': obj_name_disp})
                    st.rerun()

                # Plot Display Area (Inside Expander)
                if st.session_state.show_plot and st.session_state.plot_object_name == obj_name_disp:
                    plot_data_disp = st.session_state.active_result_plot_data
                    min_alt_plot = st.session_state.min_alt_slider
                    max_alt_plot = st.session_state.max_alt_slider
                    st.markdown("---")
                    with st.spinner(t['results_spinner_plotting']):
                        try:
                            fig_disp = create_plot(plot_data_disp, min_alt_plot, max_alt_plot, st.session_state.plot_type_selection, lang)
                            if fig_disp:
                                st.pyplot(fig_disp)
                                if st.button(t['results_close_graph_button'], key=f"close_plot_{obj_name_disp}_{i}"):
                                    st.session_state.update({'show_plot': False, 'active_result_plot_data': None, 'expanded_object_name': None})
                                    st.rerun()
                            else: st.error(t['results_graph_not_created'])
                        except Exception as plot_err_disp: st.error(t['results_graph_error'].format(plot_err_disp)); traceback.print_exc()

        # CSV Export Button
        csv_export_placeholder = results_placeholder.empty() # Placeholder at the end
        if results_data_disp:
            try:
                export_data_list = []
                for obj_exp in results_data_disp:
                    peak_utc_exp = obj_exp.get('Time at Max (UTC)')
                    loc_time_exp, _ = get_local_time_str(peak_utc_exp, st.session_state.selected_timezone)
                    export_data_list.append({
                        t['results_export_name']: obj_exp.get('Name'), t['results_export_type']: obj_exp.get('Type'),
                        t['results_export_constellation']: obj_exp.get('Constellation'), t['results_export_mag']: obj_exp.get('Magnitude'),
                        t['results_export_size']: obj_exp.get('Size (arcmin)'), t['results_export_ra']: obj_exp.get('RA'),
                        t['results_export_dec']: obj_exp.get('Dec'), t['results_export_max_alt']: obj_exp.get('Max Altitude (°)'),
                        t['results_export_az_at_max']: obj_exp.get('Azimuth at Max (°)'), t['results_export_direction_at_max']: obj_exp.get('Direction at Max'),
                        t['results_export_time_max_utc']: peak_utc_exp.iso if peak_utc_exp else "N/A",
                        t['results_export_time_max_local']: loc_time_exp, t['results_export_cont_duration']: obj_exp.get('Max Cont. Duration (h)')
                    })
                df_export = pd.DataFrame(export_data_list)
                decimal_sep = ',' if lang == 'de' else '.'
                csv_string = df_export.to_csv(index=False, sep=';', encoding='utf-8-sig', decimal=decimal_sep)
                now_str = datetime.now().strftime("%Y%m%d_%H%M")
                csv_filename = t['results_csv_filename'].format(now_str)
                csv_export_placeholder.download_button(label=t['results_save_csv_button'], data=csv_string, file_name=csv_filename, mime='text/csv', key='csv_dl_btn')
            except Exception as csv_e_disp: csv_export_placeholder.error(t['results_csv_export_error'].format(csv_e_disp))

    elif st.session_state.find_button_pressed: # Show message if button was pressed but no results
        results_placeholder.info(t['warning_no_objects_found'])


    # --- Custom Target Plotting ---
    st.markdown("---")
    with st.expander(t['custom_target_expander']):
        with st.form("custom_target_form"):
             st.text_input(t['custom_target_ra_label'], key="custom_target_ra", placeholder=t['custom_target_ra_placeholder'])
             st.text_input(t['custom_target_dec_label'], key="custom_target_dec", placeholder=t['custom_target_dec_placeholder'])
             st.text_input(t['custom_target_name_label'], key="custom_target_name", placeholder="Mein Komet")
             custom_plot_submitted = st.form_submit_button(t['custom_target_button'])

        custom_plot_error_placeholder = st.empty()
        custom_plot_display_area = st.empty()

        if custom_plot_submitted:
            st.session_state.update({'show_plot': False, 'show_custom_plot': False, 'custom_target_plot_data': None, 'custom_target_error': ""})
            custom_ra, custom_dec = st.session_state.custom_target_ra, st.session_state.custom_target_dec
            custom_name = st.session_state.custom_target_name or "Eigenes Ziel"
            window_start_cust = st.session_state.get('window_start_time')
            window_end_cust = st.session_state.get('window_end_time')

            if not custom_ra or not custom_dec: st.session_state.custom_target_error = t['custom_target_error_coords']
            elif not observer_for_run_main or not isinstance(window_start_cust, Time) or not isinstance(window_end_cust, Time): st.session_state.custom_target_error = t['custom_target_error_window']
            else:
                try:
                    custom_coord = SkyCoord(ra=custom_ra, dec=custom_dec, unit=(u.hourangle, u.deg))
                    if window_start_cust < window_end_cust:
                        time_res_cust = 5 * u.minute
                        obs_times_cust = Time(np.arange(window_start_cust.jd, window_end_cust.jd, time_res_cust.to(u.day).value), format='jd', scale='utc')
                        if len(obs_times_cust) < 2: raise ValueError("Custom plot time window too short.")
                    else: raise ValueError("Valid time window needed for custom plot.")

                    altaz_frame_cust = AltAz(obstime=obs_times_cust, location=observer_for_run_main.location)
                    custom_altazs = custom_coord.transform_to(altaz_frame_cust)
                    st.session_state.custom_target_plot_data = {
                        'Name': custom_name, 'altitudes': custom_altazs.alt.to(u.deg).value,
                        'azimuths': custom_altazs.az.to(u.deg).value, 'times': obs_times_cust
                    }
                    st.session_state.show_custom_plot = True; st.session_state.custom_target_error = ""
                    st.rerun()
                except ValueError as cust_coord_err: st.session_state.custom_target_error = f"{t['custom_target_error_coords']} ({cust_coord_err})"
                except Exception as cust_e: st.session_state.custom_target_error = f"Error creating custom plot: {cust_e}"; traceback.print_exc()

            if st.session_state.custom_target_error: custom_plot_error_placeholder.error(st.session_state.custom_target_error)

        # Display custom plot
        if st.session_state.show_custom_plot and st.session_state.custom_target_plot_data:
            cust_plot_data = st.session_state.custom_target_plot_data
            min_alt_cust_plot = st.session_state.min_alt_slider
            max_alt_cust_plot = st.session_state.max_alt_slider
            with custom_plot_display_area.container():
                st.markdown("---")
                with st.spinner(t['results_spinner_plotting']):
                    try:
                        fig_cust_disp = create_plot(cust_plot_data, min_alt_cust_plot, max_alt_cust_plot, st.session_state.plot_type_selection, lang)
                        if fig_cust_disp:
                            st.pyplot(fig_cust_disp)
                            if st.button(t['results_close_graph_button'], key="close_custom_plot"):
                                st.session_state.update({'show_custom_plot': False, 'custom_target_plot_data': None})
                                st.rerun()
                        else: st.error(t['results_graph_not_created'])
                    except Exception as plot_err_cust_disp: st.error(t['results_graph_error'].format(plot_err_cust_disp)); traceback.print_exc()

    # --- Donation Link ---
    st.markdown("---")
    st.caption(t['donation_text'], unsafe_allow_html=True)


# --- Plotting Function ---
#@st.cache_data(show_spinner=False) # Caching plot might be complex due to theme dependency
def create_plot(plot_data: dict, min_altitude_deg: float, max_altitude_deg: float, plot_type: str, lang: str) -> plt.Figure | None:
    """Creates either an Altitude vs Time or Sky Path (Alt/Az) plot."""
    t = translations.get(lang, translations['en'])
    # Theme detection (simplified fallback)
    try: from streamlit.config import get_option; theme = get_option("theme.base")
    except: theme = "light" # Default to light if detection fails
    is_dark = theme == "dark"
    plt.style.use('dark_background' if is_dark else 'default')
    line_color = 'skyblue' if is_dark else 'dodgerblue'
    grid_color = 'gray' if is_dark else 'lightgray'
    label_color = '#e0e0e0' if is_dark else '#333333'
    title_color = '#ffffff' if is_dark else '#000000'
    legend_facecolor = '#333333' if is_dark else '#eeeeee'
    min_alt_color = 'tomato' if is_dark else 'red'
    max_alt_color = 'orange' if is_dark else 'darkorange'

    fig, ax = plt.subplots(figsize=(10, 6))
    times, altitudes, azimuths = plot_data.get('times'), plot_data.get('altitudes'), plot_data.get('azimuths')
    obj_name = plot_data.get('Name', 'Object')
    if times is None or altitudes is None or len(times) != len(altitudes): print("Plot Error: Missing/mismatched data."); plt.close(fig); return None
    plot_times = times.plot_date

    if plot_type == 'Altitude Plot':
        ax.scatter(plot_times, altitudes, c=line_color, s=10, alpha=0.7, edgecolors='none')
        ax.axhline(min_altitude_deg, color=min_alt_color, linestyle='--', lw=1, label=t['graph_min_altitude_label'].format(min_altitude_deg))
        if max_altitude_deg < 90: ax.axhline(max_altitude_deg, color=max_alt_color, linestyle=':', lw=1, label=t['graph_max_altitude_label'].format(max_altitude_deg))
        ax.set_xlabel("Time (UTC)", color=label_color); ax.set_ylabel(t['graph_ylabel'], color=label_color)
        ax.set_title(t['graph_title_alt_time'].format(obj_name), color=title_color); ax.set_ylim(0, 90)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M')); fig.autofmt_xdate()
        ax.tick_params(axis='x', colors=label_color); ax.tick_params(axis='y', colors=label_color)
    elif plot_type == 'Sky Path':
        if azimuths is None: print("Plot Error: Azimuth data missing."); plt.close(fig); return None
        ax.remove(); ax = fig.add_subplot(111, projection='polar'); ax.set_facecolor(fig.get_facecolor())
        az_rad = np.deg2rad(azimuths); radius = 90 - altitudes
        time_norm = (times.jd - times.jd.min()) / (times.jd.max() - times.jd.min() + 1e-9)
        colors = plt.cm.plasma(time_norm)
        ax.scatter(az_rad, radius, c=colors, s=10, alpha=0.7, edgecolors='none')
        ax.plot(np.linspace(0, 2*np.pi, 100), np.full(100, 90 - min_altitude_deg), color=min_alt_color, ls='--', lw=1, label=t['graph_min_altitude_label'].format(min_altitude_deg))
        if max_altitude_deg < 90: ax.plot(np.linspace(0, 2*np.pi, 100), np.full(100, 90 - max_altitude_deg), color=max_alt_color, ls=':', lw=1, label=t['graph_max_altitude_label'].format(max_altitude_deg))
        ax.set_theta_zero_location('N'); ax.set_theta_direction(-1)
        ax.set_yticks(np.arange(0, 91, 15)); ax.set_yticklabels([f"{90-alt}°" for alt in np.arange(0, 91, 15)], color=label_color)
        ax.set_ylim(0, 90); ax.set_title(t['graph_title_sky_path'].format(obj_name), va='bottom', color=title_color)
        ax.grid(True, linestyle=':', alpha=0.5, color=grid_color); ax.spines['polar'].set_color(label_color)
        cbar = fig.colorbar(scatter, ax=ax, label="Time Progression (UTC)", pad=0.1)
        cbar.set_ticks([0, 1])
        try: start_lbl, end_lbl = times[0].to_datetime(timezone.utc).strftime('%H:%M'), times[-1].to_datetime(timezone.utc).strftime('%H:%M'); cbar.ax.set_yticklabels([start_lbl, end_lbl])
        except IndexError: cbar.ax.set_yticklabels(['Start', 'End'])
        cbar.set_label("Time Progression (UTC)", color=label_color); cbar.ax.yaxis.set_tick_params(color=label_color)
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=label_color)
    else: print(f"Plot Error: Unknown type '{plot_type}'"); plt.close(fig); return None

    legend = ax.legend(loc='upper right', fontsize='small', facecolor=legend_facecolor, framealpha=0.7)
    for text in legend.get_texts(): text.set_color(label_color)
    plt.tight_layout()
    return fig

# --- Run the App ---
if __name__ == "__main__":
    main()
