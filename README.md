# Advanced DSO Finder 🔭

An interactive web tool for amateur astronomers to plan Deep Sky observations, originally inspired by the Vespera Pro telescope but generally useful.

This application, built with Streamlit, helps find Deep Sky Objects (DSOs) observable from a specific location at a chosen time, considering sky quality and other factors. It utilizes an external catalog file (e.g., from OpenNGC) for its object data.

---

## ✨ Key Features

* **External Catalog:** Uses data loaded from a local CSV file (e.g., `ongc.csv`) containing object information (like OpenNGC).
* **Location Selection:** Default location (Schötz, Switzerland) or manual input of longitude, latitude, and altitude.
* **Time & Timezone Selection:**
    * Plan for the upcoming night (based on current time) or select any specific date.
    * Select your local timezone for accurate display of observation times.
* **Brightness Filter:**
    * Automatically based on the Bortle scale (1-9).
    * Or manual input of a magnitude range (Min/Max).
* **Minimum Altitude:** Adjustable minimum height above the horizon that objects must reach.
* **Object Type Filter:** Selection of specific DSO types (e.g., Galaxy, Nebula, Star Cluster) via multiselect.
* **Peak Direction Filter:** Filter results to show only objects peaking in a specific cardinal direction (N, NE, E, SE, S, SW, W, NW) or "All".
* **Moon Phase Display & Warning:** Shows the current moon illumination and warns (in red) if an adjustable threshold is exceeded.
* **Result Options:**
    * Adjustable maximum number of objects to display.
    * Choice of sorting results by:
        * **Visibility Duration & Altitude** (longest duration first, then highest peak altitude).
        * **Brightness** (brightest magnitude first).
* **Detail View:** Expandable detailed information for each object (coordinates, max altitude, azimuth, peak direction, visible duration, best observation time in selected timezone).
* **Altitude Plot:** Option to display an altitude graph over the night for each result object (requires Matplotlib), respecting the selected timezone. Plotting is cached for better performance.
* **CSV Export:** Download the results list (including duration and direction) as a CSV file (semicolon-separated).

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
    * Download a suitable catalog file (e.g., from the [OpenNGC](https://github.com/mattiaverga/OpenNGC) project). Ensure it contains columns like `Name`, `Type`, `RA`, `Dec`, and a magnitude column (e.g., `B-Mag` or `Mag`).
    * Place the downloaded CSV file (e.g., `ongc.csv`) **in the main directory** of the cloned repository, alongside the Python script.
    * **Verify/Adjust Code:** Make sure the `CATALOG_FILENAME` variable in the Python script matches the name of your downloaded file. Check the `load_ongc_data` function to ensure the `sep` argument in `pd.read_csv` matches your file's delimiter (likely `;`) and the `mag_col` variable matches the magnitude column name in your file.

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

5.  **Start Streamlit App:**
    ```bash
    # Replace Advanced_DSO_Finder.py with the actual name of your Python script if different
    streamlit run Advanced_DSO_Finder.py
    ```

The app should now open in your web browser.

---

## 🌐 Live Version

A live version of this app can be found here: `https://advanced-dso-finder-22.streamlit.app`

---

## 📚 Dependencies

The main libraries used by this application:

* Streamlit
* Astropy
* Astroplan
* NumPy
* Pandas
* Matplotlib
* Pytz (for timezone handling)

The exact versions are listed in the `requirements.txt` file.

---

## License

No license specified.

---

## Contact

Email: debrun2005@gmail.com

---

## Support

If you find this project helpful, consider supporting me via PayPal: https://www.paypal.com/ncp/payment/3NW2DLWYMSSJ4
Thank you!
