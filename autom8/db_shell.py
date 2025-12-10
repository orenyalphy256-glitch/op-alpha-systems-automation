"""
db_shell.py - Interactive database exploration
Run: python -m autom8.db_shell
"""

from autom8.models import (
    get_session,
    list_contacts,
    search_contacts,
    create_contact,
    delete_contact,
)


def main():
    session = get_session()

    print("=" * 60)
    print("AUTOM8 DATABASE SHELL")
    print("=" * 60)

    while True:
        print("\nCommands:")
        print(" list    - List all contacts")
        print(" search  - Search contacts by name")
        print(" add - Add new contact")
        print(" delete  - Delete contact by ID")
        print(" quit    - Exit shell")

        cmd = input("\nEnter command: ").strip().lower()

        if cmd == "quit":
            print("Goodbye!")
            break

        elif cmd == "list":
            contacts = list_contacts(session)
            print(f"\nTotal contacts: {len(contacts)}")
            for contact in contacts:
                print(f" [{contact.id}] {contact.name} - {contact.phone}")

        elif cmd == "search":
            query = input("Search term: ").strip()
            results = search_contacts(session, query)
            print(f"\nFound {len(results)} results:")
            for contact in results:
                print(f" [{contact.id}] {contact.name} - {contact.phone}")

        elif cmd == "add":
            name = input("Name: ").strip()
            phone = input("Phone: ").strip()
            email = input("Email (optional): ").strip() or None
            try:
                contact = create_contact(session, name, phone, email)
                print(f"Created contact ID {contact.id}")
            except Exception as e:
                print(f"Error: {e}")
                session.rollback()

        elif cmd == "delete":
            try:
                contact_id = int(input("Contact ID: ").strip())
                if delete_contact(session, contact_id):
                    print(f"Deleted contact ID {contact_id}")
                else:
                    print(f"Contact ID {contact_id} not found")
            except ValueError:
                print("Invalid ID")

        else:
            print("Unknown command")

    session.close()


if __name__ == "__main__":
    main()
