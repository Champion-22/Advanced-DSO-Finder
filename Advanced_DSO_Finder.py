# -*- coding: utf-8 -*-
# --- Basic Imports ---
from __future__ import annotations
import streamlit as st
import random
from datetime import datetime, date, time, timedelta, timezone
# import io # Removed unused import
import traceback
import os  # Needed for file path joining
import urllib.parse # Needed for robust URL encoding
import pandas as pd
import math # For isnan check

# --- Library Imports (Try after set_page_config) ---
try:
    # Attempt to import necessary libraries
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
    # Display error and stop if libraries are missing
    st.error(f"Error: Missing libraries. Please install the required packages. ({e})")
    st.stop()

# --- Page Config (MUST BE FIRST Streamlit command) ---
st.set_page_config(page_title="Advanced DSO Finder", layout="wide")

# --- Global Configuration & Initial Values ---
INITIAL_LAT = 47.17
INITIAL_LON = 8.01
INITIAL_HEIGHT = 550
INITIAL_TIMEZONE = "Europe/Zurich"
# APP_VERSION = "v8.0-plotfix" # Removed unused variable

# --- Path to Catalog File ---
try:
    # Determine the application directory
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback for environments where __file__ is not defined (e.g., interactive)
    APP_DIR = os.getcwd()
CATALOG_FILENAME = "ongc.csv"
CATALOG_FILEPATH = os.path.join(APP_DIR, CATALOG_FILENAME)


# Define cardinal directions
CARDINAL_DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
ALL_DIRECTIONS_KEY = 'All' # Internal key for 'All' option

# --- Translations --- (Start Zeile 62)
# Using German as the primary language based on user prompt
translations = {
    'de': {
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
        'donation_text': "Gefällt dir die App? [Unterstütze die Entwicklung auf Ko-fi ☕](https://ko-fi.com/advanceddsofinder)",
        'bug_report_button': "🐞 Fehler melden", # Added
        'bug_report_body': "\n\n(Bitte beschreiben Sie den Fehler und die Schritte zur Reproduktion)" # Added
        },
    'en': { # Start Zeile 234
        # --- Englische Übersetzungen ---
        'settings_header': "Settings", # Bereits vorhanden
        'language_select_label': "Language",
        'location_expander': "📍 Location",
        'location_select_label': "Select Location Method",
        'location_option_manual': "Enter Manually",
        'location_option_search': "Search by Name",
        'location_search_label': "Enter location name:",
        'location_search_submit_button': "Find Coordinates",
        'location_search_placeholder': "e.g., London, UK", # Beispiel angepasst
        'location_search_found': "Found (Nominatim): {}",
        'location_search_found_fallback': "Found via Fallback (ArcGIS): {}",
        'location_search_found_fallback2': "Found via 2nd Fallback (Photon): {}",
        'location_search_coords': "Lat: {:.4f}, Lon: {:.4f}",
        'location_search_error_not_found': "Location not found.",
        'location_search_error_service': "Geocoding service error: {}",
        'location_search_error_timeout': "Geocoding service timed out.",
        'location_search_error_refused': "Geocoding connection refused.",
        'location_search_info_fallback': "Nominatim failed, trying fallback service (ArcGIS)...",
        'location_search_info_fallback2': "ArcGIS failed, trying 2nd fallback service (Photon)...",
        'location_search_error_fallback_failed': "Primary (Nominatim) and fallback (ArcGIS) failed: {}",
        'location_search_error_fallback2_failed': "All geocoding services (Nominatim, ArcGIS, Photon) failed: {}",
        'location_lat_label': "Latitude (°N)",
        'location_lon_label': "Longitude (°E)",
        'location_elev_label': "Elevation (meters)",
        'location_manual_display': "Manual ({:.4f}, {:.4f})",
        'location_search_display': "Searched: {} ({:.4f}, {:.4f})",
        'location_error': "Location Error: {}",
        'location_error_fallback': "ERROR - Fallback used",
        'location_error_manual_none': "Manual location fields cannot be empty or invalid.",
        'time_expander': "⏱️ Time & Timezone",
        'time_select_label': "Select Time",
        'time_option_now': "Now (Upcoming Night)",
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
        'mag_filter_bortle_help': "Sky darkness: 1=Excellent Dark, 9=Inner-city Sky",
        'mag_filter_min_mag_label': "Min. Magnitude:",
        'mag_filter_min_mag_help': "Brightest object magnitude to include",
        'mag_filter_max_mag_label': "Max. Magnitude:",
        'mag_filter_max_mag_help': "Dimest object magnitude to include",
        'mag_filter_warning_min_max': "Min. Magnitude is greater than Max. Magnitude!",
        'min_alt_header': "**Object Altitude Above Horizon**",
        'min_alt_label': "Min. Object Altitude (°):",
        'max_alt_label': "Max. Object Altitude (°):",
        'moon_warning_header': "**Moon Warning**",
        'moon_warning_label': "Warn if Moon > (% Illumination):",
        'object_types_header': "**Object Types**",
        'object_types_error_extract': "Could not extract object types from catalog.",
        'object_types_label': "Filter Types (leave empty for all):",
        'size_filter_header': "**Angular Size Filter**",
        'size_filter_label': "Object Size (arcminutes):",
        'size_filter_help': "Filter objects by their apparent size (major axis). 1 arcminute = 1/60 degree.",
        'direction_filter_header': "**Filter by Cardinal Direction**",
        'direction_filter_label': "Show objects culminating towards:",
        'direction_option_all': "All",
        'object_type_glossary_title': "Object Type Glossary", # Bereits vorhanden
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
        'search_params_time_now': "Upcoming Night (from {} UTC)",
        'search_params_time_specific': "Night after {}",
        'search_params_filter_mag': "✨ Filter: {}",
        'search_params_filter_mag_bortle': "Bortle {} (<= {:.1f} mag)",
        'search_params_filter_mag_manual': "Manual ({:.1f}-{:.1f} mag)",
        'search_params_filter_alt_types': "🔭 Filter: Alt {}-{}°, Types: {}",
        'search_params_filter_size': "📐 Filter: Size {:.1f} - {:.1f} arcmin",
        'search_params_filter_direction': "🧭 Filter: Direction at Max: {}",
        'search_params_types_all': "All",
        'search_params_direction_all': "All",
        'spinner_searching': "Calculating window & searching objects...",
        'spinner_geocoding': "Searching for location...",
        'window_info_template': "Observation window: {} to {} UTC (Astronomical Twilight)",
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
        'results_export_cont_duration': "Max Cont Duration (h)",
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
        'results_graph_not_created': "Plot could not be created.",
        'results_close_graph_button': "Close Plot",
        'results_save_csv_button': "💾 Save Result List as CSV",
        'results_csv_filename': "dso_observation_list_{}.csv",
        'results_csv_export_error': "CSV Export Error: {}",
        'warning_no_objects_found': "No objects found matching all criteria for the calculated observation window.",
        'info_initial_prompt': "Welcome! Please **Enter Coordinates** or **Search Location** to enable object search.",
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
        'custom_target_ra_placeholder': "e.g., 10:45:03.6 or 161.265",
        'custom_target_dec_placeholder': "e.g., -16:42:58 or -16.716",
        'custom_target_button': "Create Custom Plot",
        'custom_target_error_coords': "Invalid RA/Dec format. Use HH:MM:SS.s / DD:MM:SS or decimal degrees.",
        'custom_target_error_window': "Cannot create plot. Ensure location and time window are valid (try clicking 'Find Observable Objects' first).",
        'error_processing_object': "Error processing {}: {}",
        'window_calc_error': "Error calculating observation window: {}\n{}",
        'window_fallback_info': "\nUsing fallback window: {} to {} UTC",
        'error_loading_catalog': "Error loading catalog file: {}",
        'warning_catalog_empty': "Catalog file loaded, but no matching objects found after filtering.",
        'donation_text': "Like the app? [Support the development on Ko-fi ☕](https://ko-fi.com/advanceddsofinder)", # Bereits vorhanden
        'bug_report_button': "🐞 Report Bug", # Bereits vorhanden
        'bug_report_body': "\n\n(Please describe the bug and the steps to reproduce it)", # Bereits vorhanden
    },
    'fr': {
        # --- Französische Übersetzungen ---
        'settings_header': "Paramètres", # Bereits vorhanden
        'language_select_label': "Langue",
        'location_expander': "📍 Emplacement",
        'location_select_label': "Choisir la méthode d'emplacement",
        'location_option_manual': "Saisir manuellement",
        'location_option_search': "Rechercher par nom",
        'location_search_label': "Entrer le nom du lieu :",
        'location_search_submit_button': "Trouver les coordonnées",
        'location_search_placeholder': "p.ex. Paris, France", # Beispiel angepasst
        'location_search_found': "Trouvé (Nominatim) : {}",
        'location_search_found_fallback': "Trouvé via fallback (ArcGIS) : {}",
        'location_search_found_fallback2': "Trouvé via 2e fallback (Photon) : {}",
        'location_search_coords': "Lat : {:.4f}, Lon : {:.4f}",
        'location_search_error_not_found': "Lieu non trouvé.",
        'location_search_error_service': "Erreur du service de géocodage : {}",
        'location_search_error_timeout': "Délai d'attente du service de géocodage dépassé.",
        'location_search_error_refused': "Connexion de géocodage refusée.",
        'location_search_info_fallback': "Échec de Nominatim, tentative de service de secours (ArcGIS)...",
        'location_search_info_fallback2': "Échec d'ArcGIS, tentative de 2e service de secours (Photon)...",
        'location_search_error_fallback_failed': "Échec du service primaire (Nominatim) et de secours (ArcGIS) : {}",
        'location_search_error_fallback2_failed': "Échec de tous les services de géocodage (Nominatim, ArcGIS, Photon) : {}",
        'location_lat_label': "Latitude (°N)",
        'location_lon_label': "Longitude (°E)",
        'location_elev_label': "Altitude (mètres)",
        'location_manual_display': "Manuel ({:.4f}, {:.4f})",
        'location_search_display': "Recherché : {} ({:.4f}, {:.4f})",
        'location_error': "Erreur d'emplacement : {}",
        'location_error_fallback': "ERREUR - Utilisation du fallback",
        'location_error_manual_none': "Les champs d'emplacement manuel ne peuvent pas être vides ou invalides.",
        'time_expander': "⏱️ Heure & Fuseau horaire",
        'time_select_label': "Choisir l'heure",
        'time_option_now': "Maintenant (nuit prochaine)",
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
        'mag_filter_bortle_help': "Obscurité du ciel : 1=Excellent ciel noir, 9=Ciel de centre-ville",
        'mag_filter_min_mag_label': "Magnitude Min. :",
        'mag_filter_min_mag_help': "Magnitude de l'objet le plus brillant à inclure",
        'mag_filter_max_mag_label': "Magnitude Max. :",
        'mag_filter_max_mag_help': "Magnitude de l'objet le plus faible à inclure",
        'mag_filter_warning_min_max': "Magnitude Min. est supérieure à la Magnitude Max. !",
        'min_alt_header': "**Altitude de l'objet au-dessus de l'horizon**",
        'min_alt_label': "Altitude Min. de l'objet (°) :",
        'max_alt_label': "Altitude Max. de l'objet (°) :",
        'moon_warning_header': "**Avertissement Lunaire**",
        'moon_warning_label': "Avertir si Lune > (% Illumination) :",
        'object_types_header': "**Types d'objets**",
        'object_types_error_extract': "Impossible d'extraire les types d'objets du catalogue.",
        'object_types_label': "Filtrer les types (laisser vide pour tous) :",
        'size_filter_header': "**Filtre de Taille Angulaire**",
        'size_filter_label': "Taille de l'objet (minutes d'arc) :",
        'size_filter_help': "Filtrer les objets par leur taille apparente (axe majeur). 1 minute d'arc = 1/60 degré.",
        'direction_filter_header': "**Filtre par Direction Cardinale**",
        'direction_filter_label': "Afficher les objets culminant vers :",
        'direction_option_all': "Toutes",
        'object_type_glossary_title': "Glossaire des types d'objets", # Bereits vorhanden
        'object_type_glossary': {
            "OCl": "Amas Ouvert", "GCl": "Amas Globulaire", "Cl+N": "Amas + Nébuleuse",
            "Gal": "Galaxie", "PN": "Nébuleuse Planétaire", "SNR": "Rémanent de Supernova",
            "Neb": "Nébuleuse (général)", "EmN": "Nébuleuse en Émission", "RfN": "Nébuleuse par Réflexion",
            "HII": "Région HII", "AGN": "Noyau Actif de Galaxie"
        },
        'results_options_expander': "⚙️ Options de Résultats",
        'results_options_max_objects_label': "Nombre max. d'objets à afficher :",
        'results_options_sort_method_label': "Trier les résultats par :",
        'results_options_sort_duration': "Durée & Altitude",
        'results_options_sort_magnitude': "Luminosité",
        'moon_metric_label': "Illumination lunaire (env.)",
        'moon_warning_message': "Attention : La Lune est plus brillante ({:.0f}%) que le seuil ({:.0f}%) !",
        'moon_phase_error': "Erreur lors du calcul de la phase lunaire : {}",
        'find_button_label': "🔭 Trouver les objets observables",
        'search_params_header': "Paramètres de recherche",
        'search_params_location': "📍 Emplacement : {}",
        'search_params_time': "⏱️ Heure : {}",
        'search_params_timezone': "🌍 Fuseau horaire : {}",
        'search_params_time_now': "Nuit prochaine (à partir de {} UTC)",
        'search_params_time_specific': "Nuit après {}",
        'search_params_filter_mag': "✨ Filtre : {}",
        'search_params_filter_mag_bortle': "Bortle {} (<= {:.1f} mag)",
        'search_params_filter_mag_manual': "Manuel ({:.1f}-{:.1f} mag)",
        'search_params_filter_alt_types': "🔭 Filtre : Alt {}-{}°, Types : {}",
        'search_params_filter_size': "📐 Filtre : Taille {:.1f} - {:.1f} arcmin",
        'search_params_filter_direction': "🧭 Filtre : Direction à l'apogée : {}",
        'search_params_types_all': "Tous",
        'search_params_direction_all': "Toutes",
        'spinner_searching': "Calcul de la fenêtre & recherche d'objets...",
        'spinner_geocoding': "Recherche de l'emplacement...",
        'window_info_template': "Fenêtre d'observation : {} à {} UTC (Crépuscule Astronomique)",
        'window_already_passed': "La fenêtre nocturne calculée pour 'Maintenant' est déjà passée. Calcul pour la nuit suivante.",
        'error_no_window': "Aucune fenêtre de noirceur astronomique valide trouvée pour la date et l'emplacement sélectionnés.",
        'error_polar_night': "La noirceur astronomique dure >24h (Nuit polaire ?). Fenêtre de secours utilisée.",
        'error_polar_day': "Aucune noirceur astronomique ne se produit (Jour polaire ?). Fenêtre de secours utilisée.",
        'success_objects_found': "{} objets correspondants trouvés.",
        'info_showing_list_duration': "Affichage de {} objets, triés par durée de visibilité et altitude de culmination :",
        'info_showing_list_magnitude': "Affichage de {} objets, triés par luminosité (le plus brillant en premier) :",
        'error_search_unexpected': "Une erreur inattendue s'est produite lors de la recherche :",
        'results_list_header': "Liste des résultats",
        'results_export_name': "Nom",
        'results_export_type': "Type",
        'results_export_constellation': "Constellation",
        'results_export_mag': "Magnitude",
        'results_export_size': "Taille (arcmin)",
        'results_export_ra': "AD", # Ascension Droite
        'results_export_dec': "Dec", # Déclinaison
        'results_export_max_alt': "Altitude Max (°)",
        'results_export_az_at_max': "Azimut à l'apogée (°)",
        'results_export_direction_at_max': "Direction à l'apogée",
        'results_export_time_max_utc': "Heure à l'apogée (UTC)",
        'results_export_time_max_local': "Heure à l'apogée (Fuseau local)",
        'results_export_cont_duration': "Durée cont. max (h)",
        'results_expander_title': "{} ({}) - Mag : {:.1f}",
        'google_link_text': "Google",
        'simbad_link_text': "SIMBAD",
        'results_coords_header': "**Détails :**",
        'results_constellation_label': "Constellation :",
        'results_size_label': "Taille (axe majeur) :",
        'results_size_value': "{:.1f} arcmin",
        'results_max_alt_header': "**Altitude Max. :**",
        'results_azimuth_label': "(Azimut : {:.1f}°{})",
        'results_direction_label': ", Direction : {}",
        'results_best_time_header': "**Meilleure heure (Fuseau local) :**",
        'results_cont_duration_header': "**Durée cont. max :**",
        'results_duration_value': "{:.1f} heures",
        'graph_type_label': "Type de graphique (pour tous) :",
        'graph_type_sky_path': "Trajectoire céleste (Az/Alt)",
        'graph_type_alt_time': "Courbe d'altitude (Alt/Temps)",
        'results_graph_button': "📈 Afficher le graphique",
        'results_spinner_plotting': "Création du graphique...",
        'results_graph_error': "Erreur de graphique : {}",
        'results_graph_not_created': "Le graphique n'a pas pu être créé.",
        'results_close_graph_button': "Fermer le graphique",
        'results_save_csv_button': "💾 Enregistrer la liste en CSV",
        'results_csv_filename': "liste_observation_dso_{}.csv",
        'results_csv_export_error': "Erreur d'exportation CSV : {}",
        'warning_no_objects_found': "Aucun objet trouvé correspondant à tous les critères pour la fenêtre d'observation calculée.",
        'info_initial_prompt': "Bienvenue ! Veuillez **saisir les coordonnées** ou **rechercher un lieu** pour activer la recherche d'objets.",
        'graph_altitude_label': "Altitude (°)",
        'graph_azimuth_label': "Azimut (°)",
        'graph_min_altitude_label': "Altitude minimale ({:.0f}°)",
        'graph_max_altitude_label': "Altitude maximale ({:.0f}°)",
        'graph_title_sky_path': "Trajectoire céleste pour {}",
        'graph_title_alt_time': "Courbe d'altitude pour {}",
        'graph_ylabel': "Altitude (°)",
        'custom_target_expander': "Tracer une cible personnalisée",
        'custom_target_ra_label': "Ascension droite (AD) :",
        'custom_target_dec_label': "Déclinaison (Dec) :",
        'custom_target_name_label': "Nom de la cible (Optionnel) :",
        'custom_target_ra_placeholder': "p.ex. 10:45:03.6 ou 161.265",
        'custom_target_dec_placeholder': "p.ex. -16:42:58 ou -16.716",
        'custom_target_button': "Créer un graphique personnalisé",
        'custom_target_error_coords': "Format AD/Dec invalide. Utilisez HH:MM:SS.s / DD:MM:SS ou degrés décimaux.",
        'custom_target_error_window': "Impossible de créer le graphique. Assurez-vous que l'emplacement et la fenêtre temporelle sont valides (essayez d'abord de cliquer sur 'Trouver les objets observables').",
        'error_processing_object': "Erreur lors du traitement de {}: {}",
        'window_calc_error': "Erreur lors du calcul de la fenêtre d'observation : {}\n{}",
        'window_fallback_info': "\nFenêtre de secours utilisée : {} à {} UTC",
        'error_loading_catalog': "Erreur lors du chargement du fichier catalogue : {}",
        'warning_catalog_empty': "Fichier catalogue chargé, mais aucun objet correspondant trouvé après filtrage.",
        'donation_text': "Vous aimez l'application ? [Soutenez le développement sur Ko-fi ☕](https://ko-fi.com/advanceddsofinder)", # Bereits vorhanden
        'bug_report_button': "🐞 Signaler un bug", # Bereits vorhanden
        'bug_report_body': "\n\n(Veuillez décrire le bug et les étapes pour le reproduire)", # Bereits vorhanden
    },
}


# --- Initialize TimezoneFinder (cached) ---
@st.cache_resource
def get_timezone_finder():
    """Initializes and returns a TimezoneFinder instance."""
    if TimezoneFinder:
        try:
            # Initialize TimezoneFinder, loading data into memory
            return TimezoneFinder(in_memory=True)
        except Exception as e:
            # Log and warn if initialization fails
            print(f"Error initializing TimezoneFinder: {e}")
            st.warning(f"TimezoneFinder init failed: {e}. Automatic timezone detection disabled.")
            return None
    return None

# Get the TimezoneFinder instance
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
        'location_is_valid_for_run': False, # FIX: Added location validity state
        'time_choice_exp': 'Now',           # FIX: Initialize time_choice_exp
        'window_start_time': None,          # FIX: Initialize window times
        'window_end_time': None,            # FIX: Initialize window times
        'selected_date_widget': date.today()# FIX: Initialize selected date for date_input
    }
    # Set default values in session state if keys don't exist
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# --- Helper Functions ---
def get_magnitude_limit(bortle_scale: int) -> float:
    """Calculates the approximate limiting magnitude based on Bortle scale."""
    # These limits are approximate and can vary.
    limits = {1: 15.5, 2: 15.5, 3: 14.5, 4: 14.5, 5: 13.5, 6: 12.5, 7: 11.5, 8: 10.5, 9: 9.5}
    return limits.get(bortle_scale, 9.5) # Default to Bortle 9 if scale is invalid

def azimuth_to_direction(azimuth_deg: float) -> str:
    """Converts an azimuth angle (degrees) to a cardinal direction string."""
    if math.isnan(azimuth_deg):
        return "N/A" # Handle potential NaN input
    azimuth_deg = azimuth_deg % 360 # Normalize to 0-360
    # Calculate the index in the CARDINAL_DIRECTIONS list
    # Each direction covers 45 degrees (360 / 8 = 45)
    # We add 22.5 degrees (half of 45) to center the bins, then divide by 45
    index = round((azimuth_deg + 22.5) / 45) % 8
    # Ensure index stays within bounds (although % 8 should handle it)
    index = max(0, min(index, len(CARDINAL_DIRECTIONS) - 1))
    return CARDINAL_DIRECTIONS[index]

# --- Moon Phase SVG (Corrected) ---
def create_moon_phase_svg(illumination: float, size: int = 100) -> str:
    """
    Creates an SVG representation of the moon phase (corrected).

    Args:
        illumination (float): Moon illumination fraction (0=new, 0.5=half, 1=full).
        size (int): Size of the SVG image in pixels.

    Returns:
        str: SVG string representing the moon phase.
    """
    # Validate and clamp illumination value
    if not 0 <= illumination <= 1:
        print(f"Warning: Invalid moon illumination value ({illumination}). Clamping to [0, 1].")
        illumination = max(0.0, min(1.0, illumination))

    radius = size / 2
    cx = cy = radius
    # Use CSS variables for theme compatibility (fallback provided)
    light_color = "var(--text-color, #e0e0e0)" # Use text color for light part
    dark_color = "var(--secondary-background-color, #333333)" # Use secondary bg for dark part

    svg = f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'

    # Draw the background (always the dark side color)
    svg += f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{dark_color}"/>'

    if illumination < 0.01: # New moon - only dark circle needed
        pass
    elif illumination > 0.99: # Full moon - draw full light circle on top
        svg += f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{light_color}"/>'
    else:
        # Calculate the horizontal position of the terminator's center relative to the moon's center
        # x varies from -radius (new moon side) to +radius (full moon side)
        x_terminator_center = radius * (illumination * 2 - 1)

        # Calculate the semi-major axis of the ellipse forming the terminator
        rx_terminator = abs(x_terminator_center)

        # Determine sweep flags for the arcs
        # Sweep flag 1 means "clockwise" or "positive angle" direction
        # Large arc flag 1 means take the longer path between two points

        # We draw the illuminated portion
        if illumination <= 0.5: # Crescent phase (less than half illuminated)
            # Illuminated part is on the right (assuming waxing for simplicity)
            # Path: Move to top, elliptical arc down (terminator), circular arc up (limb)
            large_arc_flag_ellipse = 0
            sweep_flag_ellipse = 1
            large_arc_flag_circle = 0
            sweep_flag_circle = 1
            d = (f"M {cx},{cy - radius} " # Move to top of circle
                 f"A {rx_terminator},{radius} 0 {large_arc_flag_ellipse},{sweep_flag_ellipse} {cx},{cy + radius} " # Elliptical arc for terminator
                 f"A {radius},{radius} 0 {large_arc_flag_circle},{sweep_flag_circle} {cx},{cy - radius} " # Circular arc for limb
                 "Z")
        else: # Gibbous phase (more than half illuminated)
            # Illuminated part includes the left half circle plus an ellipse on the right
            # Path: Move to top, circular arc down (left limb), elliptical arc up (terminator)
            large_arc_flag_circle = 1 # Take the long way around the circle limb
            sweep_flag_circle = 1
            large_arc_flag_ellipse = 1
            sweep_flag_ellipse = 1
            d = (f"M {cx},{cy - radius} " # Move to top of circle
                 f"A {radius},{radius} 0 {large_arc_flag_circle},{sweep_flag_circle} {cx},{cy + radius} " # Circular arc for left limb
                 f"A {rx_terminator},{radius} 0 {large_arc_flag_ellipse},{sweep_flag_ellipse} {cx},{cy - radius} " # Elliptical arc for terminator
                 "Z")

        svg += f'<path d="{d}" fill="{light_color}"/>'

    svg += '</svg>'
    return svg


def load_ongc_data(catalog_path: str, lang: str) -> pd.DataFrame | None:
    """Loads, filters, and preprocesses data from the OpenNGC CSV file."""
    t_load = translations.get(lang, translations['en']) # Fallback to English if lang not found
    required_cols = ['Name', 'RA', 'Dec', 'Type']
    mag_cols = ['V-Mag', 'B-Mag', 'Mag'] # Prioritize V-Mag, then B-Mag, then generic Mag
    size_col = 'MajAx' # Major Axis for size

    try:
        # Check if the catalog file exists
        if not os.path.exists(catalog_path):
             # Use the 'error_loading_catalog' key which is now guaranteed to exist
             st.error(f"{t_load['error_loading_catalog'].split(':')[0]}: File not found at {catalog_path}")
             st.info(f"Please ensure the file '{CATALOG_FILENAME}' is in the directory: {APP_DIR}")
             return None

        # Read the CSV file
        df = pd.read_csv(catalog_path, sep=';', comment='#', low_memory=False)

        # --- Data Cleaning and Validation ---

        # Check essential columns first
        missing_req_cols = [col for col in required_cols if col not in df.columns]
        if missing_req_cols:
            st.error(f"Missing required columns in catalog '{os.path.basename(catalog_path)}': {', '.join(missing_req_cols)}")
            return None

        # --- Process Coordinates (Strings) ---
        # Keep RA/Dec as strings for SkyCoord parsing later, handle potential NaN/empty strings
        df['RA_str'] = df['RA'].astype(str).str.strip()
        df['Dec_str'] = df['Dec'].astype(str).str.strip()
        df.dropna(subset=['RA_str', 'Dec_str'], inplace=True)
        df = df[df['RA_str'] != '']
        df = df[df['Dec_str'] != '']
        # Further validation could be added here if needed (e.g., regex for expected format)

        # --- Process Magnitude ---
        # Find the best available magnitude column
        mag_col_found = None
        for col in mag_cols:
            if col in df.columns:
                # Check if the column has *any* non-null numeric values
                numeric_mags = pd.to_numeric(df[col], errors='coerce')
                if numeric_mags.notna().any():
                    mag_col_found = col
                    print(f"Using magnitude column: {mag_col_found}")
                    break # Use the first valid one found in the preferred order

        if mag_col_found is None:
            st.error(f"No usable magnitude column ({', '.join(mag_cols)}) found with valid numeric data in catalog.")
            return None

        # Rename the chosen column to 'Mag' and convert to numeric, coercing errors
        df['Mag'] = pd.to_numeric(df[mag_col_found], errors='coerce')
        # Drop rows where magnitude conversion failed
        df.dropna(subset=['Mag'], inplace=True)

        # --- Process Size Column ---
        if size_col not in df.columns:
            st.warning(f"Size column '{size_col}' not found in catalog. Angular size filtering will be disabled.")
            df[size_col] = np.nan # Add the column with NaN values
        else:
            df[size_col] = pd.to_numeric(df[size_col], errors='coerce')
            # Keep rows with invalid size for now, filter later if size filter is active
            # Check if any valid size data exists at all after conversion
            if not df[size_col].notna().any():
                st.warning(f"No valid numeric data found in size column '{size_col}' after cleaning. Size filter disabled.")
                df[size_col] = np.nan # Ensure column exists but is all NaN if no valid data

        # --- Filter by Object Type (using a more robust list) ---
        # Define common DSO type identifiers from ONGC documentation/common usage
        dso_type_identifiers = [
            "Gal", "Gxy", "AGN", # Galaxy types
            "OC", "OCl", "MWSC", # Open Cluster types
            "GC", "GCl", # Globular Cluster types
            "PN", # Planetary Nebula
            "SNR", # Supernova Remnant
            "Neb", "EmN", "RfN", "HII", # Nebula types (general, emission, reflection, HII region)
            "C+N", # Cluster + Nebula
            "Ast", # Asterism (sometimes included, debatable if DSO)
            "Kt", "Str", # Star related (usually excluded, but might be in some catalogs)
            "Dup", # Duplicate entry marker
            "?", # Unknown/Uncertain type
            # Add more specific types if needed based on catalog variations
        ]
        # Create a regex pattern to match any of these identifiers at the start of the 'Type' string
        # Using word boundaries (\b) might be safer if types can be combined like 'GalAGN'
        # type_pattern = r'\b(' + '|'.join(dso_type_identifiers) + r')\b'
        # Simpler approach: Check if the type string *contains* any known valid DSO type abbreviation
        # Be careful, "Neb" is substring of "Planetary Nebula" (PN) - order might matter or use stricter matching
        # Let's stick to the provided list for now, assuming it covers the main DSO categories well enough
        dso_types_provided = ['Galaxy', 'Globular Cluster', 'Open Cluster', 'Nebula',
                              'Planetary Nebula', 'Supernova Remnant', 'HII', 'Emission Nebula',
                              'Reflection Nebula', 'Cluster + Nebula', 'Gal', 'GCl', 'Gx', 'OC',
                              'PN', 'SNR', 'Neb', 'EmN', 'RfN', 'C+N', 'Gxy', 'AGN', 'MWSC', 'OCl']
        type_pattern = '|'.join(dso_types_provided) # Case-insensitive match

        if 'Type' in df.columns:
            # Ensure 'Type' is string, handle potential NaNs before filtering
            df_filtered = df[df['Type'].astype(str).str.contains(type_pattern, case=False, na=False)].copy()
        else:
            # This case should be caught by the initial required_cols check, but double-check
            st.error("Catalog is missing the required 'Type' column.")
            return None

        # --- Select Final Columns ---
        # Do NOT include 'Constellation' here, it's calculated on the fly
        final_cols = ['Name', 'RA_str', 'Dec_str', 'Mag', 'Type', size_col]
        # Ensure all final columns actually exist in the filtered dataframe (size_col might be added)
        final_cols_exist = [col for col in final_cols if col in df_filtered.columns]
        df_final = df_filtered[final_cols_exist].copy()

        # --- Final Cleanup ---
        # Drop duplicate objects based on Name, keeping the first occurrence
        df_final.drop_duplicates(subset=['Name'], inplace=True, keep='first')
        # Reset index after filtering and dropping duplicates
        df_final.reset_index(drop=True, inplace=True)

        if not df_final.empty:
            print(f"Catalog loaded and processed: {len(df_final)} objects.")
            # st.success(t_load['info_catalog_loaded'].format(len(df_final))) # Moved to sidebar
            return df_final
        else:
            st.warning(t_load['warning_catalog_empty'])
            return None

    except FileNotFoundError:
        # This specific handler might not be strictly needed anymore if os.path.exists catches it,
        # but it's safe to leave it. It will now use the correct translation key.
        st.error(f"{t_load['error_loading_catalog'].split(':')[0]}: File not found at {catalog_path}")
        st.info(f"Please ensure the file '{CATALOG_FILENAME}' is in the directory: {APP_DIR}")
        return None
    except pd.errors.ParserError as e:
        st.error(f"Error parsing catalog file '{os.path.basename(catalog_path)}': {e}")
        st.info("Please ensure the file is a valid CSV with ';' separator.")
        return None
    except Exception as e:
        # Use the 'error_loading_catalog' key which is now guaranteed to exist
        st.error(f"{t_load['error_loading_catalog']}: An unexpected error occurred: {e}")
        traceback.print_exc() # Print full traceback to console for debugging
        return None


# --- Fallback Window ---
def _get_fallback_window(reference_time: Time) -> tuple[Time, Time]:
    """
    Provides a simple fallback observation window (e.g., 6 PM to 6 AM UTC).
    """
    # Get the date part of the reference time
    ref_dt_utc = reference_time.to_datetime(timezone.utc)
    ref_date = ref_dt_utc.date()

    # Define fallback start and end times (e.g., 18:00 UTC to 06:00 UTC next day)
    fallback_start_dt = datetime.combine(ref_date, time(18, 0), tzinfo=timezone.utc)
    fallback_end_dt = datetime.combine(ref_date + timedelta(days=1), time(6, 0), tzinfo=timezone.utc)

    # Convert back to Astropy Time objects
    fallback_start_time = Time(fallback_start_dt, scale='utc')
    fallback_end_time = Time(fallback_end_dt, scale='utc')

    print(f"Using fallback window: {fallback_start_time.iso} to {fallback_end_time.iso}")
    return fallback_start_time, fallback_end_time

# --- Observation Window Calculation ---
def get_observable_window(observer: Observer, reference_time: Time, is_now: bool, lang: str) -> tuple[Time | None, Time | None, str]:
    """
    Calculates the astronomical darkness window for observation.

    Args:
        observer: The astroplan Observer object.
        reference_time: The reference time for calculation (Time object).
        is_now: Boolean indicating if "Now" was selected (affects window start).
        lang: Language code for translations.

    Returns:
        A tuple containing:
            - start_time: Astropy Time object for window start (or None).
            - end_time: Astropy Time object for window end (or None).
            - status_message: String describing the window or errors.
    """
    t = translations.get(lang, translations['en']) # Fallback language
    status_message = ""
    start_time, end_time = None, None # Initialize here
    current_utc_time = Time.now() # Get current UTC time

    # Determine the calculation base time (noon UTC of the target night)
    calc_base_time = reference_time
    if is_now:
        current_dt_utc = current_utc_time.to_datetime(timezone.utc)
        noon_today_utc = datetime.combine(current_dt_utc.date(), time(12, 0), tzinfo=timezone.utc)
        # Base calculation on previous noon if it's before noon today
        if current_dt_utc < noon_today_utc:
            calc_base_time = Time(noon_today_utc - timedelta(days=1))
        else:
            calc_base_time = Time(noon_today_utc)
        print(f"Calculating 'Now' window based on UTC noon: {calc_base_time.iso}")
    else:
        # For specific date, use noon UTC of that date
        selected_date_noon_utc = datetime.combine(reference_time.to_datetime(timezone.utc).date(), time(12, 0), tzinfo=timezone.utc)
        calc_base_time = Time(selected_date_noon_utc, scale='utc')
        print(f"Calculating specific night window based on UTC noon: {calc_base_time.iso}")


    try:
        # Validate observer input type
        if not isinstance(observer, Observer):
            raise TypeError(f"Internal Error: Expected astroplan.Observer, got {type(observer)}")

        # Calculate astronomical twilight times
        astro_set = observer.twilight_evening_astronomical(calc_base_time, which='next')
        astro_rise = observer.twilight_morning_astronomical(astro_set if astro_set else calc_base_time, which='next')

        # Check if twilight times are valid
        if astro_set is None or astro_rise is None:
            raise ValueError("Could not determine one or both astronomical twilight times.")
        if astro_rise <= astro_set:
            # This case can happen near poles or if twilight persists > 24h
            # Check if it's likely polar night/day before raising generic error
            try:
                # Check sun altitude at reference time and 12 hours later
                sun_alt_ref = observer.sun_altaz(calc_base_time).alt
                sun_alt_12h_later = observer.sun_altaz(calc_base_time + 12*u.hour).alt
                if sun_alt_ref < -18*u.deg and sun_alt_12h_later < -18*u.deg:
                    # Likely polar night
                    status_message = t.get('error_polar_night', "Astronomical darkness lasts >24h (Polar night?). Using fallback window.")
                    start_time, end_time = _get_fallback_window(calc_base_time)
                    status_message += t.get('window_fallback_info', "\nUsing fallback window: {} to {} UTC").format(start_time.iso, end_time.iso)
                    return start_time, end_time, status_message
                elif sun_alt_ref > -18*u.deg: # Check polar day more thoroughly
                    # Check sun altitude over a 24-hour period
                    times_check = calc_base_time + np.linspace(0, 24, 49)*u.hour
                    sun_alts_check = observer.sun_altaz(times_check).alt
                    if np.min(sun_alts_check) > -18*u.deg:
                        # Likely polar day
                        status_message = t.get('error_polar_day', "No astronomical darkness occurs (Polar day?). Using fallback window.")
                        start_time, end_time = _get_fallback_window(calc_base_time)
                        status_message += t.get('window_fallback_info', "\nUsing fallback window: {} to {} UTC").format(start_time.iso, end_time.iso)
                        return start_time, end_time, status_message
            except Exception as check_e:
                print(f"Error during polar check: {check_e}")
            # If not clearly polar night/day, raise the original error
            raise ValueError("Calculated morning twilight is not after evening twilight.")


        start_time = astro_set
        end_time = astro_rise

        # Adjust window if 'Now' is selected and current time is within or after the calculated window
        if is_now:
            if end_time < current_utc_time:
                # Window has already passed, calculate for the next night
                status_message = t.get('window_already_passed', "Calculated night window for 'Now' has already passed. Calculating for next night.") + "\n"
                next_noon_utc = datetime.combine(current_utc_time.to_datetime(timezone.utc).date() + timedelta(days=1), time(12, 0), tzinfo=timezone.utc)
                astro_set_next = observer.twilight_evening_astronomical(Time(next_noon_utc), which='next')
                astro_rise_next = observer.twilight_morning_astronomical(astro_set_next if astro_set_next else Time(next_noon_utc), which='next')

                if astro_set_next is None or astro_rise_next is None or astro_rise_next <= astro_set_next:
                    raise ValueError("Could not determine valid twilight times for the *next* night.")

                start_time = astro_set_next
                end_time = astro_rise_next

            elif start_time < current_utc_time:
                # Window is ongoing, adjust start time to now
                print(f"Adjusting window start from {start_time.iso} to current time {current_utc_time.iso}")
                start_time = current_utc_time

        # Format window times for display
        start_fmt = start_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')
        end_fmt = end_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')
        status_message += t.get('window_info_template', "Observation window: {} to {} UTC (Astronomical Twilight)").format(start_fmt, end_fmt)

    except ValueError as ve:
        # Handle specific ValueErrors from astroplan (e.g., twilight calculation issues)
        error_detail = f"{ve}"
        print(f"Astroplan ValueError calculating window: {error_detail}")
        # Check for polar conditions if not already handled
        if 'polar' not in status_message: # Avoid double messages if already caught above
            try:
                sun_alt_ref = observer.sun_altaz(calc_base_time).alt
                sun_alt_12h_later = observer.sun_altaz(calc_base_time + 12*u.hour).alt

                if sun_alt_ref < -18*u.deg and sun_alt_12h_later < -18*u.deg:
                    status_message = t.get('error_polar_night', "Astronomical darkness lasts >24h (Polar night?). Using fallback window.")
                elif sun_alt_ref > -18*u.deg:
                    times_check = calc_base_time + np.linspace(0, 24, 49)*u.hour
                    sun_alts_check = observer.sun_altaz(times_check).alt
                    if np.min(sun_alts_check) > -18*u.deg:
                        status_message = t.get('error_polar_day', "No astronomical darkness occurs (Polar day?). Using fallback window.")
                    else: # Normal error if twilight calculation failed but it's not polar day/night
                        status_message = t.get('window_calc_error', "Error calculating observation window: {}\n{}").format(error_detail, " (Check location/time)")
                else: # Normal error if twilight calculation failed
                    status_message = t.get('window_calc_error', "Error calculating observation window: {}\n{}").format(error_detail, traceback.format_exc())
            except Exception as check_e:
                print(f"Error checking sun altitude for polar conditions: {check_e}")
                status_message = t.get('window_calc_error', "Error calculating observation window: {}\n{}").format(error_detail, traceback.format_exc())
        # Apply fallback window
        start_time, end_time = _get_fallback_window(calc_base_time)
        status_message += t.get('window_fallback_info', "\nUsing fallback window: {} to {} UTC").format(start_time.iso, end_time.iso)


    except Exception as e:
        # Handle unexpected errors during window calculation
        status_message = t.get('window_calc_error', "Error calculating observation window: {}\n{}").format(e, traceback.format_exc())
        print(f"Unexpected error calculating window: {e}")
        start_time, end_time = _get_fallback_window(calc_base_time)
        status_message += t.get('window_fallback_info', "\nUsing fallback window: {} to {} UTC").format(start_time.iso, end_time.iso)

    # Final check and fallback if times are still invalid
    if start_time is None or end_time is None or end_time <= start_time:
        if not status_message or "Error" not in status_message and "Fallback" not in status_message:
             status_message += ("\n" if status_message else "") + t.get('error_no_window', "No valid astronomical darkness window found for the selected date and location.")

        start_time_fb, end_time_fb = _get_fallback_window(calc_base_time)
        # Only add fallback info if it wasn't already added
        if t.get('window_fallback_info', "\nUsing fallback window: {} to {} UTC").format(start_time_fb.iso, end_time_fb.iso) not in status_message:
             status_message += t.get('window_fallback_info', "\nUsing fallback window: {} to {} UTC").format(start_time_fb.iso, end_time_fb.iso)
        start_time, end_time = start_time_fb, end_time_fb


    return start_time, end_time, status_message


# --- Object Finding Logic ---
def find_observable_objects(observer_location: EarthLocation,
                            observing_times: Time,
                            min_altitude_limit: u.Quantity,
                            catalog_df: pd.DataFrame,
                            lang: str) -> list[dict]:
    """
    Finds Deep Sky Objects from the catalog that are observable
    above a minimum altitude for the given observer and times.
    Note: Max altitude filtering is done *after* this function in main().

    Args:
        observer_location: The observer's location (EarthLocation).
        observing_times: Times at which to check object visibility (Time array).
        min_altitude_limit: Minimum altitude for an object to be considered observable.
        catalog_df: DataFrame containing the DSO catalog data.
        lang: The user's language ('de', 'en', 'fr').

    Returns:
        A list of dictionaries, where each dictionary represents an observable DSO.
        Returns empty list if no objects are found or errors occur.
    """
    t = translations.get(lang, translations['en']) # Fallback language
    observable_objects = []

    # --- Input Validation ---
    if not isinstance(observer_location, EarthLocation):
        st.error(f"Internal Error: observer_location must be an astropy EarthLocation. Got {type(observer_location)}")
        return []
    if not isinstance(observing_times, Time) or not observing_times.shape: # Check if it's a valid Time array
        st.error(f"Internal Error: observing_times must be a non-empty astropy Time array. Got {type(observing_times)}")
        return []
    if not isinstance(min_altitude_limit, u.Quantity) or not min_altitude_limit.unit.is_equivalent(u.deg):
        st.error(f"Internal Error: min_altitude_limit must be an astropy Quantity in angular units. Got {type(min_altitude_limit)}")
        return []
    if not isinstance(catalog_df, pd.DataFrame):
        st.error(f"Internal Error: catalog_df must be a pandas DataFrame. Got {type(catalog_df)}")
        return []
    if catalog_df.empty:
        print("Input catalog_df is empty. No objects to process.")
        return []
    if len(observing_times) < 2:
        st.warning("Observing window has less than 2 time points. Duration calculation might be inaccurate.")


    # Pre-calculate AltAz frame for efficiency
    altaz_frame = AltAz(obstime=observing_times, location=observer_location)
    min_alt_deg = min_altitude_limit.to(u.deg).value
    time_step_hours = 0 # Initialize outside loop
    if len(observing_times) > 1:
        time_diff_seconds = (observing_times[1] - observing_times[0]).sec
        time_step_hours = time_diff_seconds / 3600.0


    # --- Iterate through Catalog Objects ---
    for index, obj in catalog_df.iterrows():
        try:
            # --- Get Object Data ---
            ra_str = obj.get('RA_str', None)
            dec_str = obj.get('Dec_str', None)
            dso_name = obj.get('Name', f"Unnamed Object {index}")
            obj_type = obj.get('Type', "Unknown")
            obj_mag = obj.get('Mag', np.nan)
            obj_size = obj.get('MajAx', np.nan)

            if not ra_str or not dec_str:
                print(f"Skipping object '{dso_name}': Missing RA or Dec string.")
                continue

            # --- Handle Coordinates ---
            try:
                dso_coord = SkyCoord(ra=ra_str, dec=dec_str, unit=(u.hourangle, u.deg))
            except ValueError as coord_err:
                print(f"Skipping object '{dso_name}': Invalid coordinate format ('{ra_str}', '{dec_str}'). Error: {coord_err}")
                continue

            # --- Calculate Alt/Az ---
            # Add extra check for potential coordinate transformation errors
            try:
                dso_altazs = dso_coord.transform_to(altaz_frame)
                dso_alts = dso_altazs.alt.to(u.deg).value
                dso_azs = dso_altazs.az.to(u.deg).value
            except Exception as transform_err:
                print(f"Skipping object '{dso_name}': Error transforming coordinates. Error: {transform_err}")
                continue

            # --- Check if Observable (Reaches Minimum Altitude) ---
            max_alt_this_object = np.max(dso_alts) if len(dso_alts) > 0 else -999 # Handle empty array case
            if max_alt_this_object >= min_alt_deg:
                # Object is potentially observable (reaches min alt)

                # --- Find Peak Altitude Details ---
                peak_alt_index = np.argmax(dso_alts)
                peak_alt = dso_alts[peak_alt_index]
                peak_time_utc = observing_times[peak_alt_index]
                peak_az = dso_azs[peak_alt_index]
                peak_direction = azimuth_to_direction(peak_az)

                # --- Get Constellation ---
                try:
                    constellation = get_constellation(dso_coord)
                except Exception as const_err:
                    print(f"Warning: Could not determine constellation for {dso_name}: {const_err}")
                    constellation = "N/A"

                # --- Calculate Continuous Duration Above Minimum Altitude ---
                above_min_alt = dso_alts >= min_alt_deg
                continuous_duration_hours = 0
                if time_step_hours > 0 and np.any(above_min_alt):
                    # Find contiguous blocks where above_min_alt is True
                    # Based on https://stackoverflow.com/a/4495197/1169513
                    runs = np.split(np.arange(len(above_min_alt)), np.where(np.diff(above_min_alt))[0]+1)
                    max_duration_indices = 0
                    for run in runs:
                        if run.size > 0 and above_min_alt[run[0]]: # Check if this run is 'True' and not empty
                            max_duration_indices = max(max_duration_indices, len(run))

                    # Duration is (number of steps - 1) * time_step, but since we count indices,
                    # len(run) directly gives the number of time points.
                    # For N points, there are N-1 intervals.
                    # However, counting points * step size gives a good approximation.
                    continuous_duration_hours = max_duration_indices * time_step_hours


                # --- Store Result (Max Altitude filter applied later) ---
                result_dict = {
                    'Name': dso_name,
                    'Type': obj_type,
                    'Constellation': constellation,
                    'Magnitude': obj_mag if not np.isnan(obj_mag) else None,
                    'Size (arcmin)': obj_size if not np.isnan(obj_size) else None,
                    'RA': ra_str,
                    'Dec': dec_str,
                    'Max Altitude (°)': peak_alt, # Store calculated peak altitude
                    'Azimuth at Max (°)': peak_az,
                    'Direction at Max': peak_direction,
                    'Time at Max (UTC)': peak_time_utc,
                    'Max Cont. Duration (h)': continuous_duration_hours,
                    'skycoord': dso_coord,
                    'altitudes': dso_alts,
                    'azimuths': dso_azs,
                    'times': observing_times
                }
                observable_objects.append(result_dict)

        except Exception as obj_proc_e:
            # Catch any other unexpected error during object processing
            error_msg = t.get('error_processing_object', "Error processing {}: {}").format(obj.get('Name', f'Object at index {index}'), obj_proc_e)
            print(error_msg)
            # traceback.print_exc() # Uncomment for detailed traceback during debugging

    return observable_objects

# --- Time Formatting ---
def get_local_time_str(utc_time: Time | None, timezone_str: str) -> tuple[str, str]:
    """
    Converts a UTC Time object to a localized time string, or returns "N/A".

    Args:
        utc_time: UTC time as an astropy Time object, or None.
        timezone_str: Timezone string (e.g., 'Europe/Zurich').

    Returns:
        A tuple containing the localized time string (e.g., '2023-12-24 22:15:30')
        and the timezone name, or ("N/A", "N/A") on error or if utc_time is None.
    """
    if utc_time is None:
        return "N/A", "N/A" # Handle None input gracefully

    if not isinstance(utc_time, Time):
        print(f"Error: utc_time must be an astropy Time object. Got {type(utc_time)}")
        return "N/A", "N/A"

    if not isinstance(timezone_str, str) or not timezone_str:
        print(f"Error: timezone_str must be a non-empty string. Got '{timezone_str}' ({type(timezone_str)})")
        return "N/A", "N/A"

    try:
        # Get the timezone object
        local_tz = pytz.timezone(timezone_str)
        # Convert astropy Time to datetime object with UTC timezone
        utc_dt = utc_time.to_datetime(timezone.utc)
        # Convert to the target local timezone
        local_dt = utc_dt.astimezone(local_tz)
        # Format the local time string
        local_time_str = local_dt.strftime('%Y-%m-%d %H:%M:%S')
        # Get the timezone abbreviation (e.g., CET, CEST)
        tz_display_name = local_dt.tzname()
        if not tz_display_name:
            tz_display_name = local_tz.zone # Fallback to full zone name if abbreviation fails
        return local_time_str, tz_display_name
    except pytz.exceptions.UnknownTimeZoneError:
        # Handle case where the timezone string is invalid
        print(f"Error: Unknown timezone '{timezone_str}'.")
        return utc_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), "UTC (TZ Error)"
    except Exception as e:
        # Handle any other conversion errors
        print(f"Error converting time to local timezone '{timezone_str}': {e}")
        traceback.print_exc()
        return utc_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), "UTC (Conv. Error)"


# --- Main App ---
def main():
    """Main function to run the Streamlit application."""

    # --- Initialize Session State ---
    initialize_session_state()

    # --- Get Current Language and Translations ---
    # This needs to run early to get 't' for the rest of the UI
    lang = st.session_state.language
    if lang not in translations:
        lang = 'de' # Default to German if invalid language in state
        st.session_state.language = lang
    t = translations[lang] # Get translation dictionary for the selected language

    # --- Load Catalog Data (Cached) ---
    @st.cache_data
    def cached_load_ongc_data(path, current_lang):
        """Cached function to load ONGC data."""
        print(f"Cache miss: Loading ONGC data from {path} for lang={current_lang}")
        # Pass the corrected lang value here too
        return load_ongc_data(path, current_lang)

    # Use the language determined *before* the sidebar widgets
    df_catalog_data = cached_load_ongc_data(CATALOG_FILEPATH, lang)

    # --- Custom CSS Styling (Removed hardcoded dark theme) ---
    # Streamlit's default theme handling will now apply.

    # --- Title ---
    st.title("Advanced DSO Finder")

    # --- Object Type Glossary ---
    with st.expander(t.get('object_type_glossary_title', "Object Type Glossary")): # Use .get() for safety
        glossary_items = t.get('object_type_glossary', {}) # Use .get for safety
        if glossary_items:
            col1, col2 = st.columns(2)
            col_index = 0
            sorted_items = sorted(glossary_items.items())
            # Display glossary items in two columns
            for abbr, full_name in sorted_items:
                if col_index % 2 == 0:
                    col1.markdown(f"**{abbr}:** {full_name}")
                else:
                    col2.markdown(f"**{abbr}:** {full_name}")
                col_index += 1
        else:
            st.info("Glossary not available for the selected language.")

    st.markdown("---")

    # --- Sidebar ---
    with st.sidebar:
        st.header(t.get('settings_header', "Settings")) # Use .get() for safety

        # Show catalog loaded message or error
        if 'catalog_status_msg' not in st.session_state:
            st.session_state.catalog_status_msg = "" # Initialize
        if df_catalog_data is not None:
            new_msg = t.get('info_catalog_loaded', "Catalog loaded: {} objects.").format(len(df_catalog_data))
            if st.session_state.catalog_status_msg != new_msg:
                st.success(new_msg)
                st.session_state.catalog_status_msg = new_msg
        else:
            new_msg = "Catalog loading failed. Check file or logs."
            if st.session_state.catalog_status_msg != new_msg:
                st.error(new_msg)
                st.session_state.catalog_status_msg = new_msg


        # --- Language Selector ---
        language_options = {'de': 'Deutsch', 'en': 'English', 'fr': 'Français'}
        lang_keys = list(language_options.keys())
        try:
            # Use the language already determined at the start of the script run
            current_lang_key_for_index = lang # lang variable already holds the correct current language
            if current_lang_key_for_index not in lang_keys:
                current_lang_key_for_index = 'de'
                st.session_state.language = current_lang_key_for_index # Ensure state matches if correction needed
            current_lang_index = lang_keys.index(current_lang_key_for_index)
        except ValueError:
            current_lang_index = 0
            st.session_state.language = lang_keys[0] # Default if something went wrong

        # Language selection radio buttons
        selected_lang_key = st.radio(
            t.get('language_select_label', "Language"), # Label uses 't' from this run
            options=lang_keys,
            format_func=lambda key: language_options[key],
            key='language_radio', # Specific key for the widget
            index=current_lang_index, # Sets the initial selection based on 'lang'
            horizontal=True
        )

        # Update language state and rerun if changed
        # This check happens *after* the widget is drawn
        if selected_lang_key != st.session_state.language:
            st.session_state.language = selected_lang_key
            st.session_state.location_search_status_msg = "" # Reset related state if needed
            # print(f"Sprache geändert zu: {selected_lang_key}, Rerun wird ausgelöst.") # Debug-Ausgabe (optional)
            st.rerun() # Force immediate rerun with the new language state


        # --- Location Settings ---
        with st.expander(t.get('location_expander', "📍 Location"), expanded=True):
            location_options_map = {
                'Search': t.get('location_option_search', "Search by Name"),
                'Manual': t.get('location_option_manual', "Enter Manually")
            }

            # Location method selection (Manual/Search)
            st.radio(
                t.get('location_select_label', "Select Location Method"),
                options=list(location_options_map.keys()),
                format_func=lambda key: location_options_map[key],
                key="location_choice_key", # Use session state key
                horizontal=True
            )

            lat_val, lon_val, height_val = None, None, None
            location_valid_for_tz = False
            current_location_valid = False # Flag to track if location is valid *in this run*

            # Manual Location Input
            if st.session_state.location_choice_key == "Manual":
                # Use session state keys for number inputs
                st.number_input(t.get('location_lat_label', "Latitude (°N)"), min_value=-90.0, max_value=90.0, step=0.01, format="%.4f", key="manual_lat_val")
                st.number_input(t.get('location_lon_label', "Longitude (°E)"), min_value=-180.0, max_value=180.0, step=0.01, format="%.4f", key="manual_lon_val")
                st.number_input(t.get('location_elev_label', "Elevation (meters)"), min_value=-500, step=10, format="%d", key="manual_height_val")

                # Read values from session state after widgets are drawn
                lat_val = st.session_state.manual_lat_val
                lon_val = st.session_state.manual_lon_val
                height_val = st.session_state.manual_height_val

                # Validate manual inputs
                if isinstance(lat_val, (int, float)) and isinstance(lon_val, (int, float)) and isinstance(height_val, (int, float)):
                    location_valid_for_tz = True
                    current_location_valid = True
                    # Update the persistent validity flag only if valid
                    st.session_state.location_is_valid_for_run = True
                    # Reset search-related state if switching to valid manual input
                    if st.session_state.location_search_success:
                        st.session_state.location_search_success = False
                        st.session_state.searched_location_name = None
                        st.session_state.location_search_status_msg = ""
                else:
                    st.warning(t.get('location_error_manual_none', "Manual location fields cannot be empty or invalid."))
                    current_location_valid = False
                    st.session_state.location_is_valid_for_run = False # Set persistent flag to invalid

            # Location Search Input
            elif st.session_state.location_choice_key == "Search":
                # Use session state keys for inputs inside the form
                with st.form("location_search_form"):
                    st.text_input(t.get('location_search_label', "Enter location name:"), key="location_search_query", placeholder=t.get('location_search_placeholder', "e.g., Berlin, Germany"))
                    st.number_input(t.get('location_elev_label', "Elevation (meters)"), min_value=-500, step=10, format="%d", key="manual_height_val") # Reuse height key
                    location_search_form_submitted = st.form_submit_button(t.get('location_search_submit_button', "Find Coordinates"))

                status_placeholder = st.empty()
                # Display previous search status from session state
                if st.session_state.location_search_status_msg:
                    if st.session_state.location_search_success:
                        status_placeholder.success(st.session_state.location_search_status_msg)
                    else:
                        status_placeholder.error(st.session_state.location_search_status_msg)

                # Process location search if form submitted and query exists
                if location_search_form_submitted and st.session_state.location_search_query:
                    location = None
                    service_used = None
                    final_error = None
                    query = st.session_state.location_search_query
                    user_agent_str = f"AdvancedDSOFinder/{random.randint(1000, 9999)}/streamlit_app_{datetime.now().timestamp()}"

                    with st.spinner(t.get('spinner_geocoding', "Searching for location...")):
                        # --- Geocoding Logic (Nominatim -> ArcGIS -> Photon) ---
                        # Try Nominatim First
                        try:
                            print("Trying Nominatim...")
                            geolocator = Nominatim(user_agent=user_agent_str)
                            location = geolocator.geocode(query, timeout=10)
                            if location: service_used = "Nominatim"; print("Nominatim success.")
                            else: print("Nominatim returned None.")
                        except (GeocoderTimedOut, GeocoderServiceError) as e:
                            print(f"Nominatim failed: {e}. Trying fallback 1 (ArcGIS).")
                            status_placeholder.info(t.get('location_search_info_fallback', "Nominatim failed, trying fallback service (ArcGIS)..."))
                        except Exception as e:
                            print(f"Nominatim failed unexpectedly: {e}. Trying fallback 1 (ArcGIS).")
                            status_placeholder.info(t.get('location_search_info_fallback', "Nominatim failed, trying fallback service (ArcGIS)..."))
                            final_error = e

                        # Try ArcGIS (Fallback 1) if Nominatim failed
                        if not location:
                            try:
                                print("Trying ArcGIS...")
                                fallback_geolocator = ArcGIS(timeout=15)
                                location = fallback_geolocator.geocode(query, timeout=15)
                                if location: service_used = "ArcGIS"; print("ArcGIS success.")
                                else: print("ArcGIS returned None.")
                            except (GeocoderTimedOut, GeocoderServiceError) as e2:
                                print(f"ArcGIS failed: {e2}. Trying fallback 2 (Photon).")
                                status_placeholder.info(t.get('location_search_info_fallback2', "ArcGIS failed, trying 2nd fallback service (Photon)..."))
                                if not final_error: final_error = e2
                            except Exception as e2:
                                print(f"ArcGIS failed unexpectedly: {e2}. Trying fallback 2 (Photon).")
                                status_placeholder.info(t.get('location_search_info_fallback2', "ArcGIS failed, trying 2nd fallback service (Photon)..."))
                                if not final_error: final_error = e2

                        # Try Photon (Fallback 2) if ArcGIS failed
                        if not location:
                            try:
                                print("Trying Photon...")
                                fallback_geolocator2 = Photon(user_agent=user_agent_str, timeout=15)
                                location = fallback_geolocator2.geocode(query, timeout=15)
                                if location: service_used = "Photon"; print("Photon success.")
                                else:
                                    print("Photon returned None.")
                                    if not final_error: final_error = GeocoderServiceError("All services failed or returned None.")
                            except (GeocoderTimedOut, GeocoderServiceError) as e3:
                                print(f"Photon failed: {e3}. All fallbacks exhausted.")
                                if not final_error: final_error = e3
                            except Exception as e3:
                                print(f"Photon failed unexpectedly: {e3}. All fallbacks exhausted.")
                                if not final_error: final_error = e3
                        # --- End Geocoding Logic ---

                        # Process Geocoding Result
                        if location and service_used:
                            found_lat = location.latitude
                            found_lon = location.longitude
                            found_name = location.address
                            # Update session state with successful search results
                            st.session_state.searched_location_name = found_name
                            st.session_state.location_search_success = True
                            st.session_state.manual_lat_val = found_lat # Store found coords
                            st.session_state.manual_lon_val = found_lon
                            # Height is already in session state from the form

                            coord_str = t.get('location_search_coords', "Lat: {:.4f}, Lon: {:.4f}").format(found_lat, found_lon)
                            # Store success message in session state
                            if service_used == "Nominatim":
                                st.session_state.location_search_status_msg = f"{t.get('location_search_found', 'Found (Nominatim): {}').format(found_name)}\n({coord_str})"
                            elif service_used == "ArcGIS":
                                st.session_state.location_search_status_msg = f"{t.get('location_search_found_fallback', 'Found via Fallback (ArcGIS): {}').format(found_name)}\n({coord_str})"
                            elif service_used == "Photon":
                                st.session_state.location_search_status_msg = f"{t.get('location_search_found_fallback2', 'Found via 2nd Fallback (Photon): {}').format(found_name)}\n({coord_str})"

                            # Display the stored message
                            status_placeholder.success(st.session_state.location_search_status_msg)

                            # Set current run variables and persistent validity flag
                            lat_val = found_lat
                            lon_val = found_lon
                            height_val = st.session_state.manual_height_val
                            location_valid_for_tz = True
                            current_location_valid = True
                            st.session_state.location_is_valid_for_run = True

                        else: # Geocoding failed
                            # Update session state for failure
                            st.session_state.location_search_success = False
                            st.session_state.searched_location_name = None
                            # Store appropriate error message in session state
                            if final_error:
                                if isinstance(final_error, GeocoderTimedOut): st.session_state.location_search_status_msg = t.get('location_search_error_timeout', "Geocoding service timed out.")
                                elif isinstance(final_error, GeocoderServiceError): st.session_state.location_search_status_msg = t.get('location_search_error_service', "Geocoding service error: {}").format(final_error)
                                else: st.session_state.location_search_status_msg = t.get('location_search_error_fallback2_failed', "All geocoding services (Nominatim, ArcGIS, Photon) failed: {}").format(final_error)
                            else: st.session_state.location_search_status_msg = t.get('location_search_error_not_found', "Location not found.")

                            # Display the stored error message
                            status_placeholder.error(st.session_state.location_search_status_msg)
                            # Set current run variables and persistent validity flag
                            current_location_valid = False
                            st.session_state.location_is_valid_for_run = False

                # If search was previously successful (and form not submitted this run), use stored values
                elif st.session_state.location_search_success:
                    lat_val = st.session_state.manual_lat_val
                    lon_val = st.session_state.manual_lon_val
                    height_val = st.session_state.manual_height_val
                    location_valid_for_tz = True
                    current_location_valid = True
                    st.session_state.location_is_valid_for_run = True # Ensure persistent flag is set
                    # Display existing success message from state
                    status_placeholder.success(st.session_state.location_search_status_msg)
                else:
                     # If search mode is selected but no successful search yet
                     current_location_valid = False
                     st.session_state.location_is_valid_for_run = False # Ensure persistent flag is unset


            # --- Automatic Timezone Detection ---
            st.markdown("---")
            auto_timezone_msg = ""
            # Check if location is valid *in this run* for TZ detection
            if location_valid_for_tz and lat_val is not None and lon_val is not None:
                if tf: # Check if TimezoneFinder initialized successfully
                    try:
                        # Find timezone at the given coordinates
                        found_tz = tf.timezone_at(lng=lon_val, lat=lat_val)
                        if found_tz:
                            pytz.timezone(found_tz) # Validate timezone using pytz
                            st.session_state.selected_timezone = found_tz # Update state
                            auto_timezone_msg = f"{t.get('timezone_auto_set_label', 'Detected Timezone:')} **{found_tz}**"
                        else:
                            # Fallback to UTC if timezone not found
                            st.session_state.selected_timezone = 'UTC'
                            auto_timezone_msg = f"{t.get('timezone_auto_fail_label', 'Timezone:')} **UTC** ({t.get('timezone_auto_fail_msg', 'Could not detect timezone, using UTC.')})"
                    except pytz.UnknownTimeZoneError:
                        # Handle case where found timezone is invalid
                        st.session_state.selected_timezone = 'UTC'
                        auto_timezone_msg = f"{t.get('timezone_auto_fail_label', 'Timezone:')} **UTC** (Invalid TZ: '{found_tz}')"
                    except Exception as tz_find_e:
                        # Handle other errors during timezone lookup
                        print(f"Error finding timezone for ({lat_val}, {lon_val}): {tz_find_e}")
                        st.session_state.selected_timezone = 'UTC'
                        auto_timezone_msg = f"{t.get('timezone_auto_fail_label', 'Timezone:')} **UTC** (Error)"
                else:
                    # TimezoneFinder not available
                    auto_timezone_msg = f"{t.get('timezone_auto_fail_label', 'Timezone:')} **{INITIAL_TIMEZONE}** (Auto-detect N/A)"
                    st.session_state.selected_timezone = INITIAL_TIMEZONE # Use initial default
            else:
                # Location is invalid for timezone detection *in this run*
                auto_timezone_msg = f"{t.get('timezone_auto_fail_label', 'Timezone:')} **{st.session_state.selected_timezone}** (Location Invalid/Not Set)"
                # Keep the existing timezone in state if location becomes invalid

            st.markdown(auto_timezone_msg, unsafe_allow_html=True)


        # --- Time Settings ---
        with st.expander(t.get('time_expander', "⏱️ Time & Timezone"), expanded=False):
            time_options_map = {'Now': t.get('time_option_now', "Now (Upcoming Night)"), 'Specific': t.get('time_option_specific', "Specific Night")}

            # Time selection (Now/Specific Night) - Reads from and writes to session state
            st.radio(
                t.get('time_select_label', "Select Time"), options=list(time_options_map.keys()),
                format_func=lambda key: time_options_map[key],
                key="time_choice_exp", # This key is initialized
                horizontal=True
            )

            # is_time_now is determined based on current session state
            is_time_now = (st.session_state.time_choice_exp == "Now")

            if is_time_now:
                st.caption(f"Current UTC: {Time.now().iso}") # Show current time for info
            else:
                # Use date_input for specific night selection - Reads from and writes to session state
                st.date_input(
                    t.get('time_date_select_label', "Select Date:"),
                    value=st.session_state.selected_date_widget, # Use initialized value
                    min_value=date.today()-timedelta(days=365*10), # Allow further back
                    max_value=date.today()+timedelta(days=365*2), # Allow further forward
                    key='selected_date_widget' # Use a key to preserve state
                )


        # --- Filter Settings ---
        with st.expander(t.get('filters_expander', "✨ Filters & Conditions"), expanded=False):
            # --- Magnitude Filter ---
            st.markdown(t.get('mag_filter_header', "**Magnitude Filter**"))
            mag_filter_options_map = {'Bortle Scale': t.get('mag_filter_option_bortle', "Bortle Scale"), 'Manual': t.get('mag_filter_option_manual', "Manual")}
            # Ensure state is valid, default if not (already handled by init)
            if st.session_state.mag_filter_mode_exp not in mag_filter_options_map:
                st.session_state.mag_filter_mode_exp = 'Bortle Scale'

            # Magnitude filter method selection - Reads/Writes state
            st.radio(t.get('mag_filter_method_label', "Filter Method:"), options=list(mag_filter_options_map.keys()),
                     format_func=lambda key: mag_filter_options_map[key],
                     key="mag_filter_mode_exp", horizontal=True)

            # Bortle scale slider - Reads/Writes state
            st.slider(t.get('mag_filter_bortle_label', "Bortle Scale:"), min_value=1, max_value=9, key='bortle_slider', help=t.get('mag_filter_bortle_help', "Sky darkness: 1=Excellent Dark, 9=Inner-city Sky"))

            # Manual magnitude sliders (shown only if Manual mode selected)
            if st.session_state.mag_filter_mode_exp == "Manual":
                # Reads/Writes state
                st.slider(t.get('mag_filter_min_mag_label', "Min. Magnitude:"), min_value=-5.0, max_value=20.0, step=0.5, format="%.1f", help=t.get('mag_filter_min_mag_help', "Brightest object magnitude to include"), key='manual_min_mag_slider')
                st.slider(t.get('mag_filter_max_mag_label', "Max. Magnitude:"), min_value=-5.0, max_value=20.0, step=0.5, format="%.1f", help=t.get('mag_filter_max_mag_help', "Dimest object magnitude to include"), key='manual_max_mag_slider')

                # Warn if min magnitude > max magnitude (based on current state)
                if isinstance(st.session_state.manual_min_mag_slider, (int, float)) and \
                   isinstance(st.session_state.manual_max_mag_slider, (int, float)) and \
                   st.session_state.manual_min_mag_slider > st.session_state.manual_max_mag_slider:
                    st.warning(t.get('mag_filter_warning_min_max', "Min. Magnitude is greater than Max. Magnitude!"))

            # --- Altitude Filter ---
            st.markdown("---")
            st.markdown(t.get('min_alt_header', "**Object Altitude Above Horizon**"))
            # Read current values before drawing sliders
            min_alt_val = st.session_state.min_alt_slider
            max_alt_val = st.session_state.max_alt_slider
            # Ensure min <= max logic *before* rendering sliders if state is inconsistent
            if min_alt_val > max_alt_val:
                st.session_state.min_alt_slider = max_alt_val # Adjust state before drawing
                min_alt_val = max_alt_val # Update local var for this run

            # Min altitude slider - Reads/Writes state
            st.slider(t.get('min_alt_label', "Min. Object Altitude (°):"), min_value=0, max_value=90, key='min_alt_slider', step=1)
            # Max altitude slider - Reads/Writes state
            st.slider(t.get('max_alt_label', "Max. Object Altitude (°):"), min_value=0, max_value=90, key='max_alt_slider', step=1)

            # Re-check min/max after both sliders are drawn and warn if still inconsistent (e.g., user interaction)
            if st.session_state.min_alt_slider > st.session_state.max_alt_slider:
                # Use German for the warning as per original code context
                st.warning("Min. Höhe ist größer als Max. Höhe!")


            # --- Moon Filter ---
            st.markdown("---")
            st.markdown(t.get('moon_warning_header', "**Moon Warning**"))
            # Moon illumination warning threshold slider - Reads/Writes state
            st.slider(t.get('moon_warning_label', "Warn if Moon > (% Illumination):"), min_value=0, max_value=100, key='moon_phase_slider', step=5)

            # --- Object Type Filter ---
            st.markdown("---")
            st.markdown(t.get('object_types_header', "**Object Types**"))
            all_types = []
            # Populate object types if catalog is loaded
            if df_catalog_data is not None and not df_catalog_data.empty:
                try:
                    if 'Type' in df_catalog_data.columns:
                        all_types = sorted(list(df_catalog_data['Type'].dropna().astype(str).unique()))
                    else: st.warning("Catalog is missing the 'Type' column.")
                except Exception as e: st.warning(f"{t.get('object_types_error_extract', 'Could not extract object types from catalog')}: {e}")

            # Object type multiselect widget - Reads/Writes state
            if all_types:
                # Ensure current selection in state is valid against available types
                current_selection_in_state = [sel for sel in st.session_state.object_type_filter_exp if sel in all_types]
                if current_selection_in_state != st.session_state.object_type_filter_exp:
                    st.session_state.object_type_filter_exp = current_selection_in_state # Correct state if needed

                # Set default for the widget based on corrected state
                default_for_widget = current_selection_in_state # Use current state as default
                st.multiselect(
                    t.get('object_types_label', "Filter Types (leave empty for all):"), options=all_types,
                    default=default_for_widget, # Default to current selection
                    key="object_type_filter_exp" # Reads/Writes state
                )
            else:
                # Disable filter if types cannot be determined
                st.info("Object types cannot be determined from the catalog. Type filter disabled.")
                st.session_state.object_type_filter_exp = [] # Ensure state is empty


            # --- Angular Size Filter ---
            st.markdown("---")
            st.markdown(t.get('size_filter_header', "**Angular Size Filter**"))
            # Check if size data is available and valid
            size_col_exists = df_catalog_data is not None and 'MajAx' in df_catalog_data.columns and df_catalog_data['MajAx'].notna().any()
            size_slider_disabled = not size_col_exists

            # Angular size range slider - Reads/Writes state
            if size_col_exists:
                try:
                    # Determine min/max possible size values from catalog
                    valid_sizes = df_catalog_data['MajAx'].dropna()
                    min_size_possible = max(0.1, float(valid_sizes.min())) if not valid_sizes.empty else 0.1
                    max_size_possible = float(valid_sizes.max()) if not valid_sizes.empty else 120.0

                    # Clamp current slider values in state to possible range
                    current_min_state, current_max_state = st.session_state.size_arcmin_range
                    clamped_min = max(min_size_possible, min(current_min_state, max_size_possible))
                    clamped_max = min(max_size_possible, max(current_max_state, min_size_possible))
                    if clamped_min > clamped_max: clamped_min = clamped_max # Ensure min <= max
                    # Update state if clamping occurred
                    if (clamped_min, clamped_max) != st.session_state.size_arcmin_range:
                        st.session_state.size_arcmin_range = (clamped_min, clamped_max)

                    # Determine slider step based on max size
                    slider_step = 0.1 if max_size_possible <= 20 else (0.5 if max_size_possible <= 100 else 1.0)

                    st.slider(
                        t.get('size_filter_label', "Object Size (arcminutes):"),
                        min_value=min_size_possible,
                        max_value=max_size_possible,
                        # value=st.session_state.size_arcmin_range, # Value is implicitly handled by key
                        step=slider_step,
                        format="%.1f arcmin",
                        key='size_arcmin_range', # Reads/Writes state
                        help=t.get('size_filter_help', "Filter objects by their apparent size (major axis). 1 arcminute = 1/60 degree."),
                        disabled=size_slider_disabled
                    )
                except Exception as size_slider_e:
                    st.error(f"Error setting up size slider: {size_slider_e}")
                    size_slider_disabled = True # Disable if error
            else:
                # Show info if size data is unavailable
                st.info("Angular size data ('MajAx') not found or invalid. Size filter disabled.")
                size_slider_disabled = True # Ensure slider is disabled

            # Render a disabled slider placeholder if needed
            if size_slider_disabled:
                st.slider(
                    t.get('size_filter_label', "Object Size (arcminutes):"), min_value=0.0, max_value=1.0, value=(0.0, 1.0),
                    key='size_arcmin_range_disabled', # Use a different key for the disabled one
                    disabled=True
                )


            # --- Direction Filter ---
            st.markdown("---")
            st.markdown(t.get('direction_filter_header', "**Filter by Cardinal Direction**")) # Uses updated translation
            all_directions_str = t.get('direction_option_all', "All")
            # Display options use translated 'All', internal use ALL_DIRECTIONS_KEY
            direction_options_display = [all_directions_str] + CARDINAL_DIRECTIONS
            direction_options_internal = [ALL_DIRECTIONS_KEY] + CARDINAL_DIRECTIONS

            # Get current selection from state and ensure it's valid
            current_direction_internal = st.session_state.selected_peak_direction
            if current_direction_internal not in direction_options_internal:
                current_direction_internal = ALL_DIRECTIONS_KEY
                st.session_state.selected_peak_direction = current_direction_internal # Correct state

            try: current_direction_index = direction_options_internal.index(current_direction_internal)
            except ValueError: current_direction_index = 0 # Default to 'All' index

            # Direction selection selectbox - Reads/Writes state
            selected_direction_display = st.selectbox(
                t.get('direction_filter_label', "Show objects culminating towards:"), # Uses updated translation
                options=direction_options_display,
                index=current_direction_index, # Set initial display based on state
                key='direction_selectbox' # Use a key to manage state implicitly
            )

            # Update internal state based on display selection *after* widget interaction
            selected_internal_value = ALL_DIRECTIONS_KEY # Default
            if selected_direction_display != all_directions_str:
                try:
                    # Find the internal value corresponding to the selected display value
                    selected_internal_index = direction_options_display.index(selected_direction_display)
                    selected_internal_value = direction_options_internal[selected_internal_index]
                except ValueError:
                    selected_internal_value = ALL_DIRECTIONS_KEY # Fallback if display value not found
            # Update the main session state key if the selectbox changed it
            if selected_internal_value != st.session_state.selected_peak_direction:
                 st.session_state.selected_peak_direction = selected_internal_value


        # --- Result Options ---
        with st.expander(t.get('results_options_expander', "⚙️ Result Options"), expanded=False):
            # Max number of objects slider - Reads/Writes state
            max_slider_val = len(df_catalog_data) if df_catalog_data is not None and not df_catalog_data.empty else 50
            min_slider_val = 5
            actual_max_slider = max(min_slider_val, max_slider_val)
            slider_disabled = actual_max_slider <= min_slider_val

            # Ensure default value in state is within valid range
            default_num_objects = st.session_state.get('num_objects_slider', 20)
            clamped_default = max(min_slider_val, min(default_num_objects, actual_max_slider))
            if clamped_default != default_num_objects:
                 st.session_state.num_objects_slider = clamped_default # Correct state if needed

            st.slider(
                t.get('results_options_max_objects_label', "Max. Number of Objects to Display:"),
                min_value=min_slider_val,
                max_value=actual_max_slider,
                # value=st.session_state.num_objects_slider, # Value handled by key
                step=1,
                key='num_objects_slider', # Reads/Writes state
                disabled=slider_disabled
            )

            # Result sorting method radio buttons - Reads/Writes state
            sort_options_map = {
                'Duration & Altitude': t.get('results_options_sort_duration', "Duration & Altitude"),
                'Brightness': t.get('results_options_sort_magnitude', "Brightness")
            }
            # Ensure state is valid (already handled by init)
            if st.session_state.sort_method not in sort_options_map:
                st.session_state.sort_method = 'Duration & Altitude'

            st.radio(
                t.get('results_options_sort_method_label', "Sort Results By:"),
                options=list(sort_options_map.keys()),
                format_func=lambda key: sort_options_map[key],
                key='sort_method', # Reads/Writes state
                horizontal=True
            )

        # --- Bug Report Button ---
        st.sidebar.markdown("---")
        bug_report_email = "debrun2005@gmail.com"
        bug_report_subject = urllib.parse.quote("Bug Report: Advanced DSO Finder")
        # Use translation key for body placeholder
        bug_report_body = urllib.parse.quote(t.get('bug_report_body', "\n\n(Please describe the bug and steps to reproduce)"))
        bug_report_link = f"mailto:{bug_report_email}?subject={bug_report_subject}&body={bug_report_body}"
        # Use translation key for button label
        st.sidebar.markdown(f"<a href='{bug_report_link}' target='_blank'>{t.get('bug_report_button', '🐞 Report Bug')}</a>", unsafe_allow_html=True)

    # --- Main Area ---

    # --- Display Search Parameters ---
    st.subheader(t.get('search_params_header', "Search Parameters"))
    param_col1, param_col2 = st.columns(2)

    # Location Parameter Display
    location_display = t.get('location_error', "Location Error: {}").format("Not Set")
    observer_for_run = None
    # Create observer object only if location state is valid
    if st.session_state.location_is_valid_for_run:
        lat = st.session_state.manual_lat_val
        lon = st.session_state.manual_lon_val
        height = st.session_state.manual_height_val
        tz_str = st.session_state.selected_timezone
        try:
            # Attempt to create observer
            observer_for_run = Observer(latitude=lat * u.deg, longitude=lon * u.deg, elevation=height * u.m, timezone=tz_str)
            # Format location display string based on input method state
            if st.session_state.location_choice_key == "Manual":
                location_display = t.get('location_manual_display', "Manual ({:.4f}, {:.4f})").format(lat, lon)
            elif st.session_state.searched_location_name: # Check if search was successful
                location_display = t.get('location_search_display', "Searched: {} ({:.4f}, {:.4f})").format(st.session_state.searched_location_name, lat, lon)
            else: # Fallback if state is somehow inconsistent (e.g., valid coords but no search name)
                location_display = f"Lat: {lat:.4f}, Lon: {lon:.4f}" # Should ideally not happen
        except Exception as obs_e:
             # Handle observer creation errors
             location_display = t.get('location_error', "Location Error: {}").format(f"Observer creation failed: {obs_e}")
             st.session_state.location_is_valid_for_run = False # Mark state as invalid if observer fails
             observer_for_run = None # Ensure observer is None

    param_col1.markdown(t.get('search_params_location', "📍 Location: {}").format(location_display))

    # Time Parameter Display
    time_display = ""
    # Read time choice from session state
    is_time_now_main = (st.session_state.time_choice_exp == "Now")
    # Calculate reference time based on current state
    if is_time_now_main:
        ref_time_main = Time.now()
        # Format time display for 'Now' case
        try:
            # Attempt to get local time for display, fallback to UTC
            local_now_str, local_tz_now = get_local_time_str(ref_time_main, st.session_state.selected_timezone)
            time_display = t.get('search_params_time_now', "Upcoming Night (from {} UTC)").format(f"{local_now_str} {local_tz_now}")
        except Exception:
            time_display = t.get('search_params_time_now', "Upcoming Night (from {} UTC)").format(f"{ref_time_main.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    else:
        # Read selected date from session state
        selected_date_main = st.session_state.selected_date_widget
        ref_time_main = Time(datetime.combine(selected_date_main, time(12, 0)), scale='utc')
        time_display = t.get('search_params_time_specific', "Night after {}").format(selected_date_main.strftime('%Y-%m-%d'))

    param_col1.markdown(t.get('search_params_time', "⏱️ Time: {}").format(time_display))

    # Magnitude Filter Display
    mag_filter_display = ""
    min_mag_filter, max_mag_filter = -np.inf, np.inf # Initialize filter bounds
    # Determine magnitude filter range based on selected method state
    if st.session_state.mag_filter_mode_exp == "Bortle Scale":
        max_mag_filter = get_magnitude_limit(st.session_state.bortle_slider)
        mag_filter_display = t.get('search_params_filter_mag_bortle', "Bortle {} (<= {:.1f} mag)").format(st.session_state.bortle_slider, max_mag_filter)
    else: # Manual mode
        min_mag_filter = st.session_state.manual_min_mag_slider
        max_mag_filter = st.session_state.manual_max_mag_slider
        mag_filter_display = t.get('search_params_filter_mag_manual', "Manual ({:.1f}-{:.1f} mag)").format(min_mag_filter, max_mag_filter)
    param_col2.markdown(t.get('search_params_filter_mag', "✨ Filter: {}").format(mag_filter_display))

    # Altitude and Type Filter Display
    min_alt_disp = st.session_state.min_alt_slider
    max_alt_disp = st.session_state.max_alt_slider
    selected_types_disp = st.session_state.object_type_filter_exp # Read from state
    types_str = ', '.join(selected_types_disp) if selected_types_disp else t.get('search_params_types_all', "All")
    param_col2.markdown(t.get('search_params_filter_alt_types', "🔭 Filter: Alt {}-{}°, Types: {}").format(min_alt_disp, max_alt_disp, types_str))

    # Size Filter Display
    size_min_disp, size_max_disp = st.session_state.size_arcmin_range # Read from state
    param_col2.markdown(t.get('search_params_filter_size', "📐 Filter: Size {:.1f} - {:.1f} arcmin").format(size_min_disp, size_max_disp))

    # Direction Filter Display
    direction_disp = st.session_state.selected_peak_direction # Read from state
    if direction_disp == ALL_DIRECTIONS_KEY:
        direction_disp = t.get('search_params_direction_all', "All")
    param_col2.markdown(t.get('search_params_filter_direction', "🧭 Filter: Direction at Max: {}").format(direction_disp))


    # --- Find Objects Button ---
    st.markdown("---")
    # Disable button if catalog not loaded or location state is invalid
    find_button_clicked = st.button(
        t.get('find_button_label', "🔭 Find Observable Objects"),
        key="find_button",
        disabled=(df_catalog_data is None or not st.session_state.location_is_valid_for_run)
    )

    # Show initial prompt if location state is invalid but catalog is loaded
    if not st.session_state.location_is_valid_for_run and df_catalog_data is not None:
        st.warning(t.get('info_initial_prompt', "Welcome! Please **Enter Coordinates** or **Search Location** to enable object search."))


    # --- Results Area ---
    results_placeholder = st.container()

    # --- Processing Logic (Triggered by Button Click) ---
    if find_button_clicked:
        # Reset states when starting a new search
        st.session_state.find_button_pressed = True
        st.session_state.show_plot = False
        st.session_state.show_custom_plot = False
        st.session_state.active_result_plot_data = None
        st.session_state.custom_target_plot_data = None
        st.session_state.last_results = []
        # Reset window times before calculation
        st.session_state.window_start_time = None
        st.session_state.window_end_time = None


        # Proceed only if observer was successfully created and catalog loaded
        if observer_for_run and df_catalog_data is not None:
            with st.spinner(t.get('spinner_searching', "Calculating window & searching objects...")):
                try:
                    # 1. Calculate Observation Window
                    # Use the reference time calculated earlier based on main area state
                    start_time_calc, end_time_calc, window_status = get_observable_window(
                        observer_for_run, ref_time_main, is_time_now_main, lang
                    )
                    results_placeholder.info(window_status) # Display window info/errors immediately

                    # Store calculated window times in session state
                    st.session_state.window_start_time = start_time_calc
                    st.session_state.window_end_time = end_time_calc

                    # Proceed only if a valid window was calculated
                    if start_time_calc and end_time_calc and start_time_calc < end_time_calc:
                        # Define time steps for observation period
                        time_resolution = 5 * u.minute
                        observing_times = Time(np.arange(start_time_calc.jd, end_time_calc.jd, time_resolution.to(u.day).value), format='jd', scale='utc')
                        if len(observing_times) < 2:
                            results_placeholder.warning("Warning: Observation window is too short for detailed calculation.")
                            # Continue anyway, duration might be 0

                        # 2. Filter Catalog based on Sidebar Settings (using values from state)
                        filtered_df = df_catalog_data.copy()
                        # Apply magnitude filter (using min/max determined earlier)
                        filtered_df = filtered_df[
                            (filtered_df['Mag'] >= min_mag_filter) &
                            (filtered_df['Mag'] <= max_mag_filter)
                        ]
                        # Apply object type filter (using selected_types_disp from state)
                        if selected_types_disp:
                            filtered_df = filtered_df[filtered_df['Type'].isin(selected_types_disp)]

                        # Apply angular size filter if data is available (using size_min/max_disp from state)
                        size_col_exists_main = df_catalog_data is not None and 'MajAx' in df_catalog_data.columns and df_catalog_data['MajAx'].notna().any()
                        if size_col_exists_main:
                            filtered_df = filtered_df.dropna(subset=['MajAx']) # Drop rows with NaN size before filtering
                            filtered_df = filtered_df[
                                (filtered_df['MajAx'] >= size_min_disp) &
                                (filtered_df['MajAx'] <= size_max_disp)
                            ]

                        # Check if any objects remain after initial filtering
                        if filtered_df.empty:
                            results_placeholder.warning(t.get('warning_no_objects_found', "No objects found matching all criteria for the calculated observation window.") + " (after initial filtering)")
                            st.session_state.last_results = []
                        else:
                            # 3. Find Observable Objects (reaching min alt)
                            min_altitude_for_search = st.session_state.min_alt_slider * u.deg # Use state value
                            found_objects = find_observable_objects(
                                observer_for_run.location,
                                observing_times,
                                min_altitude_for_search,
                                filtered_df,
                                lang
                            )

                            # 4. Apply Max Altitude and Direction Filters (post-calculation, using state)
                            final_objects = []
                            selected_direction = st.session_state.selected_peak_direction # Use state value
                            max_alt_filter = st.session_state.max_alt_slider # Use state value

                            for obj in found_objects:
                                # Apply Max Altitude Filter (based on peak altitude)
                                peak_alt = obj.get('Max Altitude (°)', -999)
                                if peak_alt > max_alt_filter:
                                    continue # Skip if peak altitude is above max limit

                                # Apply Direction Filter
                                if selected_direction != ALL_DIRECTIONS_KEY:
                                    if obj.get('Direction at Max') != selected_direction:
                                        continue # Skip if direction doesn't match

                                final_objects.append(obj) # Add object if it passes all filters


                            # 5. Sort Results (using state)
                            sort_key = st.session_state.sort_method
                            if sort_key == 'Brightness':
                                final_objects.sort(key=lambda x: x.get('Magnitude', float('inf')) if x.get('Magnitude') is not None else float('inf'))
                            else: # Default: Duration & Altitude
                                final_objects.sort(key=lambda x: (x.get('Max Cont. Duration (h)', 0), x.get('Max Altitude (°)', 0)), reverse=True)


                            # 6. Limit Number of Results (using state)
                            num_to_show = st.session_state.num_objects_slider
                            st.session_state.last_results = final_objects[:num_to_show] # Store results in state

                            # Display summary message
                            if not final_objects:
                                results_placeholder.warning(t.get('warning_no_objects_found', "No objects found matching all criteria for the calculated observation window."))
                            else:
                                results_placeholder.success(t.get('success_objects_found', "{} matching objects found.").format(len(final_objects)))
                                sort_msg_key = 'info_showing_list_duration' if sort_key != 'Brightness' else 'info_showing_list_magnitude'
                                results_placeholder.info(t[sort_msg_key].format(len(st.session_state.last_results)))

                    else: # Window calculation failed
                        results_placeholder.error(t.get('error_no_window', "No valid astronomical darkness window found for the selected date and location.") + " Cannot proceed with search.")
                        st.session_state.last_results = [] # Clear results in state
                        # Ensure window times remain None in session state

                except Exception as search_e:
                    # Catch unexpected errors during the search process
                    results_placeholder.error(t.get('error_search_unexpected', "An unexpected error occurred during the search:") + f"\n```\n{search_e}\n```")
                    traceback.print_exc()
                    st.session_state.last_results = [] # Clear results in state
                    # Ensure window times remain None in session state

        else: # Observer or catalog invalid at the time button was clicked
            if df_catalog_data is None: results_placeholder.error("Cannot search: Catalog data not loaded.")
            if not observer_for_run: results_placeholder.error("Cannot search: Location is not valid.")
            st.session_state.last_results = [] # Clear results in state
            # Ensure window times remain None in session state


    # --- Display Results Block ---
    # Display results if they exist in session state from a previous run or the current run
    if st.session_state.last_results:
        results_data = st.session_state.last_results
        results_placeholder.subheader(t.get('results_list_header', "Result List"))

        # --- Moon Phase Display ---
        # Retrieve window times from session state if available
        window_start = st.session_state.get('window_start_time')
        window_end = st.session_state.get('window_end_time')
        observer_exists = observer_for_run is not None # Check if observer was valid in this run

        # Check if window times are valid Time objects and observer exists before calculating moon phase
        if observer_exists and isinstance(window_start, Time) and isinstance(window_end, Time):
            # Calculate moon phase at the middle of the observation window
            mid_time = window_start + (window_end - window_start) / 2
            try:
                illum = moon_illumination(mid_time)
                moon_phase_percent = illum * 100
                moon_svg = create_moon_phase_svg(illum, size=50) # Use corrected SVG function

                # Display moon SVG and illumination percentage
                moon_col1, moon_col2 = results_placeholder.columns([1, 3])
                with moon_col1: st.markdown(moon_svg, unsafe_allow_html=True)
                with moon_col2:
                    st.metric(label=t.get('moon_metric_label', "Moon Illumination (approx.)"), value=f"{moon_phase_percent:.0f}%")
                    # Warn if moon illumination exceeds threshold (use state)
                    moon_warn_threshold = st.session_state.moon_phase_slider
                    if moon_phase_percent > moon_warn_threshold:
                        st.warning(t.get('moon_warning_message', "Warning: Moon is brighter ({:.0f}%) than threshold ({:.0f}%)!").format(moon_phase_percent, moon_warn_threshold))

            except Exception as moon_e:
                # Handle errors during moon phase calculation
                results_placeholder.warning(t.get('moon_phase_error', "Error calculating moon phase: {}").format(moon_e))
        elif st.session_state.find_button_pressed: # Only show info if search was attempted but window/observer failed
             results_placeholder.info("Moon phase cannot be calculated (invalid observation window or location).")


        # --- Display Object List ---
        # --- Plot Type Selection ---
        plot_options_map = {
            'Sky Path': t.get('graph_type_sky_path', "Sky Path (Az/Alt)"),
            'Altitude Plot': t.get('graph_type_alt_time', "Altitude Plot (Alt/Time)")
        }
        # Ensure state is valid (handled by init)
        if st.session_state.plot_type_selection not in plot_options_map:
             st.session_state.plot_type_selection = 'Sky Path'

        # Plot type selection radio buttons - Reads/Writes state
        results_placeholder.radio(
            t.get('graph_type_label', "Graph Type (for all plots):"),
            options=list(plot_options_map.keys()),
            format_func=lambda key: plot_options_map[key],
            key='plot_type_selection', # Reads/Writes state
            horizontal=True
        )

        # --- Display Individual Objects ---
        for i, obj_data in enumerate(results_data):
            obj_name = obj_data.get('Name', 'N/A')
            obj_type = obj_data.get('Type', 'N/A')
            obj_mag = obj_data.get('Magnitude')
            mag_str = f"{obj_mag:.1f}" if obj_mag is not None else "N/A"
            expander_title = t.get('results_expander_title', "{} ({}) - Mag: {:.1f}").format(obj_name, obj_type, obj_mag if obj_mag is not None else 99)

            # Check if this object's expander should be open based on state
            is_expanded = (st.session_state.expanded_object_name == obj_name)

            # Create a container for each object's expander and potential plot
            object_container = results_placeholder.container()

            with object_container.expander(expander_title, expanded=is_expanded):
                col1, col2, col3 = st.columns([2,2,1])

                # Col 1: Details (Constellation, Size, RA/Dec)
                col1.markdown(t.get('results_coords_header', "**Details:**"))
                col1.markdown(f"**{t.get('results_export_constellation', 'Constellation')}:** {obj_data.get('Constellation', 'N/A')}")
                size_arcmin = obj_data.get('Size (arcmin)')
                col1.markdown(f"**{t.get('results_size_label', 'Size (Major Axis):')}** {t.get('results_size_value', '{:.1f} arcmin').format(size_arcmin) if size_arcmin is not None else 'N/A'}")
                col1.markdown(f"**RA:** {obj_data.get('RA', 'N/A')}")
                col1.markdown(f"**Dec:** {obj_data.get('Dec', 'N/A')}")

                # Col 2: Visibility (Max Alt, Azimuth, Direction, Best Time, Duration)
                col2.markdown(t.get('results_max_alt_header', "**Max. Altitude:**"))
                max_alt = obj_data.get('Max Altitude (°)', 0)
                az_at_max = obj_data.get('Azimuth at Max (°)', 0)
                dir_at_max = obj_data.get('Direction at Max', 'N/A')
                azimuth_formatted = t.get('results_azimuth_label', "(Azimuth: {:.1f}°{})").format(az_at_max, "")
                direction_formatted = t.get('results_direction_label', ", Direction: {}").format(dir_at_max)
                col2.markdown(f"**{max_alt:.1f}°** {azimuth_formatted}{direction_formatted}")

                col2.markdown(t.get('results_best_time_header', "**Best Time (Local TZ):**"))
                peak_time_utc = obj_data.get('Time at Max (UTC)')
                # Use timezone from session state for conversion
                local_time_str, local_tz_name = get_local_time_str(peak_time_utc, st.session_state.selected_timezone)
                col2.markdown(f"{local_time_str} ({local_tz_name})")

                col2.markdown(t.get('results_cont_duration_header', "**Max. Cont. Duration:**"))
                duration_h = obj_data.get('Max Cont. Duration (h)', 0)
                col2.markdown(t.get('results_duration_value', "{:.1f} hours").format(duration_h))

                # Col 3: Links & Actions (Google, SIMBAD, Plot Button)
                google_query = urllib.parse.quote_plus(f"{obj_name} astronomy")
                google_url = f"https://www.google.com/search?q={google_query}"
                col3.markdown(f"[{t.get('google_link_text', 'Google')}]({google_url})", unsafe_allow_html=True)

                simbad_query = urllib.parse.quote_plus(obj_name)
                simbad_url = f"http://simbad.u-strasbg.fr/simbad/sim-basic?Ident={simbad_query}"
                col3.markdown(f"[{t.get('simbad_link_text', 'SIMBAD')}]({simbad_url})", unsafe_allow_html=True)

                # Plot button for the specific object
                plot_button_key = f"plot_{obj_name}_{i}"
                if st.button(t.get('results_graph_button', "📈 Show Plot"), key=plot_button_key):
                    # Update state to show plot for this object
                    st.session_state.plot_object_name = obj_name
                    st.session_state.active_result_plot_data = obj_data
                    st.session_state.show_plot = True
                    st.session_state.show_custom_plot = False # Hide custom plot
                    st.session_state.expanded_object_name = obj_name # Keep this expander open
                    st.rerun() # Rerun to display the plot

                # --- Plot Display Area (Inside Expander) ---
                # Display the plot if the state indicates it should be shown for this object
                if st.session_state.show_plot and st.session_state.plot_object_name == obj_name:
                    plot_data = st.session_state.active_result_plot_data
                    min_alt_line = st.session_state.min_alt_slider # Use state
                    max_alt_line = st.session_state.max_alt_slider # Use state

                    st.markdown("---") # Separator before plot
                    with st.spinner(t.get('results_spinner_plotting', "Creating plot...")):
                        try:
                            # Create the plot using the updated function (pass state values)
                            fig = create_plot(plot_data, min_alt_line, max_alt_line, st.session_state.plot_type_selection, lang)
                            if fig:
                                st.pyplot(fig)
                                # Add a button to close the plot
                                close_button_key = f"close_plot_{obj_name}_{i}"
                                if st.button(t.get('results_close_graph_button', "Close Plot"), key=close_button_key):
                                    # Update state to hide the plot
                                    st.session_state.show_plot = False
                                    st.session_state.active_result_plot_data = None
                                    st.session_state.expanded_object_name = None # Close this expander
                                    st.rerun() # Rerun to hide the plot
                            else:
                                st.error(t.get('results_graph_not_created', "Plot could not be created."))
                        except Exception as plot_err:
                            st.error(t.get('results_graph_error', "Plot Error: {}").format(plot_err))
                            traceback.print_exc()


        # --- CSV Export Button ---
        if results_data:
            # Place button below the list of expanders
            csv_export_placeholder = results_placeholder.empty()
            try:
                # Prepare data for CSV export
                export_data = []
                for obj in results_data:
                    peak_time_utc = obj.get('Time at Max (UTC)')
                    # Use timezone from state for local time conversion
                    local_time_str, _ = get_local_time_str(peak_time_utc, st.session_state.selected_timezone)
                    export_data.append({
                        t.get('results_export_name', "Name"): obj.get('Name', 'N/A'),
                        t.get('results_export_type', "Type"): obj.get('Type', 'N/A'),
                        t.get('results_export_constellation', "Constellation"): obj.get('Constellation', 'N/A'),
                        t.get('results_export_mag', "Magnitude"): obj.get('Magnitude'),
                        t.get('results_export_size', "Size (arcmin)"): obj.get('Size (arcmin)'),
                        t.get('results_export_ra', "RA"): obj.get('RA', 'N/A'),
                        t.get('results_export_dec', "Dec"): obj.get('Dec', 'N/A'),
                        t.get('results_export_max_alt', "Max Altitude (°)"): obj.get('Max Altitude (°)', 0),
                        t.get('results_export_az_at_max', "Azimuth at Max (°)"): obj.get('Azimuth at Max (°)', 0),
                        t.get('results_export_direction_at_max', "Direction at Max"): obj.get('Direction at Max', 'N/A'),
                        t.get('results_export_time_max_utc', "Time at Max (UTC)"): peak_time_utc.iso if peak_time_utc else "N/A",
                        t.get('results_export_time_max_local', "Time at Max (Local TZ)"): local_time_str,
                        t.get('results_export_cont_duration', "Max Cont Duration (h)"): obj.get('Max Cont. Duration (h)', 0)
                    })

                df_export = pd.DataFrame(export_data)
                # Conditional decimal separator based on language state
                decimal_sep = ',' if lang == 'de' else '.'
                # Convert DataFrame to CSV string
                csv_string = df_export.to_csv(index=False, sep=';', encoding='utf-8-sig', decimal=decimal_sep)

                now_str = datetime.now().strftime("%Y%m%d_%H%M")
                csv_filename = t.get('results_csv_filename', "dso_observation_list_{}.csv").format(now_str)

                # Create download button using the placeholder
                csv_export_placeholder.download_button(
                    label=t.get('results_save_csv_button', "💾 Save Result List as CSV"),
                    data=csv_string,
                    file_name=csv_filename,
                    mime='text/csv',
                    key='csv_download_button'
                )
            except Exception as csv_e:
                # Handle errors during CSV export
                csv_export_placeholder.error(t.get('results_csv_export_error', "CSV Export Error: {}").format(csv_e))

    elif st.session_state.find_button_pressed: # Show message if button was pressed but no results in state
        results_placeholder.info(t.get('warning_no_objects_found', "No objects found matching all criteria for the calculated observation window."))


    # --- Custom Target Plotting ---
    st.markdown("---")
    with st.expander(t.get('custom_target_expander', "Plot Custom Target")):
        with st.form("custom_target_form"):
             # Input fields read/write state
             st.text_input(t.get('custom_target_ra_label', "Right Ascension (RA):"), key="custom_target_ra", placeholder=t.get('custom_target_ra_placeholder', "e.g., 10:45:03.6 or 161.265"))
             st.text_input(t.get('custom_target_dec_label', "Declination (Dec):"), key="custom_target_dec", placeholder=t.get('custom_target_dec_placeholder', "e.g., -16:42:58 or -16.716"))
             st.text_input(t.get('custom_target_name_label', "Target Name (Optional):"), key="custom_target_name", placeholder="My Comet")
             custom_plot_submitted = st.form_submit_button(t.get('custom_target_button', "Create Custom Plot"))

        custom_plot_error_placeholder = st.empty()
        custom_plot_display_area = st.empty()

        # Process custom plot request if form submitted
        if custom_plot_submitted:
             # Reset plot states
             st.session_state.show_plot = False # Hide result plot
             st.session_state.show_custom_plot = False # Reset custom plot flag
             st.session_state.custom_target_plot_data = None # Clear old data
             st.session_state.custom_target_error = "" # Clear old error

             custom_ra = st.session_state.custom_target_ra
             custom_dec = st.session_state.custom_target_dec
             custom_name = st.session_state.custom_target_name or t.get('custom_target_name_label', "Target Name (Optional):").replace(":", "") # Use translated default if empty

             # Retrieve window times and check observer from session state
             window_start_cust = st.session_state.get('window_start_time')
             window_end_cust = st.session_state.get('window_end_time')
             observer_exists_cust = observer_for_run is not None # Check if observer was valid in this run

             # Validate inputs: RA/Dec must be provided
             if not custom_ra or not custom_dec:
                 st.session_state.custom_target_error = t.get('custom_target_error_coords', "Invalid RA/Dec format. Use HH:MM:SS.s / DD:MM:SS or decimal degrees.")
                 custom_plot_error_placeholder.error(st.session_state.custom_target_error)
             # Validate inputs: Observer and valid window times must exist from state
             elif not observer_exists_cust or not isinstance(window_start_cust, Time) or not isinstance(window_end_cust, Time):
                 st.session_state.custom_target_error = t.get('custom_target_error_window', "Cannot create plot. Ensure location and time window are valid (try clicking 'Find Observable Objects' first).")
                 custom_plot_error_placeholder.error(st.session_state.custom_target_error)
             else:
                 # Proceed with custom plot calculation
                 try:
                     # Create SkyCoord for the custom target
                     custom_coord = SkyCoord(ra=custom_ra, dec=custom_dec, unit=(u.hourangle, u.deg))

                     # Use times from the main search window (stored in state)
                     if window_start_cust < window_end_cust:
                         time_resolution_cust = 5 * u.minute
                         observing_times_custom = Time(np.arange(window_start_cust.jd, window_end_cust.jd, time_resolution_cust.to(u.day).value), format='jd', scale='utc')
                     else:
                         raise ValueError("Valid time window from main search not available for custom plot.")

                     if len(observing_times_custom) < 2:
                         raise ValueError("Calculated time window for custom plot is too short.")


                     # Calculate Alt/Az for the custom target using valid observer
                     altaz_frame_custom = AltAz(obstime=observing_times_custom, location=observer_for_run.location)
                     custom_altazs = custom_coord.transform_to(altaz_frame_custom)
                     custom_alts = custom_altazs.alt.to(u.deg).value
                     custom_azs = custom_altazs.az.to(u.deg).value

                     # Store plot data in session state
                     st.session_state.custom_target_plot_data = {
                         'Name': custom_name,
                         'altitudes': custom_alts,
                         'azimuths': custom_azs,
                         'times': observing_times_custom
                     }
                     st.session_state.show_custom_plot = True # Set flag to show
                     st.session_state.custom_target_error = "" # Clear error
                     st.rerun() # Rerun to display the custom plot

                 except ValueError as custom_coord_err:
                     # Handle coordinate format errors
                     st.session_state.custom_target_error = f"{t.get('custom_target_error_coords', 'Invalid RA/Dec format. Use HH:MM:SS.s / DD:MM:SS or decimal degrees.')} ({custom_coord_err})"
                     custom_plot_error_placeholder.error(st.session_state.custom_target_error)
                 except Exception as custom_e:
                     # Handle other errors during custom plot creation
                     st.session_state.custom_target_error = f"Error creating custom plot: {custom_e}"
                     custom_plot_error_placeholder.error(st.session_state.custom_target_error)
                     traceback.print_exc()

        # Display custom plot if data exists and flag is set in state
        if st.session_state.show_custom_plot and st.session_state.custom_target_plot_data:
            custom_plot_data = st.session_state.custom_target_plot_data
            min_alt_line_cust = st.session_state.min_alt_slider # Use state
            max_alt_line_cust = st.session_state.max_alt_slider # Use state

            with custom_plot_display_area.container():
                 st.markdown("---")
                 with st.spinner(t.get('results_spinner_plotting', "Creating plot...")):
                     try:
                         # Create the custom plot (pass state values)
                         fig_cust = create_plot(custom_plot_data, min_alt_line_cust, max_alt_line_cust, st.session_state.plot_type_selection, lang)
                         if fig_cust:
                             st.pyplot(fig_cust)
                             # Add button to close the custom plot
                             if st.button(t.get('results_close_graph_button', "Close Plot"), key="close_custom_plot"):
                                 # Update state to hide the plot
                                 st.session_state.show_custom_plot = False
                                 st.session_state.custom_target_plot_data = None
                                 st.rerun() # Rerun to hide the plot
                         else: st.error(t.get('results_graph_not_created', "Plot could not be created."))
                     except Exception as plot_err_cust:
                         # Handle errors during custom plot display
                         st.error(t.get('results_graph_error', "Plot Error: {}").format(plot_err_cust))
                         traceback.print_exc()
        # Display error message if it exists in state
        elif st.session_state.custom_target_error:
             custom_plot_error_placeholder.error(st.session_state.custom_target_error)


    # --- Add Donation Link at the bottom ---
    st.markdown("---") # Add a separator line
    st.caption(t.get('donation_text', "Like the app? [Support the development on Ko-fi ☕](https://ko-fi.com/advanceddsofinder)"), unsafe_allow_html=True)


# --- Plotting Function (Revised for Robustness and Visibility) ---
#@st.cache_data(show_spinner=False) # Cache plot generation - consider if plot_data is hashable
def create_plot(plot_data: dict, min_altitude_deg: float, max_altitude_deg: float, plot_type: str, lang: str) -> plt.Figure | None:
    """Creates either an Altitude vs Time or Sky Path (Alt/Az) plot with improved robustness and theme handling."""
    t = translations.get(lang, translations['en'])
    fig = None # Initialize fig to None

    try:
        # --- Validate Input Data ---
        if not isinstance(plot_data, dict):
            st.error("Plot Error: Invalid plot_data type (expected dict).")
            return None
        times = plot_data.get('times')
        altitudes = plot_data.get('altitudes')
        azimuths = plot_data.get('azimuths') # Needed for both plot types now (coloring/polar coords)
        obj_name = plot_data.get('Name', 'Object')

        # Check essential data presence and type
        if not isinstance(times, Time) or not isinstance(altitudes, np.ndarray):
            st.error("Plot Error: Missing or invalid 'times' or 'altitudes' in plot_data.")
            return None
        if plot_type == 'Sky Path' and not isinstance(azimuths, np.ndarray):
             st.error("Plot Error: Missing or invalid 'azimuths' for Sky Path plot.")
             return None
        if len(times) != len(altitudes) or (azimuths is not None and len(times) != len(azimuths)):
            st.error(f"Plot Error: Mismatched array lengths (times: {len(times)}, alts: {len(altitudes)}, azs: {len(azimuths) if azimuths is not None else 'N/A'}).")
            return None
        if len(times) < 1: # Need at least one point to plot
             st.error("Plot Error: Not enough data points to create a plot.")
             return None

        plot_times = times.plot_date # Convert astropy Time to matplotlib format

        # --- Theme Detection and Color Setup ---
        try:
            # Use Streamlit's recommended way to get theme info
            theme_opts = st.get_option("theme.base")
            is_dark_theme = (theme_opts == "dark")
        except Exception:
            print("Warning: Could not detect Streamlit theme via get_option. Assuming light theme.")
            is_dark_theme = False

        # Define color palettes for light and dark themes
        if is_dark_theme:
            plt.style.use('dark_background')
            fig_facecolor = '#0E1117' # Streamlit dark bg
            ax_facecolor = '#0E1117'
            primary_color = 'deepskyblue' #'skyblue'
            secondary_color = 'lightgrey' # For less important elements if needed
            grid_color = '#444444' # Darker gray for grid
            label_color = '#FAFAFA' # Off-white for labels/ticks
            title_color = '#FFFFFF' # White for title
            legend_facecolor = '#262730' # Slightly lighter dark for legend bg
            min_alt_color = 'tomato'
            max_alt_color = 'orange'
            spine_color = '#AAAAAA' # Color for plot borders
        else: # Light theme
            plt.style.use('default') # Matplotlib default light style
            fig_facecolor = '#FFFFFF' # White bg
            ax_facecolor = '#FFFFFF'
            primary_color = 'dodgerblue'
            secondary_color = '#555555'
            grid_color = 'darkgray' # Made slightly darker for light theme visibility
            label_color = '#333333' # Dark gray for labels/ticks
            title_color = '#000000' # Black for title
            legend_facecolor = '#F0F0F0' # Light gray for legend bg
            min_alt_color = 'red'
            max_alt_color = 'darkorange'
            spine_color = '#555555' # Darker gray for plot borders

        # --- Create Figure and Axes ---
        # Use constrained_layout for better spacing
        fig, ax = plt.subplots(figsize=(10, 6), facecolor=fig_facecolor, constrained_layout=True)
        ax.set_facecolor(ax_facecolor) # Set axes background explicitly

        # --- Plot Logic ---
        if plot_type == 'Altitude Plot':
            # Altitude vs Time Plot
            ax.plot(plot_times, altitudes, color=primary_color, alpha=0.9, linewidth=1.5, label=obj_name)

            # Add Min/Max Altitude Lines
            ax.axhline(min_altitude_deg, color=min_alt_color, linestyle='--', linewidth=1.2, label=t.get('graph_min_altitude_label', "Min Altitude ({:.0f}°)").format(min_altitude_deg), alpha=0.8)
            if max_altitude_deg < 90: # Only plot max line if it's not 90
                 ax.axhline(max_altitude_deg, color=max_alt_color, linestyle=':', linewidth=1.2, label=t.get('graph_max_altitude_label', "Max Altitude ({:.0f}°)").format(max_altitude_deg), alpha=0.8)

            # Configure Altitude Plot axes
            ax.set_xlabel("Time (UTC)", color=label_color, fontsize=11)
            ax.set_ylabel(t.get('graph_ylabel', "Altitude (°)"), color=label_color, fontsize=11)
            ax.set_title(t.get('graph_title_alt_time', "Altitude Plot for {}").format(obj_name), color=title_color, fontsize=13, weight='bold')
            ax.set_ylim(0, 90)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            fig.autofmt_xdate(rotation=30) # Slightly rotate labels

            # Set grid and tick colors
            ax.grid(True, linestyle='-', alpha=0.5, color=grid_color) # Increased alpha for visibility
            ax.tick_params(axis='x', colors=label_color)
            ax.tick_params(axis='y', colors=label_color)
            # Set spine colors
            for spine in ax.spines.values():
                spine.set_color(spine_color)
                spine.set_linewidth(0.5)

        elif plot_type == 'Sky Path':
            # Sky Path (Polar) Plot
            # Ensure azimuths are valid before proceeding
            if azimuths is None or not isinstance(azimuths, np.ndarray) or len(azimuths) != len(times):
                 st.error("Plot Error: Invalid or missing azimuth data for Sky Path plot.")
                 plt.close(fig)
                 return None

            ax.remove() # Remove the default Cartesian axes
            ax = fig.add_subplot(111, projection='polar', facecolor=ax_facecolor)

            az_rad = np.deg2rad(azimuths)
            radius = 90 - altitudes # Radius 0 is zenith (alt 90), radius 90 is horizon (alt 0)

            # Use time progression for color mapping
            # Add a small epsilon to avoid division by zero if times are identical
            time_delta = times.jd.max() - times.jd.min()
            time_norm = (times.jd - times.jd.min()) / (time_delta + 1e-9)
            colors = plt.cm.plasma(time_norm) # Plasma colormap often works well

            # Plot the path
            scatter = ax.scatter(az_rad, radius, c=colors, s=15, alpha=0.8, edgecolors='none', label=obj_name)
            # Optionally connect points with a line
            ax.plot(az_rad, radius, color=primary_color, alpha=0.4, linewidth=0.8)


            # Add Min/Max Altitude Circles
            ax.plot(np.linspace(0, 2*np.pi, 100), np.full(100, 90 - min_altitude_deg), color=min_alt_color, linestyle='--', linewidth=1.2, label=t.get('graph_min_altitude_label', "Min Altitude ({:.0f}°)").format(min_altitude_deg), alpha=0.8)
            if max_altitude_deg < 90: # Only plot max circle if not 90
                 ax.plot(np.linspace(0, 2*np.pi, 100), np.full(100, 90 - max_altitude_deg), color=max_alt_color, linestyle=':', linewidth=1.2, label=t.get('graph_max_altitude_label', "Max Altitude ({:.0f}°)").format(max_altitude_deg), alpha=0.8)


            # Configure Polar Plot axes
            ax.set_theta_zero_location('N') # North at top
            ax.set_theta_direction(-1) # Clockwise azimuth
            ax.set_yticks(np.arange(0, 91, 15)) # Altitude circles every 15 deg
            ax.set_yticklabels([f"{90-alt}°" for alt in np.arange(0, 91, 15)], color=label_color)
            ax.set_ylim(0, 90) # Radial limit (0=zenith, 90=horizon) -> Corrected radius means ylim is 0-90
            ax.set_title(t.get('graph_title_sky_path', "Sky Path for {}").format(obj_name), va='bottom', color=title_color, fontsize=13, weight='bold', y=1.1) # Adjust title position

            # Set grid and spine colors
            ax.grid(True, linestyle=':', alpha=0.5, color=grid_color) # Increased alpha for visibility
            ax.spines['polar'].set_color(spine_color)
            ax.spines['polar'].set_linewidth(0.5)

            # Colorbar for time progression
            try:
                cbar = fig.colorbar(scatter, ax=ax, label="Time Progression (UTC)", pad=0.1, shrink=0.7)
                cbar.set_ticks([0, 1])
                # Check if times array has at least two elements for labels
                if len(times) > 0:
                    start_label = times[0].to_datetime(timezone.utc).strftime('%H:%M')
                    end_label = times[-1].to_datetime(timezone.utc).strftime('%H:%M')
                    cbar.ax.set_yticklabels([start_label, end_label])
                else:
                    cbar.ax.set_yticklabels(['Start', 'End'])

                # Set colorbar label and tick colors
                cbar.set_label("Time Progression (UTC)", color=label_color, fontsize=10)
                cbar.ax.yaxis.set_tick_params(color=label_color, labelsize=9)
                plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=label_color)
                # Set colorbar outline color
                cbar.outline.set_edgecolor(spine_color)
                cbar.outline.set_linewidth(0.5)
            except Exception as cbar_err:
                 print(f"Warning: Could not create colorbar for Sky Path plot: {cbar_err}")


        else:
            st.error(f"Plot Error: Unknown plot type '{plot_type}'")
            plt.close(fig)
            return None


        # --- Common Plot Settings ---
        # Configure legend - MOVED TO BOTTOM RIGHT
        legend = ax.legend(loc='lower right', fontsize='small', facecolor=legend_facecolor, framealpha=0.8, edgecolor=spine_color)
        for text in legend.get_texts():
            text.set_color(label_color)

        # plt.tight_layout() # Replaced by constrained_layout=True in subplots

        return fig

    except Exception as e:
        # Catch any unexpected error during plot creation
        st.error(f"Plot Error: An unexpected error occurred: {e}")
        traceback.print_exc()
        if fig:
            plt.close(fig) # Ensure figure is closed if an error occurs
        return None


# --- Run the App ---
if __name__ == "__main__":
    main()
