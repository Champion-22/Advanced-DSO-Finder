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

# --- Page Config (MUST BE FIRST Streamlit command after st import) ---
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

# Timezone Library
try:
    import pytz
except ImportError as e:
     import_errors.append(f"Error: Required timezone library not found. Install: pip install pytz ({e})")
     pytz = None


# --- Display Import Errors (NOW it's safe to use st.error) ---
if import_errors:
    st.error("### Library Import Errors")
    for error in import_errors:
        st.error(error)
    st.info("Please install the missing libraries and restart the app.")
    st.stop() # Stop execution if imports failed

# --- Check if essential classes/functions were imported ---
essential_imports_ok = all([
    Time, np, u, EarthLocation, SkyCoord, get_sun, AltAz, moon_illumination, pd, plt, pytz, mdates
])
if not essential_imports_ok:
    st.error("Stopping execution due to missing essential libraries.")
    st.stop()

# --- Translations ---
# (Unverändert)
translations = {
    'en': {
        'page_title': "Advanced DSO Finder",
        'app_title': "✨ Advanced DSO Finder ✨",
        'settings_header': "Settings",
        'language_select_label': "Language / Sprache",
        'location_expander': "📍 Location",
        'location_select_label': "Select Location",
        'location_option_default': "Default ({})",
        'location_option_manual': "Enter Manually",
        'location_lat_label': "Latitude (°N)",
        'location_lon_label': "Longitude (°E)",
        'location_elev_label': "Elevation (Meters)",
        'location_manual_display': "Manual ({:.4f}, {:.4f})",
        'location_error': "Location Error: {}",
        'location_error_fallback': "ERROR - Using Default",
        'location_error_manual_none': "Manual location fields cannot be empty.",
        'location_error_manual_search': "Cannot search: Manual location fields are invalid or empty.",
        'location_error_undefined': "Cannot search: Location is not defined.",
        'time_expander': "⏱️ Time & Timezone",
        'time_select_label': "Select Time",
        'time_option_now': "Now (upcoming night)",
        'time_option_specific': "Specific Night",
        'time_date_select_label': "Select Date:",
        'timezone_select_label': "Select Timezone:",
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
        'window_info_template': "{}",
        'error_no_window': "No valid observation window found.",
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
        'results_export_time_max_local': "Time at Max (Selected TZ)",
        'results_export_duration': "Visible Duration (h)",
        'results_expander_title': "{} ({}) - Mag: {:.1f}",
        'results_coords_header': "**Coordinates:**",
        'results_max_alt_header': "**Max. Altitude:**",
        'results_azimuth_label': "(Azimuth: {:.1f}°{})",
        'results_direction_label': ", Direction: {}",
        'results_best_time_header': "**Best Time (Selected TZ):**",
        'results_duration_header': "**Visible Duration:**",
        'results_duration_value': "{:.1f} hours",
        'results_plot_button': "📈 Altitude Plot",
        'results_spinner_plotting': "Creating plot...",
        'results_plot_error': "Plot Error: {}",
        'results_plot_not_created': "Plot could not be created.",
        'results_close_plot_button': "Close Plot",
        'results_save_csv_button': "💾 Save Result List as CSV",
        'results_csv_filename': "dso_observation_list_{}.csv",
        'results_csv_export_error': "CSV Export Error: {}",
        'warning_no_objects_found': "No objects found matching all criteria.",
        'info_initial_prompt': "Adjust settings in the sidebar and click 'Find Observable Objects' to start.",
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
        'app_title': "✨ Erweiterter DSO Finder ✨",
        'settings_header': "Einstellungen",
        'language_select_label': "Sprache / Language",
        'location_expander': "📍 Standort",
        'location_select_label': "Standort wählen",
        'location_option_default': "Standard ({})",
        'location_option_manual': "Manuell eingeben",
        'location_lat_label': "Breitengrad (°N)",
        'location_lon_label': "Längengrad (°E)",
        'location_elev_label': "Höhe (Meter)",
        'location_manual_display': "Manuell ({:.4f}, {:.4f})",
        'location_error': "Standort Fehler: {}",
        'location_error_fallback': "FEHLER - Nutze Standard",
        'location_error_manual_none': "Manuelle Standortfelder dürfen nicht leer sein.",
        'location_error_manual_search': "Suche nicht möglich: Manuelle Standortfelder sind ungültig oder leer.",
        'location_error_undefined': "Suche nicht möglich: Standort ist nicht definiert.",
        'time_expander': "⏱️ Zeitpunkt & Zeitzone",
        'time_select_label': "Zeitpunkt wählen",
        'time_option_now': "Jetzt (kommende Nacht)",
        'time_option_specific': "Andere Nacht",
        'time_date_select_label': "Datum auswählen:",
        'timezone_select_label': "Zeitzone auswählen:",
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
        'window_info_template': "{}",
        'error_no_window': "Kein gültiges Beobachtungsfenster gefunden.",
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
        'results_export_time_max_local': "Zeit bei Max (Gewählte ZZ)",
        'results_export_duration': "Sichtbare Dauer (h)",
        'results_expander_title': "{} ({}) - Mag: {:.1f}",
        'results_coords_header': "**Koordinaten:**",
        'results_max_alt_header': "**Max. Höhe:**",
        'results_azimuth_label': "(Azimut: {:.1f}°{})",
        'results_direction_label': ", Richtung: {}",
        'results_best_time_header': "**Beste Zeit (Gewählte ZZ):**",
        'results_duration_header': "**Sichtbare Dauer:**",
        'results_duration_value': "{:.1f} Stunden",
        'results_plot_button': "📈 Höhenverlauf",
        'results_spinner_plotting': "Erstelle Plot...",
        'results_plot_error': "Plot Fehler: {}",
        'results_plot_not_created': "Plot konnte nicht erstellt werden.",
        'results_close_plot_button': "Plot schliessen",
        'results_save_csv_button': "💾 Ergebnisliste als CSV speichern",
        'results_csv_filename': "dso_beobachtungsliste_{}.csv",
        'results_csv_export_error': "CSV Export Fehler: {}",
        'warning_no_objects_found': "Keine Objekte gefunden, die allen Kriterien entsprechen.",
        'info_initial_prompt': "Einstellungen in der Seitenleiste anpassen & 'Beobachtbare Objekte finden' klicken.",
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
    }
}

# --- Global Configuration ---
DEFAULT_LOCATION_NAME = "Schötz, Lucerne"
DEFAULT_LAT = 47.17
DEFAULT_LON = 8.01
DEFAULT_HEIGHT = 550
DEFAULT_LOCATION = EarthLocation(lat=DEFAULT_LAT * u.deg, lon=DEFAULT_LON * u.deg, height=DEFAULT_HEIGHT * u.m)
DEFAULT_TIMEZONE = "Europe/Zurich" # Default timezone

# --- Path to Catalog File ---
# Assume the script and the data file are in the same directory when deployed
APP_DIR = os.path.dirname(os.path.abspath(__file__))
# !!! WICHTIG: Stelle sicher, dass dieser Dateiname GENAU mit deiner hochgeladenen Datei übereinstimmt !!!
CATALOG_FILENAME = "ongc.csv"
# Construct path assuming CSV is in the SAME directory as the script
CATALOG_FILEPATH = os.path.join(APP_DIR, CATALOG_FILENAME)


# Define cardinal directions
CARDINAL_DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
# Add an option for 'All' for the selectbox (use English key for state)
ALL_DIRECTIONS_KEY = translations['en']['direction_option_all'] # e.g., "All"
DIRECTION_OPTIONS_EN = [ALL_DIRECTIONS_KEY] + CARDINAL_DIRECTIONS
DIRECTION_OPTIONS_DE = [translations['de']['direction_option_all']] + CARDINAL_DIRECTIONS

# --- Initialize Session State ---
def initialize_session_state():
    """Initializes all required session state keys if they don't exist."""
    defaults = {
        'language': 'en',
        'plot_object_name': None,
        'show_plot': False,
        'last_results': [],
        'find_button_pressed': False,
        'manual_lat_val': DEFAULT_LAT,
        'manual_lon_val': DEFAULT_LON,
        'manual_height_val': DEFAULT_HEIGHT,
        'location_choice_key': 'Default',
        'expanded_object_name': None,
        'manual_min_mag_slider': 0.0,
        'manual_max_mag_slider': 16.0,
        'object_type_filter_exp': [],
        'selected_timezone': DEFAULT_TIMEZONE,
        'mag_filter_mode_exp': 'Bortle Scale',
        'sort_method': 'Duration & Altitude',
        'selected_peak_direction': ALL_DIRECTIONS_KEY, # Default to "All"
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

initialize_session_state()

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
        utc_offset_hours = 1 # Fallback offset

    start_date = reference_time.datetime.date()
    end_date = start_date + timedelta(days=1)
    local_dt_start = datetime.combine(start_date, time(21, 0))
    local_dt_end = datetime.combine(end_date, time(3, 0))
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
        midnight_date = reference_date + timedelta(days=1)
        midnight = Time(datetime.combine(midnight_date, time(0, 0)))
        time_range = midnight + np.linspace(-12, 12, 100) * u.hour
        sun_altaz = get_sun(time_range).transform_to(AltAz(obstime=time_range, location=observer_location))
        dark_indices = np.where(sun_altaz.alt < -18 * u.deg)[0]

        if len(dark_indices) > 0:
            start_time_calc = time_range[dark_indices[0]]
            end_time_calc = time_range[dark_indices[-1]]
            if end_time_calc <= start_time_calc:
                status_message = t['window_invalid_calc'].format(start_time_calc.iso, end_time_calc.iso)
                start_time, end_time = _get_fallback_window(reference_time)
                status_message += t['window_fallback_append'].format(start_time.iso, end_time.iso)
            else:
                start_time = start_time_calc
                end_time = end_time_calc
                date_str = reference_date.strftime('%Y-%m-%d')
                start_fmt = start_time.to_datetime(timezone.utc).strftime('%H:%M %Z')
                end_fmt = end_time.to_datetime(timezone.utc).strftime('%H:%M %Z')
                if is_now and start_time < reference_time:
                    start_time = reference_time
                    start_fmt = start_time.to_datetime(timezone.utc).strftime('%H:%M %Z') # Update formatted time
                    status_message = t['window_starts_now'].format(start_fmt, end_fmt)
                elif is_now and start_time >= reference_time:
                     status_message = t['window_starts_at'].format(start_fmt, end_fmt)
                else:
                     status_message = t['window_for_night'].format(date_str, start_fmt, end_fmt)
                if is_now and end_time < reference_time:
                    status_message = t['window_already_passed']
                    return get_observable_window(observer_location, reference_time + timedelta(days=1), True, lang)
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
    selected_object_types: list,
    df_catalog: pd.DataFrame, # Pass DataFrame instead of using global
    lang: str
) -> list:
    """
    Finds DSOs from the catalog DataFrame visible during the observing times.
    Calculates visibility duration and peak direction for sorting/filtering.
    """
    t = translations[lang]
    observable_objects = []
    magnitude_limit = None

    # Determine magnitude limit based on filter mode
    if magnitude_filter_mode == 'Bortle Scale':
        magnitude_limit = get_magnitude_limit(bortle_scale)
    elif magnitude_filter_mode == 'Manual':
        if isinstance(manual_min_mag, (int, float)) and isinstance(manual_max_mag, (int, float)):
            if manual_min_mag > manual_max_mag:
                manual_min_mag, manual_max_mag = manual_max_mag, manual_min_mag
        else:
             manual_min_mag = None # Disable filter if invalid
             manual_max_mag = None

    # Iterate over the DataFrame rows
    for index, row in df_catalog.iterrows():
        # Get data from row
        name = row['Name']
        ra_str = row['RA_str'] # Use the pre-formatted string for SkyCoord
        dec_str = row['Dec_str'] # Use the pre-formatted string for SkyCoord
        mag = row['Mag'] # Use the cleaned magnitude
        obj_type = row['Type']

        # Apply Type Filter (if any types are selected)
        if selected_object_types and obj_type not in selected_object_types:
            continue

        # Apply Magnitude Filter
        if not isinstance(mag, (int, float)): continue # Skip if magnitude is invalid

        if magnitude_filter_mode == 'Bortle Scale':
            if magnitude_limit is not None and mag > magnitude_limit:
                continue
        elif magnitude_filter_mode == 'Manual':
            if isinstance(manual_min_mag, (int, float)) and isinstance(manual_max_mag, (int, float)):
                 if not (manual_min_mag <= mag <= manual_max_mag):
                     continue

        # Calculate observability
        try:
            target = SkyCoord(ra=ra_str, dec=dec_str, frame='icrs', unit=(u.hourangle, u.deg))
            altaz_frame = AltAz(obstime=observing_times, location=location)
            target_altaz = target.transform_to(altaz_frame)
            altitudes = target_altaz.alt
            azimuths = target_altaz.az
            valid_indices = np.where(altitudes >= min_altitude_limit)[0]

            if len(valid_indices) > 0:
                # Calculate peak altitude within the valid window
                peak_in_window_index = valid_indices[np.argmax(altitudes[valid_indices])]
                peak_alt_val = altitudes[peak_in_window_index].to(u.deg).value
                peak_az_val = azimuths[peak_in_window_index].to(u.deg).value
                peak_direction = azimuth_to_direction(peak_az_val) # Calculate direction

                # Calculate duration above horizon
                first_valid_time = observing_times[valid_indices[0]]
                last_valid_time = observing_times[valid_indices[-1]]
                duration = last_valid_time - first_valid_time
                duration_hours = duration.to(u.hour).value if hasattr(duration, 'to') else duration.total_seconds() / 3600.0

                observable_objects.append({
                    "name": name, "type": obj_type, "magnitude": mag,
                    "ra_str": ra_str, "dec_str": dec_str,
                    "ra": target.ra.to_string(unit=u.hour, sep='hms', precision=1), # Formatted RA
                    "dec": target.dec.to_string(unit=u.deg, sep='dms', precision=0), # Formatted Dec
                    "peak_alt": peak_alt_val,
                    "peak_az": peak_az_val,
                    "peak_direction": peak_direction, # Store direction
                    "peak_time_utc": observing_times[peak_in_window_index].iso,
                    "duration_hours": duration_hours, # Store duration
                    "times_jd": observing_times.jd,
                    "altitudes": altitudes.to(u.deg).value,
                    "azimuths": azimuths.to(u.deg).value,
                    "min_alt_limit": min_altitude_limit.value
                })
        except Exception as e:
            st.warning(t['error_processing_object'].format(name, e))

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

@st.cache_resource(show_spinner=False)
def plot_altitude(obj_data: dict, location_tuple: tuple, lang: str, tz_name: str): # Added tz_name
    """Creates a Matplotlib altitude plot. Caches the figure object."""
    t = translations[lang]
    if plt is None or mdates is None: return None
    if pytz is None: return None

    fig, ax = plt.subplots()
    try:
        times = Time(obj_data['times_jd'], format='jd')
        try:
            selected_tz = pytz.timezone(tz_name)
            times_local = [t_inst.to_datetime(timezone=selected_tz) for t_inst in times]
            tz_name_display = tz_name
            xlabel = t['plot_time_label_local'].format(tz_name_display)
        except Exception as tz_err:
             print(f"Timezone conversion/lookup error in plot: {tz_err}")
             times_local = times.datetime
             xlabel = t['plot_time_label_utc']

        ax.plot(times_local, obj_data['altitudes'], label=t['plot_altitude_label'], color='#00C0F0')
        ax.axhline(obj_data['min_alt_limit'], color='#FF4040', linestyle='--', label=t['plot_min_altitude_label'].format(obj_data["min_alt_limit"]))
        ax.set_ylim(0, 90)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(t['plot_ylabel'])
        ax.set_title(t['plot_title'].format(obj_data['name']))
        ax.legend()
        ax.grid(True, linestyle=':', linewidth=0.5, color='#555555')
        xfmt = mdates.DateFormatter('%H:%M') # Use 24-hour format
        ax.xaxis.set_major_formatter(xfmt)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        plt.tight_layout()
    except Exception as e:
        print(f"Error plotting altitude for {obj_data.get('name', 'Unknown')}: {e}")
        plt.close(fig)
        return None
    return fig

def get_local_time_str(utc_iso_time: str, tz_name: str) -> tuple[str, str]:
    """Converts UTC ISO time string to time string in the specified timezone."""
    try:
        if Time is None or pytz is None: return "N/A", ""
        selected_tz = pytz.timezone(tz_name)
        dt_peak_utc = Time(utc_iso_time).datetime.replace(tzinfo=timezone.utc)
        dt_peak_local = dt_peak_utc.astimezone(selected_tz)
        tz_display_name = tz_name
        peak_time_local_str = dt_peak_local.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Error converting time to timezone {tz_name}: {e}")
        tz_display_name = tz_name
        peak_time_local_str = "N/A"
    return peak_time_local_str, tz_display_name

# --- Data Loading Function ---
@st.cache_data # Cache the loaded and processed data
def load_ongc_data(catalog_path: str, lang: str) -> pd.DataFrame | None:
    """Loads, filters, and preprocesses data from the OpenNGC CSV file."""
    t = translations[lang]
    try:
        # Reverted to sep=';' based on user feedback
        # Removed engine='python' as likely not needed for semicolon
        df = pd.read_csv(catalog_path, sep=';', comment='#')

        # --- Data Cleaning & Filtering ---
        # 1. Filter by Object Type (Keep common DSO types)
        dso_types = ['Galaxy', 'Globular Cluster', 'Open Cluster', 'Nebula',
                     'Planetary Nebula', 'Supernova Remnant', 'HII', 'Emission Nebula',
                     'Reflection Nebula', 'Cluster + Nebula', 'Gal', 'GCl', 'Gx', 'OC',
                     'PN', 'SNR', 'Neb', 'EmN', 'RfN', 'C+N', 'Gxy', 'AGN']
        type_pattern = '|'.join(dso_types)
        if 'Type' not in df.columns:
            st.error("Column 'Type' not found in the catalog file.")
            return None
        df_filtered = df[df['Type'].str.contains(type_pattern, case=False, na=False)].copy()

        # 2. Handle Magnitude (Convert to numeric, handle errors/missing values)
        mag_col = None
        if 'B-Mag' in df_filtered.columns: mag_col = 'B-Mag'
        elif 'Mag' in df_filtered.columns: mag_col = 'Mag'

        if mag_col is None:
            st.error(f"Magnitude column ('B-Mag' or 'Mag') not found.")
            return None
        df_filtered['Mag'] = pd.to_numeric(df_filtered[mag_col], errors='coerce')
        df_filtered.dropna(subset=['Mag'], inplace=True)

        # 3. Handle Coordinates
        if 'RA' not in df_filtered.columns or 'Dec' not in df_filtered.columns:
             st.error("RA or Dec column not found.")
             return None
        df_filtered['RA_str'] = df_filtered['RA']
        df_filtered['Dec_str'] = df_filtered['Dec']

        # 4. Select and Rename Columns
        if 'Name' not in df_filtered.columns:
            st.error("'Name' column not found.")
            return None
        df_final = df_filtered[['Name', 'RA_str', 'Dec_str', 'Mag', 'Type']].copy()

        st.success(t['info_catalog_loaded'].format(len(df_final)))
        if df_final.empty:
             st.warning(t['warning_catalog_empty'])
             return None
        return df_final

    except FileNotFoundError:
        st.error(f"Catalog file not found at: {catalog_path}")
        st.info("Please ensure the file exists and the path/filename in the script are correct.")
        return None
    except pd.errors.EmptyDataError:
        st.error(f"Catalog file is empty: {catalog_path}")
        return None
    except Exception as e:
        st.error(t['error_loading_catalog'].format(e))
        if "tokenizing data" in str(e):
             st.info("This often means the wrong separator (delimiter) or inconsistent file structure. Please check the actual separator in your file (e.g., ';', ',', '\\t') and adjust the 'sep=...' argument in the load_ongc_data function accordingly.")
        else:
             st.info("Please check the file path, filename, and format.")
        st.exception(e)
        return None

# --- Get Current Language and Translations ---
lang = st.session_state.language
t = translations[lang]

# --- Load Catalog Data ---
df_catalog_data = load_ongc_data(CATALOG_FILEPATH, lang)

# --- Custom CSS Styling ---
st.markdown("""
<style>
    /* (CSS unchanged) */
    .main .block-container { background-color: #1E1E1E; color: #EAEAEA; border-radius: 10px; padding: 2rem; }
    div[data-testid="stButton"] > button:not([kind="secondary"]) { background-image: linear-gradient(to right, #007bff, #0056b3); color: white; border: none; padding: 10px 24px; text-align: center; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px; transition-duration: 0.4s; }
    div[data-testid="stButton"] > button:not([kind="secondary"]):hover { background-image: linear-gradient(to right, #0056b3, #003d80); color: white; }
     div[data-testid="stButton"] > button[kind="secondary"] { background-color: #555; color: #eee; }
     div[data-testid="stButton"] > button[kind="secondary"]:hover { background-color: #777; color: white; }
    .streamlit-expanderHeader { background-color: #333333; color: #EAEAEA; border-radius: 5px; }
    div[data-testid="stMetric"] { background-color: #2a2a2a; border-radius: 8px; padding: 10px; }
    div[data-testid="stMetric"] > div[data-testid="stMetricLabel"] { color: #AAAAAA; }
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.title(t['app_title']) # Use translated title

# --- Sidebar ---
with st.sidebar:
    st.header(t['settings_header'])

    # --- Language Selector ---
    language_options = {'en': 'English', 'de': 'Deutsch'}
    selected_lang_key = st.radio(
        t['language_select_label'], options=language_options.keys(),
        format_func=lambda key: language_options[key], key='language_radio',
        index=list(language_options.keys()).index(st.session_state.language)
    )
    if selected_lang_key != st.session_state.language:
        st.session_state.language = selected_lang_key
        st.rerun()

    # --- Location Settings (Simplified - No Cookies) ---
    with st.expander(t['location_expander'], expanded=True):
        location_options_map = {
            'Default': t['location_option_default'].format(DEFAULT_LOCATION_NAME),
            'Manual': t['location_option_manual']
        }
        st.radio(t['location_select_label'], options=list(location_options_map.keys()),
            format_func=lambda key: location_options_map[key], key="location_choice_key")
        current_location_for_run = None
        location_is_valid_for_run = False
        location_display_name_for_run = ""
        warning_placeholder = st.empty()

        if st.session_state.location_choice_key == "Manual":
            st.number_input(t['location_lat_label'], min_value=-90.0, max_value=90.0, step=0.01, format="%.4f", key="manual_lat_val")
            st.number_input(t['location_lon_label'], min_value=-180.0, max_value=180.0, step=0.01, format="%.4f", key="manual_lon_val")
            st.number_input(t['location_elev_label'], min_value=-500, step=10, format="%d", key="manual_height_val")
            lat_val = st.session_state.manual_lat_val
            lon_val = st.session_state.manual_lon_val
            height_val = st.session_state.manual_height_val
            if lat_val is None or lon_val is None or height_val is None or \
               not isinstance(lat_val, (int, float)) or not isinstance(lon_val, (int, float)) or not isinstance(height_val, (int, float)):
                warning_placeholder.warning(t['location_error_manual_none'])
                location_display_name_for_run = t['location_error_fallback']
            else:
                try:
                    current_location_for_run = EarthLocation(lat=lat_val * u.deg, lon=lon_val * u.deg, height=height_val * u.m)
                    location_display_name_for_run = t['location_manual_display'].format(lat_val, lon_val)
                    location_is_valid_for_run = True
                    warning_placeholder.empty()
                except Exception as e:
                    st.error(t['location_error'].format(e))
                    location_display_name_for_run = t['location_error_fallback']
        else: # Default location
             current_location_for_run = DEFAULT_LOCATION
             location_display_name_for_run = t['location_option_default'].format(DEFAULT_LOCATION_NAME)
             location_is_valid_for_run = True
             warning_placeholder.empty()

    # --- Time & Timezone Settings ---
    with st.expander(t['time_expander'], expanded=True):
        time_options_map = {'Now': t['time_option_now'], 'Specific': t['time_option_specific']}
        time_choice_key = st.radio(
            t['time_select_label'], options=time_options_map.keys(),
            format_func=lambda key: time_options_map[key], key="time_choice_exp"
        )
        is_time_now = (time_choice_key == "Now")
        reference_time = Time.now()
        if not is_time_now:
            selected_date = st.date_input(
                t['time_date_select_label'], date.today(),
                min_value=date.today()-timedelta(days=365*5),
                max_value=date.today()+timedelta(days=365*1)
            )
            reference_time = Time(datetime.combine(selected_date, time(12, 0)))
        st.markdown("---")
        common_timezones = ["UTC", "Europe/Zurich", "Europe/Berlin", "Europe/London", "America/New_York", "America/Los_Angeles", "Asia/Tokyo"]
        if DEFAULT_TIMEZONE not in common_timezones: common_timezones.insert(0, DEFAULT_TIMEZONE)
        try:
            current_tz_index = common_timezones.index(st.session_state.selected_timezone)
        except ValueError:
            st.session_state.selected_timezone = DEFAULT_TIMEZONE
            current_tz_index = common_timezones.index(DEFAULT_TIMEZONE)
        st.selectbox(t['timezone_select_label'], options=common_timezones, index=current_tz_index, key="selected_timezone")

    # --- Filter Settings ---
    with st.expander(t['filters_expander'], expanded=True):
        # Magnitude Filter
        st.markdown(t['mag_filter_header'])
        mag_filter_options_map = {'Bortle Scale': t['mag_filter_option_bortle'], 'Manual': t['mag_filter_option_manual']}
        st.radio(t['mag_filter_method_label'], options=mag_filter_options_map.keys(),
            format_func=lambda key: mag_filter_options_map[key], key="mag_filter_mode_exp", horizontal=True)
        bortle_val = 5
        manual_min_mag_val = st.session_state.manual_min_mag_slider
        manual_max_mag_val = st.session_state.manual_max_mag_slider
        if st.session_state.mag_filter_mode_exp == "Bortle Scale":
            bortle_val = st.slider(t['mag_filter_bortle_label'], min_value=1, max_value=9, value=5, step=1, help=t['mag_filter_bortle_help'], key='bortle_slider')
        elif st.session_state.mag_filter_mode_exp == "Manual":
            manual_min_mag_val = st.slider(t['mag_filter_min_mag_label'], min_value=0.0, max_value=20.0, step=0.5, format="%.1f", help=t['mag_filter_min_mag_help'], key='manual_min_mag_slider')
            manual_max_mag_val = st.slider(t['mag_filter_max_mag_label'], min_value=0.0, max_value=20.0, step=0.5, format="%.1f", help=t['mag_filter_max_mag_help'], key='manual_max_mag_slider')
            if isinstance(st.session_state.manual_min_mag_slider, (int, float)) and isinstance(st.session_state.manual_max_mag_slider, (int, float)):
                 if st.session_state.manual_min_mag_slider > st.session_state.manual_max_mag_slider:
                     st.warning(t['mag_filter_warning_min_max'])

        # Altitude Filter
        st.markdown("---")
        st.markdown(t['min_alt_header'])
        min_altitude_deg = st.slider(t['min_alt_label'], min_value=5, max_value=45, value=20, step=1)
        min_altitude_limit = min_altitude_deg * u.deg

        # Moon Filter
        st.markdown("---")
        st.markdown(t['moon_warning_header'])
        moon_phase_threshold = st.slider(t['moon_warning_label'], min_value=0, max_value=100, value=35, step=5)

        # Object Type Filter (Kept as Multiselect)
        st.markdown("---")
        st.markdown(t['object_types_header'])
        effective_selected_types = []
        if df_catalog_data is not None and not df_catalog_data.empty:
            try:
                all_types = sorted(list(df_catalog_data['Type'].astype(str).unique()))
            except Exception as e:
                st.warning(f"Could not extract object types from loaded data: {e}")
                all_types = []
            if all_types:
                current_selection_in_state = st.session_state.object_type_filter_exp
                default_for_widget = current_selection_in_state if current_selection_in_state else all_types
                selected_object_types = st.multiselect(
                    t['object_types_label'], options=all_types,
                    default=default_for_widget, key="object_type_filter_exp"
                )
                if selected_object_types is None: selected_object_types = []
                effective_selected_types = selected_object_types if selected_object_types else all_types
            else: st.info("No object types found in catalog data.")
        else: st.info("Catalog not loaded, cannot filter by type.")

        # Direction Filter (Changed to Selectbox)
        st.markdown("---")
        st.markdown(t['direction_filter_header'])
        # Prepare options including "All" using the current language
        all_directions_str = t['direction_option_all']
        direction_options = [all_directions_str] + CARDINAL_DIRECTIONS
        # Find index of current selection in state
        try:
            # Ensure the value in state is one of the valid options
            current_direction = st.session_state.selected_peak_direction
            if current_direction not in direction_options:
                 current_direction = all_directions_str # Fallback to "All"
                 st.session_state.selected_peak_direction = current_direction
            current_direction_index = direction_options.index(current_direction)
        except ValueError:
             # Fallback if state is somehow completely wrong
             st.session_state.selected_peak_direction = all_directions_str
             current_direction_index = 0

        st.selectbox(
             t['direction_filter_label'],
             options=direction_options,
             index=current_direction_index,
             key='selected_peak_direction' # State key stores the selected direction string ("All", "N", "NE", etc.)
        )

    # --- Result Options ---
    with st.expander(t['results_options_expander']):
        max_slider_val = len(df_catalog_data) if df_catalog_data is not None else 50
        num_objects_to_suggest = st.slider(t['results_options_max_objects_label'], min_value=5, max_value=max_slider_val, value=min(20, max_slider_val), step=1)
        # --- Add Sort Method Selection ---
        sort_options_map = {
            'Duration & Altitude': t['results_options_sort_duration'],
            'Brightness': t['results_options_sort_magnitude']
        }
        st.radio(
            t['results_options_sort_method_label'],
            options=list(sort_options_map.keys()),
            format_func=lambda key: sort_options_map[key],
            key='sort_method', # Use state key
            horizontal=True
        )


# --- Main Area ---
# Display Moon Phase
try:
    current_moon_illumination = moon_illumination(reference_time)
    moon_percentage = current_moon_illumination * 100
    moon_col1, moon_col2 = st.columns([1, 4])
    with moon_col1: st.markdown(create_moon_phase_svg(current_moon_illumination, size=80), unsafe_allow_html=True)
    with moon_col2:
        st.metric(label=t['moon_metric_label'], value=f"{moon_percentage:.0f}%")
        if moon_percentage > moon_phase_threshold: st.error(t['moon_warning_message'].format(moon_percentage, moon_phase_threshold))
except Exception as e: st.error(t['moon_phase_error'].format(e))

st.markdown("---")

# Search Button & Logic
if st.button(t['find_button_label'], key="find_button"):
    st.session_state.expanded_object_name = None
    st.session_state.show_plot = False
    st.session_state.plot_object_name = None

    if df_catalog_data is None or df_catalog_data.empty: st.error("Cannot search: Catalog data is not loaded or empty.")
    elif not location_is_valid_for_run: st.error(t['location_error_manual_search'])
    elif current_location_for_run is None: st.error(t['location_error_undefined'])
    else:
        # --- Start Search Process ---
        st.session_state.find_button_pressed = True
        st.session_state.last_results = []

        # Display search parameters used
        with st.container(border=True):
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
                 if magnitude_filter_mode_disp == "Bortle Scale":
                     mag_limit_display = get_magnitude_limit(bortle_val)
                     mag_info = t['search_params_filter_mag_bortle'].format(bortle_val, mag_limit_display)
                 else: # Manual
                     mag_info = t['search_params_filter_mag_manual'].format(min_mag_disp, max_mag_disp)
                 st.info(t['search_params_filter_mag'].format(mag_info))
                 types_display = t['search_params_types_all'] if not effective_selected_types or len(effective_selected_types) == len(all_types) else ', '.join(effective_selected_types)
                 st.info(t['search_params_filter_alt_types'].format(min_altitude_deg, types_display))
                 # Display Direction Filter
                 selected_dir_disp = st.session_state.selected_peak_direction # Get selected direction for display
                 st.info(t['search_params_filter_direction'].format(selected_dir_disp))

        st.markdown("---")

        # --- Perform Calculations ---
        selected_objects = []
        all_found_objects = []
        try:
            with st.spinner(t['spinner_searching']):
                # 1. Calculate Observation Window
                start_time, end_time, window_msg = get_observable_window(current_location_for_run, reference_time, is_time_now, lang)
                if window_msg:
                    formatted_window_msg = window_msg.replace("\n", "\n\n")
                    if "Warning" in window_msg or "Warnung" in window_msg or "Error" in window_msg or "Fehler" in window_msg: st.warning(formatted_window_msg)
                    else: st.info(formatted_window_msg)

                # 2. Find Objects if window is valid
                if start_time and end_time and start_time < end_time:
                    time_delta_hours = (end_time - start_time).to(u.hour).value
                    num_time_steps = max(30, int(time_delta_hours * 10))
                    observing_times = Time(np.linspace(start_time.jd, end_time.jd, num_time_steps), format='jd')
                    magnitude_filter_mode_calc = st.session_state.mag_filter_mode_exp
                    min_mag_calc = st.session_state.manual_min_mag_slider
                    max_mag_calc = st.session_state.manual_max_mag_slider
                    all_found_objects = find_observable_objects(
                        current_location_for_run, observing_times, min_altitude_limit,
                        magnitude_filter_mode_calc, bortle_val, min_mag_calc, max_mag_calc,
                        effective_selected_types, df_catalog_data, lang
                    )
                else:
                     if not window_msg or ("valid" not in window_msg and "gültig" not in window_msg): st.error(t['error_no_window'])

            # 3. Apply Direction Filter (if needed)
            objects_after_direction_filter = []
            selected_dir_filter = st.session_state.selected_peak_direction
            all_directions_str = t['direction_option_all'] # Get translated "All" string

            # Only filter if a specific direction (not "All") is selected
            if selected_dir_filter != all_directions_str:
                for obj in all_found_objects:
                    if obj.get('peak_direction') == selected_dir_filter: # Compare with selected direction
                        objects_after_direction_filter.append(obj)
            else: # "All" selected, no direction filter needed
                objects_after_direction_filter = all_found_objects

            # 4. Process and Display Results Summary
            if objects_after_direction_filter:
                st.success(t['success_objects_found'].format(len(objects_after_direction_filter))) # Show count *after* direction filter

                # --- Conditional Sorting ---
                sort_method = st.session_state.sort_method
                # Apply sorting to the potentially filtered list
                if sort_method == 'Duration & Altitude':
                    objects_after_direction_filter.sort(key=lambda x: (x.get('duration_hours', 0), x.get('peak_alt', 0)), reverse=True)
                    info_message = t['info_showing_list_duration']
                elif sort_method == 'Brightness':
                    objects_after_direction_filter.sort(key=lambda x: x['magnitude']) # Ascending magnitude = Brightest first
                    info_message = t['info_showing_list_magnitude']
                else: # Default fallback
                    objects_after_direction_filter.sort(key=lambda x: (x.get('duration_hours', 0), x.get('peak_alt', 0)), reverse=True)
                    info_message = t['info_showing_list_duration']

                selected_objects = objects_after_direction_filter[:num_objects_to_suggest]
                st.write(info_message.format(len(selected_objects))) # Use appropriate message
                st.session_state.last_results = selected_objects
            else:
                 # Check if objects were found *before* direction filter
                 if all_found_objects and selected_dir_filter != all_directions_str:
                      st.warning(f"No objects found peaking in the selected direction: {selected_dir_filter}")
                 elif all_found_objects and selected_dir_filter == all_directions_str:
                     # This case means no objects matched *other* criteria
                     st.warning(t['warning_no_objects_found'])
                 elif start_time and end_time and start_time < end_time:
                     # No objects found even before direction filter
                     st.warning(t['warning_no_objects_found'])

                 st.session_state.last_results = []
        except Exception as main_e:
            st.error(t['error_search_unexpected'])
            st.exception(main_e)
            st.session_state.last_results = []
        # --- End Search Process ---

# Display Results List
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
            t['results_export_az_at_max']: f"{obj.get('peak_az', ''):.1f}",
            t['results_export_direction_at_max']: obj.get('peak_direction', ''),
            t['results_export_duration']: f"{obj.get('duration_hours', 0):.1f}",
            t['results_export_time_max_utc']: obj['peak_time_utc'],
            t['results_export_time_max_local']: f"{peak_time_local_str} ({tz_display_name})"
        })
        expander_title = t['results_expander_title'].format(obj['name'], obj['type'], obj['magnitude'])
        is_expanded = (st.session_state.expanded_object_name == obj['name'])
        with st.expander(expander_title, expanded=is_expanded):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1: st.markdown(t['results_coords_header']); st.markdown(f"RA: {obj['ra']}"); st.markdown(f"Dec: {obj['dec']}")
            with col2: st.markdown(t['results_max_alt_header']); st.markdown(f"**{obj['peak_alt']:.1f}°**"); st.markdown(t['results_azimuth_label'].format(obj.get('peak_az', 0.0), f" ({obj.get('peak_direction', '?')})")) # Show direction with Azimuth
            with col3: st.markdown(t['results_duration_header']); st.markdown(f"**{t['results_duration_value'].format(obj.get('duration_hours', 0))}**")
            with col4: st.markdown(t['results_best_time_header']); st.markdown(f"**{peak_time_local_str}**"); st.markdown(f"({tz_display_name})")
            with col5: st.markdown(f"**Type:**"); st.markdown(f"{obj['type']}")

            st.markdown("---")

            # Plotting Logic
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
                            if current_location_for_run is not None:
                                location_tuple = (
                                    current_location_for_run.lat.deg,
                                    current_location_for_run.lon.deg,
                                    current_location_for_run.height.value
                                )
                            if location_tuple:
                                fig = plot_altitude(obj, location_tuple, lang, st.session_state.selected_timezone)
                                if fig:
                                    st.pyplot(fig)
                                    if st.button(t['results_close_plot_button'], key=close_button_key, type="secondary"):
                                        st.session_state.show_plot = False
                                        st.session_state.plot_object_name = None
                                        st.session_state.expanded_object_name = None
                                        st.rerun()
                                else:
                                    st.warning(t['results_plot_not_created'])
                                    st.session_state.show_plot = False; st.session_state.plot_object_name = None; st.session_state.expanded_object_name = None
                            else: st.error("Location not defined for plotting.")
                        except Exception as plot_e:
                            st.error(t['results_plot_error'].format(plot_e))
                            st.session_state.show_plot = False; st.session_state.plot_object_name = None; st.session_state.expanded_object_name = None
                 else: st.warning("Plotting skipped: Matplotlib library missing.")

    # --- CSV Export ---
    if export_data and pd:
        st.markdown("---")
        try:
            df = pd.DataFrame(export_data)
            cols = [t['results_export_name'], t['results_export_type'], t['results_export_mag'],
                    t['results_export_duration'], t['results_export_max_alt'], t['results_export_az_at_max'], t['results_export_direction_at_max'],
                    t['results_export_time_max_local'], t['results_export_time_max_utc'],
                    t['results_export_ra'], t['results_export_dec']]
            cols_exist = [col for col in cols if col in df.columns]
            df = df[cols_exist]
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8-sig')
            file_date = reference_time.datetime.date().strftime('%Y%m%d')
            st.download_button(
                label=t['results_save_csv_button'], data=csv_buffer.getvalue(),
                file_name=t['results_csv_filename'].format(file_date), mime="text/csv"
            )
        except Exception as csv_e:
            st.error(t['results_csv_export_error'].format(csv_e))

# Message if search was run but found nothing
elif st.session_state.find_button_pressed and not st.session_state.last_results:
    st.session_state.find_button_pressed = False # Reset state

# Initial message
elif not st.session_state.find_button_pressed and df_catalog_data is not None:
    st.info(t['info_initial_prompt'])
elif df_catalog_data is None:
     st.error("Failed to load the DSO catalog. Please check the file path and format.")

