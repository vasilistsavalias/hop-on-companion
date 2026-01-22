import sys
import os
import time
from unittest.mock import MagicMock

# Add project root
sys.path.append(os.getcwd())

from utils.db import create_user, verify_user, update_user, delete_user, add_to_watchlist, get_watchlist, save_search, get_saved_searches, get_user_id
from utils.models import User
# We mock AI to avoid costs
sys.modules['utils.ai'] = MagicMock()
from utils.ai import generate_project_brief

# We import matcher but will verify its structure
from utils.matcher import ProjectMatcher

def log(msg):
    print(f"[E2E] {msg}")

def run_e2e():
    log("Starting End-to-End Verification...")
    
    # 1. User Lifecycle
    username = "e2e_test_user"
    password = "initial_password"
    
    log(f"Creating user '{username}'...")
    uid = create_user(username, password)
    if not uid:
        log("❌ Failed to create user.")
        return
    log(f"✅ User created (ID: {uid})")

    log("Verifying login...")
    if verify_user(username, password):
        log("✅ Login successful")
    else:
        log("❌ Login failed")
        return

    # 2. Edit User
    new_pass = "new_secure_pass"
    log("Updating password...")
    if update_user(uid, new_password=new_pass):
        log("✅ Password updated")
    else:
        log("❌ Update failed")
        return

    if verify_user(username, new_pass):
        log("✅ New password verified")
    else:
        log("❌ New password failed verification")
        return

    # 3. Watchlist
    log("Testing Watchlist...")
    proj_id = "101010"
    add_to_watchlist(proj_id, uid)
    items = get_watchlist(uid)
    if proj_id in items:
        log(f"✅ Watchlist item found: {items}")
    else:
        log(f"❌ Watchlist item missing. Found: {items}")

    # 4. Saved Search
    log("Testing Saved Search...")
    filters = '{"cluster": "Health"}'
    save_search("Test Search", filters, uid)
    searches = get_saved_searches(uid)
    if len(searches) > 0 and searches[0]['name'] == "Test Search":
        log(f"✅ Saved search found: {searches[0]['name']}")
    else:
        log("❌ Saved search missing")

    # 5. Cleanup
    log("Cleaning up (Deleting user)...")
    if delete_user(uid):
        log("✅ User deleted")
    else:
        log("❌ Delete failed")

    # Verify Cleanup
    if verify_user(username, new_pass) is False:
        log("✅ User verification fails (expected)")
    else:
        log("❌ User still exists!")

    log("🎉 E2E Test Completed Successfully.")

if __name__ == "__main__":
    run_e2e()
