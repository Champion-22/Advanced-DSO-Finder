<p align="center">
  <img width="120" alt="Main_Logo_transparent_schatten" src="https://github.com/user-attachments/assets/342ef375-8a81-442e-b993-86ffdf58ca4c" />
</p>

<h1 align="center">Advanced DSO Finder & Redshift Calculator 🔭🌌</h1>

<p align="center">
  An interactive web tool for amateur astronomers to plan Deep Sky observations and calculate cosmological distances.
</p>

This application, built with Streamlit, helps find Deep Sky Objects (DSOs) observable from a specific location at a chosen time, considering various astronomical conditions and user preferences. It utilizes an external catalog file (e.g., from OpenNGC) for its object data, provides graphical representations of object visibility, and includes an integrated calculator for cosmological redshift parameters.

---

## 🌐 Live Demo

Access the live application here:

**➡️ [https://advanced-dso-finder-22.streamlit.app/](https://advanced-dso-finder-22.streamlit.app/)**

*(Note: Update this link if your app is hosted elsewhere.)*

---

## ✨ Key Features

**General & Setup:**
* 📄 **External DSO Catalog:** Uses data loaded from a local CSV file (e.g., `ongc.csv`).
* 🌍 **Multilingual:** Interface available in English, German, and French.
* 🎨 **Dynamic Plot Theme:** Plots adapt to Streamlit's light or dark theme automatically.

**Location & Time:**
* 📍 **Location Input:**
    * *Search by Name:* Automatically fetch coordinates using geocoding (Nominatim, ArcGIS, Photon fallbacks).
    * *Manual Entry:* Input precise longitude, latitude, and altitude.
* ⏱️ **Time Selection:**
    * Plan for the upcoming night.
    * Select any specific date.
* 🗺️ **Automatic Timezone:** Detects and uses the local timezone based on coordinates.

**DSO Finder:**
* 🔭 **DSO Filters:**
    * *Brightness:* Filter by Bortle Scale estimate or a manual magnitude range.
    * *Altitude:* Set minimum and maximum required peak altitude.
    * *Object Type:* Select specific DSO types (Galaxy, Nebula, etc.) with glossary provided.
    * *Peak Direction:* Filter by cardinal direction (N, NE, E, etc.) where the object culminates.
* 🌕 **Moon Phase Display & Warning:** Shows illumination and warns if above a user-set threshold.
* 📊 **DSO Result Sorting & Limiting:**
    * Limit the number of results.
    * Sort by Visibility Duration & Altitude or by Brightness.
* 📋 **Detailed DSO Results:** Shows Name, Type, Mag, Constellation, RA/Dec, Max Altitude (with Az/Dir), Best Local Time, Max Continuous Visibility Duration.
* 💾 **CSV Export (DSO):** Download filtered/sorted results (semicolon-separated UTF-8, locale-aware decimal separator).

**Graphing:**
* 📈 **Interactive Graphs (DSO & Custom):**
    * *Graph Type Selector:* Choose Sky Path (Az/Alt) or Altitude/Time globally.
    * *Sky Path:* Shows path, colored by time, with altitude limits.
    * *Altitude/Time:* Shows altitude over time, with altitude limits.
* 🎯 **Custom Target Graph:** Generate graphs for any RA/Dec coordinate.

**Integrated Redshift Calculator:**
* 🧮 **Cosmological Calculations:** Determine distances based on redshift (z) and cosmological parameters (H₀, Ωm, ΩΛ).
* <0xE2><0x8F><0x9A>️ **Outputs:** Lookback Time, Comoving Distance, Luminosity Distance, Angular Diameter Distance.
* 📏 **Multiple Units:** Provides distances in Mpc, Gly, km, ly, AU, Ls.
* 💡 **Context:** Includes illustrative examples and explanations for the calculated values.
* 📜 **Model:** Uses the flat ΛCDM model.

---

## 🚀 Run App (Locally)

To run the app on your own computer:

1.  **Clone the Repository:** Gitea clone
    ```bash
    # Replace YOUR_USERNAME and YOUR_REPO_NAME with your details
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
    cd YOUR_REPO_NAME
    ```

2.  **Obtain Catalog File:** 💾
    * Download a suitable catalog file (e.g., from [OpenNGC](https://github.com/mattiaverga/OpenNGC)).
    * Ensure it's **semicolon-separated (`;`)** and has required columns (`Name`, `Type`, `RA`, `Dec`, magnitude).
    * Place the CSV (e.g., `ongc.csv`) in the repository's main directory.
    * Verify `CATALOG_FILENAME` in the script matches your file name. Check `load_ongc_data` if needed for magnitude column matching.

3.  **Create & Activate Virtual Environment:** ⚙️
    ```bash
    # Create (only needed once)
    python -m venv .venv

    # Activate (Windows PowerShell)
    .\.venv\Scripts\Activate.ps1

    # Activate (MacOS/Linux Bash)
    source .venv/bin/activate
    ```
    *(Use the command appropriate for your OS/shell)*

4.  **Install Dependencies:** 📦
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure `requirements.txt` includes: `streamlit`, `astropy`, `astroplan`, `numpy`, `pandas`, `matplotlib`, `pytz`, `geopy`, `timezonefinder`, `scipy`)*

5.  **Start Streamlit App:** ▶️
    ```bash
    # Replace Your_Main_Script.py with the actual script name
    streamlit run Your_Main_Script.py
    ```

The app should now open in your web browser.

---

## 📚 Dependencies

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

## 📜 License

No license specified.

---

## 📧 Contact

Email: debrun2005@gmail.com

---

## ❤️ Support

If you find this project helpful, consider supporting me via Ko-fi:

[https://ko-fi.com/advanceddsofinder](https://ko-fi.com/advanceddsofinder)

Thank you!
