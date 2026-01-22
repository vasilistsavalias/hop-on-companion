# Data Pipeline

The data flows through a simple, two-stage pipeline:

1. **Raw Data Ingestion:**
    * **Source:** Raw data is provided as Excel files (`.xlsx`) from the EU CORDIS database.
    * **Location:** These files are placed in the `data/raw/` directory.
    * **Files:** `project.xlsx`, `organization.xlsx`, `topics.xlsx`, `euroSciVoc.xlsx`.

2. **Processing and Filtering:**
    * **Tool:** The `notebooks/data_viewer.ipynb` Jupyter Notebook is the single processing engine.
    * **Process:** The notebook reads the raw Excel files, merges them, applies the "Hop-on Facility" eligibility filters, and classifies projects into clusters.
    * **Output:** The processed data is saved as two pipe-delimited CSV files (`projects.csv`, `orgs.csv`) in the `data/processed/` directory.

3. **Application Consumption:**
    * The main Streamlit application (`app.py`) only reads from the clean, processed CSV files in `data/processed/`. It does not interact with the raw data.

This separation ensures that the main application is fast and does not have to perform heavy data processing on every run.
