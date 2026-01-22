# HopOn - Horizon Europe Project Finder

**Live Application:** [https://hop-on-companion.streamlit.app/](https://hop-on-companion.streamlit.app/)

**HopOn** is a specialized Streamlit dashboard designed to identify "Hop-on" opportunities within Horizon Europe projects, which allow entities from Widening countries to join specific ongoing research consortiums.

## Architecture Overview

The application follows a simple, functional structure suitable for Streamlit development:

* `app.py`: The main entry point. Handles **Authentication** and routing.
* `components/`: Modular UI components (`sidebar.py`, `project_list.py`, `admin.py`, `profile.py`).
* `utils/`: Backend logic:
  * `data_loader.py`: Efficient Parquet/CSV hybrid data loading.
  * `db.py` & `models.py`: **SQLAlchemy ORM** layer for database interactions.
  * `ai.py`: Interface for GenAI features.
* `migrations/`: **Alembic** database migration scripts.
* `data/`:
  * `raw/` & `processed/`: Project data (CSV/Parquet).

For more details, see:

* [**Tech Stack**](./readmes/tech_stack.md)
* [**Data Pipeline**](./readmes/pipeline.md)
* [**AI Engine & Intelligence**](./readmes/ai_engine.md) 🧠
* [**Performance & Optimization**](./readmes/performance.md) ⚡
* [**Security Architecture**](./readmes/security.md) 🛡️

## Developer Setup

Follow these steps to set up the project locally.

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/vasilistsavalias/hop-on-companion.git
cd hop-on-companion

# Create a virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Create a virtual environment (Mac/Linux)
# python3 -m venv venv
# source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Configuration

You need a PostgreSQL database. You can run one locally via Docker or use a cloud provider.

**Option A: Docker (Quickest)**
```bash
docker run --name hopon-db -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_DB=hopon -p 5433:5432 -d postgres
```

**Configuration:**
Create a `.env` file in the root directory:

```env
# Database Connection
DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5433/hopon

# Optional: AI API Keys (for Summaries/Search)
OPENROUTER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

### 4. Initialize Database

Run the migrations to create the database schema:

```bash
alembic upgrade head
```

### 5. Create Admin User

The application requires an initial admin user. Run the seeding script:

```bash
# Promotes 'Vasilis' (default seed) or a user of your choice to Admin
python -m scripts.promote_admin
```

*Alternatively, create a user manually:*
```bash
python scripts/manage_users.py add admin_user secure_password
```

### 6. Run the Application

Start the Streamlit dashboard:

```bash
python run.py
```
*Access the app at `http://localhost:8501`*
