# Security Architecture & Decisions

This document outlines the security measures implemented in HopOn to protect against common vulnerabilities, specifically focusing on AI interactions, data handling, and access control.

## 1. Authentication & Session Management

**Architecture:**

* **Library:** `streamlit-authenticator` handles session cookies and password management.
* **Hashing:** Passwords are hashed using **Bcrypt** before storage.
* **Session Security:**
  * Auth cookies expire after 30 days.
  * The application logic is protected by a strict `authentication_status` check at the entry point (`app.py`).

## 2. AI Safety & Prompt Injection

**Risk:** "Prompt Injection" where malicious instructions hidden in the project data (e.g., in a project description from CORDIS) could override the system prompt and manipulate the AI's output.

**Mitigation:**

* **XML Delimiters:** We use strict XML-style tags (`<project_data>...</project_data>`) to wrap user-provided content. The system prompt is explicitly instructed to *only* process information within these tags.
* **Sanitization:** The `utils/ai.py` module constructs prompts defensively, ensuring that data is treated as context, not instruction.

## 3. Secrets Management & Logging

**Risk:** Leaking API keys (like `OPENROUTER_API_KEY`) or sensitive PII in application logs or error tracebacks.

**Mitigation:**

* **Log Sanitization:** We explicitly removed code that logged raw API response bodies (`response.text`) in error handlers.
* **Environment Variables:** All secrets are managed via `.env` and `python-dotenv`.

## 4. Deployment Security

**Database:**

* **Development:** Uses local SQLite (`user_prefs.db`).
* **Production:** The architecture supports **PostgreSQL** via SQLAlchemy. When deploying to stateless containers (e.g., Streamlit Cloud), you **must** provide a `DATABASE_URL` environment variable pointing to a persistent external database (e.g., Supabase, Neon).

**Admin Access:**

* Registration is **Invite Only**.
* Users can only be created via the CLI script (`scripts/manage_users.py`), preventing unauthorized public sign-ups.
