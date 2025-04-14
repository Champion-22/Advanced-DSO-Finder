# -*- coding: utf-8 -*-
# --- Basic Imports ---
from __future__ import annotations # Keep for flexible type hinting
import streamlit as st
import random
from datetime import datetime, date, time, timedelta, timezone
# import math # Unused import removed
import io
import traceback
# import locale # Unused import removed
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

# Geopy für Ortsuche (Nominatim + ArcGIS Fallback + Photon Fallback)
try:
    from geopy.geocoders import Nominatim, ArcGIS, Photon # Added Photon
    from geopy.exc import GeocoderTimedOut, GeocoderServiceError, GeocoderQueryError
except ImportError as e:
    import_errors.append(f"Error: Required geocoding library not found. Install: pip install geopy ({e})")
    Nominatim = None; ArcGIS = None; Photon = None; GeocoderTimedOut = None; GeocoderServiceError = None; GeocoderQueryError = None

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
    Nominatim, ArcGIS, Photon, GeocoderTimedOut, GeocoderServiceError, GeocoderQueryError, # Geopy essentials + Fallbacks
    TimezoneFinder, # TimezoneFinder
    Observer, AtNightConstraint, # Astroplan
    get_constellation # Astropy constellation function
])
if not essential_imports_ok:
    st.error("Stopping execution due to missing essential libraries (astropy, astroplan, pandas, matplotlib, pytz, geopy, timezonefinder).")
    st.stop()

# --- Translations (DEUTSCH) ---
# Using German as the primary example based on user interaction
translations = {
    'en': { # English Fallback/Option
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
        'location_search_found': "Found (Nominatim): {}", # Clarified source
        'location_search_found_fallback': "Found via Fallback (ArcGIS): {}",
        'location_search_found_fallback2': "Found via 2nd Fallback (Photon): {}", # NEU
        'location_search_coords': "Lat: {:.4f}, Lon: {:.4f}",
        'location_search_error_not_found': "Location not found using Nominatim, ArcGIS, or Photon.", # Updated
        'location_search_error_service': "Geocoding service error (Nominatim): {}",
        'location_search_error_timeout': "Geocoding service timed out (Nominatim).",
        'location_search_error_refused': "Geocoding connection refused (Nominatim). Server busy or IP blocked?",
        'location_search_info_fallback': "Nominatim failed, trying Fallback service (ArcGIS)...",
        'location_search_info_fallback2': "ArcGIS failed, trying 2nd Fallback service (Photon)...", # NEU
        'location_search_error_fallback_failed': "Primary (Nominatim) and Fallback (ArcGIS) failed: {}",
        'location_search_error_fallback2_failed': "All geocoding services (Nominatim, ArcGIS, Photon) failed: {}", # NEU
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
        'window_info_template': "Observation window: {} to {} UTC (Astronomical Twilight)",
        'window_already_passed': "Calculated night window has already passed for 'Now'. Calculating for next night.",
        'error_no_window': "No valid astronomical darkness window found for the selected date and location.",
        'error_polar_night': "Astronomical darkness persists for >24h (polar night?). Using fallback window.",
        'error_polar_day': "No astronomical darkness occurs (polar day?). Using fallback window.",
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
        'graph_type_label': "Graph Type (for all graphs):",
        'graph_type_sky_path': "Sky Path (Az/Alt)",
        'graph_type_alt_time': "Altitude/Time",
        'results_graph_button': "📈 Show Graph",
        'results_spinner_plotting': "Creating graph...",
        'results_graph_error': "Graph Error: {}",
        'results_graph_not_created': "Graph could not be created.",
        'results_close_graph_button': "Close Graph",
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
        'error_loading_catalog': "Error loading catalog file: {}",
        'info_catalog_loaded': "Catalog loaded: {} objects.",
        'warning_catalog_empty': "Catalog file loaded, but no suitable objects found after filtering.",
     },
     'de': { # German Translations
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
        'location_search_found': "Gefunden (Nominatim): {}", # Clarified source
        'location_search_found_fallback': "Gefunden via Fallback (ArcGIS): {}",
        'location_search_found_fallback2': "Gefunden via 2. Fallback (Photon): {}", # NEU
        'location_search_coords': "Breite: {:.4f}, Länge: {:.4f}",
        'location_search_error_not_found': "Ort nicht gefunden (via Nominatim, ArcGIS oder Photon).", # Updated
        'location_search_error_service': "Fehler beim Geocoding-Dienst (Nominatim): {}",
        'location_search_error_timeout': "Zeitüberschreitung beim Geocoding-Dienst (Nominatim).",
        'location_search_error_refused': "Geocoding-Verbindung abgelehnt (Nominatim). Server ausgelastet oder IP blockiert?",
        'location_search_info_fallback': "Nominatim fehlgeschlagen, versuche Fallback-Dienst (ArcGIS)...",
        'location_search_info_fallback2': "ArcGIS fehlgeschlagen, versuche 2. Fallback-Dienst (Photon)...", # NEU
        'location_search_error_fallback_failed': "Primärer (Nominatim) und Fallback (ArcGIS) fehlgeschlagen: {}",
        'location_search_error_fallback2_failed': "Alle Geocoding-Dienste (Nominatim, ArcGIS, Photon) fehlgeschlagen: {}", # NEU
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
        'window_info_template': "Beobachtungsfenster: {} bis {} UTC (Astronomische Dämmerung)",
        'window_already_passed': "Berechnetes Nachtfenster für 'Jetzt' liegt in der Vergangenheit. Berechne für die nächste Nacht.",
        'error_no_window': "Kein gültiges astronomisches Dämmerungsfenster für gewähltes Datum und Ort gefunden.",
        'error_polar_night': "Astronomische Dunkelheit dauert >24h an (Polarnacht?). Nutze Fallback-Fenster.",
        'error_polar_day': "Keine astronomische Dunkelheit vorhanden (Polartag?). Nutze Fallback-Fenster.",
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
        'graph_type_label': "Grafik-Typ (für alle Grafiken):",
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
        'error_processing_object': "Fehler bei Verarbeitung von {}: {}",
        'window_calc_error': "Fehler bei der Berechnung des Beobachtungsfensters: {}\n{}",
        'window_fallback_info': "\nVerwende Fallback-Fenster: {} bis {} UTC",
        'error_loading_catalog': "Fehler beim Laden der Katalogdatei: {}",
        'info_catalog_loaded': "Katalog geladen: {} Objekte.",
        'warning_catalog_empty': "Katalogdatei geladen, aber keine passenden Objekte nach Filterung gefunden.",
     },
     'fr': { # French Translations
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
        'location_search_found': "Trouvé (Nominatim): {}", # Clarified source
        'location_search_found_fallback': "Trouvé via Fallback (ArcGIS) : {}",
        'location_search_found_fallback2': "Trouvé via 2ème Fallback (Photon) : {}", # NEU
        'location_search_coords': "Lat : {:.4f}, Lon : {:.4f}",
        'location_search_error_not_found': "Lieu non trouvé (via Nominatim, ArcGIS ou Photon).", # Updated
        'location_search_error_service': "Erreur du service de géocodage (Nominatim) : {}",
        'location_search_error_timeout': "Le service de géocodage (Nominatim) a expiré.",
        'location_search_error_refused': "Connexion de géocodage (Nominatim) refusée. Serveur occupé ou IP bloquée ?",
        'location_search_info_fallback': "Échec de Nominatim, tentative de service de secours (ArcGIS)...",
        'location_search_info_fallback2': "Échec de ArcGIS, tentative de 2ème service de secours (Photon)...", # NEU
        'location_search_error_fallback_failed': "Échec des services primaire (Nominatim) et de secours (ArcGIS) : {}",
        'location_search_error_fallback2_failed': "Échec de tous les services de géocodage (Nominatim, ArcGIS, Photon) : {}", # NEU
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
        'window_info_template': "Fenêtre d'observation : {} à {} UTC (Crépuscule Astronomique)",
        'window_already_passed': "La fenêtre nocturne calculée pour 'Maintenant' est déjà passée. Calcul pour la nuit suivante.",
        'error_no_window': "Aucune fenêtre d'obscurité astronomique valide trouvée pour la date et le lieu sélectionnés.",
        'error_polar_night': "L'obscurité astronomique persiste >24h (nuit polaire ?). Utilisation de la fenêtre de repli.",
        'error_polar_day': "Aucune obscurité astronomique (jour polaire ?). Utilisation de la fenêtre de repli.",
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
        'graph_type_label': "Type de Graphique (pour tous) :",
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
        'custom_target_expander': "Tracer une cible personnalisée",
        'custom_target_ra_label': "Ascension Droite (AD) :",
        'custom_target_dec_label': "Déclinaison (Dec) :",
        'custom_target_name_label': "Nom de la cible (Optionnel) :",
        'custom_target_ra_placeholder': "ex : 10:45:03.6 ou 161.265",
        'custom_target_dec_placeholder': "ex : -16:42:58 ou -16.716",
        'custom_target_button': "Générer le graphique personnalisé",
        'custom_target_error_coords': "Format AD/Dec invalide. Utilisez HH:MM:SS.s / DD:MM:SS ou degrés décimaux.",
        'custom_target_error_window': "Impossible de générer le graphique. Assurez-vous que le lieu est défini et que la fenêtre d'observation est calculée (cliquez sur 'Trouver les Objets Observables' si nécessaire).",
        'error_processing_object': "Erreur lors du traitement de {}: {}",
        'window_calc_error': "Erreur lors du calcul de la fenêtre d'observation : {}\n{}",
        'window_fallback_info': "\nUtilisation de la fenêtre de repli : {} à {} UTC",
        'error_loading_catalog': "Erreur lors du chargement du fichier catalogue : {}",
        'info_catalog_loaded': "Catalogue chargé : {} objets.",
        'warning_catalog_empty': "Fichier catalogue chargé, mais aucun objet approprié trouvé après filtrage.",
     }
}

# --- Global Configuration & Initial Values ---
# Removed default location name, keeps coordinates
INITIAL_LAT = 47.17
INITIAL_LON = 8.01
INITIAL_HEIGHT = 550
INITIAL_TIMEZONE = "Europe/Zurich" # Fallback if auto-detection fails initially
APP_VERSION = "v6.1-hotfix" # Manual version for now

# --- Path to Catalog File ---
# WICHTIG: Die Katalogdatei (z.B. 'ongc.csv') muss sich im selben Verzeichnis
#         wie dieses Python-Skript befinden, damit sie gefunden wird!
try:
    # Get the directory where the script is located
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback for environments where __file__ is not defined (like some notebooks)
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
            # in_memory=True loads data into RAM for faster lookups
            return TimezoneFinder(in_memory=True)
        except Exception as e:
            # Catch potential errors during initialization (e.g., data file issues)
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
        'location_search_query': "", # *** FIX: Removed default "Schötz" ***
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
    # These are approximate values, can be adjusted
    limits = {1: 15.5, 2: 15.5, 3: 14.5, 4: 14.5, 5: 13.5, 6: 12.5, 7: 11.5, 8: 10.5, 9: 9.5}
    return limits.get(bortle_scale, 9.5) # Default to worst case if scale is invalid

def azimuth_to_direction(azimuth_deg: float) -> str:
    """Converts an azimuth angle (degrees) to a cardinal direction string."""
    # Ensure angle is within 0-360 degrees
    azimuth_deg = azimuth_deg % 360
    # Calculate the index (0=N, 1=NE, 2=E, ..., 7=NW)
    index = round(azimuth_deg / 45) % 8
    return CARDINAL_DIRECTIONS[index]

def _get_fallback_window(reference_time: 'Time') -> tuple['Time', 'Time']:
    """
    Provides a default observation window (e.g., 9 PM to 3 AM local time) in UTC.
    Tries to estimate local time based on system time, falls back to a fixed offset.
    """
    try:
        # Try getting local timezone info from the system where the script runs
        local_tz = datetime.now(timezone.utc).astimezone().tzinfo
        dt_ref = reference_time.datetime
        # Get the UTC offset for the reference time in the local timezone
        utc_offset_seconds = local_tz.utcoffset(dt_ref).total_seconds() if local_tz and local_tz.utcoffset(dt_ref) is not None else 3600 # Default to +1 hour offset
        utc_offset_hours = utc_offset_seconds / 3600
    except Exception:
        # Fallback if local timezone detection fails
        utc_offset_hours = 1 # e.g., CET offset

    # Define start/end times in local time for the night *of* the reference_time date
    start_date = reference_time.datetime.date()
    local_dt_start = datetime.combine(start_date, time(21, 0)) # 9 PM local time on the reference date
    local_dt_end = datetime.combine(start_date + timedelta(days=1), time(3, 0)) # 3 AM local time the *next* morning

    # Convert local start/end times to UTC using the calculated offset
    start_time_utc = Time(local_dt_start - timedelta(hours=utc_offset_hours))
    end_time_utc = Time(local_dt_end - timedelta(hours=utc_offset_hours))

    # Ensure the window is in the future relative to the reference time if needed
    # (This logic might need refinement depending on how reference_time is used)
    if end_time_utc < reference_time:
         start_time_utc += timedelta(days=1)
         end_time_utc += timedelta(days=1)

    return start_time_utc, end_time_utc

# --- Updated Observation Window Calculation using Astroplan ---
def get_observable_window(observer: 'Observer', reference_time: 'Time', is_now: bool, lang: str) -> tuple['Time' | None, 'Time' | None, str]:
    """
    Calculates the astronomical twilight window using astroplan.
    Handles 'now' logic and potential polar conditions.
    """
    t = translations[lang]
    status_message = ""
    start_time, end_time = None, None
    current_utc_time = Time.now() # Get current time once

    # Define the time for calculation
    # For 'Specific Night', use noon UTC on that day to avoid ambiguity near midnight
    # For 'Now', use the actual current time
    calc_time = reference_time
    if not is_now:
        # Combine selected date with noon UTC
        calc_time = Time(datetime.combine(reference_time.datetime.date(), time(12, 0)), scale='utc')


    try:
        # Ensure observer object is valid
        if not isinstance(observer, Observer):
            raise TypeError(f"Internal Error: Expected astroplan.Observer, got {type(observer)}")

        # Find the next evening astronomical twilight (-18 deg) starting from calc_time
        astro_set = observer.twilight_evening_astronomical(calc_time, which='next')

        # Find the next morning astronomical twilight (-18 deg) *after* the evening twilight
        astro_rise = observer.twilight_morning_astronomical(astro_set, which='next')

        # Basic validation of calculated times
        if astro_set is None or astro_rise is None or astro_rise <= astro_set:
            # This can happen in polar regions or if calculations fail unexpectedly
             raise ValueError("Could not determine valid twilight times (set or rise invalid/order wrong).")

        # --- Initial Window Set ---
        start_time = astro_set
        end_time = astro_rise

        # --- Adjust window based on 'is_now' ---
        if is_now:
            # If the calculated start time is in the past, adjust start to now
            if start_time < current_utc_time:
                start_time = current_utc_time

            # If the entire calculated window has passed for 'Now', calculate for the next night
            if end_time < current_utc_time:
                status_message = t['window_already_passed'] + "\n"
                # Recalculate starting from noon tomorrow UTC
                next_day_noon = Time(datetime.combine(current_utc_time.datetime.date() + timedelta(days=1), time(12, 0)), scale='utc')
                # Recursive call - ensure this doesn't lead to infinite loops in edge cases
                return get_observable_window(observer, next_day_noon, False, lang) # Treat as specific date for next day

        # Format times for status message *after* adjustments
        start_fmt = start_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')
        end_fmt = end_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')
        status_message += t['window_info_template'].format(start_fmt, end_fmt)

    except ValueError as ve: # Catch specific astroplan errors or our ValueError
        # Handle cases where twilight events might not occur (polar day/night)
        try:
            # Check if sun is always up (-18 deg horizon) or always down around the reference time
            sun_alt_ref = observer.altaz(reference_time, observer.sun).alt
            sun_alt_12h_later = observer.altaz(reference_time + 12*u.hour, observer.sun).alt

            if sun_alt_ref < -18*u.deg and sun_alt_12h_later < -18*u.deg:
                 # Potentially polar night (sun stays below -18 deg)
                 status_message = t['error_polar_night']
            elif sun_alt_ref > -18*u.deg and sun_alt_12h_later > -18*u.deg:
                 # Potentially polar day (sun stays above -18 deg)
                 status_message = t['error_polar_day']
            else:
                 # Other ValueError, use generic message
                 status_message = t['window_calc_error'].format(ve, traceback.format_exc())

        except Exception as check_e: # Error during sun altitude check
            print(f"Error checking sun altitude for polar conditions: {check_e}")
            status_message = t['window_calc_error'].format(ve, traceback.format_exc()) # Show original error

        # Use fallback window if calculation failed
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
        # Ensure fallback is used if times are invalid after all checks
        start_time_fb, end_time_fb = _get_fallback_window(reference_time)
        if start_time is None or start_time != start_time_fb: # Avoid duplicate fallback message
            status_message += t['window_fallback_info'].format(start_time_fb.iso, end_time_fb.iso)
        start_time, end_time = start_time_fb, end_time_fb


    return start_time, end_time, status_message


def find_observable_objects(
    location: 'EarthLocation',
    observing_times: 'Time',
    min_altitude_limit: 'u.Quantity',
    # magnitude_filter_mode: str, # No longer needed here, applied before call
    # bortle_scale: int, # No longer needed here
    # manual_min_mag: float | None, # No longer needed here
    # manual_max_mag: float | None, # No longer needed here
    # selected_object_types: list, # No longer needed here, applied before call
    df_search_subset: pd.DataFrame, # Pass the pre-filtered DataFrame
    lang: str
) -> list:
    """
    Finds DSOs from the pre-filtered catalog DataFrame visible during the observing_times.
    Calculates max continuous visibility duration within the dark window.
    Assumes df_search_subset is already filtered by type and magnitude.
    """
    t = translations[lang]
    observable_objects = []
    # magnitude_limit = None # Magnitude filter already applied
    MAX_REALISTIC_NIGHT_DURATION = 16.0 # Hours, simple cap for duration display

    # Pre-calculate AltAz frame for the entire observation window
    altaz_frame = AltAz(obstime=observing_times, location=location)
    # Calculate time step duration in hours for duration calculation
    # Handle case with only one time step (or zero)
    time_step_duration = (observing_times[1] - observing_times[0]).to(u.hour).value if len(observing_times) > 1 else 0

    # Iterate through the *pre-filtered* catalog DataFrame
    # This loop should be significantly smaller if filters were effective
    for index, row in df_search_subset.iterrows():
        # Extract object data from the row
        name = row['Name']; ra_str = row['RA_str']; dec_str = row['Dec_str']
        mag = row['Mag']; obj_type = row['Type']
        # Constellation will be fetched using astropy's get_constellation

        # --- Filters already applied before calling this function ---
        # No need to check type or magnitude again here

        # --- Calculate Observability ---
        try:
            # Create SkyCoord object for the target
            target = SkyCoord(ra=ra_str, dec=dec_str, frame='icrs', unit=(u.hourangle, u.deg))
            # Get full constellation name using astropy
            constellation_full = get_constellation(target)

            # Transform target coordinates to AltAz frame for the entire window
            target_altaz = target.transform_to(altaz_frame)
            altitudes = target_altaz.alt
            azimuths = target_altaz.az

            # Find indices where object is above minimum altitude *within the observing_times array*
            valid_indices = np.where(altitudes >= min_altitude_limit)[0]

            # If the object is ever above the minimum altitude during the window
            if len(valid_indices) > 0:
                # Find peak altitude within the valid period (indices where it's above min alt)
                peak_in_window_index = valid_indices[np.argmax(altitudes[valid_indices])]
                peak_alt_val = altitudes[peak_in_window_index].to(u.deg).value
                peak_az_val = azimuths[peak_in_window_index].to(u.deg).value
                peak_direction = azimuth_to_direction(peak_az_val)
                peak_time = observing_times[peak_in_window_index] # Time of peak altitude

                # --- Calculate Max Continuous Duration (within the dark window) ---
                # This duration represents how long the object is continuously above
                # min_altitude_limit *during the calculated observation window*.
                max_cont_duration_hours = 0.0
                if time_step_duration > 0 and len(valid_indices) > 1:
                    # Find breaks in consecutive indices (where difference > 1)
                    diffs = np.diff(valid_indices)
                    splits = np.where(diffs > 1)[0] + 1
                    # Split the valid_indices into blocks of continuous visibility
                    blocks = np.split(valid_indices, splits)
                    for block in blocks:
                        block_len = len(block)
                        if block_len > 1:
                            # Duration = time of last point in block - time of first point in block
                            # Add one time step to account for the duration *of* the last interval itself
                            duration = (observing_times[block[-1]] - observing_times[block[0]]).to(u.hour).value + time_step_duration
                        elif block_len == 1:
                            # Single point visibility, duration is approx one time step
                            duration = time_step_duration
                        else: # Empty block (shouldn't happen with split logic)
                            duration = 0.0
                        # Keep track of the longest single block duration
                        max_cont_duration_hours = max(max_cont_duration_hours, duration)
                elif len(valid_indices) == 1 and time_step_duration > 0:
                     # Exactly one point above limit
                     max_cont_duration_hours = time_step_duration


                # Apply a cap to prevent unrealistically long durations (e.g., >16h for circumpolar)
                capped_max_cont_duration = min(max_cont_duration_hours, MAX_REALISTIC_NIGHT_DURATION)

                # Append object data to results list
                observable_objects.append({
                    "name": name, "type": obj_type, "magnitude": mag,
                    "constellation": constellation_full, # Use full name from get_constellation
                    "ra_str": ra_str, "dec_str": dec_str, # Keep original strings if needed
                    "ra": target.ra.to_string(unit=u.hour, sep='hms', precision=1), # Formatted RA
                    "dec": target.dec.to_string(unit=u.deg, sep='dms', precision=0), # Formatted Dec
                    "peak_alt": peak_alt_val,
                    "peak_az": peak_az_val,
                    "peak_direction": peak_direction,
                    "peak_time_utc": peak_time.iso, # Peak time in UTC ISO format
                    "cont_duration_hours": capped_max_cont_duration, # Use capped continuous duration
                    # Store data needed for plotting
                    "times_jd": observing_times.jd,
                    "altitudes": altitudes.to(u.deg).value,
                    "azimuths": azimuths.to(u.deg).value,
                    "min_alt_limit": min_altitude_limit.value
                })
        except ValueError as coord_err:
            # Skip objects with invalid coordinates in the catalog
            # print(f"Skipping {name}: Invalid coordinates ({ra_str}, {dec_str}) - {coord_err}")
            pass
        except Exception as e:
            # Log other errors encountered during processing a specific object
            st.warning(t['error_processing_object'].format(name, e))
            # traceback.print_exc() # Optional: print full traceback to console for debugging

    return observable_objects

def create_moon_phase_svg(illumination_fraction: float, size: int = 80) -> str:
    """Generates an SVG image representing the moon phase illumination percentage."""
    percentage = illumination_fraction * 100
    # Define SVG parameters
    radius = size // 2 - 6 # Radius of the circle, leaving some padding
    cx = cy = size // 2 # Center coordinates
    stroke_color = "#DDDDDD" # Light grey stroke
    stroke_width = 3
    text_fill = "#EEEEEE" # Light text color
    font_size = size * 0.3 # Adjust font size relative to overall size
    # Create the SVG string
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
    # Check if plotting libraries are available
    if plt is None or mdates is None or pytz is None:
        st.error("Plotting libraries (matplotlib, pytz) not available.")
        return None

    # Create figure and axes
    fig, ax = plt.subplots()
    try:
        # Extract data from the object dictionary
        times = Time(_obj_data['times_jd'], format='jd') # Convert JD times back to Astropy Time objects
        altitudes = _obj_data['altitudes']
        min_alt_limit = _obj_data['min_alt_limit']

        # --- Timezone Conversion for X-axis ---
        try:
            # Get the selected timezone object
            selected_tz = pytz.timezone(tz_name)
            # Convert Astropy Time objects to datetime objects in the selected local timezone
            times_local_dt = [t_inst.to_datetime(timezone=selected_tz) for t_inst in times]
            xlabel = f"Time ({tz_name})" # Use the actual tz_name used for the axis label
        except Exception as tz_err:
            # Fallback to UTC if timezone conversion fails
            print(f"Timezone conversion/lookup error in graph for '{tz_name}': {tz_err}. Falling back to UTC.")
            times_local_dt = times.datetime # Use UTC datetime objects directly
            xlabel = "Time (UTC)"

        # --- Plotting Data ---
        # *** COLOR CHANGE: Use user color for main line ***
        ax.plot(times_local_dt, altitudes, label=t['graph_altitude_label'], color='#C1EDBE', linewidth=2) # User color line
        # *** COLOR CHANGE: Use RED for min alt line ***
        ax.axhline(min_alt_limit, color='#FF6347', linestyle='--', label=t['graph_min_altitude_label'].format(min_alt_limit)) # RED dashed line

        # --- Axis Setup ---
        ax.set_ylim(0, 90) # Altitude range 0-90 degrees
        ax.set_xlabel(xlabel) # Set x-axis label (local time or UTC)
        ax.set_ylabel(t['graph_ylabel']) # Set y-axis label (Altitude)
        ax.set_title(t['graph_title_alt_time'].format(_obj_data.get('name', 'Target'))) # Set graph title
        ax.legend() # Display legend
        ax.grid(True, linestyle=':', linewidth=0.5, color='#666666') # Add subtle grid

        # --- Formatting X-axis (Time) ---
        # Use a DateFormatter to show time as HH:MM
        xfmt = mdates.DateFormatter('%H:%M')
        ax.xaxis.set_major_formatter(xfmt)
        # Set major ticks to appear every hour
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        plt.tight_layout() # Adjust layout to prevent labels overlapping

    except Exception as e:
        # Handle any errors during plotting
        print(f"Error plotting altitude/time for {_obj_data.get('name', 'Unknown')}: {e}")
        st.error(t['results_graph_error'].format(e)) # Show error in Streamlit UI
        plt.close(fig) # Ensure figure is closed on error to free memory
        return None # Return None if plotting failed
    return fig # Return the Matplotlib figure object


# --- Updated Plot Function for Azimuth vs Altitude (Sky Path) ---
def plot_sky_path(_obj_data: dict, _location_tuple: tuple, lang: str, tz_name: str):
    """Creates a Matplotlib Azimuth vs Altitude graph with time markers."""
    t = translations[lang]
    # Check if plotting libraries are available
    if plt is None or mdates is None or pytz is None:
        st.error("Plotting libraries (matplotlib, pytz) not available.")
        return None

    # Create figure and axes
    fig, ax = plt.subplots()
    try:
        # Extract data from the object dictionary
        times = Time(_obj_data['times_jd'], format='jd') # Convert JD times back to Astropy Time objects
        altitudes = np.array(_obj_data['altitudes']) # Ensure numpy array for filtering
        azimuths = np.array(_obj_data['azimuths'])   # Ensure numpy array for filtering
        min_alt_limit = _obj_data['min_alt_limit']

        # Filter data to only include points *above* the minimum altitude for plotting
        valid_plot_indices = np.where(altitudes >= min_alt_limit)[0]
        if len(valid_plot_indices) == 0:
            # If the object never rises above the limit, show a warning and don't plot
            st.warning(f"Object '{_obj_data.get('name', 'Target')}' does not rise above {min_alt_limit}° during the observation window.")
            plt.close(fig)
            return None

        # Select the valid data points for plotting
        plot_times = times[valid_plot_indices]
        plot_altitudes = altitudes[valid_plot_indices]
        plot_azimuths = azimuths[valid_plot_indices]

        # --- Timezone Conversion for Time Markers ---
        times_local_dt = []
        try:
            # Get the selected timezone object
            selected_tz = pytz.timezone(tz_name)
            # Convert valid Astropy Time objects to datetime objects in the selected local timezone
            times_local_dt = [t_inst.to_datetime(timezone=selected_tz) for t_inst in plot_times]
        except Exception as tz_err:
            # Fallback to UTC if timezone conversion fails
            print(f"Timezone conversion/lookup error in graph for '{tz_name}': {tz_err}. Using UTC for markers.")
            times_local_dt = [t_inst.to_datetime(timezone=timezone.utc) for t_inst in plot_times]
            tz_name = "UTC" # Ensure label reflects fallback


        # --- Plotting Data ---
        # Use scatter plot: Azimuth (X) vs Altitude (Y)
        # Keep colormap for path as color indicates azimuth
        scatter = ax.scatter(plot_azimuths, plot_altitudes, c=plot_azimuths, cmap='viridis_r', s=25, zorder=3, alpha=0.8)

        # Add a color bar to show the mapping of color to azimuth
        cbar = fig.colorbar(scatter, ax=ax, orientation='vertical', fraction=0.046, pad=0.04)
        cbar.set_label(t['graph_azimuth_label']) # Label for the color bar

        # --- Add Time Markers (hourly) ---
        last_hour = -1
        for i, dt_local in enumerate(times_local_dt):
            current_hour = dt_local.hour
            # Add marker at the start, end, and roughly every hour (near the top of the hour)
            if i == 0 or i == len(times_local_dt) - 1 or (current_hour != last_hour and dt_local.minute < 10):
                time_str = dt_local.strftime('%H:%M') # Format time as HH:MM
                # Add text annotation for the time marker
                ax.text(plot_azimuths[i], plot_altitudes[i] + 0.5, time_str, fontsize=9, # Position slightly above point
                        ha='center', va='bottom', color='white', # White text, centered horizontally
                        bbox=dict(facecolor='black', alpha=0.7, pad=0.2, edgecolor='none')) # Semi-transparent black background
                last_hour = current_hour # Update last marked hour

        # *** COLOR CHANGE: Use RED for min alt line ***
        ax.axhline(min_alt_limit, color='#FF6347', linestyle='--', label=t['graph_min_altitude_label'].format(min_alt_limit)) # RED dashed line

        # --- Axis Setup ---
        ax.set_xlabel(t['graph_azimuth_label']) # Azimuth label
        ax.set_ylabel(t['graph_altitude_label']) # Altitude label
        ax.set_title(t['graph_title_sky_path'].format(_obj_data.get('name', 'Target'))) # Graph title
        ax.set_xlim(0, 360) # Azimuth range 0-360 degrees
        ax.set_ylim(0, 90) # Altitude range 0-90 degrees

        # Add cardinal directions (N, E, S, W) to the X-axis (Azimuth)
        ax.set_xticks([0, 90, 180, 270, 360])
        ax.set_xticklabels(['N', 'E', 'S', 'W', 'N'])

        ax.legend() # Display legend
        ax.grid(True, linestyle=':', linewidth=0.5, color='#666666') # Add subtle grid
        plt.tight_layout() # Adjust layout

    except Exception as e:
        # Handle any errors during plotting
        print(f"Error plotting sky path for {_obj_data.get('name', 'Unknown')}: {e}")
        st.error(t['results_graph_error'].format(e)) # Show error in Streamlit UI
        plt.close(fig) # Ensure figure is closed on error
        return None # Return None if plotting failed
    return fig # Return the Matplotlib figure object


def get_local_time_str(utc_iso_time: str, tz_name: str) -> tuple[str, str]:
    """Converts UTC ISO time string to a formatted time string in the specified timezone."""
    try:
        # Check if required libraries are available
        if Time is None or pytz is None: return "N/A", ""
        # Get the target timezone object
        selected_tz = pytz.timezone(tz_name) # tz_name should be valid here
        # Parse the UTC ISO time string using Astropy Time, making it timezone-aware (UTC)
        dt_peak_utc = Time(utc_iso_time, format='iso', scale='utc').datetime.replace(tzinfo=timezone.utc)
        # Convert the UTC datetime to the target local timezone
        dt_peak_local = dt_peak_utc.astimezone(selected_tz)
        # Format the local datetime string
        peak_time_local_str = dt_peak_local.strftime('%Y-%m-%d %H:%M:%S')
        return peak_time_local_str, tz_name # Return formatted string and the timezone name used
    except Exception as e:
        # Handle errors during time conversion or timezone lookup
        print(f"Error converting time {utc_iso_time} to timezone {tz_name}: {e}")
        return "N/A", tz_name # Return N/A on error


# --- Data Loading Function ---
@st.cache_data # Cache the loaded data to avoid reloading on every interaction
def load_ongc_data(catalog_path: str, lang: str) -> pd.DataFrame | None:
    """Loads, filters, and preprocesses data from the OpenNGC CSV file."""
    # Access translations using the provided lang argument
    t_load = translations[lang]
    # Base required columns for core functionality
    required_cols = ['Name', 'RA', 'Dec', 'Type']
    # Optional columns for magnitude - will try these in order
    mag_cols = ['V-Mag', 'B-Mag', 'Mag']
    # Constellation column is no longer loaded/used here; fetched via astropy

    try:
        # Check if the catalog file exists
        if not os.path.exists(catalog_path):
            st.error(f"{t_load['error_loading_catalog'].split(':')[0]}: File not found at {catalog_path}")
            st.info("Please ensure the file 'ongc.csv' is in the same directory as the Python script.")
            return None

        # Load the CSV file
        # Assumes semicolon separator and '#' as comment character
        # low_memory=False can help with mixed data types, but uses more memory
        df = pd.read_csv(catalog_path, sep=';', comment='#', low_memory=False)

        # --- Check for required columns ---
        missing_req_cols = [col for col in required_cols if col not in df.columns]
        if missing_req_cols:
            st.error(f"Missing required columns in catalog '{os.path.basename(catalog_path)}': {', '.join(missing_req_cols)}")
            return None

        # --- Find available magnitude column ---
        mag_col_found = None
        for col in mag_cols:
            if col in df.columns:
                mag_col_found = col
                break # Use the first one found (V-Mag preferred, then B-Mag, then Mag)
        if mag_col_found is None:
            st.error(f"Magnitude column ('V-Mag', 'B-Mag' or 'Mag') not found in catalog.")
            return None
        # Rename the found magnitude column to a standard 'Mag' for consistency
        df = df.rename(columns={mag_col_found: 'Mag'})

        # --- Filter by Object Type ---
        # Define a list of common DSO type identifiers found in ONGC
        # Includes full names and abbreviations
        dso_types = ['Galaxy', 'Globular Cluster', 'Open Cluster', 'Nebula',
                     'Planetary Nebula', 'Supernova Remnant', 'HII', 'Emission Nebula',
                     'Reflection Nebula', 'Cluster + Nebula', 'Gal', 'GCl', 'Gx', 'OC',
                     'PN', 'SNR', 'Neb', 'EmN', 'RfN', 'C+N', 'Gxy', 'AGN', 'MWSC', 'OCl'] # Added OCl
        # Create a regex pattern to match any of these types (case-insensitive)
        type_pattern = '|'.join(dso_types)
        # Filter the DataFrame, keeping rows where 'Type' column contains any of the DSO types
        df_filtered = df[df['Type'].astype(str).str.contains(type_pattern, case=False, na=False)].copy()

        # --- Process Magnitude ---
        # Convert the 'Mag' column to numeric, coercing errors to NaN (Not a Number)
        df_filtered['Mag'] = pd.to_numeric(df_filtered['Mag'], errors='coerce')
        # Drop rows where magnitude could not be converted (is NaN)
        df_filtered.dropna(subset=['Mag'], inplace=True)

        # --- Process Coordinates ---
        # Ensure RA and Dec columns are strings (they should be HH:MM:SS.s / DD:MM:SS format)
        df_filtered['RA_str'] = df_filtered['RA'].astype(str)
        df_filtered['Dec_str'] = df_filtered['Dec'].astype(str)
        # Drop rows with missing RA or Dec strings
        df_filtered.dropna(subset=['RA_str', 'Dec_str'], inplace=True)
        # Drop rows with empty RA or Dec strings after stripping whitespace
        df_filtered = df_filtered[df_filtered['RA_str'].str.strip() != '']
        df_filtered = df_filtered[df_filtered['Dec_str'].str.strip() != '']

        # --- Select Final Columns ---
        # Keep only the necessary columns for the application
        # Constellation is no longer needed from the CSV
        final_cols = ['Name', 'RA_str', 'Dec_str', 'Mag', 'Type']

        # Create the final DataFrame with selected columns
        df_final = df_filtered[final_cols].copy()
        # Drop duplicate objects based on 'Name', keeping the first occurrence
        df_final.drop_duplicates(subset=['Name'], inplace=True, keep='first')
        # Reset the index of the final DataFrame
        df_final.reset_index(drop=True, inplace=True)

        # Check if any objects remain after filtering
        if not df_final.empty:
            # Return the processed DataFrame
            return df_final
        else:
            # Show a warning if the catalog is loaded but empty after filtering
            st.warning(t_load['warning_catalog_empty'])
            return None

    except FileNotFoundError:
        # Handle case where the file doesn't exist at the specified path
        st.error(f"{t_load['error_loading_catalog'].split(':')[0]}: File not found at {catalog_path}")
        st.info("Please ensure the file 'ongc.csv' is in the same directory as the Python script.")
        return None
    except pd.errors.EmptyDataError:
        # Handle case where the CSV file is empty
        st.error(f"Catalog file is empty: {catalog_path}")
        return None
    except Exception as e:
        # Handle other potential errors during loading/processing
        st.error(t_load['error_loading_catalog'].format(e))
        # Provide specific hint for common CSV parsing errors
        if "tokenizing data" in str(e):
            st.info("This often means the wrong separator (delimiter) or inconsistent file structure. The app expects a semicolon (;) separator. Please check your 'ongc.csv' file.")
        else:
            st.info("Please check the file path, filename, and format.")
        st.exception(e) # Show full traceback in Streamlit for debugging
        return None

# --- Initialize Session State ---
# Call this *before* accessing session state for the first time
initialize_session_state()

# --- Get Current Language and Translations ---
# This needs to happen *after* state initialization but *before* UI elements that use translations
lang = st.session_state.language
# Ensure language exists in translations, fallback to 'en' if needed
if lang not in translations:
    lang = 'en' # Fallback to English
    st.session_state.language = lang # Update state
t = translations[lang] # Get the translation dictionary for the current language


# --- Load Catalog Data ---
# Load data after language is set, so load_ongc_data gets correct translations for potential messages
# The result is cached, so it only loads once unless the path or language changes
df_catalog_data = load_ongc_data(CATALOG_FILEPATH, lang)


# --- Custom CSS Styling ---
# Updated colors for a more modern dark theme + user color #C1EDBE
st.markdown("""
<style>
    /* Base container styling */
    .main .block-container {
        background-color: #1a1a1a; /* Darker background */
        color: #e0e0e0; /* Slightly softer white text */
        border-radius: 10px; /* Rounded corners for the main container */
        padding: 2rem; /* Add padding around the content */
    }
    /* Primary Button Styling (e.g., Find Objects) */
    div[data-testid="stButton"] > button:not([kind="secondary"]) {
        /* *** COLOR CHANGE: Use user color gradient, black text *** */
        background-image: linear-gradient(to right, #C1EDBE, #a8d7a4); /* User color gradient */
        color: #111111; /* Black text for contrast */
        border: none; /* No border */
        padding: 10px 24px; /* Padding */
        text-align: center; /* Center text */
        font-size: 16px; /* Font size */
        margin: 4px 2px; /* Margins */
        cursor: pointer; /* Pointer cursor on hover */
        border-radius: 8px; /* Rounded corners */
        transition-duration: 0.4s; /* Smooth transition for hover effect */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* Subtle shadow */
    }
    /* Primary Button Hover Effect */
    div[data-testid="stButton"] > button:not([kind="secondary"]):hover {
         /* *** COLOR CHANGE: Darker user color gradient *** */
        background-image: linear-gradient(to right, #a8d7a4, #8fcb8a); /* Darker user color gradient */
        color: #000000; /* Black text */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); /* Larger shadow on hover */
    }
    /* Secondary Button Styling (e.g., Close Graph) - Remains grey */
     div[data-testid="stButton"] > button[kind="secondary"] {
         background-color: #4a4a4a; /* Dark grey */
         color: #e0e0e0; /* Light grey text */
         border: 1px solid #666; /* Subtle border */
         border-radius: 8px;
         padding: 8px 18px; /* Slightly smaller padding */
     }
     /* Secondary Button Hover Effect */
     div[data-testid="stButton"] > button[kind="secondary"]:hover {
         background-color: #5a5a5a; /* Slightly lighter grey */
         color: white;
         border: 1px solid #888;
     }
     /* Form Submit Button (e.g., Find Coordinates) - Inherits primary style */
     div[data-testid="stFormSubmitButton"] > button {
         margin-top: 28px; /* Keep vertical alignment with input above */
     }
    /* Expander Header Styling */
    .streamlit-expanderHeader {
        background-color: #282828; /* Slightly lighter dark grey */
        color: #e0e0e0; /* Light text */
        border-radius: 5px; /* Rounded corners */
        border-bottom: 1px solid #444; /* Subtle bottom border */
    }
    /* Metric Box Styling */
    div[data-testid="stMetric"] {
        background-color: #2c2c2c; /* Consistent dark element background */
        border-radius: 8px; /* Rounded corners */
        padding: 12px; /* Padding inside the metric box */
        border: 1px solid #444; /* Subtle border */
    }
    /* Metric Label Styling */
    div[data-testid="stMetric"] > div[data-testid="stMetricLabel"] {
        color: #aaaaaa; /* Grey color for the label */
    }
    /* Input Widgets Styling (Text, Number, Date, Selectbox) */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stDateInput"] input,
    div[data-testid="stSelectbox"] div[role="button"],
    div[data-testid="stMultiselect"] div[data-baseweb="select"] > div { /* Target multiselect input area */
        background-color: #2c2c2c !important; /* Dark background */
        color: #e0e0e0 !important; /* Light text */
        border: 1px solid #555 !important; /* Border color */
        border-radius: 5px; /* Rounded corners */
    }
    /* Slider Track Styling */
    div[data-testid="stSlider"] div[role="slider"] {
        background-color: #555; /* Dark grey track */
    }
    /* Slider Thumb Styling */
    /* Targets the thumb element */
    div[data-testid="stSlider"] div[data-baseweb="slider"] > div:nth-child(3) {
         /* *** COLOR CHANGE: Use user color for thumb *** */
        background-color: #C1EDBE !important;
    }
    /* Slider Range Track Styling (the 'bar') */
    /* Targets the track showing the selected range/value */
     div[data-testid="stSlider"] div[data-baseweb="slider"] > div:nth-child(2) {
          /* *** COLOR CHANGE: Use user color for track bar *** */
         background-color: #C1EDBE !important;
     }
     /* Slider Value Text Color (Above Thumb) */
     /* Targets the text label showing the current value */
     div[data-testid="stSlider"] div[data-baseweb="slider"] > div:nth-child(4) { /* This selector might change with Streamlit versions */
         /* *** COLOR CHANGE: Use dark text for slider value *** */
         color: #111111 !important; /* Dark text for readability on light green background */
     }
     /* Slider Min/Max Labels Color */
     /* Targets the divs likely holding the min/max labels at the ends */
     /* Sets color back to light grey for readability against dark background */
     div[data-testid="stSlider"] div[data-baseweb="slider"] > div:first-child,
     div[data-testid="stSlider"] div[data-baseweb="slider"] > div:last-child {
         /* *** FIX: Light text for min/max labels on dark background *** */
         color: #e0e0e0 !important;
         background-color: transparent !important; /* Ensure no background color interferes */
         /* z-index: 1; /* Probably not needed anymore */ */
     }

</style>
""", unsafe_allow_html=True)

# --- Title ---
# Static English Title - avoids changing with language selection
st.title("Advanced DSO Finder")
# Display App Version (manual for now)
st.caption(f"Version: {APP_VERSION}")

# --- Object Type Glossary (Moved near top for visibility) ---
with st.expander(t['object_type_glossary_title']):
    glossary_items = t.get('object_type_glossary', {}) # Use .get for safety
    # Use Streamlit columns for better layout if many items
    col1, col2 = st.columns(2)
    col_index = 0
    # Sort glossary items alphabetically by abbreviation for consistent order
    sorted_items = sorted(glossary_items.items())
    for abbr, full_name in sorted_items:
        # Distribute items between the two columns
        if col_index % 2 == 0:
            col1.markdown(f"**{abbr}:** {full_name}")
        else:
            col2.markdown(f"**{abbr}:** {full_name}")
        col_index += 1

st.markdown("---") # Add separator after glossary

# --- Sidebar ---
with st.sidebar:
    # Show catalog loaded message here now that translations are ready and data loaded
    if df_catalog_data is not None and 'catalog_loaded_msg_shown' not in st.session_state:
         st.success(t['info_catalog_loaded'].format(len(df_catalog_data)))
         st.session_state.catalog_loaded_msg_shown = True # Flag to prevent re-showing on rerun
    elif df_catalog_data is None and 'catalog_error_msg_shown' not in st.session_state:
         # Optionally show a persistent error in sidebar if loading failed
         st.error("Catalog loading failed. Check file.")
         st.session_state.catalog_error_msg_shown = True


    st.header(t['settings_header'])

    # --- Language Selector ---
    language_options = {'en': 'English', 'de': 'Deutsch', 'fr': 'Français'} # Added French
    lang_keys = list(language_options.keys())
    try:
        # Find the index of the currently selected language
        current_lang_index = lang_keys.index(st.session_state.language)
    except ValueError:
        # If current language in state is invalid, default to the first one (English)
        current_lang_index = 0
        st.session_state.language = lang_keys[0] # Reset state to default

    # Create the language selection radio button
    selected_lang_key = st.radio(
        t['language_select_label'], options=lang_keys,
        format_func=lambda key: language_options[key], # Display full language name
        key='language_radio', # Unique key for the widget
        index=current_lang_index # Set the default selection
    )
    # If language changed, update state and rerun the script
    if selected_lang_key != st.session_state.language:
        st.session_state.language = selected_lang_key
        # Clear status messages that might be language-specific
        st.session_state.location_search_status_msg = ""
        # Optionally reset other state variables if needed upon language change
        # st.session_state.location_search_success = False
        st.rerun() # Rerun the script immediately to apply the new language

    # --- Location Settings ---
    # Location expander starts expanded by default
    with st.expander(t['location_expander'], expanded=True):
        # Map internal keys to translated display options
        location_options_map = {
            'Search': t['location_option_search'],
            'Manual': t['location_option_manual']
        }
        # Ensure the current choice in state is valid
        current_choice = st.session_state.location_choice_key
        if current_choice not in location_options_map:
            st.session_state.location_choice_key = 'Search' # Default to Search if invalid
            current_choice = 'Search'
        # Create the location method selection radio button
        st.radio(
            t['location_select_label'], options=list(location_options_map.keys()),
            format_func=lambda key: location_options_map[key], # Display translated options
            key="location_choice_key" # Update session state directly
        )

        # --- Location Input Area ---
        lat_val, lon_val, height_val = None, None, None # Initialize coordinate variables
        warning_placeholder = st.empty() # Placeholder for manual input warnings
        location_valid_for_tz = False # Flag to check if coordinates are valid for timezone lookup

        # --- Manual Location Input ---
        if st.session_state.location_choice_key == "Manual":
            # Use default values from session state for number inputs
            # Keys match session state keys for direct updates
            st.number_input(t['location_lat_label'], min_value=-90.0, max_value=90.0, step=0.01, format="%.4f", key="manual_lat_val")
            st.number_input(t['location_lon_label'], min_value=-180.0, max_value=180.0, step=0.01, format="%.4f", key="manual_lon_val")
            st.number_input(t['location_elev_label'], min_value=-500, step=10, format="%d", key="manual_height_val")
            # Get current values from state
            lat_val = st.session_state.manual_lat_val
            lon_val = st.session_state.manual_lon_val
            height_val = st.session_state.manual_height_val
            # Basic validation for manual input: check if all are valid numbers
            if isinstance(lat_val, (int, float)) and isinstance(lon_val, (int, float)) and isinstance(height_val, (int, float)):
                location_valid_for_tz = True # Coordinates are valid
                warning_placeholder.empty() # Clear any previous warnings
            else:
                # Show warning if any field is invalid/empty
                warning_placeholder.warning(t['location_error_manual_none'])
                location_valid_for_tz = False # Coordinates are invalid

        # --- Location Search Input ---
        elif st.session_state.location_choice_key == "Search":
            # Use a form for the search input and button
            with st.form("location_search_form"):
                # Text input for location name, key matches session state
                # Default value is now empty string "" from initialize_session_state
                st.text_input(t['location_search_label'], key="location_search_query", placeholder=t['location_search_placeholder'])
                # Form submit button
                location_search_form_submitted = st.form_submit_button(t['location_search_submit_button'])
            # Elevation input outside the form, but still relevant for searched locations
            st.number_input(t['location_elev_label'], min_value=-500, step=10, format="%d", key="manual_height_val")
            # Placeholder to display search status messages (success or error)
            status_placeholder = st.empty()

            # Display previous search status message if it exists
            if st.session_state.location_search_status_msg:
                 # Check for error keywords or fallback success
                 if any(err_key in st.session_state.location_search_status_msg.lower() for err_key in ["error", "fehler", "not found", "non trouvé", "refused", "abgelehnt", "fehlgeschlagen"]):
                     status_placeholder.error(st.session_state.location_search_status_msg)
                 elif "Fallback" in st.session_state.location_search_status_msg: # Show fallback success as info
                     status_placeholder.info(st.session_state.location_search_status_msg)
                 else: # Regular success
                     status_placeholder.success(st.session_state.location_search_status_msg)

            # Process form submission if button was clicked and query is not empty
            if location_search_form_submitted and st.session_state.location_search_query:
                location = None # Reset location variable
                service_used = None # Track which service succeeded
                final_error = None # Store the final error if all fail

                with st.spinner(t['spinner_geocoding']): # Show spinner during search
                    query = st.session_state.location_search_query
                    user_agent_str = f"AdvancedDSOFinder/{random.randint(1000,9999)}/streamlit_app_{datetime.now().timestamp()}"

                    # --- Try Nominatim First ---
                    try:
                        print("Trying Nominatim...")
                        geolocator = Nominatim(user_agent=user_agent_str)
                        location = geolocator.geocode(query, timeout=10)
                        if location:
                            service_used = "Nominatim"
                            print("Nominatim success.")
                        else:
                             print("Nominatim returned None.")
                             # Don't raise error here, let it proceed to fallback if applicable

                    except (GeocoderTimedOut, GeocoderServiceError) as e:
                        print(f"Nominatim failed: {e}. Trying fallback 1 (ArcGIS).")
                        status_placeholder.info(t['location_search_info_fallback']) # Inform user
                        # --- Try ArcGIS (Fallback 1) ---
                        try:
                            fallback_geolocator = ArcGIS(timeout=15)
                            location = fallback_geolocator.geocode(query, timeout=15)
                            if location:
                                service_used = "ArcGIS"
                                print("ArcGIS success.")
                            else:
                                print("ArcGIS returned None.")

                        except (GeocoderTimedOut, GeocoderServiceError) as e2:
                            print(f"ArcGIS failed: {e2}. Trying fallback 2 (Photon).")
                            status_placeholder.info(t['location_search_info_fallback2']) # Inform user
                            # --- Try Photon (Fallback 2) ---
                            try:
                                fallback_geolocator2 = Photon(user_agent=user_agent_str, timeout=15) # Add user agent
                                location = fallback_geolocator2.geocode(query, timeout=15)
                                if location:
                                    service_used = "Photon"
                                    print("Photon success.")
                                else:
                                    print("Photon returned None.")
                                    final_error = GeocoderServiceError("All services failed or returned None.") # Set final error if Photon also returns None

                            except (GeocoderTimedOut, GeocoderServiceError) as e3:
                                print(f"Photon failed: {e3}. All fallbacks exhausted.")
                                final_error = e3 # Store the last error
                            except Exception as e3: # Catch other Photon errors
                                print(f"Photon failed unexpectedly: {e3}. All fallbacks exhausted.")
                                final_error = e3
                        except Exception as e2: # Catch other ArcGIS errors
                            print(f"ArcGIS failed unexpectedly: {e2}. Trying fallback 2 (Photon).")
                            status_placeholder.info(t['location_search_info_fallback2']) # Inform user
                            # --- Try Photon (Fallback 2) ---
                            try:
                                fallback_geolocator2 = Photon(user_agent=user_agent_str, timeout=15)
                                location = fallback_geolocator2.geocode(query, timeout=15)
                                if location:
                                    service_used = "Photon"
                                    print("Photon success.")
                                else:
                                     print("Photon returned None.")
                                     final_error = GeocoderServiceError("All services failed or returned None.")
                            except (GeocoderTimedOut, GeocoderServiceError) as e3:
                                 print(f"Photon failed: {e3}. All fallbacks exhausted.")
                                 final_error = e3
                            except Exception as e3:
                                 print(f"Photon failed unexpectedly: {e3}. All fallbacks exhausted.")
                                 final_error = e3

                    except Exception as e: # Catch other potential errors from Nominatim
                        print(f"Nominatim failed unexpectedly: {e}. Trying fallback 1 (ArcGIS).")
                        status_placeholder.info(t['location_search_info_fallback']) # Inform user
                        # --- Try ArcGIS (Fallback 1) ---
                        try:
                            fallback_geolocator = ArcGIS(timeout=15)
                            location = fallback_geolocator.geocode(query, timeout=15)
                            if location:
                                service_used = "ArcGIS"
                                print("ArcGIS success.")
                            else:
                                print("ArcGIS returned None.")
                                # Try Photon if ArcGIS returns None after Nominatim exception
                                print("Trying fallback 2 (Photon)...")
                                status_placeholder.info(t['location_search_info_fallback2'])
                                try:
                                    fallback_geolocator2 = Photon(user_agent=user_agent_str, timeout=15)
                                    location = fallback_geolocator2.geocode(query, timeout=15)
                                    if location:
                                        service_used = "Photon"
                                        print("Photon success.")
                                    else:
                                        print("Photon returned None.")
                                        final_error = GeocoderServiceError("All services failed or returned None.")
                                except Exception as e3:
                                    print(f"Photon failed: {e3}. All fallbacks exhausted.")
                                    final_error = e3

                        except Exception as e2: # Catch ArcGIS errors after Nominatim exception
                            print(f"ArcGIS failed: {e2}. Trying fallback 2 (Photon).")
                            status_placeholder.info(t['location_search_info_fallback2'])
                            # --- Try Photon (Fallback 2) ---
                            try:
                                fallback_geolocator2 = Photon(user_agent=user_agent_str, timeout=15)
                                location = fallback_geolocator2.geocode(query, timeout=15)
                                if location:
                                    service_used = "Photon"
                                    print("Photon success.")
                                else:
                                    print("Photon returned None.")
                                    final_error = GeocoderServiceError("All services failed or returned None.")
                            except Exception as e3:
                                 print(f"Photon failed: {e3}. All fallbacks exhausted.")
                                 final_error = e3


                # --- Process final result ---
                if location and service_used:
                    found_lat = location.latitude; found_lon = location.longitude; found_name = location.address
                    st.session_state.searched_location_name = found_name
                    st.session_state.location_search_success = True
                    st.session_state.manual_lat_val = found_lat
                    st.session_state.manual_lon_val = found_lon
                    coord_str = t['location_search_coords'].format(found_lat, found_lon)
                    # Choose success message based on which service worked
                    if service_used == "Nominatim":
                        st.session_state.location_search_status_msg = f"{t['location_search_found'].format(found_name)}\n({coord_str})"
                        status_placeholder.success(st.session_state.location_search_status_msg)
                    elif service_used == "ArcGIS":
                         st.session_state.location_search_status_msg = f"{t['location_search_found_fallback'].format(found_name)}\n({coord_str})"
                         status_placeholder.info(st.session_state.location_search_status_msg)
                    elif service_used == "Photon":
                         st.session_state.location_search_status_msg = f"{t['location_search_found_fallback2'].format(found_name)}\n({coord_str})"
                         status_placeholder.info(st.session_state.location_search_status_msg)
                    location_valid_for_tz = True
                else: # No location found by any service or an error occurred in the last fallback
                    st.session_state.location_search_success = False
                    st.session_state.searched_location_name = None
                    if final_error:
                        st.session_state.location_search_status_msg = t['location_search_error_fallback2_failed'].format(final_error)
                    else: # No error, but no location found
                        st.session_state.location_search_status_msg = t['location_search_error_not_found']
                    status_placeholder.error(st.session_state.location_search_status_msg)
                    location_valid_for_tz = False


            # If search was previously successful, use the stored coordinates
            if st.session_state.location_search_success:
                 lat_val = st.session_state.manual_lat_val
                 lon_val = st.session_state.manual_lon_val
                 height_val = st.session_state.manual_height_val
                 location_valid_for_tz = True # Search was successful, coords are valid


        # --- Determine Final Location and Timezone ---
        # This block runs regardless of Manual/Search choice, using the latest valid coordinates
        current_location_for_run = None # Initialize observer object
        location_is_valid_for_run = False # Flag: can we run the main DSO search?
        location_display_name_for_run = "" # Name to show in search parameters
        auto_timezone_msg = "" # Message about timezone detection

        # Get current coordinates from session state (updated by Manual or Search)
        current_lat = st.session_state.manual_lat_val
        current_lon = st.session_state.manual_lon_val
        current_height = st.session_state.manual_height_val

        # Validate coordinates before creating Observer and finding timezone
        if isinstance(current_lat, (int, float)) and isinstance(current_lon, (int, float)) and isinstance(current_height, (int, float)):
            try:
                # Create astroplan Observer object (holds EarthLocation)
                current_location_for_run = Observer(latitude=current_lat * u.deg, longitude=current_lon * u.deg, elevation=current_height * u.m)
                location_is_valid_for_run = True # Valid Observer created, can run main search

                # Determine display name based on how location was set
                if st.session_state.location_choice_key == "Manual":
                    location_display_name_for_run = t['location_manual_display'].format(current_lat, current_lon)
                elif st.session_state.location_choice_key == "Search" and st.session_state.location_search_success:
                    # Use the successfully searched name (truncated if too long)
                    name_val = st.session_state.searched_location_name
                    display_name_short = (name_val[:35] + '...') if name_val and len(name_val) > 38 else name_val
                    location_display_name_for_run = t['location_search_display'].format(display_name_short or "Found", current_lat, current_lon)
                else: # Search mode selected, but no successful search yet
                    location_display_name_for_run = "Pending Search"
                    location_is_valid_for_run = False # Cannot run main search without successful location search

                # --- Automatic Timezone Detection ---
                # Only run if TimezoneFinder is available and location coordinates are valid
                if tf and location_is_valid_for_run:
                    try:
                        # Find timezone name at the current coordinates
                        found_tz = tf.timezone_at(lng=current_lon, lat=current_lat)
                        if found_tz:
                            # Validate the found timezone name using pytz
                            pytz.timezone(found_tz) # This will raise UnknownTimeZoneError if invalid
                            st.session_state.selected_timezone = found_tz # Store valid timezone
                            auto_timezone_msg = f"{t['timezone_auto_set_label']} **{found_tz}**"
                        else:
                            # TimezoneFinder returned None (e.g., location in ocean)
                            st.session_state.selected_timezone = 'UTC' # Fallback to UTC
                            auto_timezone_msg = f"{t['timezone_auto_fail_label']} **UTC** ({t['timezone_auto_fail_msg']})"
                    except pytz.UnknownTimeZoneError:
                        # Handle case where TimezoneFinder returns an invalid name
                         st.session_state.selected_timezone = 'UTC'
                         auto_timezone_msg = f"{t['timezone_auto_fail_label']} **UTC** (Invalid TZ '{found_tz}')"
                    except Exception as tz_find_e:
                        # Handle other errors during timezone lookup
                        print(f"Error finding timezone: {tz_find_e}")
                        st.session_state.selected_timezone = 'UTC' # Fallback to UTC
                        auto_timezone_msg = f"{t['timezone_auto_fail_label']} **UTC** (Error)"

                elif not tf:
                    # TimezoneFinder library is not available
                    auto_timezone_msg = "Timezonefinder library not available. Using fallback."
                    st.session_state.selected_timezone = INITIAL_TIMEZONE # Use initial default
                elif not location_is_valid_for_run:
                    # Don't try finding timezone if location isn't valid yet
                    st.session_state.selected_timezone = INITIAL_TIMEZONE
                    # No message needed here, user needs to set location first

            except Exception as e: # Error creating Observer object
                warning_placeholder.error(t['location_error'].format(e))
                location_display_name_for_run = t['location_error_fallback']
                location_is_valid_for_run = False # Cannot run main search
                st.session_state.selected_timezone = INITIAL_TIMEZONE # Use fallback timezone

        else: # Coordinates are not valid numbers (e.g., initial state in Manual mode before input)
            location_is_valid_for_run = False
            if st.session_state.location_choice_key == "Search":
                location_display_name_for_run = "Please search for a location"
            elif st.session_state.location_choice_key == "Manual":
                location_display_name_for_run = "Enter valid coordinates"
            st.session_state.selected_timezone = INITIAL_TIMEZONE # Use fallback timezone


    # --- Time & Timezone Settings (Starts collapsed) ---
    with st.expander(t['time_expander'], expanded=False):
        # Map internal keys to translated display options
        time_options_map = {'Now': t['time_option_now'], 'Specific': t['time_option_specific']}
        # Radio button for selecting time mode
        time_choice_key = st.radio(
            t['time_select_label'], options=time_options_map.keys(),
            format_func=lambda key: time_options_map[key], # Display translated options
            key="time_choice_exp" # Update session state directly
        )
        is_time_now = (time_choice_key == "Now") # Boolean flag for current mode

        if is_time_now:
            # If 'Now', use the current time as the reference
            reference_time = Time.now()
        else:
            # If 'Specific Night', show date input
            selected_date = st.date_input(
                t['time_date_select_label'], date.today(), # Default to today
                min_value=date.today()-timedelta(days=365*5), # Allow dates 5 years in the past
                max_value=date.today()+timedelta(days=365*1) # Allow dates 1 year in the future
            )
            # Use noon UTC on the selected date as the reference time
            # This avoids ambiguity around midnight when calculating the *next* twilight
            reference_time = Time(datetime.combine(selected_date, time(12, 0)), scale='utc')


        st.markdown("---") # Separator
        # Display the automatically determined timezone or the fallback
        if auto_timezone_msg:
            # Use markdown to allow bold formatting in the message
            st.markdown(auto_timezone_msg, unsafe_allow_html=True)
        else:
            # Show fallback timezone if auto-detection hasn't run or failed silently
            st.markdown(f"{t['timezone_auto_fail_label']} **{st.session_state.selected_timezone}**")


    # --- Filter Settings (Starts collapsed) ---
    with st.expander(t['filters_expander'], expanded=False):
        # --- Magnitude Filter ---
        st.markdown(t['mag_filter_header'])
        # Map internal keys to translated display options
        mag_filter_options_map = {'Bortle Scale': t['mag_filter_option_bortle'], 'Manual': t['mag_filter_option_manual']}
        # Radio button for magnitude filter mode
        st.radio(t['mag_filter_method_label'], options=mag_filter_options_map.keys(),
             format_func=lambda key: mag_filter_options_map[key], # Display translated options
             key="mag_filter_mode_exp", # Update session state directly
             horizontal=True) # Display options horizontally

        # Bortle scale slider (always visible, but only used if mode is 'Bortle Scale')
        # Use state key directly for slider value persistence
        bortle_val = st.slider(t['mag_filter_bortle_label'], min_value=1, max_value=9, key='bortle_slider', help=t['mag_filter_bortle_help'])

        # Manual magnitude sliders (only shown if mode is 'Manual')
        if st.session_state.mag_filter_mode_exp == "Manual":
            manual_min_mag_val = st.slider(t['mag_filter_min_mag_label'], min_value=-5.0, max_value=20.0, step=0.5, format="%.1f", help=t['mag_filter_min_mag_help'], key='manual_min_mag_slider')
            manual_max_mag_val = st.slider(t['mag_filter_max_mag_label'], min_value=-5.0, max_value=20.0, step=0.5, format="%.1f", help=t['mag_filter_max_mag_help'], key='manual_max_mag_slider')
            # Check if min > max and show warning
            if isinstance(st.session_state.manual_min_mag_slider, (int, float)) and isinstance(st.session_state.manual_max_mag_slider, (int, float)):
                 if st.session_state.manual_min_mag_slider > st.session_state.manual_max_mag_slider:
                     st.warning(t['mag_filter_warning_min_max'])

        # --- Altitude Filter ---
        st.markdown("---") # Separator
        st.markdown(t['min_alt_header'])
        # Minimum altitude slider
        # Use state key directly for slider value persistence
        min_altitude_deg_widget = st.slider(t['min_alt_label'], min_value=5, max_value=45, key='min_alt_slider', step=1)
        # The actual astropy quantity (min_altitude_limit) is created later before the search

        # --- Moon Filter ---
        st.markdown("---") # Separator
        st.markdown(t['moon_warning_header'])
        # Moon phase warning threshold slider
        # Use state key directly for slider value persistence
        moon_phase_threshold = st.slider(t['moon_warning_label'], min_value=0, max_value=100, key='moon_phase_slider', step=5)

        # --- Object Type Filter ---
        st.markdown("---") # Separator
        st.markdown(t['object_types_header'])
        effective_selected_types = [] # List of types to actually use in the filter
        all_types = [] # List of all unique types found in the catalog
        # Check if catalog data is loaded and not empty
        if df_catalog_data is not None and not df_catalog_data.empty:
            try:
                # Extract unique object types from the 'Type' column
                if 'Type' in df_catalog_data.columns:
                    all_types = sorted(list(df_catalog_data['Type'].dropna().astype(str).unique()))
                else:
                    st.warning("Catalog is missing the 'Type' column.")
                    all_types = []
            except Exception as e:
                # Handle errors during type extraction
                st.warning(f"Could not extract object types from loaded data: {e}")
                all_types = []

            # If types were found, create the multiselect widget
            if all_types:
                # Ensure the default selection in state only contains valid types from the current catalog
                current_selection_in_state = [sel for sel in st.session_state.object_type_filter_exp if sel in all_types]
                # Update state if it contained invalid types
                if current_selection_in_state != st.session_state.object_type_filter_exp:
                    st.session_state.object_type_filter_exp = current_selection_in_state

                # Set default for the widget: use state if not empty, otherwise select all
                default_for_widget = current_selection_in_state if current_selection_in_state else all_types
                # Create the multiselect widget
                selected_object_types_widget = st.multiselect(
                    t['object_types_label'], options=all_types,
                    default=default_for_widget, key="object_type_filter_exp" # Update state directly
                )
                # Determine the effective filter list: empty list means 'all'
                # If nothing is selected, or if everything is selected, treat as 'all' (empty list)
                if not selected_object_types_widget or set(selected_object_types_widget) == set(all_types):
                    effective_selected_types = [] # Empty list signifies no type filter
                else:
                    # Use the user's specific selection
                    effective_selected_types = selected_object_types_widget
            else: st.info("No object types found in catalog data to filter.")
        else: st.info("Catalog not loaded, cannot filter by type.")


        # --- Direction Filter ---
        st.markdown("---") # Separator
        st.markdown(t['direction_filter_header'])
        all_directions_str = t['direction_option_all'] # Get translated string for "All"
        # Options to display in the selectbox (using translated "All")
        direction_options_display = [all_directions_str] + CARDINAL_DIRECTIONS
        # Corresponding internal values used in logic ('All', 'N', 'NE', ...)
        direction_options_internal = [ALL_DIRECTIONS_KEY] + CARDINAL_DIRECTIONS
        try:
            # Get the current internal value from state
            current_direction_internal = st.session_state.selected_peak_direction
            # Ensure the value in state is valid, default to 'All' if not
            if current_direction_internal not in direction_options_internal:
                 current_direction_internal = ALL_DIRECTIONS_KEY
                 st.session_state.selected_peak_direction = current_direction_internal
            # Find the index corresponding to the current internal value
            current_direction_index = direction_options_internal.index(current_direction_internal)
        except ValueError:
            # Handle case where state value is somehow invalid
            st.session_state.selected_peak_direction = ALL_DIRECTIONS_KEY
            current_direction_index = 0
        # Create the selectbox for direction filter
        selected_direction_display = st.selectbox(
             t['direction_filter_label'], options=direction_options_display,
             index=current_direction_index, # Set default selection based on state
        )
        # Map the selected display value back to the internal value and update state
        if selected_direction_display == all_directions_str:
            st.session_state.selected_peak_direction = ALL_DIRECTIONS_KEY
        else:
            # The display value for cardinal directions is the same as the internal value
            st.session_state.selected_peak_direction = selected_direction_display


    # --- Result Options (Starts collapsed) ---
    with st.expander(t['results_options_expander'], expanded=False):
        # Determine max value for the 'number of objects' slider based on loaded catalog size
        max_slider_val = len(df_catalog_data) if df_catalog_data is not None and not df_catalog_data.empty else 50
        min_slider_val = 5 # Minimum number of objects to show
        # Ensure max value is at least the min value
        actual_max_slider = max(min_slider_val, max_slider_val)
        # Set default value for the slider (e.g., 20, but not more than max)
        default_num_objects = min(20, actual_max_slider)
        # Disable slider if catalog is very small or not loaded
        slider_disabled = actual_max_slider <= min_slider_val
        # Create the slider for max number of objects
        num_objects_to_suggest = st.slider(
             t['results_options_max_objects_label'], min_value=min_slider_val,
             max_value=actual_max_slider, value=default_num_objects,
             step=1, disabled=slider_disabled
        )
        # Map internal keys to translated display options for sorting
        sort_options_map = {
            'Duration & Altitude': t['results_options_sort_duration'],
            'Brightness': t['results_options_sort_magnitude']
        }
        # Ensure the current sort method in state is valid
        if st.session_state.sort_method not in sort_options_map:
            st.session_state.sort_method = 'Duration & Altitude' # Default if invalid
        # Create radio button for sorting method
        st.radio(
            t['results_options_sort_method_label'], options=list(sort_options_map.keys()),
            format_func=lambda key: sort_options_map[key], # Display translated options
            key='sort_method', # Update session state directly
            horizontal=True # Display options horizontally
        )


# --- Main Area ---
# Display Moon Phase information
if moon_illumination: # Check if astroplan function is available
    try:
        # Calculate moon illumination for the reference time
        current_moon_illumination = moon_illumination(reference_time)
        moon_percentage = current_moon_illumination * 100
        # Use columns for layout: SVG image and metric value
        moon_col1, moon_col2 = st.columns([1, 4]) # Adjust column ratios as needed
        # Display SVG in the first column
        with moon_col1: st.markdown(create_moon_phase_svg(current_moon_illumination, size=80), unsafe_allow_html=True)
        # Display metric and warning (if applicable) in the second column
        with moon_col2:
            st.metric(label=t['moon_metric_label'], value=f"{moon_percentage:.0f}%")
            # Show warning if illumination exceeds the user-defined threshold
            if moon_percentage > st.session_state.moon_phase_slider: # Use state key
                 st.error(t['moon_warning_message'].format(moon_percentage, st.session_state.moon_phase_slider))
    except NameError:
        # Handle case where astroplan might be imported but moon_illumination specifically failed
        st.warning("Moon phase calculation requires 'astroplan'. Please install it.")
    except Exception as e:
        # Handle other errors during moon phase calculation
        st.error(t['moon_phase_error'].format(e))
else:
    # Handle case where astroplan itself failed to import
    st.warning("Moon phase calculation disabled: 'astroplan' library not found.")

st.markdown("---") # Separator

# --- Custom Target Plotter ---
with st.expander(t['custom_target_expander']):
    # Use columns for RA, Dec, and Name inputs
    col_ra, col_dec, col_name = st.columns(3)
    with col_ra:
        st.text_input(t['custom_target_ra_label'], key='custom_target_ra', placeholder=t['custom_target_ra_placeholder'])
    with col_dec:
        st.text_input(t['custom_target_dec_label'], key='custom_target_dec', placeholder=t['custom_target_dec_placeholder'])
    with col_name:
        st.text_input(t['custom_target_name_label'], key='custom_target_name', placeholder="e.g., M42")

    # Button to trigger custom graph generation
    custom_target_button_pressed = st.button(t['custom_target_button'])
    custom_target_error_placeholder = st.empty() # Placeholder for errors specific to this section

    if custom_target_button_pressed:
        st.session_state.custom_target_error = "" # Clear previous errors
        st.session_state.custom_target_plot_data = None # Clear previous custom plot data
        st.session_state.show_custom_plot = False # Hide plot area initially

        # Get inputs from state
        custom_ra_str = st.session_state.custom_target_ra
        custom_dec_str = st.session_state.custom_target_dec
        custom_name = st.session_state.custom_target_name or "Custom Target" # Default name if empty

        # --- Validation ---
        if not custom_ra_str or not custom_dec_str:
            st.session_state.custom_target_error = "RA and Dec cannot be empty."
        elif not location_is_valid_for_run or current_location_for_run is None:
            # Need a valid location and observer object to calculate Alt/Az
            st.session_state.custom_target_error = t['custom_target_error_window']
        else:
            # --- Calculation ---
            try:
                # Validate/Parse RA/Dec using SkyCoord
                # Try parsing as sexagesimal first (HH:MM:SS.s / DD:MM:SS), then decimal degrees
                try:
                    custom_target_coord = SkyCoord(ra=custom_ra_str, dec=custom_dec_str, unit=(u.hourangle, u.deg))
                except ValueError:
                    # If sexagesimal fails, try decimal degrees
                    custom_target_coord = SkyCoord(ra=custom_ra_str, dec=custom_dec_str, unit=(u.deg, u.deg))

                # Get current observation window based on main settings
                # Recalculate window to ensure it matches current location/time settings
                start_time, end_time, window_msg = get_observable_window(current_location_for_run, reference_time, is_time_now, lang)

                # Check if a valid window was found
                if start_time and end_time and start_time < end_time:
                    # Generate time steps within the observation window
                    time_delta_hours = (end_time - start_time).to(u.hour).value
                    num_time_steps = max(30, int(time_delta_hours * 12)) # ~5 min steps, min 30 steps
                    observing_times = Time(np.linspace(start_time.jd, end_time.jd, num_time_steps), format='jd', scale='utc')

                    # Calculate Alt/Az path for the custom target using the valid observer location
                    altaz_frame = AltAz(obstime=observing_times, location=current_location_for_run.location)
                    target_altaz = custom_target_coord.transform_to(altaz_frame)

                    # Prepare data dictionary needed for the plotting functions
                    st.session_state.custom_target_plot_data = {
                        "name": custom_name,
                        "times_jd": observing_times.jd,
                        "altitudes": target_altaz.alt.to(u.deg).value,
                        "azimuths": target_altaz.az.to(u.deg).value,
                        "min_alt_limit": st.session_state.min_alt_slider # Use current min alt slider value for the plot line
                    }
                    st.session_state.show_custom_plot = True # Set flag to show plot area below
                    # Hide main results plot if it was shown
                    st.session_state.show_plot = False
                    st.session_state.expanded_object_name = None
                    st.session_state.active_result_plot_data = None
                    st.session_state.plot_object_name = None

                else: # No valid observation window found
                     st.session_state.custom_target_error = window_msg or t['error_no_window']

            except ValueError as e:
                # Handle errors during coordinate parsing
                st.session_state.custom_target_error = f"{t['custom_target_error_coords']} ({e})"
            except Exception as e:
                # Handle other unexpected errors during calculation
                st.session_state.custom_target_error = f"Error calculating custom target path: {e}"
                st.exception(e) # Print full traceback for debugging

        # Display error if any occurred during custom target processing
        if st.session_state.custom_target_error:
             custom_target_error_placeholder.error(st.session_state.custom_target_error)
        else:
             custom_target_error_placeholder.empty() # Clear placeholder if successful
             # Use rerun to ensure the plot area below updates immediately after button press
             # This forces the script to run again, detecting show_custom_plot=True
             st.rerun()


# --- Global Plot Type Selector (Moved outside results list) ---
st.markdown("---") # Separator
# Map internal keys to translated display options
plot_type_options = {
    'Sky Path': t['graph_type_sky_path'],
    'Altitude/Time': t['graph_type_alt_time']
}
# Ensure current selection in state is valid, default to Sky Path if not
if st.session_state.plot_type_selection not in plot_type_options:
    st.session_state.plot_type_selection = 'Sky Path'

# Create radio button for selecting the plot type
# This applies to both the results plots and the custom target plot
st.radio(
    t['graph_type_label'], # Use renamed key for clarity
    options=list(plot_type_options.keys()),
    format_func=lambda key: plot_type_options[key], # Display translated options
    key='plot_type_selection', # Update session state directly
    horizontal=True # Display options horizontally
)
# Changing this radio button will trigger a rerun, updating the visible plot below


# --- Generate and Store Active Plot Figure (Custom or Result) ---
# This section runs on every rerun, including when the plot type radio button changes
active_plot_fig = None # Initialize fig variable for this run to None
plot_data_to_use = None # Initialize data variable

# Determine which plot function to use based on the selected type
plot_func = plot_sky_path if st.session_state.plot_type_selection == 'Sky Path' else plot_altitude_time

# Determine which data to use for plotting (custom target or a result from the list)
if st.session_state.show_custom_plot and st.session_state.custom_target_plot_data is not None:
    # Use custom target data if its plot is active
    plot_data_to_use = st.session_state.custom_target_plot_data
elif st.session_state.show_plot and st.session_state.active_result_plot_data is not None:
    # Use active result data if a result plot is active
    plot_data_to_use = st.session_state.active_result_plot_data

# Generate the plot figure if data is available and plotting libraries are loaded
if plot_data_to_use is not None:
    # Get location tuple needed for plotting functions (can be None if location invalid)
    location_tuple = (
        current_location_for_run.location.lat.deg,
        current_location_for_run.location.lon.deg,
        current_location_for_run.location.height.value
    ) if current_location_for_run and location_is_valid_for_run else None

    # Check if Matplotlib, the plot function, and location are valid
    if plt and plot_func and location_tuple:
        # Call the selected plotting function (plot_sky_path or plot_altitude_time)
        # No spinner here, as it runs on every interaction with the radio button, should be fast
        active_plot_fig = plot_func(
            plot_data_to_use, # The data dictionary (custom or result)
            location_tuple, # Observer location details
            lang, # Current language for labels
            st.session_state.selected_timezone # Current timezone for time axis/markers
        )
    elif not location_tuple:
         # This case should ideally be prevented by disabling buttons, but good to handle
         print("Plot generation skipped: Location is not valid.")
    elif not plt or not plot_func:
         print("Plot generation skipped: Plotting library or function not available.")


# --- Display Custom Target Plot Area ---
custom_plot_area = st.container() # Container to hold the custom plot and close button
if st.session_state.show_custom_plot:
    with custom_plot_area:
        if active_plot_fig: # Check if the figure was generated successfully
            st.pyplot(active_plot_fig) # Display the plot
            # Add a button to close/hide the custom plot
            if st.button(t['results_close_graph_button'], key="close_custom_graph", type="secondary"):
                st.session_state.show_custom_plot = False # Hide the plot area
                st.session_state.custom_target_plot_data = None # Clear the data
                st.rerun() # Rerun to update the UI and remove the plot
        else:
            # Handle case where plot generation failed but the area should be shown (e.g., error occurred)
            st.warning(t['results_graph_not_created']) # Show a message indicating plot failure


# --- Main Search Button & Logic ---
# Disable button if location is invalid or catalog is not loaded
find_disabled = not location_is_valid_for_run or df_catalog_data is None or df_catalog_data.empty
if st.button(t['find_button_label'], key="find_button", type="primary", use_container_width=True, disabled=find_disabled):

    # --- Reset states before starting a new search ---
    st.session_state.expanded_object_name = None # Collapse all result expanders
    st.session_state.show_plot = False # Hide result plot area
    st.session_state.plot_object_name = None # Clear name of plotted result object
    st.session_state.active_result_plot_data = None # Clear active result plot data
    st.session_state.show_custom_plot = False # Hide custom plot area
    st.session_state.custom_target_plot_data = None # Clear custom plot data
    st.session_state.find_button_pressed = True # Flag that search process has started
    st.session_state.last_results = [] # Clear previous results

    # Re-check conditions (mostly redundant with disabled state but safe)
    if not location_is_valid_for_run:
         # Show specific error based on location mode
         st.error(t[f'location_error_{st.session_state.location_choice_key.lower()}_search'] if st.session_state.location_choice_key != 'Default' else t['location_error_undefined'])
    elif current_location_for_run is None or not isinstance(current_location_for_run, Observer): # Check type again
         st.error(t['location_error_undefined']) # Should not happen if disabled logic is correct
    elif df_catalog_data is None or df_catalog_data.empty:
         st.error("Cannot search: Catalog data is not loaded or empty.")
    else:
        # --- Display Search Parameters ---
        with st.container(border=True): # Use a bordered container for parameters
            st.subheader(t['search_params_header'])
            col1, col2, col3 = st.columns(3) # Use columns for layout
            # Column 1: Location
            with col1: st.info(t['search_params_location'].format(location_display_name_for_run))
            # Column 2: Time & Timezone
            with col2:
                date_str_display = reference_time.datetime.date().strftime('%Y-%m-%d')
                # Format time info based on 'Now' or 'Specific' mode
                time_info = t['search_params_time_now'].format(reference_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')) if is_time_now else t['search_params_time_specific'].format(date_str_display)
                st.info(t['search_params_time'].format(time_info))
                st.info(t['search_params_timezone'].format(st.session_state.selected_timezone))
            # Column 3: Filters
            with col3:
                # Get filter values from state
                magnitude_filter_mode_disp = st.session_state.mag_filter_mode_exp
                min_mag_disp = st.session_state.manual_min_mag_slider
                max_mag_disp = st.session_state.manual_max_mag_slider
                bortle_disp = st.session_state.bortle_slider # Use state key
                # Format magnitude filter info
                if magnitude_filter_mode_disp == "Bortle Scale":
                    mag_limit_display = get_magnitude_limit(bortle_disp)
                    mag_info = t['search_params_filter_mag_bortle'].format(bortle_disp, mag_limit_display)
                else: # Manual mode
                    # Ensure min/max order for display if needed
                    if isinstance(min_mag_disp, (int, float)) and isinstance(max_mag_disp, (int, float)) and min_mag_disp > max_mag_disp:
                         min_mag_disp, max_mag_disp = max_mag_disp, min_mag_disp
                    mag_info = t['search_params_filter_mag_manual'].format(min_mag_disp or 0.0, max_mag_disp or 20.0)
                st.info(t['search_params_filter_mag'].format(mag_info))
                # Format altitude and type filter info
                types_display = t['search_params_types_all'] if not effective_selected_types else ', '.join(effective_selected_types)
                min_alt_disp = st.session_state.min_alt_slider # Use state key
                st.info(t['search_params_filter_alt_types'].format(min_alt_disp, types_display))
                # Format direction filter info
                selected_dir_internal = st.session_state.selected_peak_direction
                # Map internal key to display string (including translated "All")
                direction_display_map = {ALL_DIRECTIONS_KEY: t['direction_option_all']}
                direction_display_map.update({k: k for k in CARDINAL_DIRECTIONS}) # N, NE, etc. are same internal/display
                selected_dir_disp = direction_display_map.get(selected_dir_internal, selected_dir_internal) # Fallback to internal key if map fails
                st.info(t['search_params_filter_direction'].format(selected_dir_disp))
        st.markdown("---") # Separator

        # --- Perform Calculations ---
        selected_objects = [] # Final list after sorting/limiting
        all_found_objects = [] # List before direction filter/sorting/limiting
        window_info_placeholder = st.empty() # Placeholder for window calculation messages
        try:
            with st.spinner(t['spinner_searching']): # Show spinner during main calculation
                # Calculate the observation window using the valid Observer object
                start_time, end_time, window_msg = get_observable_window(current_location_for_run, reference_time, is_time_now, lang)

                # Display window calculation message (info, warning, or error)
                if window_msg:
                    formatted_window_msg = window_msg.replace("\n", "\n\n") # Add extra newline for readability
                    # Check keywords to determine message type
                    if "Warning" in window_msg or "Warnung" in window_msg or "Error" in window_msg or "Fehler" in window_msg or "invalid" in window_msg or "polar" in window_msg.lower() or "fallback" in window_msg.lower():
                        window_info_placeholder.warning(formatted_window_msg)
                    else:
                        window_info_placeholder.info(formatted_window_msg)

                # Proceed only if a valid window was found
                if start_time and end_time and start_time < end_time:
                    # Generate time steps for the observation window
                    time_delta_hours = (end_time - start_time).to(u.hour).value
                    # Ensure a minimum number of steps even for short windows
                    num_time_steps = max(30, int(time_delta_hours * 12)) # ~5 min steps, min 30 steps
                    observing_times = Time(np.linspace(start_time.jd, end_time.jd, num_time_steps), format='jd', scale='utc')

                    # Get filter values from state again (to be sure)
                    magnitude_filter_mode_calc = st.session_state.mag_filter_mode_exp
                    min_mag_calc = st.session_state.manual_min_mag_slider
                    max_mag_calc = st.session_state.manual_max_mag_slider
                    bortle_calc = st.session_state.bortle_slider # Use state key
                    # Calculate min altitude limit as Astropy Quantity here
                    min_alt_limit_calc = st.session_state.min_alt_slider * u.deg

                    # --- OPTIMIZATION: Pre-filter DataFrame by Magnitude and Type ---
                    # This reduces the number of objects iterated over in find_observable_objects
                    df_search_subset = df_catalog_data.copy() # Start with the base loaded data
                    # Comment: Applying filters here before the main loop improves performance
                    # Apply magnitude filter to the DataFrame
                    if magnitude_filter_mode_calc == 'Bortle Scale':
                        mag_limit_calc = get_magnitude_limit(bortle_calc)
                        # Keep rows where magnitude is less than or equal to the limit
                        df_search_subset = df_search_subset[df_search_subset['Mag'] <= mag_limit_calc]
                    elif magnitude_filter_mode_calc == 'Manual':
                        # Ensure min/max are valid and ordered before filtering
                        is_min_valid = isinstance(min_mag_calc, (int, float))
                        is_max_valid = isinstance(max_mag_calc, (int, float))
                        if is_min_valid and is_max_valid:
                            if min_mag_calc > max_mag_calc:
                                min_mag_calc, max_mag_calc = max_mag_calc, min_mag_calc # Swap if needed
                            # Keep rows within the manual magnitude range
                            df_search_subset = df_search_subset[
                                (df_search_subset['Mag'] >= min_mag_calc) &
                                (df_search_subset['Mag'] <= max_mag_calc)
                            ]

                    # Apply type filter (if any types are selected)
                    if effective_selected_types: # Check if the list is not empty
                        # Keep rows where the 'Type' is in the selected list
                        df_search_subset = df_search_subset[df_search_subset['Type'].isin(effective_selected_types)]

                    # --- End of Optimization ---

                    # Call the main function to find observable objects using the *subset* DataFrame
                    # Pass the Observer's location attribute (EarthLocation)
                    # Remove filters arguments that are now applied before the call
                    all_found_objects = find_observable_objects(
                        current_location_for_run.location, observing_times, min_alt_limit_calc,
                        df_search_subset, # Pass the pre-filtered DataFrame
                        lang
                    )
                elif not window_msg: # If no window and no message, show default error
                     st.error(t['error_no_window'])

            # --- Post-Calculation Processing (Filtering, Sorting, Limiting) ---
            objects_after_direction_filter = []
            selected_dir_filter_internal = st.session_state.selected_peak_direction
            # Apply direction filter if 'All' is not selected
            if selected_dir_filter_internal != ALL_DIRECTIONS_KEY:
                objects_after_direction_filter = [obj for obj in all_found_objects if obj.get('peak_direction') == selected_dir_filter_internal]
            else:
                # No direction filter needed
                objects_after_direction_filter = all_found_objects

            # Check if any objects remain after all filters
            if objects_after_direction_filter:
                st.success(t['success_objects_found'].format(len(objects_after_direction_filter)))
                # Sort the results based on the selected method
                sort_method = st.session_state.sort_method
                if sort_method == 'Duration & Altitude':
                    # Sort primarily by continuous duration (desc), secondarily by peak altitude (desc)
                    objects_after_direction_filter.sort(key=lambda x: (x.get('cont_duration_hours', 0), x.get('peak_alt', 0)), reverse=True)
                    info_message = t['info_showing_list_duration']
                elif sort_method == 'Brightness':
                    # Sort by magnitude (ascending - brightest first)
                    objects_after_direction_filter.sort(key=lambda x: x['magnitude'])
                    info_message = t['info_showing_list_magnitude']
                else: # Fallback sort (shouldn't happen with radio button)
                    objects_after_direction_filter.sort(key=lambda x: (x.get('cont_duration_hours', 0), x.get('peak_alt', 0)), reverse=True)
                    info_message = t['info_showing_list_duration']

                # Limit the number of results displayed based on the slider
                selected_objects = objects_after_direction_filter[:num_objects_to_suggest]
                st.write(info_message.format(len(selected_objects))) # Show info about sorting/limiting
                st.session_state.last_results = selected_objects # Store final list in state
            else:
                # No objects found matching all criteria
                if all_found_objects and selected_dir_filter_internal != ALL_DIRECTIONS_KEY:
                    # Specific message if direction filter caused no results
                    direction_display_map = {ALL_DIRECTIONS_KEY: t['direction_option_all']}
                    direction_display_map.update({k: k for k in CARDINAL_DIRECTIONS})
                    selected_dir_disp = direction_display_map.get(selected_dir_filter_internal, selected_dir_filter_internal)
                    st.warning(f"No objects found matching all criteria, including peaking in the selected direction: {selected_dir_disp}")
                elif start_time and end_time and start_time < end_time:
                    # Generic message if window was valid but no objects matched other filters
                    st.warning(t['warning_no_objects_found'])
                # Ensure last_results is empty
                st.session_state.last_results = []

        except Exception as main_e:
            # Catch any unexpected errors during the main search process
            st.error(t['error_search_unexpected'])
            st.exception(main_e) # Show full traceback
            st.session_state.last_results = [] # Clear results on error


# --- Display Results List ---
if st.session_state.last_results:
    st.markdown("---")
    st.subheader(t['results_list_header'])
    # Global Plot Type Selector is now above this section

    export_data = [] # List to hold data formatted for CSV export

    # Iterate through the final list of objects to display
    for i, obj in enumerate(st.session_state.last_results):
        # Get localized time string for the peak time
        peak_time_local_str, tz_display_name = get_local_time_str(obj['peak_time_utc'], st.session_state.selected_timezone)

        # Prepare data row for CSV export (using translated headers)
        export_data.append({
            t['results_export_name']: obj.get('name', 'N/A'),
            t['results_export_type']: obj.get('type', 'N/A'),
            t['results_export_constellation']: obj.get('constellation', 'N/A'), # Add constellation
            t['results_export_mag']: obj.get('magnitude', ''), # Use get with default for safety
            t['results_export_ra']: obj.get('ra', 'N/A'),
            t['results_export_dec']: obj.get('dec', 'N/A'),
            t['results_export_max_alt']: f"{obj.get('peak_alt', 0.0):.1f}",
            t['results_export_az_at_max']: f"{obj.get('peak_az', 0.0):.1f}",
            t['results_export_direction_at_max']: obj.get('peak_direction', '?'),
            t['results_export_cont_duration']: f"{obj.get('cont_duration_hours', 0):.1f}", # Use continuous duration
            t['results_export_time_max_utc']: obj.get('peak_time_utc', 'N/A'),
            t['results_export_time_max_local']: f"{peak_time_local_str} ({tz_display_name})" if peak_time_local_str != "N/A" else "N/A"
        })

        # Create an expander for each object
        expander_title = t['results_expander_title'].format(obj.get('name','?'), obj.get('type','?'), obj.get('magnitude', '?'))
        # Check if this expander should be open (based on state)
        is_expanded = (st.session_state.expanded_object_name == obj.get('name'))
        with st.expander(expander_title, expanded=is_expanded):
            # Repeat object name inside for emphasis
            st.markdown(f"#### **{obj.get('name', 'Unknown Object')}**")
            # Use columns for better layout of details
            col1, col2, col3 = st.columns([2, 2, 3]) # Adjust column ratios as needed
            with col1: # Coordinates & Type
                 st.markdown(t['results_coords_header'])
                 st.markdown(f"RA: {obj.get('ra', 'N/A')}")
                 st.markdown(f"Dec: {obj.get('dec', 'N/A')}")
                 st.markdown(f"**{t['results_constellation_label']}** {obj.get('constellation', 'N/A')}") # Display Constellation
                 st.markdown(f"**Type:** {obj.get('type', 'N/A')}")
            with col2: # Peak Altitude & Time
                 st.markdown(t['results_max_alt_header'])
                 st.markdown(f"**{obj.get('peak_alt', 0.0):.1f}°**")
                 st.markdown(t['results_azimuth_label'].format(obj.get('peak_az', 0.0), f" ({obj.get('peak_direction', '?')})")) # Show Azimuth and Direction
                 st.markdown(t['results_best_time_header'])
                 st.markdown(f"**{peak_time_local_str}** ({tz_display_name})")
            with col3: # Duration
                 st.markdown(t['results_cont_duration_header']) # Continuous Duration
                 st.markdown(f"**{t['results_duration_value'].format(obj.get('cont_duration_hours', 0))}**")

            st.markdown("---") # Separator before plot button/plot

            # --- Plotting within Expander ---
            plot_button_key = f"plot_btn_{obj.get('name','')}_{i}" # Unique key for plot button
            close_button_key = f"close_plot_{obj.get('name','')}_{i}" # Unique key for close button

            # Button to trigger plot generation/display for this specific object
            if st.button(t['results_graph_button'], key=plot_button_key):
                # Set state to indicate which object's plot should be shown
                st.session_state.plot_object_name = obj.get('name')
                st.session_state.show_plot = True # Flag to show the plot area
                st.session_state.expanded_object_name = obj.get('name') # Keep this expander open
                st.session_state.active_result_plot_data = obj # Store data needed for replotting on type change
                # Hide custom plot if it was shown
                st.session_state.show_custom_plot = False
                st.session_state.custom_target_plot_data = None
                st.rerun() # Rerun to generate and display the plot

            # Display area for the result plot
            # Check if the plot for *this specific object* should be shown
            if st.session_state.show_plot and st.session_state.plot_object_name == obj.get('name'):
                if active_plot_fig: # Check if the figure was generated successfully (above the loop)
                    st.pyplot(active_plot_fig) # Display the plot
                    # Add a button to close/hide this plot
                    if st.button(t['results_close_graph_button'], key=close_button_key, type="secondary"):
                        # Reset plot-related state variables
                        st.session_state.show_plot = False
                        st.session_state.plot_object_name = None
                        st.session_state.active_result_plot_data = None
                        # Optionally collapse the expander when closing the plot
                        # st.session_state.expanded_object_name = None
                        st.rerun() # Rerun to update the UI and remove the plot
                else:
                    # Show error message if plot failed but should be shown
                    st.warning(t['results_graph_not_created'])


    # --- CSV Export Button ---
    # Show button only if there is data to export and pandas is available
    if export_data and pd:
        st.markdown("---") # Separator
        try:
            # Create DataFrame from the export data list
            df_export = pd.DataFrame(export_data)
            # Define desired column order for the CSV file
            # Use translated headers from the 't' dictionary
            cols = [t['results_export_name'], t['results_export_type'], t['results_export_constellation'],
                    t['results_export_mag'], t['results_export_cont_duration'],
                    t['results_export_max_alt'], t['results_export_az_at_max'], t['results_export_direction_at_max'],
                    t['results_export_time_max_local'], t['results_export_time_max_utc'],
                    t['results_export_ra'], t['results_export_dec']]
            # Ensure only existing columns are selected (in case some data was missing)
            cols_exist = [col for col in cols if col in df_export.columns]
            df_export = df_export[cols_exist] # Reorder/select columns

            # Convert DataFrame to CSV string in memory
            csv_buffer = io.StringIO()
            # Use semicolon separator, UTF-8 encoding with BOM (for Excel compatibility)
            df_export.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8-sig')

            # Create filename including the observation date
            file_date = reference_time.datetime.date().strftime('%Y%m%d')
            # Create Streamlit download button
            st.download_button(
                label=t['results_save_csv_button'], # Button label
                data=csv_buffer.getvalue(), # CSV data as string
                file_name=t['results_csv_filename'].format(file_date), # Filename
                mime="text/csv" # MIME type for CSV
            )
        except Exception as csv_e:
            # Handle errors during CSV creation or export
            st.error(t['results_csv_export_error'].format(csv_e))


# --- Message if search was run but found nothing ---
elif st.session_state.find_button_pressed and not st.session_state.last_results:
    # The warning message (e.g., 'warning_no_objects_found') is already shown
    # in the main search logic block where the results are processed.
    # No need to repeat the message here.
    # Optionally, reset the button press state *after* attempting to display results
    # st.session_state.find_button_pressed = False # Or keep it pressed until next action
    pass # Message already handled

# --- Initial message or if catalog failed to load ---
elif not st.session_state.find_button_pressed:
    if df_catalog_data is not None:
        # Catalog loaded, show initial prompt to guide the user
        if not location_is_valid_for_run:
            # If location isn't set/valid yet, prompt user to set it
            st.warning(t['info_initial_prompt'])
        # else: # Location is set, catalog loaded, but search not run yet
            # Optionally show a message like:
            # st.info("Location set. Adjust filters and click 'Find Observable Objects'.")
            # This might be too verbose, so it's commented out.
    else:
         # Catalog failed to load. Error message is already shown by load_ongc_data.
         # Add a persistent error in the main area if needed.
         st.error("Cannot proceed: Failed to load DSO catalog. Check file and console output, then restart.")

