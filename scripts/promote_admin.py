from utils.db import get_db, User, logger

def promote_admin():
    target_username = "vasilist"  # The username to promote
    
    with get_db() as db:
        user = db.query(User).filter(User.username == target_username).first()
        if user:
            user.role = "admin"
            db.commit()
            logger.info(f"Successfully promoted '{target_username}' to admin.")
        else:
            # Fallback if specific user doesn't exist, try 'Vasilis'
            user = db.query(User).filter(User.username == "Vasilis").first()
            if user:
                user.role = "admin"
                db.commit()
                logger.info(f"Successfully promoted 'Vasilis' to admin.")
            else:
                logger.warning(f"User '{target_username}' not found. No admin promoted.")

if __name__ == "__main__":
    promote_admin()