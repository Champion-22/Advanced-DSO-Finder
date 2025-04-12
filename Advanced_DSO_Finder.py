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
    if plt: # Set style only if import succeeded
        plt.style.use('dark_background')
except ImportError as e:
    import_errors.append(f"Error: Required library not found. Install: pip install pandas matplotlib ({e})")
    pd = None
    plt = None

# --- Display Import Errors (NOW it's safe to use st.error) ---
if import_errors:
    st.error("### Library Import Errors")
    for error in import_errors:
        st.error(error)
    st.info("Please install the missing libraries and restart the app.")
    st.stop() # Stop execution if imports failed

# --- Check if essential classes/functions were imported ---
essential_imports_ok = all([
    Time, np, u, EarthLocation, SkyCoord, get_sun, AltAz, moon_illumination, pd, plt,
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
        'location_manual_display': "Manual ({:.4f}, {:.4f})", # Increased precision display
        'location_error': "Location Error: {}",
        'location_error_fallback': "ERROR - Using Default",
        'location_error_manual_none': "Manual location fields cannot be empty.",
        'location_error_manual_search': "Cannot search: Manual location fields are invalid or empty.",
        'location_error_undefined': "Cannot search: Location is not defined.",
        'time_expander': "⏱️ Time",
        'time_select_label': "Select Time",
        'time_option_now': "Now (upcoming night)",
        'time_option_specific': "Specific Night",
        'time_date_select_label': "Select Date:",
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
        'moon_warning_header': "**Moon Warning**",
        'moon_warning_label': "Warn if Moon > (% Illumination):",
        'object_types_header': "**Object Types**",
        'object_types_error_extract': "Could not extract object types from catalog.",
        'object_types_label': "Filter Types (leave empty for all):",
        'results_options_expander': "⚙️ Result Options",
        'results_options_max_objects_label': "Max Number of Objects to Display:",
        'results_options_sort_brightness_label': "Sort by Brightness (Brightest First)",
        'moon_metric_label': "Moon Illumination (approx.)",
        'moon_warning_message': "Warning: Moon is brighter ({:.0f}%) than threshold ({:.0f}%)!",
        'moon_phase_error': "Moon phase calculation error: {}",
        'find_button_label': "🔭 Find Observable Objects",
        'search_params_header': "Search Parameters",
        'search_params_location': "📍 Location: {}",
        'search_params_time': "⏱️ Time: {}",
        'search_params_time_now': "Upcoming night (from {} UTC)",
        'search_params_time_specific': "Night after {}",
        'search_params_filter_mag': "✨ Filter: {}",
        'search_params_filter_mag_bortle': "Bortle {} (<= {:.1f} mag)",
        'search_params_filter_mag_manual': "Manual ({:.1f}-{:.1f} mag)",
        'search_params_filter_alt_types': "🔭 Filter: Min. Altitude {}°, Types: {}",
        'search_params_types_all': "All",
        'spinner_searching': "Calculating window & searching objects...",
        'window_info_template': "{}",
        'error_no_window': "No valid observation window found.",
        'success_objects_found': "{} matching objects found.",
        'info_showing_brightest': "Showing the {} brightest:",
        'info_showing_random': "Random selection of {}:",
        'info_showing_list': "List of the {} objects:",
        'error_search_unexpected': "An unexpected error occurred during the search:",
        'results_list_header': "Result List",
        'results_export_name': "Name",
        'results_export_type': "Type",
        'results_export_mag': "Magnitude",
        'results_export_ra': "RA",
        'results_export_dec': "Dec",
        'results_export_max_alt': "Max Altitude (°)",
        'results_export_az_at_max': "Azimuth at Max (°)",
        'results_export_time_max_utc': "Time at Max (UTC)",
        'results_export_time_max_local': "Time at Max (Local)",
        'results_expander_title': "{} ({}) - Mag: {:.1f}",
        'results_coords_header': "**Coordinates:**",
        'results_max_alt_header': "**Max. Altitude:**",
        'results_azimuth_label': "(Azimuth: {:.1f}°)",
        'results_best_time_header': "**Best Time (Local):**",
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
        'location_manual_display': "Manuell ({:.4f}, {:.4f})", # Increased precision display
        'location_error': "Standort Fehler: {}",
        'location_error_fallback': "FEHLER - Nutze Standard",
        'location_error_manual_none': "Manuelle Standortfelder dürfen nicht leer sein.",
        'location_error_manual_search': "Suche nicht möglich: Manuelle Standortfelder sind ungültig oder leer.",
        'location_error_undefined': "Suche nicht möglich: Standort ist nicht definiert.",
        'time_expander': "⏱️ Zeitpunkt",
        'time_select_label': "Zeitpunkt wählen",
        'time_option_now': "Jetzt (kommende Nacht)",
        'time_option_specific': "Andere Nacht",
        'time_date_select_label': "Datum auswählen:",
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
        'moon_warning_header': "**Mond Warnung**",
        'moon_warning_label': "Warnen wenn Mond > (% Beleuchtung):",
        'object_types_header': "**Objekttypen**",
        'object_types_error_extract': "Objekttypen konnten nicht aus Katalog extrahiert werden.",
        'object_types_label': "Typen filtern (leer = alle):",
        'results_options_expander': "⚙️ Ergebnis-Optionen",
        'results_options_max_objects_label': "Max. Anzahl Objekte zur Anzeige:",
        'results_options_sort_brightness_label': "Nach Helligkeit sortieren (Hellste zuerst)",
        'moon_metric_label': "Mondhelligkeit (ca.)",
        'moon_warning_message': "Warnung: Mond ist heller ({:.0f}%) als Schwelle ({:.0f}%)!",
        'moon_phase_error': "Mondphasen-Berechnungsfehler: {}",
        'find_button_label': "🔭 Beobachtbare Objekte finden",
        'search_params_header': "Suchparameter",
        'search_params_location': "📍 Standort: {}",
        'search_params_time': "⏱️ Zeitpunkt: {}",
        'search_params_time_now': "Kommende Nacht (ab {} UTC)",
        'search_params_time_specific': "Nacht nach dem {}",
        'search_params_filter_mag': "✨ Filter: {}",
        'search_params_filter_mag_bortle': "Bortle {} (<= {:.1f} mag)",
        'search_params_filter_mag_manual': "Manuell ({:.1f}-{:.1f} mag)",
        'search_params_filter_alt_types': "🔭 Filter: Min. Höhe {}°, Typen: {}",
        'search_params_types_all': "Alle",
        'spinner_searching': "Berechne Fenster & suche Objekte...",
        'window_info_template': "{}",
        'error_no_window': "Kein gültiges Beobachtungsfenster gefunden.",
        'success_objects_found': "{} passende Objekte gefunden.",
        'info_showing_brightest': "Anzeige der {} hellsten:",
        'info_showing_random': "Zufällige Auswahl von {}:",
        'info_showing_list': "Liste der {} Objekte:",
        'error_search_unexpected': "Unerwarteter Fehler während der Suche:",
        'results_list_header': "Ergebnisliste",
        'results_export_name': "Name",
        'results_export_type': "Typ",
        'results_export_mag': "Magnitude",
        'results_export_ra': "RA",
        'results_export_dec': "Dec",
        'results_export_max_alt': "Max Höhe (°)",
        'results_export_az_at_max': "Azimut bei Max (°)",
        'results_export_time_max_utc': "Zeit bei Max (UTC)",
        'results_export_time_max_local': "Zeit bei Max (Lokal)",
        'results_expander_title': "{} ({}) - Mag: {:.1f}",
        'results_coords_header': "**Koordinaten:**",
        'results_max_alt_header': "**Max. Höhe:**",
        'results_azimuth_label': "(Azimut: {:.1f}°)",
        'results_best_time_header': "**Beste Zeit (Lokal):**",
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
    }
}

# --- Global Configuration & Catalog ---
DEFAULT_LOCATION_NAME = "Schötz, Lucerne"
DEFAULT_LAT = 47.17
DEFAULT_LON = 8.01
DEFAULT_HEIGHT = 550
DEFAULT_LOCATION = EarthLocation(lat=DEFAULT_LAT * u.deg, lon=DEFAULT_LON * u.deg, height=DEFAULT_HEIGHT * u.m)
# DSO Catalog (Unverändert)
DSO_CATALOG = [
    ["M1", "05h34m31.94s", "+22d00m52.2s", 8.4, "Supernova Remnant"], ["M13", "16h41m41.24s", "+36d27m35.5s", 5.8, "Globular Cluster"],
    ["M27", "19h59m36.34s", "+22d43m16.1s", 7.4, "Planetary Nebula"], ["M31", "00h42m44.3s", "+41d16m09s", 3.4, "Galaxy"],
    ["M33", "01h33m50.9s", "+30d39m37s", 5.7, "Galaxy"], ["M42", "05h35m17.3s", "-05d23m28s", 4.0, "Nebula"],
    ["M44", "08h40m24s", "+19d41m00s", 3.1, "Open Cluster"], ["M45", "03h47m24s", "+24d07m00s", 1.6, "Open Cluster"],
    ["M51", "13h29m52.7s", "+47d11m43s", 8.4, "Galaxy"], ["M57", "18h53m35.08s", "+33d01m45.0s", 8.8, "Planetary Nebula"],
    ["M63", "13h15m49.3s", "+42d01m45s", 8.6, "Galaxy"], ["M64", "12h56m43.7s", "+21d40m58s", 8.5, "Galaxy"],
    ["M81", "09h55m33.2s", "+69d03m55s", 6.9, "Galaxy"], ["M82", "09h55m52.2s", "+69d40m47s", 8.4, "Galaxy"],
    ["M92", "17h17m07.27s", "+43d08m11.5s", 6.4, "Globular Cluster"], ["M97", "11h14m47.7s", "+55d01m09s", 9.9, "Planetary Nebula"],
    ["M101", "14h03m12.6s", "+54d20m57s", 7.9, "Galaxy"], ["M104", "12h39m59.4s", "-11d37m23s", 8.0, "Galaxy"],
    ["M106", "12h18m57.5s", "+47d18m14s", 8.4, "Galaxy"], ["M108", "11h11m31.0s", "+55d40m31s", 10.0, "Galaxy"],
    ["M109", "11h57m36.0s", "+53d22m28s", 9.8, "Galaxy"], ["NGC 869", "02h19m00s", "+57d08m00s", 5.3, "Open Cluster"],
    ["NGC 884", "02h22m24s", "+57d08m00s", 6.1, "Open Cluster"], ["NGC 2392", "07h29m10.8s", "+20d54m42s", 9.1, "Planetary Nebula"],
    ["NGC 2841", "09h22m02.6s", "+50d58m35s", 9.2, "Galaxy"], ["NGC 4565", "12h36m20.8s", "+25d59m16s", 9.6, "Galaxy"],
    ["NGC 6888", "20h12m06.5s", "+38d21m18s", 7.4, "Nebula"], ["NGC 6946", "20h34m52.3s", "+60d09m14s", 8.8, "Galaxy"],
    ["NGC 6960", "20h45m38.0s", "+30d43m00s", 7.0, "Supernova Remnant"], ["NGC 6992", "20h56m24.0s", "+31d43m00s", 7.0, "Supernova Remnant"],
    ["NGC 7000", "20h59m17s", "+44d31m44s", 4.0, "Nebula"], ["NGC 7293", "22h29m38.55s", "-20d50m13.6s", 7.3, "Planetary Nebula"],
    ["NGC 7331", "22h37m04.1s", "+34d24m56s", 9.5, "Galaxy"], ["NGC 7662", "23h25m54.0s", "+42d32m06s", 8.3, "Planetary Nebula"],
    ["IC 434", "05h40m59.0s", "-02d27m30s", 7.3, "Nebula"], ["IC 5146", "21h53m29.0s", "+47d16m06s", 7.2, "Nebula"],
]

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
        'location_choice_key': 'Default', # No cookies, default to 'Default'
        # 'cookies_loaded': False, # Removed cookie logic
        'expanded_object_name': None,
        'manual_min_mag_slider': 0.0,
        'manual_max_mag_slider': 16.0,
        'object_type_filter_exp': [], # Initialize as empty list
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

# Use string literals for type hints involving potentially unimported types
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

# Use string literals for type hints involving potentially unimported types
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

# Use string literals for type hints involving potentially unimported types
def find_observable_objects(
    location: 'EarthLocation', observing_times: 'Time', min_altitude_limit: 'u.Quantity',
    magnitude_filter_mode: str, bortle_scale: int, manual_min_mag: float | None,
    manual_max_mag: float | None, selected_object_types: list, lang: str
) -> list:
    """Finds DSOs from the catalog visible during the observing times."""
    t = translations[lang]
    observable_objects = []
    magnitude_limit = None
    if magnitude_filter_mode == 'Bortle Scale':
        magnitude_limit = get_magnitude_limit(bortle_scale)
    elif magnitude_filter_mode == 'Manual':
        if isinstance(manual_min_mag, (int, float)) and isinstance(manual_max_mag, (int, float)):
            if manual_min_mag > manual_max_mag:
                manual_min_mag, manual_max_mag = manual_max_mag, manual_min_mag
        else:
             manual_min_mag = None # Disable filter if invalid
             manual_max_mag = None
    for obj_data in DSO_CATALOG:
        if len(obj_data) < 5: continue
        name, ra_str, dec_str, mag, obj_type = obj_data
        if selected_object_types and obj_type not in selected_object_types: continue
        if not isinstance(mag, (int, float)): continue
        if magnitude_filter_mode == 'Bortle Scale':
            if magnitude_limit is not None and mag > magnitude_limit: continue
        elif magnitude_filter_mode == 'Manual':
            if isinstance(manual_min_mag, (int, float)) and isinstance(manual_max_mag, (int, float)):
                 if not (manual_min_mag <= mag <= manual_max_mag): continue
        try:
            target = SkyCoord(ra=ra_str, dec=dec_str, frame='icrs')
            altaz_frame = AltAz(obstime=observing_times, location=location)
            target_altaz = target.transform_to(altaz_frame)
            altitudes = target_altaz.alt
            azimuths = target_altaz.az
            valid_indices = np.where(altitudes >= min_altitude_limit)[0]
            if len(valid_indices) > 0:
                peak_in_window_index = valid_indices[np.argmax(altitudes[valid_indices])]
                observable_objects.append({
                    "name": name, "type": obj_type, "magnitude": mag,
                    "ra_str": ra_str, "dec_str": dec_str,
                    "ra": target.ra.to_string(unit=u.hour, sep='hms', precision=1),
                    "dec": target.dec.to_string(unit=u.deg, sep='dms', precision=0),
                    "peak_alt": altitudes[peak_in_window_index].to(u.deg).value,
                    "peak_az": azimuths[peak_in_window_index].to(u.deg).value,
                    "peak_time_utc": observing_times[peak_in_window_index].iso,
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

# Use string literals for type hints involving potentially unimported types
# FIX: Change decorator to @st.cache_resource, remove invalid argument
@st.cache_resource(show_spinner=False)
def plot_altitude(obj_data: dict, location_tuple: tuple, lang: str): # Pass location as tuple for caching
    """Creates a Matplotlib altitude plot. Caches the figure object."""
    # Note: Pylance might still show errors on type hints depending on environment.
    t = translations[lang]
    if plt is None:
        # Cannot plot if matplotlib failed import
        return None
    fig, ax = plt.subplots()
    try:
        times = Time(obj_data['times_jd'], format='jd')
        try:
            local_tz = datetime.now(timezone.utc).astimezone().tzinfo
            times_local = [t_inst.to_datetime(timezone=local_tz) for t_inst in times]
            tz_name_display = local_tz.tzname(datetime.now()) if local_tz else 'Local'
            xlabel = t['plot_time_label_local'].format(tz_name_display)
        except Exception:
             local_tz = None
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
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        plt.tight_layout()
    except Exception as e:
        print(f"Error plotting altitude for {obj_data.get('name', 'Unknown')}: {e}") # Log error
        plt.close(fig)
        return None # Indicate error
    return fig

def get_local_time_str(utc_iso_time: str) -> tuple[str, str]:
    """Converts UTC ISO time string to local time string and timezone name."""
    try:
        local_tz = datetime.now(timezone.utc).astimezone().tzinfo
        if Time is None: return "N/A", ""
        dt_peak_utc = Time(utc_iso_time).datetime.replace(tzinfo=timezone.utc)
        dt_peak_local = dt_peak_utc.astimezone(local_tz)
        tz_name = local_tz.tzname(dt_peak_local) if local_tz else "Local"
        peak_time_local_str = dt_peak_local.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        tz_name = "UTC+?"
        try:
            if Time is None: return "N/A", ""
            peak_time_local = (Time(utc_iso_time) + timedelta(hours=1)).datetime
            peak_time_local_str = peak_time_local.strftime('%Y-%m-%d %H:%M:%S')
        except:
            peak_time_local_str = "N/A"; tz_name = ""
    return peak_time_local_str, tz_name

# --- Get Current Language and Translations ---
lang = st.session_state.language
t = translations[lang]

# --- Custom CSS Styling ---
st.markdown("""
<style>
    /* General container styling */
    .main .block-container { background-color: #1E1E1E; color: #EAEAEA; border-radius: 10px; padding: 2rem; }
    /* Primary button */
    div[data-testid="stButton"] > button:not([kind="secondary"]) { background-image: linear-gradient(to right, #007bff, #0056b3); color: white; border: none; padding: 10px 24px; text-align: center; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px; transition-duration: 0.4s; }
    div[data-testid="stButton"] > button:not([kind="secondary"]):hover { background-image: linear-gradient(to right, #0056b3, #003d80); color: white; }
    /* Secondary button (Close Plot) */
     div[data-testid="stButton"] > button[kind="secondary"] { background-color: #555; color: #eee; }
     div[data-testid="stButton"] > button[kind="secondary"]:hover { background-color: #777; color: white; }
    /* Expander header */
    .streamlit-expanderHeader { background-color: #333333; color: #EAEAEA; border-radius: 5px; }
    /* Metric display */
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
        t['language_select_label'],
        options=language_options.keys(),
        format_func=lambda key: language_options[key],
        key='language_radio',
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
        # Use session state to remember choice within the session
        location_choice_key = st.radio(
            t['location_select_label'],
            options=list(location_options_map.keys()),
            format_func=lambda key: location_options_map[key],
            key="location_choice_key", # Use state key directly
        )

        # Manual Input Fields - use session state via key
        # FIX: Remove 'value' argument, use only 'key' as recommended by warning
        manual_lat_input = st.number_input(
             t['location_lat_label'],
             min_value=-90.0, max_value=90.0, step=0.01, format="%.4f",
             key="manual_lat_val" # Let key handle state
        )
        manual_lon_input = st.number_input(
            t['location_lon_label'],
            min_value=-180.0, max_value=180.0, step=0.01, format="%.4f",
            key="manual_lon_val" # Let key handle state
        )
        manual_height_input = st.number_input(
            t['location_elev_label'],
            min_value=-500, step=10, format="%d",
            key="manual_height_val" # Let key handle state
        )

        # Determine final location object, name, and validity for this run
        current_location_for_run = None
        location_is_valid_for_run = False
        location_display_name_for_run = ""
        warning_placeholder = st.empty() # Placeholder for warnings inside expander

        if st.session_state.location_choice_key == "Manual":
            # Read values directly from session state (set by widgets via key)
            lat_val = st.session_state.manual_lat_val
            lon_val = st.session_state.manual_lon_val
            height_val = st.session_state.manual_height_val

            # Check if manual inputs are valid numbers
            if lat_val is None or lon_val is None or height_val is None or \
               not isinstance(lat_val, (int, float)) or \
               not isinstance(lon_val, (int, float)) or \
               not isinstance(height_val, (int, float)):
                warning_placeholder.warning(t['location_error_manual_none'])
                location_display_name_for_run = t['location_error_fallback']
            else:
                # Inputs seem valid, try creating EarthLocation
                try:
                    current_location_for_run = EarthLocation(lat=lat_val * u.deg, lon=lon_val * u.deg, height=height_val * u.m)
                    location_display_name_for_run = t['location_manual_display'].format(lat_val, lon_val)
                    location_is_valid_for_run = True
                except Exception as e:
                    # Error during EarthLocation creation (e.g., value out of range)
                    st.error(t['location_error'].format(e)) # Show error outside placeholder
                    location_display_name_for_run = t['location_error_fallback']
                    # location_is_valid_for_run remains False
        else: # Default location selected
             current_location_for_run = DEFAULT_LOCATION
             location_display_name_for_run = t['location_option_default'].format(DEFAULT_LOCATION_NAME)
             location_is_valid_for_run = True

    # --- Time Settings ---
    with st.expander(t['time_expander']):
        time_options_map = {'Now': t['time_option_now'], 'Specific': t['time_option_specific']}
        time_choice_key = st.radio(
            t['time_select_label'], options=time_options_map.keys(),
            format_func=lambda key: time_options_map[key], key="time_choice_exp"
        )
        is_time_now = (time_choice_key == "Now")
        reference_time = Time.now() # Get current time initially
        if not is_time_now:
            selected_date = st.date_input(
                t['time_date_select_label'], date.today(),
                min_value=date.today()-timedelta(days=365*5),
                max_value=date.today()+timedelta(days=365*1)
            )
            reference_time = Time(datetime.combine(selected_date, time(12, 0)))

    # --- Filter Settings ---
    with st.expander(t['filters_expander'], expanded=True):
        # Magnitude Filter
        st.markdown(t['mag_filter_header'])
        mag_filter_options_map = {'Bortle Scale': t['mag_filter_option_bortle'], 'Manual': t['mag_filter_option_manual']}
        # Radio button to choose filter method
        magnitude_filter_mode_key = st.radio(
            t['mag_filter_method_label'], options=mag_filter_options_map.keys(),
            format_func=lambda key: mag_filter_options_map[key],
            key="mag_filter_mode_exp", # Use state key
            horizontal=True
        )

        # Initialize values needed later
        bortle_val = 5
        manual_min_mag_val = st.session_state.manual_min_mag_slider
        manual_max_mag_val = st.session_state.manual_max_mag_slider

        # --- Conditionally display widgets based on radio button choice ---
        if st.session_state.mag_filter_mode_exp == "Bortle Scale":
            bortle_val = st.slider( # Display Bortle slider
                t['mag_filter_bortle_label'], min_value=1, max_value=9, value=5, step=1, help=t['mag_filter_bortle_help'],
                key='bortle_slider' # Use a unique key
            )
        elif st.session_state.mag_filter_mode_exp == "Manual":
            manual_min_mag_val = st.slider( # Display Min Mag slider
                t['mag_filter_min_mag_label'], min_value=0.0, max_value=20.0,
                step=0.5, format="%.1f", help=t['mag_filter_min_mag_help'],
                key='manual_min_mag_slider' # Use state key
            )
            manual_max_mag_val = st.slider( # Display Max Mag slider
                t['mag_filter_max_mag_label'], min_value=0.0, max_value=20.0,
                step=0.5, format="%.1f", help=t['mag_filter_max_mag_help'],
                key='manual_max_mag_slider' # Use state key
            )
            # Display warning only in Manual mode
            if isinstance(st.session_state.manual_min_mag_slider, (int, float)) and \
               isinstance(st.session_state.manual_max_mag_slider, (int, float)):
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

        # Object Type Filter
        st.markdown("---")
        st.markdown(t['object_types_header'])
        try:
            all_types = sorted(list(set(item[4] for item in DSO_CATALOG if len(item) > 4)))
        except IndexError:
            all_types = []
            st.warning(t['object_types_error_extract'])

        effective_selected_types = []
        if all_types:
            # Get current selection from state (guaranteed to be a list, initially [])
            current_selection_in_state = st.session_state.object_type_filter_exp
            # Determine default: If state holds a selection, use it. Otherwise, default to all.
            default_for_widget = current_selection_in_state if current_selection_in_state else all_types

            selected_object_types = st.multiselect(
                t['object_types_label'],
                options=all_types,
                default=default_for_widget, # Use state value or all_types
                key="object_type_filter_exp" # State manages persistence
            )
            # Ensure widget result is a list before proceeding (Safety Check)
            if selected_object_types is None:
                selected_object_types = []
            # Determine list used for filtering
            effective_selected_types = selected_object_types if selected_object_types else all_types
        else:
             st.info("No object types found in catalog to filter.")

    # --- Result Options ---
    with st.expander(t['results_options_expander']):
        num_objects_to_suggest = st.slider(t['results_options_max_objects_label'], min_value=5, max_value=len(DSO_CATALOG), value=20, step=1)
        sort_by_brightness = st.checkbox(t['results_options_sort_brightness_label'], value=True)

# --- Main Area ---
# Display Moon Phase
try:
    current_moon_illumination = moon_illumination(reference_time)
    moon_percentage = current_moon_illumination * 100
    moon_col1, moon_col2 = st.columns([1, 4])
    with moon_col1:
        st.markdown(create_moon_phase_svg(current_moon_illumination, size=80), unsafe_allow_html=True)
    with moon_col2:
        st.metric(label=t['moon_metric_label'], value=f"{moon_percentage:.0f}%")
        if moon_percentage > moon_phase_threshold:
            st.error(t['moon_warning_message'].format(moon_percentage, moon_phase_threshold))
except Exception as e:
    st.error(t['moon_phase_error'].format(e))

st.markdown("---")

# Search Button & Logic
if st.button(t['find_button_label'], key="find_button"):
    st.session_state.expanded_object_name = None
    st.session_state.show_plot = False
    st.session_state.plot_object_name = None

    # Use the validity flag determined in the sidebar for this run
    if not location_is_valid_for_run:
         st.error(t['location_error_manual_search'])
    elif current_location_for_run is None:
         st.error(t['location_error_undefined'])
    else:
        # --- Start Search Process ---
        st.session_state.find_button_pressed = True
        st.session_state.last_results = []

        # Display search parameters used
        with st.container(border=True):
             st.subheader(t['search_params_header'])
             col1, col2 = st.columns(2)
             with col1:
                 st.info(t['search_params_location'].format(location_display_name_for_run))
                 date_str_display = reference_time.datetime.date().strftime('%Y-%m-%d')
                 time_info = t['search_params_time_now'].format(reference_time.to_datetime(timezone.utc).strftime('%Y-%m-%d %H:%M %Z')) if is_time_now else t['search_params_time_specific'].format(date_str_display)
                 st.info(t['search_params_time'].format(time_info))
             with col2:
                 # Read filter values directly from state for display/use
                 min_mag_disp = st.session_state.manual_min_mag_slider
                 max_mag_disp = st.session_state.manual_max_mag_slider
                 if magnitude_filter_mode_key == "Bortle Scale":
                     mag_limit_display = get_magnitude_limit(bortle_val)
                     mag_info = t['search_params_filter_mag_bortle'].format(bortle_val, mag_limit_display)
                 else:
                     mag_info = t['search_params_filter_mag_manual'].format(min_mag_disp, max_mag_disp)
                 st.info(t['search_params_filter_mag'].format(mag_info))
                 types_display = t['search_params_types_all'] if not effective_selected_types or len(effective_selected_types) == len(all_types) else ', '.join(effective_selected_types)
                 st.info(t['search_params_filter_alt_types'].format(min_altitude_deg, types_display))
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
                    if "Warning" in window_msg or "Warnung" in window_msg or "Error" in window_msg or "Fehler" in window_msg:
                        st.warning(formatted_window_msg)
                    else:
                        st.info(formatted_window_msg)

                # 2. Find Objects if window is valid
                if start_time and end_time and start_time < end_time:
                    time_delta_hours = (end_time - start_time).to(u.hour).value
                    num_time_steps = max(30, int(time_delta_hours * 10))
                    observing_times = Time(np.linspace(start_time.jd, end_time.jd, num_time_steps), format='jd')
                    # Read filter values directly from state for calculation
                    min_mag_calc = st.session_state.manual_min_mag_slider
                    max_mag_calc = st.session_state.manual_max_mag_slider
                    all_found_objects = find_observable_objects(
                        current_location_for_run, observing_times, min_altitude_limit,
                        magnitude_filter_mode_key, bortle_val, min_mag_calc, max_mag_calc,
                        effective_selected_types, lang
                    )
                else:
                     if not window_msg or ("valid" not in window_msg and "gültig" not in window_msg):
                          st.error(t['error_no_window'])

            # 3. Process and Display Results Summary
            if all_found_objects:
                st.success(t['success_objects_found'].format(len(all_found_objects)))
                processed_objects = all_found_objects
                if sort_by_brightness:
                    processed_objects.sort(key=lambda x: x['magnitude'])
                    selected_objects = processed_objects[:num_objects_to_suggest]
                    st.write(t['info_showing_brightest'].format(len(selected_objects)))
                else:
                    if len(processed_objects) > num_objects_to_suggest:
                        selected_objects = random.sample(processed_objects, num_objects_to_suggest)
                        selected_objects.sort(key=lambda x: x['name'])
                        st.write(t['info_showing_random'].format(num_objects_to_suggest))
                    else:
                        selected_objects = processed_objects
                        selected_objects.sort(key=lambda x: x['name'])
                        st.write(t['info_showing_list'].format(len(selected_objects)))
                st.session_state.last_results = selected_objects
            else:
                 if start_time and end_time and start_time < end_time:
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
        peak_time_local_str, tz_name = get_local_time_str(obj['peak_time_utc'])
        export_data.append({
            t['results_export_name']: obj['name'], t['results_export_type']: obj['type'],
            t['results_export_mag']: obj['magnitude'], t['results_export_ra']: obj['ra'],
            t['results_export_dec']: obj['dec'], t['results_export_max_alt']: f"{obj['peak_alt']:.1f}",
            t['results_export_az_at_max']: f"{obj['peak_az']:.1f}", t['results_export_time_max_utc']: obj['peak_time_utc'],
            t['results_export_time_max_local']: f"{peak_time_local_str} {tz_name}"
        })
        expander_title = t['results_expander_title'].format(obj['name'], obj['type'], obj['magnitude'])
        is_expanded = (st.session_state.expanded_object_name == obj['name'])
        with st.expander(expander_title, expanded=is_expanded):
            col1, col2, col3 = st.columns(3)
            with col1: st.markdown(t['results_coords_header']); st.markdown(f"RA: {obj['ra']}"); st.markdown(f"Dec: {obj['dec']}")
            with col2: st.markdown(t['results_max_alt_header']); st.markdown(f"**{obj['peak_alt']:.1f}°**"); st.markdown(t['results_azimuth_label'].format(obj['peak_az']))
            with col3: st.markdown(t['results_best_time_header']); st.markdown(f"**{peak_time_local_str}**"); st.markdown(f"({tz_name})")
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
                            # Pass location tuple for caching compatibility
                            location_tuple = None
                            # FIX: Use 'is not None' for EarthLocation check
                            if current_location_for_run is not None:
                                location_tuple = (
                                    current_location_for_run.lat.deg,
                                    current_location_for_run.lon.deg,
                                    current_location_for_run.height.value
                                )

                            if location_tuple:
                                # Call the cached function
                                fig = plot_altitude(obj, location_tuple, lang)
                                if fig:
                                    # Display the cached figure object
                                    st.pyplot(fig)
                                    if st.button(t['results_close_plot_button'], key=close_button_key, type="secondary"):
                                        st.session_state.show_plot = False
                                        st.session_state.plot_object_name = None
                                        st.session_state.expanded_object_name = None
                                        st.rerun()
                                else:
                                    # Handle case where plot_altitude failed (returned None)
                                    st.warning(t['results_plot_not_created'])
                                    st.session_state.show_plot = False; st.session_state.plot_object_name = None; st.session_state.expanded_object_name = None
                            else:
                                 st.error("Location not defined for plotting.") # Should not happen if button logic is correct

                        except Exception as plot_e:
                            st.error(t['results_plot_error'].format(plot_e))
                            # Reset state on plotting error
                            st.session_state.show_plot = False; st.session_state.plot_object_name = None; st.session_state.expanded_object_name = None
                 else:
                      st.warning("Plotting skipped: Matplotlib library missing.")

    # --- CSV Export ---
    if export_data and pd:
        st.markdown("---")
        try:
            df = pd.DataFrame(export_data)
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
elif not st.session_state.find_button_pressed:
    st.info(t['info_initial_prompt'])

