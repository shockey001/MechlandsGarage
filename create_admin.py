"""
One-time script to create the first admin account.
Usage:
    python create_admin.py
Edit the three variables below, then run.
"""

from models import init_db, create_user, count_users
import getpass

# ===== EDIT THESE =====
ADMIN_EMAIL = "gachoki@mechlandsgarage.co.ke"
ADMIN_NAME = "Gachoki Ndwiga"
# ======================

def main():
    init_db()

    existing = count_users()
    if existing > 0:
        print(f"⚠️  There are already {existing} user(s) in the database.")
        answer = input("Create another admin anyway? (yes/no): ").strip().lower()
        if answer != "yes":
            print("Cancelled.")
            return

    password = getpass.getpass("Enter admin password (min 8 characters): ")
    if len(password) < 12:
        print("❌ Password must be at least 12 characters.")
        return

    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("❌ Passwords do not match.")
        return
    if len(password.encode("utf-8")) > 72:
        print("ERROR: Password exceeds bcrypt's 72-byte limit.")
        return

    user_id = create_user(
        email=ADMIN_EMAIL,
        password=password,
        full_name=ADMIN_NAME,
        role='admin'
    )

    if user_id:
        print(f"✅ Admin account created successfully.")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Name:  {ADMIN_NAME}")
        print(f"   ID:    {user_id}")
    else:
        print("❌ Failed — that email is already registered.")


if __name__ == "__main__":
    main()
