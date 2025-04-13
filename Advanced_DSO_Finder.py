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
    # Import get_constellation directly
    from astropy.coordinates import EarthLocation, SkyCoord, get_sun, AltAz, get_constellation
    # Import Observer from astroplan main
    from astroplan import Observer
    # Import constraints and exceptions from submodules
    from astroplan.constraints import AtNightConstraint
    from astroplan.moon import moon_illumination
except ImportError as e:
    import_errors.append(f"Error: Required Astropy/Astroplan library not found. Install: pip install astropy numpy astroplan ({e})")
    np = None; u = None; EarthLocation = None; SkyCoord = None; get_sun = None; AltAz = None; get_constellation = None
    Observer = None; # Astroplan specific
    AtNightConstraint = None; # Astroplan specific
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
    pd = None; plt = None; mdates = None # Define as None if matplotlib fails

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
    Nominatim = None; GeocoderTimedOut = None; GeocoderServiceError = None

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
    TimezoneFinder, # TimezoneFinder
    Observer, AtNightConstraint, # Astroplan
    get_constellation # Astropy constellation function
])
if not essential_imports_ok:
    st.error("Stopping execution due to missing essential libraries (astropy, astroplan, pandas, matplotlib, pytz, geopy, timezonefinder).")
    st.stop()

# --- Translations ---
# *** FIX: Added/Renamed graph keys ***
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
        'object_type_glossary_title': "Object Type Glossary",
        'object_type_glossary': {
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
        'window_info_template': "Observation window: {} to {} UTC (Astronomical Twilight)", # Updated template
        'error_no_window': "No valid astronomical darkness window found for the selected date and location.", # More specific
        'error_polar_night': "Astronomical darkness persists for >24h (polar night?). Using fallback window.", # NEU
        'error_polar_day': "No astronomical darkness occurs (polar day?). Using fallback window.", # NEU
        'success_objects_found': "{} matching objects found.",
        'info_showing_list_duration': "Showing {} objects, sorted by visibility duration and peak altitude:",
        'info_showing_list_magnitude': "Showing {} objects, sorted by brightness (brightest first):",
        'error_search_unexpected': "An unexpected error occurred during the search:",
        'results_list_header': "Result List",
        'results_export_name': "Name",
        'results_export_type': "Type",
        'results_export_constellation': "Constellation",
        'results_export_mag': "Magnitude",
        'results_export_ra': "RA",
        'results_export_dec': "Dec",
        'results_export_max_alt': "Max Altitude (°)",
        'results_export_az_at_max': "Azimuth at Max (°)",
        'results_export_direction_at_max': "Direction at Max",
        'results_export_time_max_utc': "Time at Max (UTC)",
        'results_export_time_max_local': "Time at Max (Local TZ)",
        'results_export_cont_duration': "Max Cont. Duration (h)",
        'results_expander_title': "{} ({}) - Mag: {:.1f}",
        'results_coords_header': "**Details:**",
        'results_constellation_label': "Constellation:",
        'results_max_alt_header': "**Max. Altitude:**",
        'results_azimuth_label': "(Azimuth: {:.1f}°{})",
        'results_direction_label': ", Direction: {}",
        'results_best_time_header': "**Best Time (Local TZ):**",
        'results_cont_duration_header': "**Max. Cont. Duration:**",
        'results_duration_value': "{:.1f} hours",
        'graph_type_label': "Graph Type (for all graphs):", # Renamed & Clarified scope
        'graph_type_sky_path': "Sky Path (Az/Alt)", # Renamed
        'graph_type_alt_time': "Altitude/Time", # Renamed
        'results_graph_button': "📈 Show Graph", # Renamed
        'results_spinner_plotting': "Creating graph...", # Renamed
        'results_graph_error': "Graph Error: {}", # Renamed
        'results_graph_not_created': "Graph could not be created.", # Renamed
        'results_close_graph_button': "Close Graph", # Renamed
        'results_save_csv_button': "💾 Save Result List as CSV",
        'results_csv_filename': "dso_observation_list_{}.csv",
        'results_csv_export_error': "CSV Export Error: {}",
        'warning_no_objects_found': "No objects found matching all criteria for the calculated observation window.",
        'info_initial_prompt': "Welcome! Please **enter coordinates** manually or **search for a location** name to enable the main search.",
        'graph_altitude_label': "Altitude (°)",
        'graph_azimuth_label': "Azimuth (°)",
        'graph_min_altitude_label': "Min. Altitude ({:.0f}°)",
        'graph_title_sky_path': "Sky Path for {}",
        'graph_title_alt_time': "Altitude Profile for {}",
        'graph_ylabel': "Altitude (°)",
        'custom_target_expander': "Graph Custom Target",
        'custom_target_ra_label': "Right Ascension (RA):",
        'custom_target_dec_label': "Declination (Dec):",
        'custom_target_name_label': "Target Name (Optional):",
        'custom_target_ra_placeholder': "e.g., 10:45:03.6 or 161.265",
        'custom_target_dec_placeholder': "e.g., -16:42:58 or -16.716",
        'custom_target_button': "Generate Custom Graph",
        'custom_target_error_coords': "Invalid RA/Dec format. Use HH:MM:SS.s / DD:MM:SS or decimal degrees.",
        'custom_target_error_window': "Cannot generate graph. Ensure location is set and observation window is calculated (click 'Find Observable Objects' first if needed).",
        'error_processing_object': "Error processing {}: {}",
        'window_calc_error': "Error calculating observation window: {}\n{}",
        'window_fallback_info': "\nUsing fallback window: {} to {} UTC",
        # Removed unused window messages
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
        'object_type_glossary_title': "Objekttyp-Glossar",
        'object_type_glossary': {
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
        'window_info_template': "Beobachtungsfenster: {} bis {} UTC (Astronomische Dämmerung)", # Updated template
        'error_no_window': "Kein gültiges astronomisches Dämmerungsfenster für gewähltes Datum und Ort gefunden.", # More specific
        'error_polar_night': "Astronomische Dunkelheit dauert >24h an (Polarnacht?). Nutze Fallback-Fenster.", # NEU
        'error_polar_day': "Keine astronomische Dunkelheit vorhanden (Polartag?). Nutze Fallback-Fenster.", # NEU
        'success_objects_found': "{} passende Objekte gefunden.",
        'info_showing_list_duration': "Anzeige von {} Objekten, sortiert nach Sichtbarkeitsdauer und max. Höhe:",
        'info_showing_list_magnitude': "Anzeige von {} Objekten, sortiert nach Helligkeit (hellste zuerst):",
        'error_search_unexpected': "Unerwarteter Fehler während der Suche:",
        'results_list_header': "Ergebnisliste",
        'results_export_name': "Name",
        'results_export_type': "Typ",
        'results_export_constellation': "Sternbild",
        'results_export_mag': "Magnitude",
        'results_export_ra': "RA",
        'results_export_dec': "Dec",
        'results_export_max_alt': "Max Höhe (°)",
        'results_export_az_at_max': "Azimut bei Max (°)",
        'results_export_direction_at_max': "Richtung bei Max",
        'results_export_time_max_utc': "Zeit bei Max (UTC)",
        'results_export_time_max_local': "Zeit bei Max (Lokale ZZ)",
        'results_export_cont_duration': "Max. kont. Dauer (h)",
        'results_expander_title': "{} ({}) - Mag: {:.1f}",
        'results_coords_header': "**Details:**",
        'results_constellation_label': "Sternbild:",
        'results_max_alt_header': "**Max. Höhe:**",
        'results_azimuth_label': "(Azimut: {:.1f}°{})",
        'results_direction_label': ", Richtung: {}",
        'results_best_time_header': "**Beste Zeit (Lokale ZZ):**",
        'results_cont_duration_header': "**Max. kont. Dauer:**",
        'results_duration_value': "{:.1f} Stunden",
        'graph_type_label': "Grafik-Typ (für alle Grafiken):", # Renamed & Clarified scope
        'graph_type_sky_path': "Himmelsbahn (Az/Alt)", # Renamed
        'graph_type_alt_time': "Höhenverlauf (Alt/Zeit)", # Renamed
        'results_graph_button': "📈 Grafik anzeigen", # Renamed
        'results_spinner_plotting': "Erstelle Grafik...", # Renamed
        'results_graph_error': "Grafik Fehler: {}", # Renamed
        'results_graph_not_created': "Grafik konnte nicht erstellt werden.", # Renamed
        'results_close_graph_button': "Grafik schliessen", # Renamed
        'results_save_csv_button': "💾 Ergebnisliste als CSV speichern",
        'results_csv_filename': "dso_beobachtungsliste_{}.csv",
        'results_csv_export_error': "CSV Export Fehler: {}",
        'warning_no_objects_found': "Keine Objekte gefunden, die allen Kriterien für das berechnete Beobachtungsfenster entsprechen.",
        'info_initial_prompt': "Willkommen! Bitte **Koordinaten eingeben** oder **Ort suchen**, um die Objektsuche zu aktivieren.",
        'graph_altitude_label': "Höhe (°)",
        'graph_azimuth_label': "Azimut (°)",
        'graph_min_altitude_label': "Mindesthöhe ({:.0f}°)",
        'graph_title_sky_path': "Himmelsbahn für {}",
        'graph_title_alt_time': "Höhenverlauf für {}",
        'graph_ylabel': "Höhe (°)",
        'custom_target_expander': "Eigenes Ziel grafisch darstellen", # NEU
        'custom_target_ra_label': "Rektaszension (RA):", # NEU
        'custom_target_dec_label': "Deklination (Dec):", # NEU
        'custom_target_name_label': "Ziel-Name (Optional):", # NEU
        'custom_target_ra_placeholder': "z.B. 10:45:03.6 oder 161.265", # NEU
        'custom_target_dec_placeholder': "z.B. -16:42:58 oder -16.716", # NEU
        'custom_target_button': "Eigene Grafik erstellen", # NEU
        'custom_target_error_coords': "Ungültiges RA/Dec Format. Verwende HH:MM:SS.s / DD:MM:SS oder Dezimalgrad.", # NEU
        'custom_target_error_window': "Grafik kann nicht erstellt werden. Stelle sicher, dass Ort und Zeitfenster gültig sind (ggf. zuerst 'Beobachtbare Objekte finden' klicken).", # NEU
        'error_processing_object': "Fehler bei Verarbeitung von {}: {}",
        'window_calc_error': "Fehler bei der Berechnung des Beobachtungsfensters: {}\n{}",
        'window_fallback_info': "\nVerwende Fallback-Fenster: {} bis {} UTC",
        # Removed unused window messages
        'error_loading_catalog': "Fehler beim Laden der Katalogdatei: {}",
        'info_catalog_loaded': "Katalog geladen: {} Objekte.",
        'warning_catalog_empty': "Katalogdatei geladen, aber keine passenden Objekte nach Filterung gefunden.",
     },
     'fr': {
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
        'direction_option_all': "Toutes",
        'moon_warning_header': "**Avertissement Lunaire**",
        'moon_warning_label': "Avertir si Lune > (% Illumination) :",
        'object_types_header': "**Types d'Objets**",
        'object_types_error_extract': "Impossible d'extraire les types d'objets du catalogue.",
        'object_types_label': "Filtrer les types (laisser vide pour tous) :",
        'object_type_glossary_title': "Glossaire des types d'objets",
        'object_type_glossary': {
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
        'window_info_template': "Fenêtre d'observation : {} à {} UTC (Crépuscule Astronomique)", # Updated template
        'error_no_window': "Aucune fenêtre d'obscurité astronomique valide trouvée pour la date et le lieu sélectionnés.", # More specific
        'error_polar_night': "L'obscurité astronomique persiste >24h (nuit polaire ?). Utilisation de la fenêtre de repli.", # NEU
        'error_polar_day': "Aucune obscurité astronomique (jour polaire ?). Utilisation de la fenêtre de repli.", # NEU
        'success_objects_found': "{} objets correspondants trouvés.",
        'info_showing_list_duration': "Affichage de {} objets, triés par durée de visibilité et altitude maximale :",
        'info_showing_list_magnitude': "Affichage de {} objets, triés par luminosité (les plus brillants d'abord) :",
        'error_search_unexpected': "Une erreur inattendue s'est produite lors de la recherche :",
        'results_list_header': "Liste des Résultats",
        'results_export_name': "Nom",
        'results_export_type': "Type",
        'results_export_constellation': "Constellation",
        'results_export_mag': "Magnitude",
        'results_export_ra': "AD",
        'results_export_dec': "Dec",
        'results_export_max_alt': "Altitude Max (°)",
        'results_export_az_at_max': "Azimut au Max (°)",
        'results_export_direction_at_max': "Direction au Max",
        'results_export_time_max_utc': "Heure au Max (UTC)",
        'results_export_time_max_local': "Heure au Max (FH Local)",
        'results_export_cont_duration': "Durée Cont. Max (h)",
        'results_expander_title': "{} ({}) - Mag : {:.1f}",
        'results_coords_header': "**Détails :**",
        'results_constellation_label': "Constellation :",
        'results_max_alt_header': "**Altitude Max. :**",
        'results_azimuth_label': "(Azimut : {:.1f}°{})",
        'results_direction_label': ", Direction : {}",
        'results_best_time_header': "**Meilleure Heure (FH Local) :**",
        'results_cont_duration_header': "**Durée Cont. Max. :**",
        'results_duration_value': "{:.1f} heures",
        'graph_type_label': "Type de Graphique (pour tous) :", # Clarified scope
        'graph_type_sky_path': "Tracé Céleste (Az/Alt)",
        'graph_type_alt_time': "Altitude/Temps",
        'results_graph_button': "📈 Afficher le graphique",
        'results_spinner_plotting': "Création du graphique...",
        'results_graph_error': "Erreur du graphique : {}",
        'results_graph_not_created': "Le graphique n'a pas pu être créé.",
        'results_close_graph_button': "Fermer le graphique",
        'results_save_csv_button': "💾 Enregistrer la liste en CSV",
        'results_csv_filename': "dso_liste_observation_{}.csv",
        'results_csv_export_error': "Erreur d'exportation CSV : {}",
        'warning_no_objects_found': "Aucun objet trouvé correspondant à tous les critères pour la fenêtre d'observation calculée.",
        'info_initial_prompt': "Bienvenue ! Veuillez **entrer des coordonnées** manuellement ou **rechercher un nom de lieu** pour activer la recherche principale.",
        'graph_altitude_label': "Altitude (°)",
        'graph_azimuth_label': "Azimut (°)",
        'graph_min_altitude_label': "Altitude Min. ({:.0f}°)",
        'graph_title_sky_path': "Tracé Céleste pour {}",
        'graph_title_alt_time': "Profil d'Altitude pour {}",
        'graph_ylabel': "Altitude (°)",
        'custom_target_expander': "Tracer une cible personnalisée", # NEU
        'custom_target_ra_label': "Ascension Droite (AD) :", # NEU
        'custom_target_dec_label': "Déclinaison (Dec) :", # NEU
        'custom_target_name_label': "Nom de la cible (Optionnel) :", # NEU
        'custom_target_ra_placeholder': "ex : 10:45:03.6 ou 161.265", # NEU
        'custom_target_dec_placeholder': "ex : -16:42:58 ou -16.716", # NEU
        'custom_target_button': "Générer le graphique personnalisé", # NEU
        'custom_target_error_coords': "Format AD/Dec invalide. Utilisez HH:MM:SS.s / DD:MM:SS ou degrés décimaux.", # NEU
        'custom_target_error_window': "Impossible de générer le graphique. Assurez-vous que le lieu est défini et que la fenêtre d'observation est calculée (cliquez sur 'Trouver les Objets Observables' si nécessaire).", # NEU
        'error_processing_object': "Erreur lors du traitement de {}: {}",
        'window_calc_error': "Erreur lors du calcul de la fenêtre d'observation : {}\n{}",
        'window_fallback_info': "\nUtilisation de la fenêtre de repli : {} à {} UTC",
        # Removed unused window messages
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
        'plot_object_name': None, # Name of the object whose plot is shown from results
        'show_plot': False, # Flag to show plot from results list
        'active_result_plot_data': None, # Data for the currently shown result plot
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
        # Plot state
        'plot_type_selection': 'Sky Path', # Default plot type
        # Custom Target State
        'custom_target_ra': "",
        'custom_target_dec': "",
        'custom_target_name': "",
        'custom_target_error': "",
        'custom_target_plot_data': None, # Stores data needed to replot custom target
        'show_custom_plot': False, # Flag to show custom plot area
        # Other state
        'expanded_object_name': None, # Tracks which result expander is open
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

# --- Updated Observation Window Calculation using Astroplan ---
def get_observable_window(observer: 'Observer', reference_time: 'Time', is_now: bool, lang: str) -> tuple['Time' | None, 'Time' | None, str]:
    """Calculates the astronomical twilight window using astroplan."""
    t = translations[lang]
    status_message = ""
    start_time, end_time = None, None

    # Define the time for calculation (use noon for specific date, now otherwise)
    calc_time = reference_time

    try:
        # Ensure observer object is valid
        if not isinstance(observer, Observer):
             raise TypeError(f"Expected astroplan.Observer, got {type(observer)}")

        # Find the next evening astronomical twilight
        # *** FIX: Removed horizon argument ***
        astro_set = observer.twilight_evening_astronomical(calc_time, which='next')

        # Find the next morning astronomical twilight *after* the evening twilight
        # *** FIX: Removed horizon argument ***
        astro_rise = observer.twilight_morning_astronomical(astro_set, which='next')

        # Check if calculated times are valid
        if astro_set is None or astro_rise is None or astro_rise <= astro_set:
             # This might happen in polar regions or if calculation fails
             raise ValueError("Could not determine valid twilight times.")

        start_time = astro_set
        end_time = astro_rise

        # --- Adjust window based on 'is_now' ---
        current_utc_time = Time.now()
        if is_now and start_time < current_utc_time:
            start_time = current_utc_time

        # If the entire calculated window has passed for 'Now', calculate for the next night
        if is_now and end_time < current_utc_time:
            status_message = t['window_already_passed'] + "\n"
            # Recalculate for the next day's midnight
            return get_observable_window(observer, current_utc_time + timedelta(days=1), True, lang)

        # Format times for status message
        start_fmt = start_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')
        end_fmt = end_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')
        status_message += t['window_info_template'].format(start_fmt, end_fmt)

    except ValueError as ve: # Catch specific astroplan errors or our ValueError
        # Handle cases where twilight events might not occur (polar day/night)
        # Check if sun is always up or always down
        try:
            # Check using -18 deg horizon for astronomical night
            is_currently_night = observer.is_night(reference_time, horizon=-18*u.deg)
            if is_currently_night: # Check if it's currently dark
                # Potentially polar night (sun never rises high enough)
                status_message = t['error_polar_night']
            else:
                # Potentially polar day (sun never sets low enough)
                 status_message = t['error_polar_day']
        except Exception as check_e: # Error during is_night check
             print(f"Error checking is_night: {check_e}")
             status_message = t['window_calc_error'].format(ve, "") # Show original error

        print(f"Astroplan ValueError calculating window: {ve}")
        start_time, end_time = _get_fallback_window(reference_time)
        status_message += t['window_fallback_info'].format(start_time.iso, end_time.iso)

    except Exception as e:
        # General error during calculation
        status_message = t['window_calc_error'].format(e, traceback.format_exc())
        start_time, end_time = _get_fallback_window(reference_time)
        status_message += t['window_fallback_info'].format(start_time.iso, end_time.iso)

    # Final check if start/end times are valid before returning
    if start_time is None or end_time is None or end_time <= start_time:
        if not status_message or "Error" not in status_message: # Add error if not already present
             status_message += "\n" + t['error_no_window']
        # Ensure fallback is used if times are invalid
        start_time, end_time = _get_fallback_window(reference_time)
        if "fallback" not in status_message.lower(): # Avoid duplicate fallback message
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
    Finds DSOs from the catalog DataFrame visible during the observing_times.
    Calculates max continuous visibility duration within the dark window.
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
    # Calculate time step duration in hours for duration calculation
    time_step_duration = (observing_times[1] - observing_times[0]).to(u.hour).value if len(observing_times) > 1 else 0

    for index, row in df_catalog.iterrows():
        name = row['Name']; ra_str = row['RA_str']; dec_str = row['Dec_str']
        mag = row['Mag']; obj_type = row['Type']
        # Constellation is fetched using astropy below

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
            # Get full constellation name using astropy
            constellation_full = get_constellation(target)

            target_altaz = target.transform_to(altaz_frame)
            altitudes = target_altaz.alt
            azimuths = target_altaz.az

            # Find indices where object is above minimum altitude *within the observing_times array*
            valid_indices = np.where(altitudes >= min_altitude_limit)[0]

            if len(valid_indices) > 0:
                # Find peak altitude within the valid period
                peak_in_window_index = valid_indices[np.argmax(altitudes[valid_indices])]
                peak_alt_val = altitudes[peak_in_window_index].to(u.deg).value
                peak_az_val = azimuths[peak_in_window_index].to(u.deg).value
                peak_direction = azimuth_to_direction(peak_az_val)
                peak_time = observing_times[peak_in_window_index]

                # --- Calculate Max Continuous Duration (within the dark window) ---
                # This duration represents how long the object is continuously above
                # min_altitude_limit *during the calculated observation window*.
                max_cont_duration_hours = 0.0
                if time_step_duration > 0:
                    # Find breaks in consecutive indices (where difference > 1)
                    diffs = np.diff(valid_indices)
                    splits = np.where(diffs > 1)[0] + 1
                    # Split the valid_indices into blocks of continuous visibility
                    blocks = np.split(valid_indices, splits)
                    for block in blocks:
                        block_len = len(block)
                        if block_len > 1:
                            # Duration = time of last point in block - time of first point in block
                            duration = observing_times[block[-1]] - observing_times[block[0]]
                            # Add one time step to account for the duration of the last interval
                            current_block_duration_hours = duration.to(u.hour).value + time_step_duration
                        elif block_len == 1:
                             # Single point visibility, duration is approx one time step
                             current_block_duration_hours = time_step_duration
                        else: # Empty block
                            current_block_duration_hours = 0.0
                        # Keep track of the longest single block
                        max_cont_duration_hours = max(max_cont_duration_hours, current_block_duration_hours)

                # Apply a cap to prevent unrealistically long durations (e.g., >16h)
                capped_max_cont_duration = min(max_cont_duration_hours, MAX_REALISTIC_NIGHT_DURATION)

                observable_objects.append({
                    "name": name, "type": obj_type, "magnitude": mag,
                    "constellation": constellation_full, # Use full name
                    "ra_str": ra_str, "dec_str": dec_str,
                    "ra": target.ra.to_string(unit=u.hour, sep='hms', precision=1),
                    "dec": target.dec.to_string(unit=u.deg, sep='dms', precision=0),
                    "peak_alt": peak_alt_val, "peak_az": peak_az_val, "peak_direction": peak_direction,
                    "peak_time_utc": peak_time.iso,
                    "cont_duration_hours": capped_max_cont_duration, # Use capped value
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

# --- Plot Function: Altitude vs Time ---
# Renamed from original plot_altitude
def plot_altitude_time(_obj_data: dict, _location_tuple: tuple, lang: str, tz_name: str):
    """Creates a Matplotlib Altitude vs Time graph."""
    t = translations[lang]
    if plt is None or mdates is None or pytz is None:
        st.error("Plotting libraries (matplotlib, pytz) not available.")
        return None

    fig, ax = plt.subplots()
    try:
        times = Time(_obj_data['times_jd'], format='jd')
        altitudes = _obj_data['altitudes']
        min_alt_limit = _obj_data['min_alt_limit']

        # --- Timezone Conversion for X-axis ---
        try:
            selected_tz = pytz.timezone(tz_name)
            times_local_dt = [t_inst.to_datetime(timezone=selected_tz) for t_inst in times]
            xlabel = f"Time ({tz_name})" # Use the actual tz_name used
        except Exception as tz_err:
             print(f"Timezone conversion/lookup error in graph for '{tz_name}': {tz_err}. Falling back to UTC.")
             times_local_dt = times.datetime # Use UTC datetime objects
             xlabel = "Time (UTC)"

        # --- Plotting Data ---
        ax.plot(times_local_dt, altitudes, label=t['graph_altitude_label'], color='#00C0F0') # Cyan line
        ax.axhline(min_alt_limit, color='#FF6347', linestyle='--', label=t['graph_min_altitude_label'].format(min_alt_limit)) # Tomato color

        # --- Axis Setup ---
        ax.set_ylim(0, 90)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(t['graph_ylabel'])
        ax.set_title(t['graph_title_alt_time'].format(_obj_data['name'])) # Specific title
        ax.legend()
        ax.grid(True, linestyle=':', linewidth=0.5, color='#666666')

        # --- Formatting X-axis ---
        xfmt = mdates.DateFormatter('%H:%M')
        ax.xaxis.set_major_formatter(xfmt)
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1)) # Tick every hour
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        plt.tight_layout()

    except Exception as e:
        print(f"Error plotting altitude/time for {_obj_data.get('name', 'Unknown')}: {e}")
        st.error(t['results_graph_error'].format(e)) # Show error in UI
        plt.close(fig) # Ensure figure is closed on error
        return None
    return fig


# --- Updated Plot Function for Azimuth vs Altitude ---
def plot_sky_path(_obj_data: dict, _location_tuple: tuple, lang: str, tz_name: str):
    """Creates a Matplotlib Azimuth vs Altitude graph with time markers."""
    t = translations[lang]
    if plt is None or mdates is None or pytz is None:
        st.error("Plotting libraries (matplotlib, pytz) not available.")
        return None

    fig, ax = plt.subplots()
    try:
        # Extract data
        times = Time(_obj_data['times_jd'], format='jd')
        altitudes = _obj_data['altitudes']
        azimuths = _obj_data['azimuths']
        min_alt_limit = _obj_data['min_alt_limit']

        # Filter data to only include points above the minimum altitude
        valid_plot_indices = np.where(altitudes >= min_alt_limit)[0]
        if len(valid_plot_indices) == 0:
             st.warning("Object does not rise above minimum altitude during the observation window.")
             plt.close(fig)
             return None

        plot_times = times[valid_plot_indices]
        plot_altitudes = altitudes[valid_plot_indices]
        plot_azimuths = azimuths[valid_plot_indices]

        # --- Timezone Conversion for Markers ---
        times_local_dt = []
        try:
            selected_tz = pytz.timezone(tz_name)
            times_local_dt = [t_inst.to_datetime(timezone=selected_tz) for t_inst in plot_times]
        except Exception as tz_err:
             print(f"Timezone conversion/lookup error in graph for '{tz_name}': {tz_err}. Using UTC for markers.")
             # Fallback to UTC datetimes if conversion fails
             times_local_dt = [t_inst.to_datetime(timezone=timezone.utc) for t_inst in plot_times]
             tz_name = "UTC" # Ensure label reflects fallback


        # --- Plotting Data ---
        # Use scatter plot with color mapped to azimuth (inverted)
        # viridis_r: starts bright (low az), goes dark (high az)
        scatter = ax.scatter(plot_azimuths, plot_altitudes, c=plot_azimuths, cmap='viridis_r', s=25, zorder=3, alpha=0.8)

        # Add a color bar for the azimuth
        cbar = fig.colorbar(scatter, ax=ax, orientation='vertical', fraction=0.046, pad=0.04)
        cbar.set_label('Azimuth (°)')

        # --- Add Time Markers (hourly) ---
        last_hour = -1
        for i, dt_local in enumerate(times_local_dt):
            current_hour = dt_local.hour
            # Add marker roughly every hour (or at start/end)
            # Mark near top of the hour (e.g., minute < 10)
            if i == 0 or i == len(times_local_dt) - 1 or (current_hour != last_hour and dt_local.minute < 10):
                time_str = dt_local.strftime('%H:%M')
                # Add text with a semi-transparent background
                ax.text(plot_azimuths[i], plot_altitudes[i] + 0.5, time_str, fontsize=9, # Slightly offset Y
                        ha='center', va='bottom', color='white', # White text
                        bbox=dict(facecolor='black', alpha=0.7, pad=0.2, edgecolor='none')) # Background box
                last_hour = current_hour

        # Add minimum altitude line
        ax.axhline(min_alt_limit, color='#FF6347', linestyle='--', label=t['graph_min_altitude_label'].format(min_alt_limit)) # Tomato color

        # --- Axis Setup ---
        ax.set_xlabel(t['graph_azimuth_label'])
        ax.set_ylabel(t['graph_altitude_label'])
        ax.set_title(t['graph_title_sky_path'].format(_obj_data['name'])) # Specific title
        ax.set_xlim(0, 360)
        ax.set_ylim(0, 90)

        # Add cardinal directions to X-axis
        ax.set_xticks([0, 90, 180, 270, 360])
        ax.set_xticklabels(['N', 'E', 'S', 'W', 'N'])

        ax.legend()
        ax.grid(True, linestyle=':', linewidth=0.5, color='#666666') # Slightly brighter grid
        plt.tight_layout()

    except Exception as e:
        print(f"Error plotting sky path for {_obj_data.get('name', 'Unknown')}: {e}")
        st.error(t['results_graph_error'].format(e)) # Use renamed key
        plt.close(fig) # Ensure figure is closed on error
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
    # Base required columns for core functionality
    required_cols = ['Name', 'RA', 'Dec', 'Type']
    # Optional columns for magnitude
    mag_cols = ['V-Mag', 'B-Mag', 'Mag']
    # Constellation column is no longer loaded/used here

    try:
        if not os.path.exists(catalog_path):
             # Use translated error message
             st.error(f"{t_load['error_loading_catalog'].split(':')[0]}: File not found at {catalog_path}")
             st.info("Please ensure the file 'ongc.csv' is in the same directory as the Python script.")
             return None
        df = pd.read_csv(catalog_path, sep=';', comment='#', low_memory=False)

        # --- Check for required columns ---
        missing_req_cols = [col for col in required_cols if col not in df.columns]
        if missing_req_cols:
            st.error(f"Missing required columns in catalog: {', '.join(missing_req_cols)}")
            return None

        # --- Find available magnitude column ---
        mag_col_found = None
        for col in mag_cols:
            if col in df.columns:
                mag_col_found = col
                break
        if mag_col_found is None:
            st.error(f"Magnitude column ('V-Mag', 'B-Mag' or 'Mag') not found.")
            return None
        df = df.rename(columns={mag_col_found: 'Mag'}) # Rename to standard 'Mag'

        # --- Filter by Object Type ---
        dso_types = ['Galaxy', 'Globular Cluster', 'Open Cluster', 'Nebula',
                     'Planetary Nebula', 'Supernova Remnant', 'HII', 'Emission Nebula',
                     'Reflection Nebula', 'Cluster + Nebula', 'Gal', 'GCl', 'Gx', 'OC',
                     'PN', 'SNR', 'Neb', 'EmN', 'RfN', 'C+N', 'Gxy', 'AGN', 'MWSC']
        type_pattern = '|'.join(dso_types)
        df_filtered = df[df['Type'].astype(str).str.contains(type_pattern, case=False, na=False)].copy()

        # --- Process Magnitude ---
        df_filtered['Mag'] = pd.to_numeric(df_filtered['Mag'], errors='coerce')
        df_filtered.dropna(subset=['Mag'], inplace=True)

        # --- Process Coordinates ---
        df_filtered['RA_str'] = df_filtered['RA'].astype(str)
        df_filtered['Dec_str'] = df_filtered['Dec'].astype(str)
        df_filtered.dropna(subset=['RA_str', 'Dec_str'], inplace=True)
        df_filtered = df_filtered[df_filtered['RA_str'].str.strip() != '']
        df_filtered = df_filtered[df_filtered['Dec_str'].str.strip() != '']

        # --- Select Final Columns (Constellation no longer needed from CSV) ---
        final_cols = ['Name', 'RA_str', 'Dec_str', 'Mag', 'Type']

        df_final = df_filtered[final_cols].copy()
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
# Updated colors for a more modern dark theme
st.markdown("""
<style>
    /* Base */
    .main .block-container {
        background-color: #1a1a1a; /* Darker background */
        color: #e0e0e0; /* Slightly softer white text */
        border-radius: 10px;
        padding: 2rem;
    }
    /* Primary Button */
    div[data-testid="stButton"] > button:not([kind="secondary"]) {
        background-image: linear-gradient(to right, #087990, #055160); /* Teal gradient */
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition-duration: 0.4s;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stButton"] > button:not([kind="secondary"]):hover {
        background-image: linear-gradient(to right, #055160, #032a31); /* Darker teal on hover */
        color: white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    /* Secondary Button */
     div[data-testid="stButton"] > button[kind="secondary"] {
         background-color: #4a4a4a; /* Dark grey */
         color: #e0e0e0;
         border: 1px solid #666;
     }
     div[data-testid="stButton"] > button[kind="secondary"]:hover {
         background-color: #5a5a5a;
         color: white;
         border: 1px solid #888;
     }
     /* Form Submit Button (uses primary style by default, but can be customized) */
    div[data-testid="stFormSubmitButton"] > button {
        margin-top: 28px; /* Keep alignment */
        /* background-image: linear-gradient(to right, #5a189a, #3c096c); */ /* Example: Purple gradient */
    }
    /* Expander Header */
    .streamlit-expanderHeader {
        background-color: #282828; /* Slightly lighter dark grey */
        color: #e0e0e0;
        border-radius: 5px;
        border-bottom: 1px solid #444; /* Subtle border */
    }
    /* Metric Box */
    div[data-testid="stMetric"] {
        background-color: #2c2c2c; /* Consistent dark element background */
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #444;
    }
    div[data-testid="stMetric"] > div[data-testid="stMetricLabel"] {
        color: #aaaaaa;
    }
    /* Input widgets */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stDateInput"] input,
    div[data-testid="stSelectbox"] div[role="button"] {
        background-color: #2c2c2c;
        color: #e0e0e0;
        border: 1px solid #555;
    }
    /* Slider track */
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #555;
    }

</style>
""", unsafe_allow_html=True)

# --- Title ---
# Static English Title
st.title("Advanced DSO Finder")

# --- Object Type Glossary (Moved near top) ---
with st.expander(t['object_type_glossary_title']):
    glossary_items = t.get('object_type_glossary', {}) # Use .get for safety
    # Use Streamlit columns for better layout
    col1, col2 = st.columns(2)
    col_index = 0
    sorted_items = sorted(glossary_items.items()) # Sort alphabetically by abbreviation
    for abbr, full_name in sorted_items:
        if col_index % 2 == 0:
            col1.markdown(f"**{abbr}:** {full_name}")
        else:
            col2.markdown(f"**{abbr}:** {full_name}")
        col_index += 1

st.markdown("---") # Add separator after glossary

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
    # Location expander starts expanded
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
                # Use astroplan.Observer which holds the EarthLocation
                current_location_for_run = Observer(latitude=current_lat * u.deg, longitude=current_lon * u.deg, elevation=current_height * u.m)
                location_is_valid_for_run = True # Valid Observer created

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

            except Exception as e: # Error creating Observer
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


    # --- Time & Timezone Settings (Starts collapsed) ---
    with st.expander(t['time_expander'], expanded=False):
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


    # --- Filter Settings (Starts collapsed) ---
    with st.expander(t['filters_expander'], expanded=False):
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
        min_altitude_deg_widget = st.slider(t['min_alt_label'], min_value=5, max_value=45, key='min_alt_slider', step=1)
        # min_altitude_limit calculation moved to main search block

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


    # --- Result Options (Starts collapsed) ---
    with st.expander(t['results_options_expander'], expanded=False):
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

# --- Custom Target Plotter ---
with st.expander(t['custom_target_expander']):
    col_ra, col_dec, col_name = st.columns(3)
    with col_ra:
        st.text_input(t['custom_target_ra_label'], key='custom_target_ra', placeholder=t['custom_target_ra_placeholder'])
    with col_dec:
        st.text_input(t['custom_target_dec_label'], key='custom_target_dec', placeholder=t['custom_target_dec_placeholder'])
    with col_name:
        st.text_input(t['custom_target_name_label'], key='custom_target_name', placeholder="e.g., M42")

    custom_target_button_pressed = st.button(t['custom_target_button'])
    custom_target_error_placeholder = st.empty() # For errors specific to this section

    if custom_target_button_pressed:
        st.session_state.custom_target_error = "" # Clear previous errors
        st.session_state.custom_target_plot_data = None # Clear previous custom plot data
        st.session_state.show_custom_plot = False # Hide plot area initially

        custom_ra_str = st.session_state.custom_target_ra
        custom_dec_str = st.session_state.custom_target_dec
        custom_name = st.session_state.custom_target_name or "Custom Target"

        if not custom_ra_str or not custom_dec_str:
            st.session_state.custom_target_error = "RA and Dec cannot be empty."
        elif not location_is_valid_for_run:
            st.session_state.custom_target_error = t['custom_target_error_window']
        else:
            try:
                # Validate/Parse RA/Dec
                # Try parsing as sexagesimal first, then decimal
                try:
                    custom_target_coord = SkyCoord(ra=custom_ra_str, dec=custom_dec_str, unit=(u.hourangle, u.deg))
                except ValueError:
                    custom_target_coord = SkyCoord(ra=custom_ra_str, dec=custom_dec_str, unit=(u.deg, u.deg))

                # Get current observation window
                # Recalculate window based on current settings to be sure
                start_time, end_time, window_msg = get_observable_window(current_location_for_run, reference_time, is_time_now, lang)

                if start_time and end_time and start_time < end_time:
                    time_delta_hours = (end_time - start_time).to(u.hour).value
                    num_time_steps = max(30, int(time_delta_hours * 12))
                    observing_times = Time(np.linspace(start_time.jd, end_time.jd, num_time_steps), format='jd', scale='utc')

                    # Calculate Alt/Az path
                    altaz_frame = AltAz(obstime=observing_times, location=current_location_for_run.location)
                    target_altaz = custom_target_coord.transform_to(altaz_frame)

                    # Prepare data for plotting function and store in state
                    st.session_state.custom_target_plot_data = {
                        "name": custom_name,
                        "times_jd": observing_times.jd,
                        "altitudes": target_altaz.alt.to(u.deg).value,
                        "azimuths": target_altaz.az.to(u.deg).value,
                        "min_alt_limit": st.session_state.min_alt_slider # Use current slider value
                    }
                    st.session_state.show_custom_plot = True # Set flag to show plot area
                    st.session_state.show_plot = False # Hide main results plot if shown
                    st.session_state.expanded_object_name = None # Collapse main results
                    st.session_state.active_result_plot_data = None # Clear active result plot data
                    st.session_state.plot_object_name = None

                else: # No valid window
                     st.session_state.custom_target_error = window_msg or t['error_no_window']

            except ValueError as e:
                st.session_state.custom_target_error = f"{t['custom_target_error_coords']} ({e})"
            except Exception as e:
                st.session_state.custom_target_error = f"Error calculating custom target path: {e}"
                st.exception(e) # Print full traceback for debugging

        # Display error if any occurred
        if st.session_state.custom_target_error:
             custom_target_error_placeholder.error(st.session_state.custom_target_error)
        else:
             custom_target_error_placeholder.empty() # Clear placeholder if successful
             # Use rerun to ensure the plot area below updates immediately after button press
             st.rerun()


# --- Global Plot Type Selector (Moved outside results list) ---
st.markdown("---") # Separator
plot_type_options = {
    'Sky Path': t['graph_type_sky_path'],
    'Altitude/Time': t['graph_type_alt_time']
}
# Ensure current selection is valid, default to Sky Path
if st.session_state.plot_type_selection not in plot_type_options:
    st.session_state.plot_type_selection = 'Sky Path'

st.radio(
    t['graph_type_label'], # Use renamed key
    options=list(plot_type_options.keys()),
    format_func=lambda key: plot_type_options[key],
    key='plot_type_selection', # Update state directly
    horizontal=True
)
# This radio button changing will trigger a rerun, updating the visible plot below


# --- Generate and Store Active Plot Figure (Custom or Result) ---
# This section runs on every rerun, including when the radio button changes
active_plot_fig = None # Initialize fig variable for this run
plot_data_to_use = None
plot_func = plot_sky_path if st.session_state.plot_type_selection == 'Sky Path' else plot_altitude_time

# Determine which data to use for plotting (custom or result)
if st.session_state.show_custom_plot and st.session_state.custom_target_plot_data is not None:
    plot_data_to_use = st.session_state.custom_target_plot_data
elif st.session_state.show_plot and st.session_state.active_result_plot_data is not None:
    plot_data_to_use = st.session_state.active_result_plot_data

# Generate the plot if data is available
if plot_data_to_use is not None:
    location_tuple = (
        current_location_for_run.location.lat.deg,
        current_location_for_run.location.lon.deg,
        current_location_for_run.location.height.value
    ) if current_location_for_run else None

    if plt and plot_func and location_tuple:
        # No spinner here, as it runs on every interaction with the radio button
        active_plot_fig = plot_func(
            plot_data_to_use,
            location_tuple,
            lang,
            st.session_state.selected_timezone
        )


# --- Display Custom Target Plot Area ---
custom_plot_area = st.container() # Container to hold the custom plot
if st.session_state.show_custom_plot:
    with custom_plot_area:
        if active_plot_fig:
            st.pyplot(active_plot_fig)
            if st.button(t['results_close_graph_button'], key="close_custom_graph", type="secondary"):
                st.session_state.show_custom_plot = False
                st.session_state.custom_target_plot_data = None
                st.rerun() # Rerun to clear the plot
        else:
            # Handle case where plot generation failed but should be shown
            st.warning(t['results_graph_not_created'])


# --- Main Search Button & Logic ---
find_disabled = not location_is_valid_for_run or df_catalog_data is None or df_catalog_data.empty
if st.button(t['find_button_label'], key="find_button", type="primary", use_container_width=True, disabled=find_disabled):

    st.session_state.expanded_object_name = None
    st.session_state.show_plot = False # Hide result plot area
    st.session_state.plot_object_name = None
    st.session_state.active_result_plot_data = None # Clear active result plot data
    st.session_state.show_custom_plot = False # Hide custom plot area
    st.session_state.custom_target_plot_data = None # Clear custom plot data

    # Re-check conditions (redundant with disabled state but safe)
    if not location_is_valid_for_run:
         st.error(t[f'location_error_{st.session_state.location_choice_key.lower()}_search'] if st.session_state.location_choice_key != 'Default' else t['location_error_undefined'])
    elif current_location_for_run is None or not isinstance(current_location_for_run, Observer): # Check type
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
                # Pass the astroplan Observer object
                start_time, end_time, window_msg = get_observable_window(current_location_for_run, reference_time, is_time_now, lang)
                if window_msg:
                    formatted_window_msg = window_msg.replace("\n", "\n\n")
                    if "Warning" in window_msg or "Warnung" in window_msg or "Error" in window_msg or "Fehler" in window_msg or "invalid" in window_msg or "polar" in window_msg.lower():
                         window_info_placeholder.warning(formatted_window_msg)
                    else:
                         window_info_placeholder.info(formatted_window_msg)

                if start_time and end_time and start_time < end_time:
                    time_delta_hours = (end_time - start_time).to(u.hour).value
                    # Ensure a minimum number of steps even for short windows
                    num_time_steps = max(30, int(time_delta_hours * 12)) # ~5 min steps
                    observing_times = Time(np.linspace(start_time.jd, end_time.jd, num_time_steps), format='jd', scale='utc')

                    magnitude_filter_mode_calc = st.session_state.mag_filter_mode_exp
                    min_mag_calc = st.session_state.manual_min_mag_slider
                    max_mag_calc = st.session_state.manual_max_mag_slider
                    bortle_calc = st.session_state.bortle_slider # Use state key
                    # Calculate min altitude limit here, using the state value
                    min_alt_limit_calc = st.session_state.min_alt_slider * u.deg

                    # Pass Observer's location to find_observable_objects
                    all_found_objects = find_observable_objects(
                        current_location_for_run.location, observing_times, min_alt_limit_calc,
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
                    # Sort primarily by CONT duration, secondarily by peak altitude
                    objects_after_direction_filter.sort(key=lambda x: (x.get('cont_duration_hours', 0), x.get('peak_alt', 0)), reverse=True)
                    info_message = t['info_showing_list_duration']
                elif sort_method == 'Brightness':
                    objects_after_direction_filter.sort(key=lambda x: x['magnitude'])
                    info_message = t['info_showing_list_magnitude']
                else: # Fallback sort
                    objects_after_direction_filter.sort(key=lambda x: (x.get('cont_duration_hours', 0), x.get('peak_alt', 0)), reverse=True)
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
    # Graph Type Selector is now above this section

    export_data = []

    for i, obj in enumerate(st.session_state.last_results):
        peak_time_local_str, tz_display_name = get_local_time_str(obj['peak_time_utc'], st.session_state.selected_timezone)
        export_data.append({
            t['results_export_name']: obj['name'],
            t['results_export_type']: obj['type'],
            t['results_export_constellation']: obj.get('constellation', 'N/A'), # Add constellation
            t['results_export_mag']: obj['magnitude'],
            t['results_export_ra']: obj['ra'],
            t['results_export_dec']: obj['dec'],
            t['results_export_max_alt']: f"{obj['peak_alt']:.1f}",
            t['results_export_az_at_max']: f"{obj.get('peak_az', 0.0):.1f}",
            t['results_export_direction_at_max']: obj.get('peak_direction', '?'),
            t['results_export_cont_duration']: f"{obj.get('cont_duration_hours', 0):.1f}", # Use new key
            # t['results_export_total_duration']: f"{obj.get('total_duration_hours', 0):.1f}", # Removed
            t['results_export_time_max_utc']: obj['peak_time_utc'],
            t['results_export_time_max_local']: f"{peak_time_local_str} ({tz_display_name})" if peak_time_local_str != "N/A" else "N/A"
        })

        expander_title = t['results_expander_title'].format(obj['name'], obj['type'], obj['magnitude'])
        is_expanded = (st.session_state.expanded_object_name == obj['name'])
        with st.expander(expander_title, expanded=is_expanded):
            # Repeat object name inside for emphasis
            st.markdown(f"#### **{obj['name']}**")
            # Use columns for better layout of details
            col1, col2, col3 = st.columns([2, 2, 3]) # Adjust ratios
            with col1:
                 st.markdown(t['results_coords_header'])
                 st.markdown(f"RA: {obj['ra']}")
                 st.markdown(f"Dec: {obj['dec']}")
                 st.markdown(f"**{t['results_constellation_label']}** {obj.get('constellation', 'N/A')}") # Display Constellation
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
                 # Removed Total Duration display

            st.markdown("---") # Separator before plot button/plot

            plot_button_key = f"plot_btn_{obj['name']}_{i}"
            close_button_key = f"close_plot_{obj['name']}_{i}"
            # Button to trigger plot generation/display
            if st.button(t['results_graph_button'], key=plot_button_key):
                st.session_state.plot_object_name = obj['name']
                st.session_state.show_plot = True
                st.session_state.expanded_object_name = obj['name']
                st.session_state.active_result_plot_data = obj # Store data for replotting
                st.session_state.show_custom_plot = False # Hide custom plot if shown
                st.session_state.custom_target_plot_data = None
                st.rerun()

            # Display area for the result plot (figure is generated above the loop now)
            if st.session_state.show_plot and st.session_state.plot_object_name == obj['name']:
                 if active_plot_fig: # Check if figure was generated successfully
                     st.pyplot(active_plot_fig)
                     if st.button(t['results_close_graph_button'], key=close_button_key, type="secondary"):
                         st.session_state.show_plot = False
                         st.session_state.plot_object_name = None
                         st.session_state.active_result_plot_data = None
                         # No need to clear active_plot_fig here, it's regenerated on rerun if needed
                         st.rerun()
                 else:
                     # Show error if plot failed but should be shown
                     st.warning(t['results_graph_not_created'])


    # --- CSV Export Button ---
    if export_data and pd:
        st.markdown("---")
        try:
            df_export = pd.DataFrame(export_data)
            # Define column order including constellation, remove total duration
            cols = [t['results_export_name'], t['results_export_type'], t['results_export_constellation'],
                    t['results_export_mag'], t['results_export_cont_duration'],
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

    # --- Object Type Glossary (already moved near top) ---


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

