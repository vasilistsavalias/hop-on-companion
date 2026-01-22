# Tech Stack

This project is built with the following core technologies:

* **Language:** Python 3.10+
* **Web Framework:** [Streamlit](https://streamlit.io/) - For creating the interactive web dashboard.
* **Authentication:** [Streamlit-Authenticator](https://github.com/mkhorasani/Streamlit-Authenticator) - Secure session management and cookie handling.
* **Data Manipulation:** [Pandas](https://pandas.pydata.org/) - For data processing.
* **Data Storage:**
  * **Cache:** Parquet (Compressed Binary) for high-speed data loading.
  * **Source:** CSV (`|` delimited) for compatibility with external workflows.
* **Database (Backend):**
  * **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) - Abstraction layer for database interactions.
  * **Migrations:** [Alembic](https://alembic.sqlalchemy.org/) - Schema version control.
  * **Engine:** **PostgreSQL** (Required). The application is stateless and requires an external Postgres database (e.g., Neon, Supabase, AWS RDS).
* **Logging:** [Loguru](https://loguru.readthedocs.io/en/stable/) - For simple and effective application logging.

## AI & Semantic Search

The application features a semantic search engine capable of understanding the *intent* behind a query.

* **Library:** [sentence-transformers](https://www.sbert.net/) (based on Hugging Face Transformers).
* **Model:** `all-MiniLM-L6-v2`.
  * **Why this choice?** This model offers the best trade-off between speed and performance. It maps sentences to a 384-dimensional dense vector space and runs efficiently on standard CPUs.
* **Mechanism:**
    1. **Vectorization:** We generate "embeddings" (vector representations) for every project by combining its Title, Objective, and Topics.
    2. **Cosine Similarity:** When a user searches, their query is converted into a vector. We calculate the cosine similarity between the query vector and all project vectors.
    3. **Ranking:** Projects are ranked by this similarity score (0 to 1).
