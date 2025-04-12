# Advanced DSO Finder 🔭

An interactive web tool for amateur astronomers to plan Deep Sky observations, originally inspired by the Vespera Pro telescope but generally useful.

This application, built with Streamlit, helps find Deep Sky Objects (DSOs) observable from a specific location at a chosen time, considering sky quality and other factors.

---

## ✨ Key Features

* **Location Selection:** Default location (Schötz, Switzerland) or manual input of longitude, latitude, and altitude.
* **Time Selection:** Plan for the upcoming night (based on current time) or select any date.
* **Brightness Filter:**
    * Automatically based on the Bortle scale (1-9).
    * Or manual input of a magnitude range (Min/Max).
* **Minimum Altitude:** Adjustable minimum height above the horizon that objects must reach.
* **Object Type Filter:** Selection of specific DSO types (e.g., Galaxy, Nebula, Star Cluster).
* **Moon Phase Display & Warning:** Shows the current moon illumination and warns (in red) if an adjustable threshold is exceeded.
* **Result Options:**
    * Adjustable number of objects to display.
    * Optional sorting by brightness (brightest first) instead of random selection.
* **Detail View:** Expandable detailed information for each object (coordinates, max altitude, best observation time).
* **Altitude Plot:** Option to display an altitude graph over the night for each result object (requires Matplotlib).
* **CSV Export:** Download the results list as a CSV file.

---

## 🚀 Run App (Locally)

To run the app on your own computer:

1.  **Clone the Repository:**
    ```bash
    # Replace YOUR_USERNAME and YOUR_REPO_NAME with your details
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
    cd YOUR_REPO_NAME
    ```

2.  **Create & Activate Virtual Environment:**
    ```bash
    # Create (only needed once)
    python -m venv .venv

    # Activate (Windows PowerShell)
    .\.venv\Scripts\Activate.ps1

    # Activate (MacOS/Linux Bash)
    source .venv/bin/activate
    ```
    *Note: Use the activation command appropriate for your operating system and shell.*

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure the `requirements.txt` file is up-to-date, see deployment instructions)*

4.  **Start Streamlit App:**
    ```bash
    # Replace YourAppFile.py with the name of your Python script, e.g., dso_app_v14.py
    streamlit run YourAppFile.py
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
