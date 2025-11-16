"""
seed_data.py - Populate database with test data
"""
from autom8.models import get_session, create_contact
from autom8.core import log

def main():
    session = get_session()

    try:
        # Sample contacts
        contacts_data = [
            ("Alphonce Liguori", "0712345678", "orenyalphy256@gmail.com"),
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

        print(f"\nDatabase seeded successfully!")

    finally:
        session.close()

if __name__ == "__main__":
    main()