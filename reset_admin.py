
"""
Secure MechlandsGarage administrator password reset.

Usage:
    python reset_admin.py

The password is requested securely and never stored in this file.
"""

import getpass

from models import (
    init_db,
    get_user_by_email,
    create_user,
    get_db,
    bcrypt
)

# Administrator account
ADMIN_EMAIL = "gachoki@mechlandsgarage.co.ke"
ADMIN_NAME = "Gachoki Ndwiga"

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_BYTES = 72


def main():

    print("\n========================================")
    print(" MECHLANDSGARAGE ADMIN PASSWORD RESET")
    print("========================================\n")

    password = getpass.getpass(
        "Enter new administrator password: "
    )

    if len(password) < MIN_PASSWORD_LENGTH:
        print("ERROR: Password must have at least 12 characters.")
        return

    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        print("ERROR: Password exceeds bcrypt's 72-byte limit.")
        return

    confirm = getpass.getpass("Confirm new password: ")

    if password != confirm:
        print("ERROR: Passwords do not match.")
        return

    init_db()

    email = ADMIN_EMAIL.strip().lower()

    existing_user = get_user_by_email(email)

    if existing_user:

        # Use the shared Bcrypt extension from models.py.
        password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        conn = get_db()

        try:
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE users
                SET password_hash = ?, role = 'admin'
                WHERE email = ?
                """,
                (password_hash, email)
            )

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "Expected exactly one administrator account to update."
                )

            conn.commit()

            print("\nSUCCESS: Administrator password reset.")
            print("Administrator:", email)
            print("Role: admin")

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    else:

        user_id = create_user(
            email=email,
            password=password,
            full_name=ADMIN_NAME,
            role="admin"
        )

        if user_id:
            print("\nSUCCESS: New administrator account created.")
            print("Administrator:", email)
            print("User ID:", user_id)
        else:
            print("\nERROR: Administrator account could not be created.")


if __name__ == "__main__":
    main()
