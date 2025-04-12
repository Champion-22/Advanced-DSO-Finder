# -*- coding: utf-8 -*-
import streamlit as st
import random
from datetime import datetime, date, time, timedelta
import math
import io
import traceback # Für detailliertere Fehlermeldungen

# --- Bibliotheks-Importe ---
# Wichtiger Import VORAB
try:
    from astropy.time import Time
except ImportError as e:
    st.error(f"Fehler: Grundlegende Astropy-Bibliothek ('astropy.time') nicht gefunden.")
    st.error("Bitte stelle sicher, dass astropy installiert ist: pip install astropy")
    st.stop()

# Haupt-Astronomie-Imports
try:
    import numpy as np
    import astropy.units as u
    from astropy import coordinates
    from astropy.coordinates import EarthLocation, SkyCoord, get_sun, AltAz
    from astroplan.moon import moon_illumination
except ImportError as e:
    st.error(f"Fehler: Benötigte Astropy/Astroplan-Bibliothek nicht gefunden ({e}).")
    st.error("Bitte stelle sicher, dass astropy, numpy und astroplan installiert sind:")
    st.code("pip install astropy numpy astroplan")
    st.stop()

# Zusätzliche Bibliotheken für Plotting und Export
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    # Setze einen dunklen Stil für Matplotlib-Plots
    plt.style.use('dark_background')
except ImportError as e:
    st.error(f"Fehler: Benötigte Bibliothek nicht gefunden ({e}).")
    st.error("Bitte stelle sicher, dass pandas und matplotlib installiert sind:")
    st.code("pip install pandas matplotlib")
    st.stop()

# --- Globale Konfiguration & Katalog ---
DEFAULT_LOCATION_NAME = "Schötz, Luzern"
DEFAULT_LAT = 47.17
DEFAULT_LON = 8.01
DEFAULT_HEIGHT = 550  # Meter
DEFAULT_LOCATION = EarthLocation(lat=DEFAULT_LAT * u.deg, lon=DEFAULT_LON * u.deg, height=DEFAULT_HEIGHT * u.m)

# TODO: Diesen Katalog idealerweise aus einer externen Datei laden (z.B. CSV)
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

# --- Hilfsfunktionen --- (Logik unverändert)

def get_magnitude_limit(bortle_scale: int) -> float:
    limits = {1: 15.5, 2: 15.5, 3: 14.5, 4: 14.5, 5: 13.5, 6: 12.5, 7: 11.5, 8: 10.5, 9: 9.5}
    return limits.get(bortle_scale, 9.5)

def _get_fallback_window(reference_time: 'Time') -> tuple['Time', 'Time']:
    try:
        from datetime import timezone
        local_tz = datetime.now(timezone.utc).astimezone().tzinfo
        dt_ref = reference_time.datetime
        utc_offset_hours = local_tz.utcoffset(dt_ref).total_seconds() / 3600 if local_tz else 1
    except: utc_offset_hours = 1
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

def get_observable_window(observer_location: EarthLocation, reference_time: 'Time', is_now: bool) -> tuple[Time | None, Time | None, str]:
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
                 status_message = f"Warnung: Ungültiges Dunkelheitsfenster berechnet ({start_time_calc.iso} bis {end_time_calc.iso}). Verwende Fallback."
                 start_time, end_time = _get_fallback_window(reference_time)
            else:
                start_time = start_time_calc
                end_time = end_time_calc

            if is_now and start_time < reference_time:
                start_time = reference_time
                status_message = f"Beobachtungsfenster beginnt jetzt ({start_time.iso} UTC) bis {end_time.iso} UTC (Astron. Dämmerung)"
            elif is_now and start_time >= reference_time:
                 status_message = f"Beobachtungsfenster beginnt um {start_time.iso} UTC bis {end_time.iso} UTC (Astron. Dämmerung)"
            else:
                 status_message = f"Beobachtungsfenster für die Nacht vom {reference_date.strftime('%d.%m.%Y')}: {start_time.iso} bis {end_time.iso} UTC (Astron. Dämmerung)"

            if is_now and end_time < reference_time:
                status_message = "Warnung: Das heutige Beobachtungsfenster ist bereits vorbei. Berechne für morgen Nacht."
                return get_observable_window(observer_location, reference_time + timedelta(days=1), True)

            return start_time, end_time, status_message
        else:
            status_message = f"Warnung: Konnte kein Fenster für astronomische Dunkelheit für die Nacht vom {reference_date.strftime('%d.%m.%Y')} finden. Verwende Fallback."
            start_time, end_time = _get_fallback_window(reference_time)
            status_message += f"\nFallback Beobachtungsfenster: {start_time.iso} bis {end_time.iso} UTC"
            return start_time, end_time, status_message
    except Exception as e:
        status_message = f"Fehler bei der Berechnung des Beobachtungsfensters: {e}\n{traceback.format_exc()}"
        start_time, end_time = _get_fallback_window(reference_time)
        status_message += f"\nVerwende Fallback-Fenster: {start_time.iso} bis {end_time.iso} UTC"
        return start_time, end_time, status_message

def find_observable_objects(
    location: EarthLocation, observing_times: Time, min_altitude_limit: u.Quantity,
    magnitude_filter_mode: str, bortle_scale: int, manual_min_mag: float,
    manual_max_mag: float, selected_object_types: list
) -> list:
    observable_objects = []
    magnitude_limit = None
    if magnitude_filter_mode == 'bortle':
        magnitude_limit = get_magnitude_limit(bortle_scale)
    else:
        if manual_min_mag > manual_max_mag: manual_min_mag, manual_max_mag = manual_max_mag, manual_min_mag

    for obj_data in DSO_CATALOG:
        name, ra_str, dec_str, mag, obj_type = obj_data
        if selected_object_types and obj_type not in selected_object_types: continue
        if magnitude_filter_mode == 'bortle':
            if mag > magnitude_limit: continue
        else:
            if not (manual_min_mag <= mag <= manual_max_mag): continue
        try:
            target = SkyCoord(ra=ra_str, dec=dec_str, frame='icrs')
            altaz_frame = AltAz(obstime=observing_times, location=location)
            target_altaz = target.transform_to(altaz_frame)
            altitudes = target_altaz.alt; azimuths = target_altaz.az
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
                    "times_jd": observing_times.jd, "altitudes": altitudes.to(u.deg).value,
                    "azimuths": azimuths.to(u.deg).value, "min_alt_limit": min_altitude_limit.value
                })
        except Exception as e: st.warning(f"Fehler bei {name}: {e}")
    return observable_objects

def create_moon_phase_svg(illumination_fraction: float, size: int = 80) -> str:
    percentage = illumination_fraction * 100
    radius = size // 2 - 6; cx = cy = size // 2
    stroke_color = "#DDDDDD"; stroke_width = 3; text_fill = "#EEEEEE"
    font_size = size * 0.3
    svg = f"""<svg width="{size}" height="{size}" viewbox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle;">
      <circle cx="{cx}" cy="{cy}" r="{radius}" stroke="{stroke_color}" stroke-width="{stroke_width}" fill="#222222" />
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="{font_size}px" fill="{text_fill}" font-weight="bold">{percentage:.0f}%</text>
    </svg>"""
    return svg

def plot_altitude(obj_data: dict, location: EarthLocation):
    fig, ax = plt.subplots()
    try:
        times = Time(obj_data['times_jd'], format='jd')
        try:
            from datetime import timezone
            local_tz = datetime.now(timezone.utc).astimezone().tzinfo
            times_local = [t.to_datetime(timezone=local_tz) for t in times]
            xlabel = f"Zeit ({local_tz.tzname(datetime.now()) if local_tz else 'Lokal'})"
        except Exception:
            local_tz = None; times_local = times.datetime; xlabel = "Zeit (UTC)"
        ax.plot(times_local, obj_data['altitudes'], label='Höhe', color='#00C0F0') # Helleres Blau
        ax.axhline(obj_data['min_alt_limit'], color='#FF4040', linestyle='--', label=f'Mindesthöhe ({obj_data["min_alt_limit"]}°)') # Helleres Rot
        ax.set_ylim(0, 90)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Höhe (°)")
        ax.set_title(f"Höhenverlauf für {obj_data['name']}")
        ax.legend()
        ax.grid(True, linestyle=':', linewidth=0.5, color='#555555') # Dezentes Grid
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        plt.tight_layout()
    except Exception as e:
        st.error(f"Fehler beim Erstellen des Plots: {e}")
        plt.close(fig); return None
    return fig

def get_local_time_str(utc_iso_time: str) -> tuple[str, str]:
    try:
        from datetime import timezone
        local_tz = datetime.now(timezone.utc).astimezone().tzinfo
        dt_peak_utc = Time(utc_iso_time).datetime.replace(tzinfo=timezone.utc)
        dt_peak_local = dt_peak_utc.astimezone(local_tz)
        tz_name = local_tz.tzname(dt_peak_local) if local_tz else "UTC+1"
        peak_time_local_str = dt_peak_local.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        tz_name = "UTC+1"
        try:
            peak_time_local = (Time(utc_iso_time) + timedelta(hours=1)).datetime
            peak_time_local_str = peak_time_local.strftime('%Y-%m-%d %H:%M:%S')
        except: peak_time_local_str = "N/A"; tz_name = ""
    return peak_time_local_str, tz_name

# --- Streamlit UI Aufbau ---
st.set_page_config(page_title="Advanced DSO Finder", layout="wide")

# --- Custom CSS Styling ---
st.markdown("""
<style>
    /* Dunkler Hintergrund für den Hauptbereich */
    .main .block-container {
        background-color: #1E1E1E; /* Dunkelgrau */
        color: #EAEAEA; /* Heller Text */
        border-radius: 10px;
        padding: 2rem;
    }
    /* Styling für den Haupt-Button */
    div[data-testid="stButton"] > button {
        background-image: linear-gradient(to right, #007bff, #0056b3);
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        transition-duration: 0.4s;
    }
    div[data-testid="stButton"] > button:hover {
        background-image: linear-gradient(to right, #0056b3, #003d80);
        color: white;
    }
    /* Styling für Expander Header */
    .streamlit-expanderHeader {
        background-color: #333333;
        color: #EAEAEA;
        border-radius: 5px;
    }
    /* Styling für Metriken */
    div[data-testid="stMetric"] {
        background-color: #2a2a2a;
        border-radius: 8px;
        padding: 10px;
    }
    div[data-testid="stMetric"] > div[data-testid="stMetricLabel"] {
        color: #AAAAAA; /* Grauer Label-Text */
    }

</style>
""", unsafe_allow_html=True)

# --- Titel ---
st.title("✨ Advanced DSO Finder ✨") # Titel geändert

# --- Session State Initialisierung ---
if 'plot_object_name' not in st.session_state: st.session_state.plot_object_name = None
if 'show_plot' not in st.session_state: st.session_state.show_plot = False
if 'last_results' not in st.session_state: st.session_state.last_results = []

# --- Seitenleiste für Eingaben (mit Expandern) ---
with st.sidebar:
    st.header("Einstellungen")

    with st.expander("📍 Standort", expanded=True): # Standort standardmässig aufgeklappt
        location_choice = st.radio("Standort wählen", (f"Standard ({DEFAULT_LOCATION_NAME})", "Manuell eingeben"), key="location_choice_exp")
        current_location = DEFAULT_LOCATION
        location_display_name = DEFAULT_LOCATION_NAME
        if location_choice == "Manuell eingeben":
            manual_lat = st.number_input("Breitengrad (°N)", DEFAULT_LAT, -90.0, 90.0, step=0.01, format="%.2f")
            manual_lon = st.number_input("Längengrad (°E)", DEFAULT_LON, -180.0, 180.0, step=0.01, format="%.2f")
            manual_height = st.number_input("Höhe (Meter)", DEFAULT_HEIGHT, -500, step=10)
            try:
                current_location = EarthLocation(lat=manual_lat*u.deg, lon=manual_lon*u.deg, height=manual_height*u.m)
                location_display_name = f"Manuell ({manual_lat:.2f}, {manual_lon:.2f})"
            except Exception as e:
                st.error(f"Fehler Standort: {e}")
                location_display_name = f"FEHLER - Nutze Standard"

    with st.expander("⏱️ Zeitpunkt"):
        time_choice = st.radio("Zeitpunkt wählen", ("Jetzt (kommende Nacht)", "Andere Nacht"), key="time_choice_exp")
        is_time_now = (time_choice == "Jetzt (kommende Nacht)")
        reference_time = Time.now()
        if not is_time_now:
            selected_date = st.date_input("Datum auswählen:", date.today(), min_value=date.today()-timedelta(days=365*5), max_value=date.today()+timedelta(days=365*1))
            reference_time = Time(datetime.combine(selected_date, time(12, 0)))

    with st.expander("✨ Filter & Bedingungen", expanded=True): # Filter standardmässig aufgeklappt
        # Helligkeitsfilter
        st.markdown("**Helligkeitsfilter**")
        magnitude_filter_mode = st.radio("Filtermethode:", ("Bortle-Skala", "Manuell"), key="mag_filter_mode_exp", horizontal=True)
        bortle = 5; manual_min_mag = 0.0; manual_max_mag = 16.0
        if magnitude_filter_mode == "Bortle-Skala":
            bortle = st.slider( "Bortle-Skala:", 1, 9, 5, 1, help="1=Dunkel, 9=Stadt")
        else:
            manual_min_mag = st.slider("Min. Magnitude:", 0.0, 20.0, 0.0, 0.5, format="%.1f", help="Hellstes Objekt")
            manual_max_mag = st.slider("Max. Magnitude:", 0.0, 20.0, 16.0, 0.5, format="%.1f", help="Schwächstes Objekt")
            if manual_min_mag > manual_max_mag: st.warning("Min > Max!")
        st.markdown("---") # Trennlinie

        # Mindesthöhe
        st.markdown("**Mindesthöhe**")
        min_altitude_deg = st.slider("Min. Objekt-Höhe (°):", 5, 45, 20, 1)
        min_altitude_limit = min_altitude_deg * u.deg
        st.markdown("---")

        # Mond Warnung
        st.markdown("**Mond Warnung**")
        moon_phase_threshold = st.slider("Warnen wenn Mond > (%):", 0, 100, 35, 5)
        st.markdown("---")

        # Objekttypen
        st.markdown("**Objekttypen**")
        try: all_types = sorted(list(set(item[4] for item in DSO_CATALOG)))
        except IndexError: all_types = []
        if not all_types: st.warning("Typen nicht extrahierbar.")
        selected_object_types = st.multiselect("Typen (leer = alle):", all_types, default=all_types, key="object_type_filter_exp")
        if not selected_object_types: selected_object_types = all_types

    with st.expander("⚙️ Ergebnis-Optionen"):
        num_objects_to_suggest = st.slider("Anzahl Objekte:", 5, 50, 20, 1)
        sort_by_brightness = st.checkbox("Nach Helligkeit sortieren", value=False)

# --- Hauptbereich ---

# Mondphase anzeigen
try:
    current_moon_illumination = moon_illumination(reference_time)
    moon_percentage = current_moon_illumination * 100
    moon_col1, moon_col2 = st.columns([1, 4]) # Spalten angepasst
    with moon_col1: st.markdown(create_moon_phase_svg(current_moon_illumination, size=80), unsafe_allow_html=True)
    with moon_col2:
        st.metric(label="Mondhelligkeit (ca.)", value=f"{moon_percentage:.0f}%")
        if moon_percentage > moon_phase_threshold: st.error(f"Mond heller ({moon_percentage:.0f}%) als Schwelle ({moon_phase_threshold}%)!")
except Exception as e: st.error(f"Mondphasen-Fehler: {e}")

st.markdown("---")

# Such-Button
if st.button("🔭 Beobachtbare Objekte finden", key="find_button"): # Emoji hinzugefügt
    st.session_state.last_results = []

    # --- Suchparameter anzeigen ---
    with st.container():
        st.subheader("Suchparameter")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📍 Standort: {location_display_name}")
            time_info = f"Kommende Nacht (ab {reference_time.iso} UTC)" if is_time_now else f"Nacht nach {reference_time.datetime.date().strftime('%d.%m.%Y')}"
            st.info(f"⏱️ Zeitpunkt: {time_info}")
        with col2:
            mag_info = f"Bortle {bortle} (<= {get_magnitude_limit(bortle):.1f} mag)" if magnitude_filter_mode == "Bortle-Skala" else f"Manuell ({manual_min_mag:.1f}-{manual_max_mag:.1f} mag)"
            st.info(f"✨ Filter: {mag_info}")
            st.info(f"🔭 Filter: Min. Höhe {min_altitude_deg}°, Typen: {', '.join(selected_object_types) if selected_object_types != all_types else 'Alle'}")

    # --- Objekte suchen & Fenster berechnen ---
    selected_objects = []
    all_found_objects = []
    try:
        with st.spinner('Berechne Fenster & suche Objekte...'):
            start_time, end_time, window_msg = get_observable_window(current_location, reference_time, is_time_now)
            if window_msg: st.info(window_msg.replace("\n", "\n\n"))

            if start_time and end_time and start_time < end_time:
                observing_times = Time(np.linspace(start_time.jd, end_time.jd, max(20, int((end_time - start_time).to(u.hour).value * 12))), format='jd')
                all_found_objects = find_observable_objects(
                    current_location, observing_times, min_altitude_limit,
                    magnitude_filter_mode, bortle, manual_min_mag, manual_max_mag,
                    selected_object_types
                )
            else: st.error("Kein gültiges Beobachtungsfenster.")

        # Ergebnisse verarbeiten
        st.success(f"{len(all_found_objects)} passende Objekte gefunden.")
        if all_found_objects:
            processed_objects = all_found_objects # Monddistanz entfernt

            if sort_by_brightness:
                processed_objects.sort(key=lambda x: x['magnitude'])
                selected_objects = processed_objects[:num_objects_to_suggest]
                st.write(f"Anzeige der {len(selected_objects)} hellsten:")
            else:
                if len(processed_objects) > num_objects_to_suggest:
                    selected_objects = random.sample(processed_objects, num_objects_to_suggest)
                    st.write(f"Zufällige Auswahl von {num_objects_to_suggest}:")
                else:
                    selected_objects = processed_objects
                    selected_objects.sort(key=lambda x: x['name'])
                    st.write(f"Liste der {len(selected_objects)} Objekte:")
            st.session_state.last_results = selected_objects
        else: st.session_state.last_results = []

    except Exception as main_e:
        st.error("Unerwarteter Fehler während der Suche:")
        st.exception(main_e)
        st.session_state.last_results = []

# Ergebnisse anzeigen (immer, aus Session State)
if st.session_state.last_results:
    st.markdown("---")
    st.subheader("Ergebnisliste")
    export_data = []

    for i, obj in enumerate(st.session_state.last_results):
        peak_time_local_str, tz_name = get_local_time_str(obj['peak_time_utc'])
        export_data.append({
            "Name": obj['name'], "Typ": obj['type'], "Magnitude": obj['magnitude'],
            "RA": obj['ra'], "Dec": obj['dec'], "Max Höhe (°)": f"{obj['peak_alt']:.1f}",
            "Azimut Max (°)": f"{obj['peak_az']:.1f}", "Zeit Max (UTC)": obj['peak_time_utc'],
            "Zeit Max (Lokal)": f"{peak_time_local_str} {tz_name}"
        })

        expander_title = f"{obj['name']} ({obj['type']}) - Mag: {obj['magnitude']:.1f}"
        with st.expander(expander_title):
            # Verbesserte Detailansicht mit 3 Spalten
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Koordinaten:**")
                st.markdown(f"&nbsp;RA: {obj['ra']}")
                st.markdown(f"&nbsp;Dec: {obj['dec']}")
            with col2:
                st.markdown(f"**Max. Höhe:**")
                st.markdown(f"&nbsp;{obj['peak_alt']:.1f}° bei {obj['peak_az']:.1f}° Azimut")
            with col3:
                st.markdown(f"**Beste Zeit (Lokal):**")
                st.markdown(f"&nbsp;**{peak_time_local_str} {tz_name}**")

            st.markdown("---") # Trenner vor Plot Button

            # Plot Button Logik
            plot_key = f"plot_btn_{obj['name']}_{i}"
            if st.button("📈 Höhenverlauf", key=plot_key): # Emoji hinzugefügt
                st.session_state.plot_object_name = obj['name']
                st.session_state.show_plot = True
                st.experimental_rerun()

            if st.session_state.show_plot and st.session_state.plot_object_name == obj['name']:
                with st.spinner("Erstelle Plot..."):
                    try:
                        fig = plot_altitude(obj, current_location)
                        if fig: st.pyplot(fig)
                        else: st.warning("Plot nicht erstellt.")
                        close_key = f"close_plot_{obj['name']}_{i}"
                        if st.button("Plot schliessen", key=close_key):
                           st.session_state.show_plot = False
                           st.session_state.plot_object_name = None
                           st.experimental_rerun()
                    except Exception as plot_e:
                        st.error(f"Plot Fehler: {plot_e}")
                        st.session_state.show_plot = False
                        st.session_state.plot_object_name = None

    # CSV Download Button
    if export_data:
        st.markdown("---")
        try:
            df = pd.DataFrame(export_data)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8-sig')
            st.download_button("💾 Ergebnisliste als CSV speichern", csv_buffer.getvalue(), # Emoji hinzugefügt
                               f"dso_beobachtungsliste_{reference_time.datetime.date()}.csv", "text/csv")
        except Exception as csv_e: st.error(f"CSV Export Fehler: {csv_e}")

elif not st.session_state.last_results and 'find_button' in st.session_state and st.session_state.find_button:
     st.warning("Keine Objekte gefunden, die allen Kriterien entsprechen.")
else:
    st.info("Einstellungen anpassen & 'Beobachtbare Objekte finden' klicken.")

