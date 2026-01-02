# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

seed_data.py - Populate database with test data
"""

from autom8.models import create_contact, get_session


def main():
    session = get_session()

    try:
        # Sample contacts
        contacts_data = [
            ("Admin User", "0712345678", "orenyalphy256@gmail.com"),
            ("John Kamau", "0723456789", "john.kamau@email.com"),
            ("Mary Wanjiku", "0734567890", None),
            ("Peter Ochieng", "0745678901", "peter.o@email.com"),
            ("Grace Akinyi", "07567890012", "grace.akinyi@email.com"),
        ]

        print("Creating test contacts...")
        for name, phone, email in contacts_data:
            try:
                contact = create_contact(session, name, phone, email)
                print(f"Created: {contact.name}")
            except Exception as e:
                print(f" Skipped {name}: {e}")
                session.rollback()

        print("\nDatabase seeded successfully!")

    finally:
        session.close()


if __name__ == "__main__":
    main()
