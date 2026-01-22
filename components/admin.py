import streamlit as st
from utils.db import create_user, delete_user, update_user, get_db, User

def render_admin_panel(current_user_id):
    """
    Renders the User Management interface for logged-in users.
    """
    st.header("👥 User Management (Admin Console)")
    st.info("Manage application access and user roles.")

    tab_list, tab_add = st.tabs(["Manage Users", "Add New User"])

    # --- TAB 1: MANAGE USERS ---
    with tab_list:
        with get_db() as db:
            users = db.query(User).all()
            # Convert to plain dicts for dataframe
            data = [{
                'ID': u.id, 
                'Username': u.username, 
                'Role': u.role,
                'Created At': u.created_at
            } for u in users]
        
        if data:
            st.dataframe(data, use_container_width=True, hide_index=True)
            
            st.divider()
            st.subheader("Edit User Role & Access")
            
            user_to_edit = st.selectbox("Select User to Edit/Delete", options=users, format_func=lambda x: f"{x.username} ({x.role})")
            
            if user_to_edit:
                col1, col2 = st.columns(2)
                
                with col1:
                    with st.form("edit_role_form"):
                        st.write(f"**Edit Role for {user_to_edit.username}**")
                        new_role = st.selectbox("Role", ["user", "admin"], index=0 if user_to_edit.role == 'user' else 1)
                        if st.form_submit_button("Update Role"):
                            if user_to_edit.id == current_user_id and new_role != 'admin':
                                st.error("You cannot demote yourself.")
                            else:
                                if update_user(user_to_edit.id, role=new_role):
                                    st.success(f"Updated {user_to_edit.username} to {new_role}")
                                    st.rerun()
                                else:
                                    st.error("Update failed.")
                
                with col2:
                    st.write(f"**Danger Zone**")
                    if user_to_edit.id == current_user_id:
                        st.warning("⚠️ You cannot delete yourself.")
                    else:
                        if st.button("🗑️ Delete User", type="primary"):
                            if delete_user(user_to_edit.id):
                                st.success(f"User {user_to_edit.username} deleted.")
                                st.rerun()
                            else:
                                st.error("Failed to delete user.")

    # --- TAB 2: ADD USER ---
    with tab_add:
        st.subheader("Create New Account")
        with st.form("create_user_form"):
            new_username = st.text_input("Username*")
            new_password = st.text_input("Password*", type="password")
            new_role = st.selectbox("Initial Role", ["user", "admin"])
            submitted = st.form_submit_button("Create User")
            
            if submitted:
                if new_username and new_password:
                    uid = create_user(new_username, new_password, name=new_username, email=None, role=new_role)
                    if uid:
                        st.success(f"User '{new_username}' created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create user.")
                else:
                    st.warning("Username and Password are required.")
