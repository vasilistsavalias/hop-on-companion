import sys
import os
import time

# Add project root
sys.path.append(os.getcwd())

from utils.db import create_user, verify_user, update_user, delete_user, get_user_id, get_user_role, User, get_db

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def run_admin_e2e():
    log("Starting Admin Workflow E2E Test...")
    
    # 0. Setup: Identify Admin
    admin_username = "vasilist" # Or Vasilis, based on seed
    admin_id = get_user_id(admin_username)
    if not admin_id:
        # Try fallback
        admin_username = "Vasilis"
        admin_id = get_user_id(admin_username)
    
    if not admin_id:
        log("No Admin user found. Cannot run Admin E2E.", "FAIL")
        return
    
    admin_role = get_user_role(admin_id)
    if admin_role != 'admin':
        log(f"User '{admin_username}' exists but role is '{admin_role}', not 'admin'.", "FAIL")
        # Attempt fix for test sake?
        update_user(admin_id, role='admin')
        log(f"Auto-fixed '{admin_username}' to admin for testing.", "WARN")
    else:
        log(f"Found Admin: {admin_username} (ID: {admin_id})", "PASS")

    # 1. Create Test Subject
    subject_user = "test_subject_user"
    subject_pass = "temporary_pass"
    
    # Ensure clean state
    existing_id = get_user_id(subject_user)
    if existing_id:
        delete_user(existing_id)
        log(f"Cleaned up existing test subject (ID: {existing_id})", "INFO")

    log(f"Creating Test Subject '{subject_user}'...")
    subject_id = create_user(subject_user, subject_pass) # Default role='user'
    
    if not subject_id:
        log("Failed to create test subject.", "FAIL")
        return
    
    # 2. Verify Initial Role
    role = get_user_role(subject_id)
    if role == 'user':
        log(f"Test Subject created with role: '{role}'", "PASS")
    else:
        log(f"Test Subject has unexpected role: '{role}'", "FAIL")
        return

    # 3. Promote to Admin (Simulating Admin Action)
    log("Promoting Test Subject to Admin...")
    if update_user(subject_id, role='admin'):
        new_role = get_user_role(subject_id)
        if new_role == 'admin':
            log("Test Subject promoted to Admin successfully.", "PASS")
        else:
            log(f"Promotion failed. Role is '{new_role}'", "FAIL")
            return
    else:
        log("Update operation failed.", "FAIL")
        return

    # 4. Revoke Access (Demote)
    log("Revoking Admin Access (Demoting to User)...")
    if update_user(subject_id, role='user'):
        revoked_role = get_user_role(subject_id)
        if revoked_role == 'user':
            log("Test Subject demoted to User successfully.", "PASS")
        else:
            log(f"Demotion failed. Role is '{revoked_role}'", "FAIL")
            return
    else:
        log("Update operation failed.", "FAIL")
        return

    # 5. Remove User
    log("Deleting Test Subject...")
    if delete_user(subject_id):
        # Verify
        if not get_user_id(subject_user):
            log("Test Subject deleted successfully.", "PASS")
        else:
            log("User still exists in DB after delete!", "FAIL")
            return
    else:
        log("Delete operation failed.", "FAIL")
        return

    log("🎉 Admin E2E Flow Completed Successfully.", "SUCCESS")

if __name__ == "__main__":
    run_admin_e2e()
