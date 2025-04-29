# -*- coding: utf-8 -*-

# --- Translations ---
translations = {
    'de': {
        # === DSO Finder Keys ===
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
        'search_params_timezone': "🌍 Zeitzone: {}",
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
        'results_export_name': "Name", 'results_export_type': "Typ", 'results_export_constellation': "Sternbild",
        'results_export_mag': "Magnitude", 'results_export_size': "Größe (arcmin)", 'results_export_ra': "RA",
        'results_export_dec': "Dec", 'results_export_max_alt': "Max Höhe (°)", 'results_export_az_at_max': "Azimut bei Max (°)",
        'results_export_direction_at_max': "Richtung bei Max", 'results_export_time_max_utc': "Zeit bei Max (UTC)",
        'results_export_time_max_local': "Zeit bei Max (Lokale TZ)", 'results_export_cont_duration': "Max Kont Dauer (h)",
        # === KORREKTUR HIER ===
        'results_expander_title': '{} ({}) - Mag: {}', # Erwartet jetzt String für Mag
        # =======================
        'google_link_text': "Google", 'simbad_link_text': "SIMBAD",
        'results_coords_header': "**Details:**", 'results_constellation_label': "Sternbild:", 'results_size_label': "Größe (Hauptachse):",
        'results_size_value': "{:.1f} arcmin", 'results_max_alt_header': "**Max. Höhe:**", 'results_azimuth_label': "(Azimut: {:.1f}°{})",
        'results_direction_label': ", Richtung: {}", 'results_best_time_header': "**Beste Zeit (Lokale TZ):**",
        'results_cont_duration_header': "**Max. Kont. Dauer:**", 'results_duration_value': "{:.1f} Stunden",
        'graph_type_label': "Grafiktyp (für alle Grafiken):", 'graph_type_sky_path': "Himmelsbahn (Az/Alt)", 'graph_type_alt_time': "Höhenverlauf (Alt/Zeit)",
        'results_graph_button': "📈 Grafik anzeigen", 'results_spinner_plotting': "Erstelle Grafik...", 'results_graph_error': "Grafik Fehler: {}",
        'results_graph_not_created': "Grafik konnte nicht erstellt werden.", 'results_close_graph_button': "Grafik schliessen",
        'results_save_csv_button': "💾 Ergebnisliste als CSV speichern", 'results_csv_filename': "dso_beobachtungsliste_{}.csv", 'results_csv_export_error': "CSV Export Fehler: {}",
        'warning_no_objects_found': "Keine Objekte gefunden, die allen Kriterien für das berechnete Beobachtungsfenster entsprechen.",
        'info_initial_prompt': "Willkommen! Bitte **Koordinaten eingeben** oder **Ort suchen**, um die Objektsuche zu aktivieren.",
        'graph_altitude_label': "Höhe (°)", 'graph_azimuth_label': "Azimut (°)", 'graph_min_altitude_label': "Mindesthöhe ({:.0f}°)",
        'graph_max_altitude_label': "Maximalhöhe ({:.0f}°)", 'graph_title_sky_path': "Himmelsbahn für {}", 'graph_title_alt_time': "Höhenverlauf für {}",
        'graph_ylabel': "Höhe (°)", 'custom_target_expander': "Eigenes Ziel grafisch darstellen",
        'custom_target_ra_label': "Rektaszension (RA):", 'custom_target_dec_label': "Deklination (Dec):", 'custom_target_name_label': "Ziel-Name (Optional):",
        'custom_target_ra_placeholder': "z.B. 10:45:03.6 oder 161.265", 'custom_target_dec_placeholder': "z.B. -16:42:58 oder -16.716",
        'custom_target_button': "Eigene Grafik erstellen", 'custom_target_error_coords': "Ungültiges RA/Dec Format. Verwende HH:MM:SS.s / DD:MM:SS oder Dezimalgrad.",
        'custom_target_error_window': "Grafik kann nicht erstellt werden. Stelle sicher, dass Ort und Zeitfenster gültig sind (ggf. zuerst 'Beobachtbare Objekte finden' klicken).",
        'error_processing_object': "Fehler bei der Verarbeitung von {}: {}", 'window_calc_error': "Fehler bei der Berechnung des Beobachtungsfensters: {}\n{}",
        'window_fallback_info': "\nFallback-Fenster wird verwendet: {} bis {} UTC", 'error_loading_catalog': "Fehler beim Laden der Katalogdatei: {}",
        'info_catalog_loaded': "Katalog geladen: {} Objekte.", 'warning_catalog_empty': "Katalogdatei geladen, aber keine passenden Objekte nach Filterung gefunden.",
        'donation_text': "Gefällt dir der DSO Finder? [Unterstütze die Entwicklung auf Ko-fi ☕](https://ko-fi.com/advanceddsofinder)", # DSO Finder Donation
        'bug_report_button': "🐞 Fehler melden", 'bug_report_body': "\n\n(Bitte beschreiben Sie den Fehler und die Schritte zur Reproduktion)",

        # === Redshift Calculator Keys ===
        'redshift_calculator_title': "Rotverschiebungs-Rechner", # Hinzugefügt
        'redshift_z_tooltip': "Geben Sie die kosmologische Rotverschiebung ein (negativ für Blauverschiebung).", # Hinzugefügt
        "lang_select": "Sprache wählen", # Already exists
        "input_params": "Eingabeparameter", # RC Key
        "redshift_z": "Rotverschiebung (z)", # RC Key
        "cosmo_params": "Kosmologische Parameter", # RC Key
        "hubble_h0": "Hubble-Konstante (H₀) [km/s/Mpc]", # RC Key
        "omega_m": "Materiedichte (Ωm)", # RC Key
        "omega_lambda": "Dunkle Energie (ΩΛ)", # RC Key
        "flat_universe_warning": "Ωm + ΩΛ ≉ 1. Berechnungen gehen von flachem Universum aus (Ωk=0).", # RC Key
        "results_for": "Ergebnisse für z = {z:.5f}", # RC Key
        "error_invalid_input": "Ungültige Eingabe. Bitte Zahlen verwenden.", # RC Key
        "error_h0_positive": "Hubble-Konstante muss positiv sein.", # RC Key
        "error_omega_negative": "Omega-Parameter dürfen nicht negativ sein.", # RC Key
        "warn_blueshift": "Warnung: Rotverschiebung ist negativ (Blueshift). Kosmologische Distanzen sind hier 0 oder nicht direkt anwendbar.", # RC Key
        "error_dep_scipy": "Abhängigkeit 'scipy' nicht gefunden. Bitte installieren.", # RC Key
        "error_calc_failed": "Berechnung fehlgeschlagen: {e}", # RC Key
        "warn_integration_accuracy": "Warnung: Relative Integrationsgenauigkeit möglicherweise nicht erreicht (Fehler: DC={err_dc:.2e}, LT={err_lt:.2e}).", # RC Key
        "lookback_time": "Rückblickzeit (Lookback Time)", # RC Key
        "cosmo_distances": "Kosmologische Distanzen", # RC Key
        "comoving_distance_title": "**Mitbewegte Distanz (Comoving Distance):**", # RC Key
        "luminosity_distance_title": "**Leuchtkraftdistanz (Luminosity Distance):**", # RC Key
        "angular_diameter_distance_title": "**Winkeldurchmesserdistanz (Angular Diameter Distance):**", # RC Key
        "unit_Gyr": "Gyr (Milliarden Jahre)", # RC Key
        "unit_Mpc": "Mpc", # RC Key
        "unit_Gly": "Gly (Milliarden Lichtjahre)", # RC Key
        "unit_km": "km", # RC Key
        "unit_km_sci": "km (wiss.)", # RC Key
        "unit_km_full": "km (ausgeschr.)", # RC Key
        "unit_LJ": "LJ", # RC Key
        "unit_AE": "AE", # RC Key
        "unit_Ls": "Ls", # RC Key
        "calculation_note": "Berechnung basiert auf dem flachen ΛCDM-Modell unter Vernachlässigung der Strahlungsdichte.", # RC Key
        "rc_donate_text": "Gefällt Ihnen dieser Rechner? Unterstützen Sie die Entwicklung mit einer kleinen Spende!", # Hinzugefügt (RC Key)
        "rc_donate_button": "Spenden via Ko-fi", # Hinzugefügt (RC Key)
        "bug_report": "Fehler gefunden?", # RC Key
        #"bug_report_button": "Problem melden", # Using DSO Finder version
        "glossary": "Glossar", # RC Key
        "example_lookback_recent": "Vor Kurzem (kosmologisch gesehen).", # RC Key
        "example_lookback_humans": "Entwicklung des modernen Menschen.", # RC Key
        "example_lookback_dinos": "Zeitalter der Dinosaurier.", # RC Key
        "example_lookback_multicellular": "Entstehung komplexen mehrzelligen Lebens.", # RC Key
        "example_lookback_earth": "Entstehung der Erde und des Sonnensystems.", # RC Key
        "example_lookback_early_univ": "Frühes Universum, Bildung erster Sterne/Galaxien.", # RC Key
        "example_comoving_local": "Innerhalb unserer lokalen Galaxiengruppe.", # RC Key
        "example_comoving_virgo": "Entfernung zum Virgo-Galaxienhaufen.", # RC Key
        "example_comoving_coma": "Entfernung zum Coma-Galaxienhaufen.", # RC Key
        "example_comoving_lss": "Skala von Superhaufen und Filamenten.", # RC Key
        "example_comoving_quasars": "Distanz zu fernen Quasaren.", # RC Key
        "example_comoving_cmb": "Entfernung zum 'Rand' des beobachtbaren Universums (CMB).", # RC Key
        "explanation_luminosity": "Relevant für Helligkeit: Objekte erscheinen bei dieser Distanz so hell wie erwartet (wichtig für Standardkerzen wie Supernovae).", # RC Key
        "explanation_angular": "Relevant für Größe: Objekte haben bei dieser Distanz die erwartete scheinbare Größe (wichtig für Standardlineale wie BAO).", # RC Key
    },
    'en': {
        # === DSO Finder Keys ===
        'settings_header': "Settings", 'language_select_label': "Language", 'location_expander': "📍 Location",
        'location_select_label': "Select Location Method", 'location_option_manual': "Enter Manually", 'location_option_search': "Search by Name",
        'location_search_label': "Enter location name:", 'location_search_submit_button': "Find Coordinates", 'location_search_placeholder': "e.g., London, UK",
        'location_search_found': "Found (Nominatim): {}", 'location_search_found_fallback': "Found via Fallback (ArcGIS): {}", 'location_search_found_fallback2': "Found via 2nd Fallback (Photon): {}",
        'location_search_coords': "Lat: {:.4f}, Lon: {:.4f}", 'location_search_error_not_found': "Location not found.", 'location_search_error_service': "Geocoding service error: {}",
        'location_search_error_timeout': "Geocoding service timed out.", 'location_search_error_refused': "Geocoding connection refused.", 'location_search_info_fallback': "Nominatim failed, trying fallback service (ArcGIS)...",
        'location_search_info_fallback2': "ArcGIS failed, trying 2nd fallback service (Photon)...", 'location_search_error_fallback_failed': "Primary (Nominatim) and fallback (ArcGIS) failed: {}",
        'location_search_error_fallback2_failed': "All geocoding services (Nominatim, ArcGIS, Photon) failed: {}", 'location_lat_label': "Latitude (°N)", 'location_lon_label': "Longitude (°E)",
        'location_elev_label': "Elevation (meters)", 'location_manual_display': "Manual ({:.4f}, {:.4f})", 'location_search_display': "Searched: {} ({:.4f}, {:.4f})", 'location_error': "Location Error: {}",
        'location_error_fallback': "ERROR - Fallback used", 'location_error_manual_none': "Manual location fields cannot be empty or invalid.", 'time_expander': "⏱️ Time & Timezone",
        'time_select_label': "Select Time", 'time_option_now': "Now (Upcoming Night)", 'time_option_specific': "Specific Night", 'time_date_select_label': "Select Date:",
        'timezone_auto_set_label': "Detected Timezone:", 'timezone_auto_fail_label': "Timezone:", 'timezone_auto_fail_msg': "Could not detect timezone, using UTC.",
        'filters_expander': "✨ Filters & Conditions", 'mag_filter_header': "**Magnitude Filter**", 'mag_filter_method_label': "Filter Method:", 'mag_filter_option_bortle': "Bortle Scale",
        'mag_filter_option_manual': "Manual", 'mag_filter_bortle_label': "Bortle Scale:", 'mag_filter_bortle_help': "Sky darkness: 1=Excellent Dark, 9=Inner-city Sky",
        'mag_filter_min_mag_label': "Min. Magnitude:", 'mag_filter_min_mag_help': "Brightest object magnitude to include", 'mag_filter_max_mag_label': "Max. Magnitude:",
        'mag_filter_max_mag_help': "Dimest object magnitude to include", 'mag_filter_warning_min_max': "Min. Magnitude is greater than Max. Magnitude!",
        'min_alt_header': "**Object Altitude Above Horizon**", 'min_alt_label': "Min. Object Altitude (°):", 'max_alt_label': "Max. Object Altitude (°):", 'moon_warning_header': "**Moon Warning**",
        'moon_warning_label': "Warn if Moon > (% Illumination):", 'object_types_header': "**Object Types**", 'object_types_error_extract': "Could not extract object types from catalog.",
        'object_types_label': "Filter Types (leave empty for all):", 'size_filter_header': "**Angular Size Filter**", 'size_filter_label': "Object Size (arcminutes):",
        'size_filter_help': "Filter objects by their apparent size (major axis). 1 arcminute = 1/60 degree.", 'direction_filter_header': "**Filter by Cardinal Direction**",
        'direction_filter_label': "Show objects culminating towards:", 'direction_option_all': "All", 'object_type_glossary_title': "Object Type Glossary",
        'object_type_glossary': { "OCl": "Open Cluster", "GCl": "Globular Cluster", "Cl+N": "Cluster + Nebula", "Gal": "Galaxy", "PN": "Planetary Nebula", "SNR": "Supernova Remnant", "Neb": "Nebula (general)", "EmN": "Emission Nebula", "RfN": "Reflection Nebula", "HII": "HII Region", "AGN": "Active Galactic Nucleus" },
        'results_options_expander': "⚙️ Result Options", 'results_options_max_objects_label': "Max. Number of Objects to Display:", 'results_options_sort_method_label': "Sort Results By:",
        'results_options_sort_duration': "Duration & Altitude", 'results_options_sort_magnitude': "Brightness", 'moon_metric_label': "Moon Illumination (approx.)",
        'moon_warning_message': "Warning: Moon is brighter ({:.0f}%) than threshold ({:.0f}%)!", 'moon_phase_error': "Error calculating moon phase: {}", 'find_button_label': "🔭 Find Observable Objects",
        'search_params_header': "Search Parameters", 'search_params_location': "📍 Location: {}", 'search_params_time': "⏱️ Time: {}", 'search_params_timezone': "🌍 Timezone: {}",
        'search_params_time_now': "Upcoming Night (from {} UTC)", 'search_params_time_specific': "Night after {}", 'search_params_filter_mag': "✨ Filter: {}",
        'search_params_filter_mag_bortle': "Bortle {} (<= {:.1f} mag)", 'search_params_filter_mag_manual': "Manual ({:.1f}-{:.1f} mag)", 'search_params_filter_alt_types': "🔭 Filter: Alt {}-{}°, Types: {}",
        'search_params_filter_size': "📐 Filter: Size {:.1f} - {:.1f} arcmin", 'search_params_filter_direction': "🧭 Filter: Direction at Max: {}", 'search_params_types_all': "All",
        'search_params_direction_all': "All", 'spinner_searching': "Calculating window & searching objects...", 'spinner_geocoding': "Searching for location...",
        'window_info_template': "Observation window: {} to {} UTC (Astronomical Twilight)", 'window_already_passed': "Calculated night window for 'Now' has already passed. Calculating for next night.",
        'error_no_window': "No valid astronomical darkness window found for the selected date and location.", 'error_polar_night': "Astronomical darkness lasts >24h (Polar night?). Using fallback window.",
        'error_polar_day': "No astronomical darkness occurs (Polar day?). Using fallback window.", 'success_objects_found': "{} matching objects found.",
        'info_showing_list_duration': "Showing {} objects, sorted by visibility duration and culmination altitude:", 'info_showing_list_magnitude': "Showing {} objects, sorted by brightness (brightest first):",
        'error_search_unexpected': "An unexpected error occurred during the search:", 'results_list_header': "Result List",
        'results_export_name': "Name", 'results_export_type': "Type", 'results_export_constellation': "Constellation", 'results_export_mag': "Magnitude", 'results_export_size': "Size (arcmin)",
        'results_export_ra': "RA", 'results_export_dec': "Dec", 'results_export_max_alt': "Max Altitude (°)", 'results_export_az_at_max': "Azimuth at Max (°)", 'results_export_direction_at_max': "Direction at Max",
        'results_export_time_max_utc': "Time at Max (UTC)", 'results_export_time_max_local': "Time at Max (Local TZ)", 'results_export_cont_duration': "Max Cont Duration (h)",
        # === KORREKTUR HIER ===
        'results_expander_title': '{} ({}) - Mag: {}', # Expects string for Mag now
        # =======================
        'google_link_text': "Google", 'simbad_link_text': "SIMBAD", 'results_coords_header': "**Details:**", 'results_constellation_label': "Constellation:",
        'results_size_label': "Size (Major Axis):", 'results_size_value': "{:.1f} arcmin", 'results_max_alt_header': "**Max. Altitude:**", 'results_azimuth_label': "(Azimuth: {:.1f}°{})",
        'results_direction_label': ", Direction: {}", 'results_best_time_header': "**Best Time (Local TZ):**", 'results_cont_duration_header': "**Max. Cont. Duration:**", 'results_duration_value': "{:.1f} hours",
        'graph_type_label': "Graph Type (for all plots):", 'graph_type_sky_path': "Sky Path (Az/Alt)", 'graph_type_alt_time': "Altitude Plot (Alt/Time)", 'results_graph_button': "📈 Show Plot",
        'results_spinner_plotting': "Creating plot...", 'results_graph_error': "Plot Error: {}", 'results_graph_not_created': "Plot could not be created.", 'results_close_graph_button': "Close Plot",
        'results_save_csv_button': "💾 Save Result List as CSV", 'results_csv_filename': "dso_observation_list_{}.csv", 'results_csv_export_error': "CSV Export Error: {}",
        'warning_no_objects_found': "No objects found matching all criteria for the calculated observation window.", 'info_initial_prompt': "Welcome! Please **Enter Coordinates** or **Search Location** to enable object search.",
        'graph_altitude_label': "Altitude (°)", 'graph_azimuth_label': "Azimuth (°)", 'graph_min_altitude_label': "Min Altitude ({:.0f}°)", 'graph_max_altitude_label': "Max Altitude ({:.0f}°)",
        'graph_title_sky_path': "Sky Path for {}", 'graph_title_alt_time': "Altitude Plot for {}", 'graph_ylabel': "Altitude (°)", 'custom_target_expander': "Plot Custom Target",
        'custom_target_ra_label': "Right Ascension (RA):", 'custom_target_dec_label': "Declination (Dec):", 'custom_target_name_label': "Target Name (Optional):",
        'custom_target_ra_placeholder': "e.g., 10:45:03.6 or 161.265", 'custom_target_dec_placeholder': "e.g., -16:42:58 or -16.716", 'custom_target_button': "Create Custom Plot",
        'custom_target_error_coords': "Invalid RA/Dec format. Use HH:MM:SS.s / DD:MM:SS or decimal degrees.", 'custom_target_error_window': "Cannot create plot. Ensure location and time window are valid (try clicking 'Find Observable Objects' first).",
        'error_processing_object': "Error processing {}: {}", 'window_calc_error': "Error calculating observation window: {}\n{}", 'window_fallback_info': "\nUsing fallback window: {} to {} UTC",
        'error_loading_catalog': "Error loading catalog file: {}", 'info_catalog_loaded': "Catalog loaded: {} objects.", 'warning_catalog_empty': "Catalog file loaded, but no matching objects found after filtering.",
        'donation_text': "Like the DSO Finder? [Support the development on Ko-fi ☕](https://ko-fi.com/advanceddsofinder)", # DSO Finder Donation
        'bug_report_button': "🐞 Report Bug", 'bug_report_body': "\n\n(Please describe the bug and the steps to reproduce it)",

        # === Redshift Calculator Keys ===
        'redshift_calculator_title': "Redshift Calculator", # Added
        'redshift_z_tooltip': "Enter cosmological redshift (negative for blueshift).", # Added
        "lang_select": "Select Language", # RC Key
        "input_params": "Input Parameters", # RC Key
        "redshift_z": "Redshift (z)", # RC Key
        "cosmo_params": "Cosmological Parameters", # RC Key
        "hubble_h0": "Hubble Constant (H₀) [km/s/Mpc]", # RC Key
        "omega_m": "Matter Density (Ωm)", # RC Key
        "omega_lambda": "Dark Energy Density (ΩΛ)", # RC Key
        "flat_universe_warning": "Ωm + ΩΛ ≉ 1. Calculations assume a flat universe (Ωk=0).", # RC Key
        "results_for": "Results for z = {z:.5f}", # RC Key
        "error_invalid_input": "Invalid input. Please use numbers.", # RC Key
        "error_h0_positive": "Hubble constant must be positive.", # RC Key
        "error_omega_negative": "Omega parameters cannot be negative.", # RC Key
        "warn_blueshift": "Warning: Redshift is negative (Blueshift). Cosmological distances are 0 or not directly applicable here.", # RC Key
        "error_dep_scipy": "Dependency 'scipy' not found. Please install.", # RC Key
        "error_calc_failed": "Calculation failed: {e}", # RC Key
        "warn_integration_accuracy": "Warning: Relative integration accuracy might not be achieved (Error: DC={err_dc:.2e}, LT={err_lt:.2e}).", # RC Key
        "lookback_time": "Lookback Time", # RC Key
        "cosmo_distances": "Cosmological Distances", # RC Key
        "comoving_distance_title": "**Comoving Distance:**", # RC Key
        "luminosity_distance_title": "**Luminosity Distance:**", # RC Key
        "angular_diameter_distance_title": "**Angular Diameter Distance:**", # RC Key
        "unit_Gyr": "Gyr (Billion Years)", # RC Key
        "unit_Mpc": "Mpc", # RC Key
        "unit_Gly": "Gly (Billion Lightyears)", # RC Key
        "unit_km": "km", # RC Key
        "unit_km_sci": "km (sci.)", # RC Key
        "unit_km_full": "km (full)", # RC Key
        "unit_LJ": "ly", # RC Key
        "unit_AE": "AU", # RC Key
        "unit_Ls": "Ls", # RC Key
        "calculation_note": "Calculation based on the flat ΛCDM model, neglecting radiation density.", # RC Key
        "rc_donate_text": "Like this calculator? Support its development with a small donation!", # Added (RC Key)
        "rc_donate_button": "Donate via Ko-fi", # Added (RC Key)
        "bug_report": "Found a bug?", # RC Key
        #"bug_report_button": "Report Issue", # Using DSO Finder version
        "glossary": "Glossary", # RC Key
        "example_lookback_recent": "Recently (cosmologically speaking).", # RC Key
        "example_lookback_humans": "Evolution of modern humans.", # RC Key
        "example_lookback_dinos": "Age of the dinosaurs.", # RC Key
        "example_lookback_multicellular": "Emergence of complex multicellular life.", # RC Key
        "example_lookback_earth": "Formation of the Earth and Solar System.", # RC Key
        "example_lookback_early_univ": "Early universe, formation of first stars/galaxies.", # RC Key
        "example_comoving_local": "Within our Local Group of galaxies.", # RC Key
        "example_comoving_virgo": "Distance to the Virgo Cluster.", # RC Key
        "example_comoving_coma": "Distance to the Coma Cluster.", # RC Key
        "example_comoving_lss": "Scale of superclusters and filaments.", # RC Key
        "example_comoving_quasars": "Distance to distant quasars.", # RC Key
        "example_comoving_cmb": "Distance to the 'edge' of the observable universe (CMB).", # RC Key
        "explanation_luminosity": "Relevant for brightness: Objects appear as bright as expected at this distance (important for standard candles like supernovae).", # RC Key
        "explanation_angular": "Relevant for size: Objects have the expected apparent size at this distance (important for standard rulers like BAO).", # RC Key
    },
    'fr': {
        # === DSO Finder Keys ===
        'settings_header': "Paramètres", 'language_select_label': "Langue", 'location_expander': "📍 Emplacement", 'location_select_label': "Choisir la méthode d'emplacement",
        'location_option_manual': "Saisir manuellement", 'location_option_search': "Rechercher par nom", 'location_search_label': "Entrer le nom du lieu :",
        'location_search_submit_button': "Trouver les coordonnées", 'location_search_placeholder': "p.ex. Paris, France", 'location_search_found': "Trouvé (Nominatim) : {}",
        'location_search_found_fallback': "Trouvé via fallback (ArcGIS) : {}", 'location_search_found_fallback2': "Trouvé via 2e fallback (Photon) : {}", 'location_search_coords': "Lat : {:.4f}, Lon : {:.4f}",
        'location_search_error_not_found': "Lieu non trouvé.", 'location_search_error_service': "Erreur du service de géocodage : {}", 'location_search_error_timeout': "Délai d'attente du service de géocodage dépassé.",
        'location_search_error_refused': "Connexion de géocodage refusée.", 'location_search_info_fallback': "Échec de Nominatim, tentative de service de secours (ArcGIS)...",
        'location_search_info_fallback2': "Échec d'ArcGIS, tentative de 2e service de secours (Photon)...", 'location_search_error_fallback_failed': "Échec du service primaire (Nominatim) et de secours (ArcGIS) : {}",
        'location_search_error_fallback2_failed': "Échec de tous les services de géocodage (Nominatim, ArcGIS, Photon) : {}", 'location_lat_label': "Latitude (°N)", 'location_lon_label': "Longitude (°E)",
        'location_elev_label': "Altitude (mètres)", 'location_manual_display': "Manuel ({:.4f}, {:.4f})", 'location_search_display': "Recherché : {} ({:.4f}, {:.4f})", 'location_error': "Erreur d'emplacement : {}",
        'location_error_fallback': "ERREUR - Utilisation du fallback", 'location_error_manual_none': "Les champs d'emplacement manuel ne peuvent pas être vides ou invalides.", 'time_expander': "⏱️ Heure & Fuseau horaire",
        'time_select_label': "Choisir l'heure", 'time_option_now': "Maintenant (nuit prochaine)", 'time_option_specific': "Nuit spécifique", 'time_date_select_label': "Choisir la date :",
        'timezone_auto_set_label': "Fuseau horaire détecté :", 'timezone_auto_fail_label': "Fuseau horaire :", 'timezone_auto_fail_msg': "Impossible de détecter le fuseau horaire, UTC est utilisé.",
        'filters_expander': "✨ Filtres & Conditions", 'mag_filter_header': "**Filtre de Magnitude**", 'mag_filter_method_label': "Méthode de filtrage :", 'mag_filter_option_bortle': "Échelle de Bortle",
        'mag_filter_option_manual': "Manuel", 'mag_filter_bortle_label': "Échelle de Bortle :", 'mag_filter_bortle_help': "Obscurité du ciel : 1=Excellent ciel noir, 9=Ciel de centre-ville",
        'mag_filter_min_mag_label': "Magnitude Min. :", 'mag_filter_min_mag_help': "Magnitude de l'objet le plus brillant à inclure", 'mag_filter_max_mag_label': "Magnitude Max. :",
        'mag_filter_max_mag_help': "Magnitude de l'objet le plus faible à inclure", 'mag_filter_warning_min_max': "Magnitude Min. est supérieure à la Magnitude Max. !",
        'min_alt_header': "**Altitude de l'objet au-dessus de l'horizon**", 'min_alt_label': "Altitude Min. de l'objet (°) :", 'max_alt_label': "Altitude Max. de l'objet (°) :", 'moon_warning_header': "**Avertissement Lunaire**",
        'moon_warning_label': "Avertir si Lune > (% Illumination) :", 'object_types_header': "**Types d'objets**", 'object_types_error_extract': "Impossible d'extraire les types d'objets du catalogue.",
        'object_types_label': "Filtrer les types (laisser vide pour tous) :", 'size_filter_header': "**Filtre de Taille Angulaire**", 'size_filter_label': "Taille de l'objet (minutes d'arc) :",
        'size_filter_help': "Filtrer les objets par leur taille apparente (axe majeur). 1 minute d'arc = 1/60 degré.", 'direction_filter_header': "**Filtre par Direction Cardinale**",
        'direction_filter_label': "Afficher les objets culminant vers :", 'direction_option_all': "Toutes", 'object_type_glossary_title': "Glossaire des types d'objets",
        'object_type_glossary': { "OCl": "Amas Ouvert", "GCl": "Amas Globulaire", "Cl+N": "Amas + Nébuleuse", "Gal": "Galaxie", "PN": "Nébuleuse Planétaire", "SNR": "Rémanent de Supernova", "Neb": "Nébuleuse (général)", "EmN": "Nébuleuse en Émission", "RfN": "Nébuleuse par Réflexion", "HII": "Région HII", "AGN": "Noyau Actif de Galaxie" },
        'results_options_expander': "⚙️ Options de Résultats", 'results_options_max_objects_label': "Nombre max. d'objets à afficher :", 'results_options_sort_method_label': "Trier les résultats par :",
        'results_options_sort_duration': "Durée & Altitude", 'results_options_sort_magnitude': "Luminosité", 'moon_metric_label': "Illumination lunaire (env.)",
        'moon_warning_message': "Attention : La Lune est plus brillante ({:.0f}%) que le seuil ({:.0f}%) !", 'moon_phase_error': "Erreur lors du calcul de la phase lunaire : {}", 'find_button_label': "🔭 Trouver les objets observables",
        'search_params_header': "Paramètres de recherche", 'search_params_location': "📍 Emplacement : {}", 'search_params_time': "⏱️ Heure : {}", 'search_params_timezone': "🌍 Fuseau horaire : {}",
        'search_params_time_now': "Nuit prochaine (à partir de {} UTC)", 'search_params_time_specific': "Nuit après {}", 'search_params_filter_mag': "✨ Filtre : {}",
        'search_params_filter_mag_bortle': "Bortle {} (<= {:.1f} mag)", 'search_params_filter_mag_manual': "Manuel ({:.1f}-{:.1f} mag)", 'search_params_filter_alt_types': "🔭 Filtre : Alt {}-{}°, Types : {}",
        'search_params_filter_size': "📐 Filtre : Taille {:.1f} - {:.1f} arcmin", 'search_params_filter_direction': "🧭 Filtre : Direction à l'apogée : {}", 'search_params_types_all': "Tous",
        'search_params_direction_all': "Toutes", 'spinner_searching': "Calcul de la fenêtre & recherche d'objets...", 'spinner_geocoding': "Recherche de l'emplacement...",
        'window_info_template': "Fenêtre d'observation : {} à {} UTC (Crépuscule Astronomique)", 'window_already_passed': "La fenêtre nocturne calculée pour 'Maintenant' est déjà passée. Calcul pour la nuit suivante.",
        'error_no_window': "Aucune fenêtre de noirceur astronomique valide trouvée pour la date et l'emplacement sélectionnés.", 'error_polar_night': "La noirceur astronomique dure >24h (Nuit polaire ?). Fenêtre de secours utilisée.",
        'error_polar_day': "Aucune noirceur astronomique ne se produit (Jour polaire ?). Fenêtre de secours utilisée.", 'success_objects_found': "{} objets correspondants trouvés.",
        'info_showing_list_duration': "Affichage de {} objets, triés par durée de visibilité et altitude de culmination :", 'info_showing_list_magnitude': "Affichage de {} objets, triés par luminosité (le plus brillant en premier) :",
        'error_search_unexpected': "Une erreur inattendue s'est produite lors de la recherche :", 'results_list_header': "Liste des résultats",
        'results_export_name': "Nom", 'results_export_type': "Type", 'results_export_constellation': "Constellation", 'results_export_mag': "Magnitude", 'results_export_size': "Taille (arcmin)",
        'results_export_ra': "AD", 'results_export_dec': "Dec", 'results_export_max_alt': "Altitude Max (°)", 'results_export_az_at_max': "Azimut à l'apogée (°)", 'results_export_direction_at_max': "Direction à l'apogée",
        'results_export_time_max_utc': "Heure à l'apogée (UTC)", 'results_export_time_max_local': "Heure à l'apogée (Fuseau local)", 'results_export_cont_duration': "Durée cont. max (h)",
        # === KORREKTUR HIER ===
        'results_expander_title': '{} ({}) - Mag : {}', # Attend maintenant une chaîne pour Mag
        # =======================
        'google_link_text': "Google", 'simbad_link_text': "SIMBAD", 'results_coords_header': "**Détails :**", 'results_constellation_label': "Constellation :",
        'results_size_label': "Taille (axe majeur) :", 'results_size_value': "{:.1f} arcmin", 'results_max_alt_header': "**Altitude Max. :**", 'results_azimuth_label': "(Azimut : {:.1f}°{})",
        'results_direction_label': ", Direction : {}", 'results_best_time_header': "**Meilleure heure (Fuseau local) :**", 'results_cont_duration_header': "**Durée cont. max :**", 'results_duration_value': "{:.1f} heures",
        'graph_type_label': "Type de graphique (pour tous) :", 'graph_type_sky_path': "Trajectoire céleste (Az/Alt)", 'graph_type_alt_time': "Courbe d'altitude (Alt/Temps)", 'results_graph_button': "📈 Afficher le graphique",
        'results_spinner_plotting': "Création du graphique...", 'results_graph_error': "Erreur de graphique : {}", 'results_graph_not_created': "Le graphique n'a pas pu être créé.", 'results_close_graph_button': "Fermer le graphique",
        'results_save_csv_button': "💾 Enregistrer la liste en CSV", 'results_csv_filename': "liste_observation_dso_{}.csv", 'results_csv_export_error': "Erreur d'exportation CSV : {}",
        'warning_no_objects_found': "Aucun objet trouvé correspondant à tous les critères pour la fenêtre d'observation calculée.", 'info_initial_prompt': "Bienvenue ! Veuillez **saisir les coordonnées** ou **rechercher un lieu** pour activer la recherche d'objets.",
        'graph_altitude_label': "Altitude (°)", 'graph_azimuth_label': "Azimut (°)", 'graph_min_altitude_label': "Altitude minimale ({:.0f}°)", 'graph_max_altitude_label': "Altitude maximale ({:.0f}°)",
        'graph_title_sky_path': "Trajectoire céleste pour {}", 'graph_title_alt_time': "Courbe d'altitude pour {}", 'graph_ylabel': "Altitude (°)", 'custom_target_expander': "Tracer une cible personnalisée",
        'custom_target_ra_label': "Ascension droite (AD) :", 'custom_target_dec_label': "Déclinaison (Dec) :", 'custom_target_name_label': "Nom de la cible (Optionnel) :",
        'custom_target_ra_placeholder': "p.ex. 10:45:03.6 ou 161.265", 'custom_target_dec_placeholder': "p.ex. -16:42:58 ou -16.716", 'custom_target_button': "Créer un graphique personnalisé",
        'custom_target_error_coords': "Format AD/Dec invalide. Utilisez HH:MM:SS.s / DD:MM:SS ou degrés décimaux.", 'custom_target_error_window': "Impossible de créer le graphique. Assurez-vous que l'emplacement et la fenêtre temporelle sont valides (essayez d'abord de cliquer sur 'Trouver les objets observables').",
        'error_processing_object': "Erreur lors du traitement de {}: {}", 'window_calc_error': "Erreur lors du calcul de la fenêtre d'observation : {}\n{}", 'window_fallback_info': "\nFenêtre de secours utilisée : {} à {} UTC",
        'error_loading_catalog': "Erreur lors du chargement du fichier catalogue : {}", 'info_catalog_loaded': "Catalogue chargé : {} objets.", 'warning_catalog_empty': "Fichier catalogue chargé, mais aucun objet correspondant trouvé après filtrage.",
        'donation_text': "Vous aimez l'application DSO Finder ? [Soutenez le développement sur Ko-fi ☕](https://ko-fi.com/advanceddsofinder)", # DSO Finder Donation
        'bug_report_button': "🐞 Signaler un bug", 'bug_report_body': "\n\n(Veuillez décrire le bug et les étapes pour le reproduire)",

        # === Redshift Calculator Keys ===
        'redshift_calculator_title': "Calculateur de Décalage Rouge", # Added
        'redshift_z_tooltip': "Entrez le décalage cosmologique vers le rouge (négatif pour le décalage vers le bleu).", # Added
        "lang_select": "Choisir la langue", # RC Key
        "input_params": "Paramètres d'entrée", # RC Key
        "redshift_z": "Décalage vers le rouge (z)", # RC Key
        "cosmo_params": "Paramètres Cosmologiques", # RC Key
        "hubble_h0": "Constante de Hubble (H₀) [km/s/Mpc]", # RC Key
        "omega_m": "Densité de matière (Ωm)", # RC Key
        "omega_lambda": "Densité d'énergie noire (ΩΛ)", # RC Key
        "flat_universe_warning": "Ωm + ΩΛ ≉ 1. Les calculs supposent un univers plat (Ωk=0).", # RC Key
        "results_for": "Résultats pour z = {z:.5f}", # RC Key
        "error_invalid_input": "Entrée invalide. Veuillez utiliser des chiffres.", # RC Key
        "error_h0_positive": "La constante de Hubble doit être positive.", # RC Key
        "error_omega_negative": "Les paramètres Omega ne peuvent pas être négatifs.", # RC Key
        "warn_blueshift": "Avertissement : Décalage vers le rouge négatif (Blueshift). Les distances cosmologiques sont 0 ou non directement applicables ici.", # RC Key
        "error_dep_scipy": "Dépendance 'scipy' introuvable. Veuillez l'installer.", # RC Key
        "error_calc_failed": "Le calcul a échoué : {e}", # RC Key
        "warn_integration_accuracy": "Avertissement : La précision relative de l'intégration pourrait ne pas être atteinte (Erreur : DC={err_dc:.2e}, LT={err_lt:.2e}).", # RC Key
        "lookback_time": "Temps de regard en arrière", # RC Key
        "cosmo_distances": "Distances Cosmologiques", # RC Key
        "comoving_distance_title": "**Distance comobile :**", # RC Key
        "luminosity_distance_title": "**Distance de luminosité :**", # RC Key
        "angular_diameter_distance_title": "**Distance de diamètre angulaire :**", # RC Key
        "unit_Gyr": "Ga (Milliards d'années)", # RC Key
        "unit_Mpc": "Mpc", # RC Key
        "unit_Gly": "Gal (Milliards d'années-lumière)", # RC Key
        "unit_km": "km", # RC Key
        "unit_km_sci": "km (sci.)", # RC Key
        "unit_km_full": "km (complet)", # RC Key
        "unit_LJ": "al", # RC Key
        "unit_AE": "UA", # RC Key
        "unit_Ls": "sl", # RC Key
        "calculation_note": "Calcul basé sur le modèle ΛCDM plat, négligeant la densité de rayonnement.", # RC Key
        "rc_donate_text": "Vous aimez ce calculateur ? Soutenez son développement avec un petit don !", # Added (RC Key)
        "rc_donate_button": "Faire un don via Ko-fi", # Added (RC Key)
        "bug_report": "Trouvé un bug ?", # RC Key
        #"bug_report_button": "Signaler un problème", # Using DSO Finder version
        "glossary": "Glossaire", # RC Key
        "example_lookback_recent": "Récemment (en termes cosmologiques).", # RC Key
        "example_lookback_humans": "Évolution des humains modernes.", # RC Key
        "example_lookback_dinos": "Ère des dinosaures.", # RC Key
        "example_lookback_multicellular": "Apparition de la vie multicellulaire complexe.", # RC Key
        "example_lookback_earth": "Formation de la Terre et du Système Solaire.", # RC Key
        "example_lookback_early_univ": "Univers primordial, formation des premières étoiles/galaxies.", # RC Key
        "example_comoving_local": "Au sein de notre Groupe Local de galaxies.", # RC Key
        "example_comoving_virgo": "Distance de l'amas de la Vierge.", # RC Key
        "example_comoving_coma": "Distance de l'amas de Coma.", # RC Key
        "example_comoving_lss": "Échelle des superamas et filaments.", # RC Key
        "example_comoving_quasars": "Distance des quasars lointains.", # RC Key
        "example_comoving_cmb": "Distance du 'bord' de l'univers observable (FDC).", # RC Key
        "explanation_luminosity": "Pertinent pour la luminosité : les objets apparaissent aussi brillants que prévu à cette distance (important pour les chandelles standard comme les supernovae).", # RC Key
        "explanation_angular": "Pertinent pour la taille : les objets ont la taille apparente attendue à cette distance (important pour les règles standard comme les BAO).", # RC Key
    },
}

DEFAULT_LANG = 'de' # Standardmäßig Deutsch

def get_translation(lang: str) -> dict:
    """
    Gibt das Übersetzungs-Dictionary für die angegebene Sprache zurück.
    Fällt auf die Standardsprache zurück, wenn die angegebene Sprache nicht existiert.

    Args:
        lang (str): Der Sprachcode (z.B. 'de', 'en', 'fr').

    Returns:
        dict: Das Dictionary mit den Übersetzungen für die gewählte Sprache.
    """
    # Stelle sicher, dass der Schlüssel existiert, bevor darauf zugegriffen wird.
    # Gib das Dictionary für die angeforderte Sprache zurück oder das für die Standardsprache.
    # Achte darauf, dass die Schlüssel im translations-Dict Kleinbuchstaben sind ('de', 'en', 'fr').
    lang_lower = lang.lower() # Sicherstellen, dass der angeforderte Key klein ist
    return translations.get(lang_lower, translations[DEFAULT_LANG])