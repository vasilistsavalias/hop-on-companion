import streamlit as st
from utils.db import update_user, get_db, User

def render_profile_page(current_user_id):
    st.header("👤 My Profile")
    
    with get_db() as db:
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            st.error("User not found.")
            return
        
        st.write(f"**Username:** {user.username}")
        st.write(f"**Role:** {user.role}")
        st.write(f"**Member since:** {user.created_at.strftime('%Y-%m-%d')}")
        
        st.divider()
        st.subheader("Update Password")
        
        with st.form("profile_update_form"):
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Update Password"):
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif not new_password:
                    st.warning("Password cannot be empty.")
                else:
                    if update_user(current_user_id, new_password=new_password):
                        st.success("Password updated successfully.")
                    else:
                        st.error("Failed to update password.")