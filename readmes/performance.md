# Performance & Optimization Decisions

This document tracks the architectural decisions made to ensure HopOn remains performant as the dataset and feature set grow.

## 1. AI Model & Embeddings

**Problem:** Generating embeddings for thousands of projects using BERT (`all-MiniLM-L6-v2`) is computationally expensive and slow ($O(N)$), causing long startup times.

**Solution:**

* **Global Resource Caching:** The `SentenceTransformer` model (~90MB) is loaded **once per server instance** using Streamlit's `@st.cache_resource`. This prevents memory bloat from multiple user sessions.
* **Persistent Embeddings:** Calculated embeddings are serialised to disk (`data/processed/embeddings.pkl`).
  * **Startup:** The app attempts to load this file first.
  * **Invalidation:** If the source data changes (IDs don't match), the app automatically re-computes and saves new embeddings.

## 2. Data Loading Strategy (CSV + Parquet)

**Problem:** Parsing large CSV files with Pandas is slow, but the primary data source remains CSV files (`projects.csv`, `orgs.csv`).

**Solution: Cache-Aside Pattern**
We implemented a hybrid approach that prioritizes speed without breaking the existing CSV workflow:

1. **Check:** The app checks if a `.parquet` version of the data exists.
2. **Validate:** It compares the file modification timestamps.
    * If `source.csv` is **newer** than `cache.parquet` (or cache is missing), the app reads the CSV (slow path) and **automatically saves** a new Parquet file.
    * If `cache.parquet` is fresh, the app reads the Parquet file (fast path).
3. **Result:** Supervisors can continue updating CSVs as normal. The app "upgrades" itself to high-speed binary loading automatically on the first run after an update.

## 3. Rendering & UI Strategy

**Problem:** Re-calculating aggregations and rendering complex charts (especially the Plotly Choropleth map) on every filter interaction caused UI lag.

**Solution:**

* **Component Caching:** Chart generation functions (in `components/charts.py`) are decorated with `@st.cache_data`. They only re-run if the input DataFrame (filtered data) changes.
* **Lazy Loading:** Expensive UI sections like the "AI One-Pager" are only generated on user request (button click), not pre-calculated.
