import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from utils.models import Base, User, Watchlist, SavedSearch
from utils.logger import logger
from dotenv import load_dotenv
import bcrypt

load_dotenv()

# Database Setup
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    logger.critical("DATABASE_URL is not set. Please configure it in .env (e.g., postgresql://user:pass@localhost:5432/hopon)")
    # We can't exit here because Streamlit reloads modules, but we can prevent the app from working
    # Ideally, we let SQLAlchemy fail, but a clear error is better.
    # raising Exception would crash the import.
    # Instead, we will log error and let create_engine fail naturally if it's None, or handle it.
    
    # Wait, create_engine(None) raises ArgumentError.
    # I'll set a dummy URL to let the import succeed (so tests might run if mocked) but log error.
    # Actually, enforcing it strictly is better for "Postgres Migration".
    # But for running tests that mock it, we should be careful.
    if "unittest" not in sys.modules:
        raise ValueError("DATABASE_URL environment variable is required.")
    else:
        DB_URL = "sqlite:///:memory:" # Fallback only for unit tests import time

# Create Engine
# Removed sqlite specific connect_args
engine = create_engine(DB_URL)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initializes the database."""
    logger.info(f"Database engine initialized at {DB_URL}")
    try:
        seed_default_admin()
    except Exception as e:
        logger.error(f"Failed to seed admin (Database might not be ready): {e}")

def seed_default_admin():
    with get_db() as db:
        admin = db.query(User).filter(User.username == "Vasilis").first()
        if not admin:
            # Default password: admin
            hashed_pw = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
            new_admin = User(username="Vasilis", name="Admin", password_hash=hashed_pw)
            db.add(new_admin)
            db.commit()
            logger.info("Seeded default admin user 'Vasilis'")

# --- User Management ---
def create_user(username, password, name=None, email=None, role='user'):
    """Creates a new user with a hashed password."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

    with get_db() as db:
        try:
            user = User(username=username, password_hash=hashed, name=name, email=email, role=role)
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {username} (Role: {role})")
            return user.id
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return None

def verify_user(username, password):
    """Verifies a user's credentials."""
    with get_db() as db:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
        
        return bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))

def get_all_users_config():
    with get_db() as db:
        users = db.query(User).all()
        config = {}
        for u in users:
            config[u.username] = {
                'email': u.email,
                'name': u.name or u.username,
                'password': u.password_hash,
                'role': u.role
            }
        return config

def get_user_id(username):
    with get_db() as db:
        user = db.query(User).filter(User.username == username).first()
        return user.id if user else None

def get_user_role(user_id):
    """Returns the role of the given user."""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        return user.role if user else None

def update_user(user_id, new_username=None, new_password=None, role=None):
    """Updates user credentials and role."""
    with get_db() as db:
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            if new_username:
                user.username = new_username
            
            if new_password:
                pwd_bytes = new_password.encode('utf-8')
                salt = bcrypt.gensalt()
                user.password_hash = bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')
            
            if role:
                user.role = role

            db.commit()
            logger.info(f"Updated user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False

def delete_user(user_id):
    """Deletes user and cascades via ORM relationships."""
    with get_db() as db:
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                db.delete(user) # Cascade deletes watchlist/searches defined in Model
                db.commit()
                logger.info(f"Deleted user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False

# --- Watchlist ---
def add_to_watchlist(project_id, user_id):
    with get_db() as db:
        try:
            exists = db.query(Watchlist).filter_by(project_id=str(project_id), user_id=user_id).first()
            if not exists:
                item = Watchlist(project_id=str(project_id), user_id=user_id)
                db.add(item)
                db.commit()
                logger.info(f"User {user_id}: Added {project_id} to watchlist.")
        except Exception as e:
            logger.error(f"Error adding to watchlist: {e}")

def remove_from_watchlist(project_id, user_id):
    with get_db() as db:
        db.query(Watchlist).filter_by(project_id=str(project_id), user_id=user_id).delete()
        db.commit()
        logger.info(f"User {user_id}: Removed {project_id} from watchlist.")

def get_watchlist(user_id):
    with get_db() as db:
        items = db.query(Watchlist).filter(Watchlist.user_id == user_id).all()
        return [item.project_id for item in items]

# --- Saved Searches ---
def save_search(name, filters_json, user_id):
    with get_db() as db:
        try:
            search = SavedSearch(name=name, filters=filters_json, user_id=user_id)
            db.add(search)
            db.commit()
            logger.info(f"User {user_id}: Saved search '{name}'")
        except Exception as e:
            logger.error(f"Error saving search: {e}")

def get_saved_searches(user_id):
    with get_db() as db:
        items = db.query(SavedSearch).filter(SavedSearch.user_id == user_id).order_by(SavedSearch.created_at.desc()).all()
        # Convert to dict for compatibility
        return [{'id': item.id, 'name': item.name, 'filters': item.filters, 'created_at': item.created_at} for item in items]

def delete_search(search_id):
    with get_db() as db:
        try:
            db.query(SavedSearch).filter(SavedSearch.id == search_id).delete()
            db.commit()
            logger.info(f"Deleted search {search_id}")
        except Exception as e:
            logger.error(f"Error deleting search: {e}")
