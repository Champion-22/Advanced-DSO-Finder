# -*- coding: utf-8 -*-
import streamlit as st
import random
from datetime import datetime, date, time, timedelta, timezone # Added timezone
import math
import io
import traceback # For more detailed error messages
import locale # For potential locale-specific formatting (optional)

# --- Library Imports ---
# Important import FIRST
try:
    from astropy.time import Time
except ImportError as e:
    st.error(f"Error: Basic Astropy library ('astropy.time') not found.")
    st.error("Please ensure astropy is installed: pip install astropy")
    st.stop()

# Main Astronomy Imports
try:
    import numpy as np
    import astropy.units as u
    from astropy.coordinates import EarthLocation, SkyCoord, get_sun, AltAz
    from astroplan.moon import moon_illumination
except ImportError as e:
    st.error(f"Error: Required Astropy/Astroplan library not found ({e}).")
    st.error("Please ensure astropy, numpy and astroplan are installed:")
    st.code("pip install astropy numpy astroplan")
    st.stop()

# Additional Libraries for Plotting and Export
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    plt.style.use('dark_background') # Set dark style globally
except ImportError as e:
    st.error(f"Error: Required library not found ({e}).")
    st.error("Please ensure pandas and matplotlib are installed:")
    st.code("pip install pandas matplotlib")
    st.stop()

# --- Translations ---
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
        'location_manual_display': "Manual ({:.2f}, {:.2f})",
        'location_error': "Location Error: {}",
        'location_error_fallback': "ERROR - Using Default",
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
        'window_info_template': "{}", # Placeholder for the message from get_observable_window
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
        'location_manual_display': "Manuell ({:.2f}, {:.2f})",
        'location_error': "Standort Fehler: {}",
        'location_error_fallback': "FEHLER - Nutze Standard",
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
        'search_params_time_specific': "Nacht nach dem {}", # Date format YYYY-MM-DD
        'search_params_filter_mag': "✨ Filter: {}",
        'search_params_filter_mag_bortle': "Bortle {} (<= {:.1f} mag)",
        'search_params_filter_mag_manual': "Manuell ({:.1f}-{:.1f} mag)",
        'search_params_filter_alt_types': "🔭 Filter: Min. Höhe {}°, Typen: {}",
        'search_params_types_all': "Alle",
        'spinner_searching': "Berechne Fenster & suche Objekte...",
        'window_info_template': "{}", # Placeholder
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

# --- Global Configuration & Catalog --- (Catalog remains the same)
DEFAULT_LOCATION_NAME = "Schötz, Lucerne" # Base name
DEFAULT_LAT = 47.17
DEFAULT_LON = 8.01
DEFAULT_HEIGHT = 550  # Meters
DEFAULT_LOCATION = EarthLocation(lat=DEFAULT_LAT * u.deg, lon=DEFAULT_LON * u.deg, height=DEFAULT_HEIGHT * u.m)

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

# --- Helper Functions --- (Logic unchanged, but using translations)

def get_magnitude_limit(bortle_scale: int) -> float:
    """Returns the approximate limiting magnitude for visual observation based on Bortle scale."""
    limits = {1: 15.5, 2: 15.5, 3: 14.5, 4: 14.5, 5: 13.5, 6: 12.5, 7: 11.5, 8: 10.5, 9: 9.5}
    return limits.get(bortle_scale, 9.5)

def _get_fallback_window(reference_time: 'Time') -> tuple['Time', 'Time']:
    """Provides a default observation window (e.g., 9 PM to 3 AM local time) in UTC."""
    try:
        local_tz = datetime.now(timezone.utc).astimezone().tzinfo
        dt_ref = reference_time.datetime
        utc_offset_hours = local_tz.utcoffset(dt_ref).total_seconds() / 3600 if local_tz else 1
    except:
        utc_offset_hours = 1
    start_date = reference_time.datetime.date()
    end_date = start_date + timedelta(days=1)
    local_dt_start = datetime.combine(start_date, time(21, 0))
    local_dt_end = datetime.combine(end_date, time(3, 0))
    start_time = Time(local_dt_start - timedelta(hours=utc_offset_hours))
    end_time = Time(local_dt_end - timedelta(hours=utc_offset_hours))
    if end_time < reference_time:
         start_time += timedelta(days=1)
         end_time += timedelta(days=1)
    return start_time, end_time

def get_observable_window(observer_location: EarthLocation, reference_time: 'Time', is_now: bool, lang: str) -> tuple[Time | None, Time | None, str]:
    """Calculates the astronomical twilight window for the night around the reference time. Returns status message in selected language."""
    t = translations[lang] # Get translations for the selected language
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
            else:
                start_time = start_time_calc
                end_time = end_time_calc

            date_str = reference_date.strftime('%Y-%m-%d') # Consistent date format

            if is_now and start_time < reference_time:
                start_time = reference_time
                status_message = t['window_starts_now'].format(start_time.iso, end_time.iso)
            elif is_now and start_time >= reference_time:
                 status_message = t['window_starts_at'].format(start_time.iso, end_time.iso)
            else: # Specific date selected
                 status_message = t['window_for_night'].format(date_str, start_time.iso, end_time.iso)

            if is_now and end_time < reference_time:
                status_message = t['window_already_passed']
                # Recursive call needs the language too
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
    location: EarthLocation, observing_times: Time, min_altitude_limit: u.Quantity,
    magnitude_filter_mode: str, bortle_scale: int, manual_min_mag: float,
    manual_max_mag: float, selected_object_types: list, lang: str
) -> list:
    """Finds DSOs from the catalog visible during the observing times, applying filters."""
    t = translations[lang]
    observable_objects = []
    magnitude_limit = None

    # Determine magnitude limit based on filter mode (use internal keys)
    if magnitude_filter_mode == 'Bortle Scale': # Internal Key 'Bortle Scale'
        magnitude_limit = get_magnitude_limit(bortle_scale)
    else: # Internal Key 'Manual'
        if manual_min_mag > manual_max_mag:
            manual_min_mag, manual_max_mag = manual_max_mag, manual_min_mag

    for obj_data in DSO_CATALOG:
        name, ra_str, dec_str, mag, obj_type = obj_data

        if selected_object_types and obj_type not in selected_object_types:
            continue

        if magnitude_filter_mode == 'Bortle Scale': # Internal Key
            if mag > magnitude_limit:
                continue
        else: # Internal Key 'Manual'
            if not (manual_min_mag <= mag <= manual_max_mag):
                continue

        try:
            target = SkyCoord(ra=ra_str, dec=dec_str, frame='icrs')
            altaz_frame = AltAz(obstime=observing_times, location=location)
            target_altaz = target.transform_to(altaz_frame)
            altitudes = target_altaz.alt
            azimuths = target_altaz.az
            valid_indices = np.where(altitudes >= min_altitude_limit)[0]

            if len(valid_indices) > 0:
                peak_overall_index = np.argmax(altitudes)
                observable_objects.append({
                    "name": name, "type": obj_type, "magnitude": mag,
                    "ra_str": ra_str, "dec_str": dec_str,
                    "ra": target.ra.to_string(unit=u.hour, sep='hms', precision=1),
                    "dec": target.dec.to_string(unit=u.deg, sep='dms', precision=0),
                    "peak_alt": altitudes[peak_overall_index].to(u.deg).value,
                    "peak_az": azimuths[peak_overall_index].to(u.deg).value,
                    "peak_time_utc": observing_times[peak_overall_index].iso,
                    "times_jd": observing_times.jd,
                    "altitudes": altitudes.to(u.deg).value,
                    "azimuths": azimuths.to(u.deg).value,
                    "min_alt_limit": min_altitude_limit.value
                })
        except Exception as e:
            st.warning(t['error_processing_object'].format(name, e))

    return observable_objects

# Moon distance function removed

def create_moon_phase_svg(illumination_fraction: float, size: int = 80) -> str:
    """Generates an SVG image representing the moon phase illumination percentage."""
    percentage = illumination_fraction * 100
    radius = size // 2 - 6; cx = cy = size // 2
    stroke_color = "#DDDDDD"; stroke_width = 3; text_fill = "#EEEEEE"
    font_size = size * 0.3
    svg = f"""<svg width="{size}" height="{size}" viewbox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle;">
      <circle cx="{cx}" cy="{cy}" r="{radius}" stroke="{stroke_color}" stroke-width="{stroke_width}" fill="#222222" />
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="{font_size}px" fill="{text_fill}" font-weight="bold">{percentage:.0f}%</text>
    </svg>"""
    return svg

def plot_altitude(obj_data: dict, location: EarthLocation, lang: str):
    """Creates a Matplotlib plot showing the altitude of an object over time, using selected language."""
    t = translations[lang]
    fig, ax = plt.subplots()
    try:
        times = Time(obj_data['times_jd'], format='jd')
        try:
            local_tz = datetime.now(timezone.utc).astimezone().tzinfo
            times_local = [t.to_datetime(timezone=local_tz) for t in times]
            xlabel = t['plot_time_label_local'].format(local_tz.tzname(datetime.now()) if local_tz else 'Local')
        except Exception:
             local_tz = None
             times_local = times.datetime
             xlabel = t['plot_time_label_utc']

        # Plot altitude vs time
        ax.plot(times_local, obj_data['altitudes'], label=t['plot_altitude_label'], color='#00C0F0')
        # Plot minimum altitude limit
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
        st.error(t['results_plot_error'].format(e)) # Use translated error message
        plt.close(fig)
        return None
    return fig

def get_local_time_str(utc_iso_time: str) -> tuple[str, str]:
    """Converts a UTC ISO time string to local time string and timezone name."""
    try:
        local_tz = datetime.now(timezone.utc).astimezone().tzinfo
        dt_peak_utc = Time(utc_iso_time).datetime.replace(tzinfo=timezone.utc)
        dt_peak_local = dt_peak_utc.astimezone(local_tz)
        tz_name = local_tz.tzname(dt_peak_local) if local_tz else "UTC+?"
        peak_time_local_str = dt_peak_local.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        tz_name = "UTC+1" # Fallback
        try:
            peak_time_local = (Time(utc_iso_time) + timedelta(hours=1)).datetime
            peak_time_local_str = peak_time_local.strftime('%Y-%m-%d %H:%M:%S')
        except:
            peak_time_local_str = "N/A"; tz_name = ""
    return peak_time_local_str, tz_name

# --- Streamlit UI Setup ---

# Initialize session state for language if it doesn't exist
if 'language' not in st.session_state:
    st.session_state.language = 'en' # Default to English

# Get translations for the selected language
lang = st.session_state.language
t = translations[lang]

st.set_page_config(page_title=t['page_title'], layout="wide")

# --- Custom CSS Styling --- (Unchanged)
st.markdown("""
<style>
    .main .block-container { background-color: #1E1E1E; color: #EAEAEA; border-radius: 10px; padding: 2rem; }
    div[data-testid="stButton"] > button { background-image: linear-gradient(to right, #007bff, #0056b3); color: white; border: none; padding: 10px 24px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer; border-radius: 8px; transition-duration: 0.4s; }
    div[data-testid="stButton"] > button:hover { background-image: linear-gradient(to right, #0056b3, #003d80); color: white; }
    .streamlit-expanderHeader { background-color: #333333; color: #EAEAEA; border-radius: 5px; }
    div[data-testid="stMetric"] { background-color: #2a2a2a; border-radius: 8px; padding: 10px; }
    div[data-testid="stMetric"] > div[data-testid="stMetricLabel"] { color: #AAAAAA; }
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.title(t['app_title'])

# --- Session State Initialization (Plotting & Results) ---
if 'plot_object_name' not in st.session_state: st.session_state.plot_object_name = None
if 'show_plot' not in st.session_state: st.session_state.show_plot = False
if 'last_results' not in st.session_state: st.session_state.last_results = []
if 'find_button_pressed' not in st.session_state: st.session_state.find_button_pressed = False # Track if button was pressed

# --- Sidebar ---
with st.sidebar:
    st.header(t['settings_header'])

    # --- Language Selector ---
    language_options = {'en': 'English', 'de': 'Deutsch'}
    selected_lang_key = st.radio(
        t['language_select_label'],
        options=language_options.keys(),
        format_func=lambda key: language_options[key], # Show full names
        key='language_radio', # Use a distinct key for the widget
        index=list(language_options.keys()).index(st.session_state.language) # Set initial selection
    )
    # Update session state if selection changed (triggers rerun)
    if selected_lang_key != st.session_state.language:
        st.session_state.language = selected_lang_key
        # Clear results when language changes to avoid confusion? Optional.
        # st.session_state.last_results = []
        # st.session_state.find_button_pressed = False
        st.rerun()

    # --- Location Settings ---
    with st.expander(t['location_expander'], expanded=True):
        # Use internal keys 'Default', 'Manual' for logic
        location_options_map = {
            'Default': t['location_option_default'].format(DEFAULT_LOCATION_NAME),
            'Manual': t['location_option_manual']
        }
        location_choice_key = st.radio(
            t['location_select_label'],
            options=location_options_map.keys(), # Use internal keys
            format_func=lambda key: location_options_map[key], # Show translated labels
            key="location_choice_exp"
        )
        current_location = DEFAULT_LOCATION
        location_display_name = DEFAULT_LOCATION_NAME

        if location_choice_key == "Manual": # Use internal key
            manual_lat = st.number_input(t['location_lat_label'], value=DEFAULT_LAT, min_value=-90.0, max_value=90.0, step=0.01, format="%.2f")
            manual_lon = st.number_input(t['location_lon_label'], value=DEFAULT_LON, min_value=-180.0, max_value=180.0, step=0.01, format="%.2f")
            manual_height = st.number_input(t['location_elev_label'], value=DEFAULT_HEIGHT, min_value=-500, step=10)
            try:
                current_location = EarthLocation(lat=manual_lat*u.deg, lon=manual_lon*u.deg, height=manual_height*u.m)
                location_display_name = t['location_manual_display'].format(manual_lat, manual_lon)
            except Exception as e:
                st.error(t['location_error'].format(e))
                location_display_name = t['location_error_fallback']
                current_location = DEFAULT_LOCATION

    # --- Time Settings ---
    with st.expander(t['time_expander']):
         # Use internal keys 'Now', 'Specific' for logic
        time_options_map = {
            'Now': t['time_option_now'],
            'Specific': t['time_option_specific']
        }
        time_choice_key = st.radio(
            t['time_select_label'],
            options=time_options_map.keys(), # Use internal keys
            format_func=lambda key: time_options_map[key], # Show translated labels
            key="time_choice_exp"
        )
        is_time_now = (time_choice_key == "Now") # Use internal key
        reference_time = Time.now()

        if not is_time_now:
            selected_date = st.date_input(
                t['time_date_select_label'],
                date.today(),
                min_value=date.today()-timedelta(days=365*5),
                max_value=date.today()+timedelta(days=365*1)
            )
            reference_time = Time(datetime.combine(selected_date, time(12, 0)))

    # --- Filter Settings ---
    with st.expander(t['filters_expander'], expanded=True):
        st.markdown(t['mag_filter_header'])
        # Use internal keys 'Bortle Scale', 'Manual' for logic
        mag_filter_options_map = {
            'Bortle Scale': t['mag_filter_option_bortle'],
            'Manual': t['mag_filter_option_manual']
        }
        magnitude_filter_mode_key = st.radio(
            t['mag_filter_method_label'],
            options=mag_filter_options_map.keys(), # Use internal keys
            format_func=lambda key: mag_filter_options_map[key], # Show translated labels
            key="mag_filter_mode_exp",
            horizontal=True
        )

        bortle = 5; manual_min_mag = 0.0; manual_max_mag = 16.0
        if magnitude_filter_mode_key == "Bortle Scale": # Use internal key
            bortle = st.slider(
                t['mag_filter_bortle_label'], min_value=1, max_value=9, value=5, step=1,
                help=t['mag_filter_bortle_help']
            )
        else: # Use internal key 'Manual'
            manual_min_mag = st.slider(
                t['mag_filter_min_mag_label'], min_value=0.0, max_value=20.0, value=0.0, step=0.5, format="%.1f",
                help=t['mag_filter_min_mag_help']
            )
            manual_max_mag = st.slider(
                t['mag_filter_max_mag_label'], min_value=0.0, max_value=20.0, value=16.0, step=0.5, format="%.1f",
                 help=t['mag_filter_max_mag_help']
            )
            if manual_min_mag > manual_max_mag:
                st.warning(t['mag_filter_warning_min_max'])

        st.markdown("---")
        st.markdown(t['min_alt_header'])
        min_altitude_deg = st.slider(t['min_alt_label'], min_value=5, max_value=45, value=20, step=1)
        min_altitude_limit = min_altitude_deg * u.deg

        st.markdown("---")
        st.markdown(t['moon_warning_header'])
        moon_phase_threshold = st.slider(t['moon_warning_label'], min_value=0, max_value=100, value=35, step=5)

        st.markdown("---")
        st.markdown(t['object_types_header'])
        try:
            all_types = sorted(list(set(item[4] for item in DSO_CATALOG)))
        except IndexError:
            all_types = []
            st.warning(t['object_types_error_extract'])

        if all_types:
            selected_object_types = st.multiselect(
                t['object_types_label'], all_types, default=all_types,
                key="object_type_filter_exp"
            )
            if not selected_object_types: selected_object_types = all_types # If empty, select all

    # --- Result Options ---
    with st.expander(t['results_options_expander']):
        num_objects_to_suggest = st.slider(t['results_options_max_objects_label'], min_value=5, max_value=50, value=20, step=1)
        sort_by_brightness = st.checkbox(t['results_options_sort_brightness_label'], value=False)

# --- Main Area ---

# Display Moon Phase
try:
    current_moon_illumination = moon_illumination(reference_time)
    moon_percentage = current_moon_illumination * 100
    moon_col1, moon_col2 = st.columns([1, 4])
    with moon_col1: st.markdown(create_moon_phase_svg(current_moon_illumination, size=80), unsafe_allow_html=True)
    with moon_col2:
        st.metric(label=t['moon_metric_label'], value=f"{moon_percentage:.0f}%")
        if moon_percentage > moon_phase_threshold:
            st.error(t['moon_warning_message'].format(moon_percentage, moon_phase_threshold))
except Exception as e:
    st.error(t['moon_phase_error'].format(e))

st.markdown("---")

# Search Button
if st.button(t['find_button_label'], key="find_button"):
    st.session_state.find_button_pressed = True # Mark that search was triggered
    st.session_state.last_results = [] # Clear previous results

    # Display search parameters used
    with st.container():
        st.subheader(t['search_params_header'])
        col1, col2 = st.columns(2)
        with col1:
            st.info(t['search_params_location'].format(location_display_name))
            date_str_display = reference_time.datetime.date().strftime('%Y-%m-%d')
            time_info = t['search_params_time_now'].format(reference_time.iso) if is_time_now else t['search_params_time_specific'].format(date_str_display)
            st.info(t['search_params_time'].format(time_info))
        with col2:
            if magnitude_filter_mode_key == "Bortle Scale": # Use internal key
                mag_limit_display = get_magnitude_limit(bortle)
                mag_info = t['search_params_filter_mag_bortle'].format(bortle, mag_limit_display)
            else:
                mag_info = t['search_params_filter_mag_manual'].format(manual_min_mag, manual_max_mag)
            st.info(t['search_params_filter_mag'].format(mag_info))
            types_display = ', '.join(selected_object_types) if selected_object_types != all_types else t['search_params_types_all']
            st.info(t['search_params_filter_alt_types'].format(min_altitude_deg, types_display))

    # Perform the search
    selected_objects = []
    all_found_objects = []
    try:
        with st.spinner(t['spinner_searching']):
            # Pass language to functions needing translated messages
            start_time, end_time, window_msg = get_observable_window(current_location, reference_time, is_time_now, lang)

            if window_msg:
                 # Use st.info or st.warning based on message content (simple check)
                if "Warning" in window_msg or "Warnung" in window_msg:
                    st.warning(t['window_info_template'].format(window_msg.replace("\n", "\n\n")))
                else:
                    st.info(t['window_info_template'].format(window_msg.replace("\n", "\n\n")))


            if start_time and end_time and start_time < end_time:
                num_time_steps = max(20, int((end_time - start_time).to(u.hour).value * 12))
                observing_times = Time(np.linspace(start_time.jd, end_time.jd, num_time_steps), format='jd')

                # Pass language to find_observable_objects
                all_found_objects = find_observable_objects(
                    current_location, observing_times, min_altitude_limit,
                    magnitude_filter_mode_key, bortle, manual_min_mag, manual_max_mag, # Pass internal key
                    selected_object_types, lang
                )
            else:
                 # Check if a message was already displayed by get_observable_window before showing this generic one
                 if not window_msg or ("Fallback" not in window_msg and "fallback" not in window_msg) :
                      st.error(t['error_no_window'])


        st.success(t['success_objects_found'].format(len(all_found_objects)))

        if all_found_objects:
            processed_objects = all_found_objects
            if sort_by_brightness:
                processed_objects.sort(key=lambda x: x['magnitude'])
                selected_objects = processed_objects[:num_objects_to_suggest]
                st.write(t['info_showing_brightest'].format(len(selected_objects)))
            else:
                if len(processed_objects) > num_objects_to_suggest:
                    selected_objects = random.sample(processed_objects, num_objects_to_suggest)
                    st.write(t['info_showing_random'].format(num_objects_to_suggest))
                else:
                    selected_objects = processed_objects
                    selected_objects.sort(key=lambda x: x['name'])
                    st.write(t['info_showing_list'].format(len(selected_objects)))

            st.session_state.last_results = selected_objects
        else:
            st.session_state.last_results = []

    except Exception as main_e:
        st.error(t['error_search_unexpected'])
        st.exception(main_e)
        st.session_state.last_results = []


# Display Results
if st.session_state.last_results:
    st.markdown("---")
    st.subheader(t['results_list_header'])
    export_data = []

    for i, obj in enumerate(st.session_state.last_results):
        peak_time_local_str, tz_name = get_local_time_str(obj['peak_time_utc'])
        # Use translated keys for export DataFrame headers
        export_data.append({
            t['results_export_name']: obj['name'],
            t['results_export_type']: obj['type'],
            t['results_export_mag']: obj['magnitude'],
            t['results_export_ra']: obj['ra'],
            t['results_export_dec']: obj['dec'],
            t['results_export_max_alt']: f"{obj['peak_alt']:.1f}",
            t['results_export_az_at_max']: f"{obj['peak_az']:.1f}",
            t['results_export_time_max_utc']: obj['peak_time_utc'],
            t['results_export_time_max_local']: f"{peak_time_local_str} {tz_name}"
        })

        expander_title = t['results_expander_title'].format(obj['name'], obj['type'], obj['magnitude'])
        with st.expander(expander_title):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(t['results_coords_header'])
                st.markdown(f"RA: {obj['ra']}")
                st.markdown(f"Dec: {obj['dec']}")
            with col2:
                st.markdown(t['results_max_alt_header'])
                st.markdown(f"{obj['peak_alt']:.1f}°")
                st.markdown(t['results_azimuth_label'].format(obj['peak_az']))
            with col3:
                st.markdown(t['results_best_time_header'])
                st.markdown(f"**{peak_time_local_str}**")
                st.markdown(f"({tz_name})")

            st.markdown("---")
            plot_key = f"plot_btn_{obj['name']}_{i}"
            if st.button(t['results_plot_button'], key=plot_key):
                st.session_state.plot_object_name = obj['name']
                st.session_state.show_plot = True
                st.rerun()

            if st.session_state.show_plot and st.session_state.plot_object_name == obj['name']:
                with st.spinner(t['results_spinner_plotting']):
                    try:
                        # Pass language to plot function
                        fig = plot_altitude(obj, current_location, lang)
                        if fig: st.pyplot(fig)
                        else: st.warning(t['results_plot_not_created'])

                        close_key = f"close_plot_{obj['name']}_{i}"
                        if st.button(t['results_close_plot_button'], key=close_key):
                            st.session_state.show_plot = False
                            st.session_state.plot_object_name = None
                            st.rerun()
                    except Exception as plot_e:
                         st.error(t['results_plot_error'].format(plot_e))
                         st.session_state.show_plot = False
                         st.session_state.plot_object_name = None

    if export_data:
        st.markdown("---")
        try:
            df = pd.DataFrame(export_data)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8-sig')
            file_date = reference_time.datetime.date().strftime('%Y%m%d')
            st.download_button(
                label=t['results_save_csv_button'],
                data=csv_buffer.getvalue(),
                file_name=t['results_csv_filename'].format(file_date), # Use translated filename template
                mime="text/csv"
            )
        except Exception as csv_e: st.error(t['results_csv_export_error'].format(csv_e))

# Message if search was run but found nothing
elif st.session_state.find_button_pressed and not st.session_state.last_results:
     st.warning(t['warning_no_objects_found'])
     st.session_state.find_button_pressed = False # Reset button press state after showing message

# Initial message
elif not st.session_state.find_button_pressed:
    st.info(t['info_initial_prompt'])
