<img width="120" alt="Main_Logo_transparent_schatten" src="https://github.com/user-attachments/assets/342ef375-8a81-442e-b993-86ffdf58ca4c" />

# Advanced DSO Finder & Redshift Calculator 🔭🌌

An interactive web tool for amateur astronomers to plan Deep Sky observations and calculate cosmological distances.

This application, built with Streamlit, helps find Deep Sky Objects (DSOs) observable from a specific location at a chosen time, considering various astronomical conditions and user preferences. It utilizes an external catalog file (e.g., from OpenNGC) for its object data and provides graphical representations of object visibility. Additionally, it includes an integrated calculator for cosmological redshift parameters.

---

## 🌐 Live Demo

Access the live application here:

**[https://advanced-dso-finder-22.streamlit.app/](https://advanced-dso-finder-22.streamlit.app/)**

*(Note: Update this link if your app is hosted elsewhere.)*

---

## ✨ Key Features

* **External DSO Catalog:** Uses data loaded from a local CSV file (e.g., `ongc.csv` from OpenNGC) containing object information (Name, Type, RA, Dec, Magnitude).
* **Location Input:**
    * **Search by Name:** Enter a location name (city, observatory, etc.) to automatically fetch coordinates using geocoding (requires internet, uses Nominatim with ArcGIS and Photon as fallbacks).
    * **Manual Entry:** Input precise longitude, latitude, and altitude.
* **Time Selection:**
    * Plan for the upcoming night (based on current time).
    * Select any specific date in the past or future.
* **Automatic Timezone:** Detects and uses the appropriate local timezone based on the provided coordinates (requires `timezonefinder`). Displays the detected timezone in the sidebar.
* **DSO Filters:**
    * **Brightness Filter:**
        * **Bortle Scale:** Filter based on estimated limiting magnitude for Bortle scale values (1-9).
        * **Manual Range:** Define a specific minimum and maximum magnitude.
    * **Altitude Filter:** Set both the **minimum** and **maximum** required altitude (degrees above the horizon) for an object's *peak* to be considered observable.
    * **Object Type Filter:** Select specific DSO types (e.g., Galaxy, Nebula, Cluster) via a multi-select dropdown. An object type glossary is provided for clarity.
    * **Peak Direction Filter:** Optionally filter results to show only objects reaching their maximum altitude in a specific cardinal direction (N, NE, E, SE, S, SW, W, NW) or select "All".
* **Moon Phase Display & Warning:** Shows the current moon illumination percentage for the calculated observation window and provides a visual warning if it exceeds a user-defined threshold.
* **DSO Result Sorting & Limiting:**
    * Limit the maximum number of results displayed.
    * Sort results by:
        * **Visibility Duration & Altitude:** Prioritizes objects visible for the longest continuous duration within the observation window, then by highest peak altitude.
        * **Brightness:** Lists the brightest objects first.
* **Detailed DSO Results:** Each result shows:
    * Name, Type, Magnitude.
    * Full Constellation Name (determined via Astropy).
    * RA/Dec coordinates.
    * Maximum Altitude reached during the observation window, along with Azimuth and Cardinal Direction at that time.
    * Best observation time (time of maximum altitude) in the detected local timezone.
    * Maximum *continuous* duration (in hours) the object is above the minimum altitude during the observation window.
* **Interactive Graphs (DSO & Custom):**
    * **Graph Type Selector:** Choose between Sky Path (Az/Alt) or Altitude/Time graphs globally.
    * **Sky Path Graph (Az/Alt):** Displays the object's path across the sky during the observation window. Points are colored by time progression. Includes Min/Max altitude limit circles.
    * **Altitude/Time Graph:** Displays the object's altitude over time during the observation window. Includes Min/Max altitude limit lines.
    * Graphs are available for each object in the results list and for custom targets.
    * **Dynamic Plot Theme:** Plots adapt to Streamlit's light or dark theme automatically.
* **Custom Target Graph:** Input custom RA/Dec coordinates (and an optional name) to generate a visibility graph for any object, using the current location, time, and filter settings.
* **Integrated Redshift Calculator:**
    * Calculate cosmological distances based on redshift (z) and cosmological parameters (H₀, Ωm, ΩΛ).
    * Displays Lookback Time, Comoving Distance, Luminosity Distance, and Angular Diameter Distance.
    * Provides distances in various units (Mpc, Gly, km, ly, AU, Ls) and includes illustrative examples and explanations for context.
    * Uses the flat ΛCDM model for calculations.
* **CSV Export (DSO):** Download the filtered and sorted DSO results list (including constellation and visibility duration) as a CSV file (semicolon-separated, UTF-8). Uses comma (`,`) as decimal separator for German language, period (`.`) otherwise.
* **Multilingual:** Interface available in English, German, and French.

---

## 🚀 Run App (Locally)

To run the app on your own computer:

1.  **Clone the Repository:**
    ```bash
    # Replace YOUR_USERNAME and YOUR_REPO_NAME with your details
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
    cd YOUR_REPO_NAME
    ```

2.  **Obtain Catalog File:**
    * Download a suitable catalog file (e.g., from the [OpenNGC](https://github.com/mattiaverga/OpenNGC) project). Ensure it's **semicolon-separated (`;`)** and contains columns like `Name`, `Type`, `RA`, `Dec`, and a magnitude column (e.g., `V-Mag`, `B-Mag`, or `Mag`).
    * Place the downloaded CSV file (e.g., `ongc.csv`) **in the main directory** of the cloned repository, alongside the Python script (`localization.py` and your main script file).
    * **Verify/Adjust Code:** Make sure the `CATALOG_FILENAME` variable in the Python script matches the name of your downloaded file. Check the `load_ongc_data` function if needed to ensure the magnitude column name detection (`mag_cols`) matches your file.

3.  **Create & Activate Virtual Environment:**
    ```bash
    # Create (only needed once)
    python -m venv .venv

    # Activate (Windows PowerShell)
    .\.venv\Scripts\Activate.ps1

    # Activate (MacOS/Linux Bash)
    source .venv/bin/activate
    ```
    *Note: Use the activation command appropriate for your operating system and shell.*

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure `requirements.txt` includes: `streamlit`, `astropy`, `astroplan`, `numpy`, `pandas`, `matplotlib`, `pytz`, `geopy`, `timezonefinder`, `scipy`)*

5.  **Start Streamlit App:**
    ```bash
    # Replace Your_Main_Script.py with the actual name of your Python script
    streamlit run Your_Main_Script.py
    ```

The app should now open in your web browser.

---

## 📚 Dependencies

The main libraries used by this application:

* Streamlit
* Astropy
* Astroplan
* NumPy
* Pandas
* Matplotlib
* Pytz (for timezone objects)
* Geopy (for location search)
* TimezoneFinder (for automatic timezone detection)
* SciPy (for integration in Redshift Calculator)

*(See `requirements.txt` for specific versions if available)*

---

## License

No license specified.

---

## Contact

Email: debrun2005@gmail.com

---

## Support

If you find this project helpful, consider supporting me via Ko-fi:

[https://ko-fi.com/advanceddsofinder](https://ko-fi.com/advanceddsofinder)

Thank you!
