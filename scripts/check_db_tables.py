import os
import sys
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found!")
    sys.exit(1)

print(f"Checking DB Host: {db_url.split('@')[1].split('/')[0] if '@' in db_url else 'Unknown'}")

try:
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables found:", tables)
    
    if 'users' in tables:
        print("✅ 'users' table exists.")
    else:
        print("❌ 'users' table MISSING!")
except Exception as e:
    print(f"Error connecting: {e}")
