import os
import sys

# Add root to path
sys.path.append(os.getcwd())

from utils.db import init_db

def verify():
    db_path = 'user_prefs.db'
    if os.path.exists(db_path):
        print(f"Existing {db_path} found.")
    
    print("Initializing DB...")
    init_db(db_path)
    
    if os.path.exists(db_path):
        print(f"SUCCESS: Database {db_path} verified.")
    else:
        print(f"FAILURE: Database {db_path} not found.")

if __name__ == "__main__":
    verify()
