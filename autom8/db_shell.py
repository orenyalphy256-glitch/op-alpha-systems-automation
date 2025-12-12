"""
db_shell.py - Interactive database exploration
Run: python -m autom8.db_shell
"""

from autom8.models import (
    create_contact,
    delete_contact,
    get_session,
    list_contacts,
    search_contacts,
)


def _list_contacts(session):
    contacts = list_contacts(session)
    print(f"\nTotal contacts: {len(contacts)}")
    for contact in contacts:
        print(f" [{contact.id}] {contact.name} - {contact.phone}")


def _search_contacts(session):
    query = input("Search term: ").strip()
    results = search_contacts(session, query)
    print(f"\nFound {len(results)} results:")
    for contact in results:
        print(f" [{contact.id}] {contact.name} - {contact.phone}")


def _add_contact(session):
    name = input("Name: ").strip()
    phone = input("Phone: ").strip()
    email = input("Email (optional): ").strip() or None
    try:
        contact = create_contact(session, name, phone, email)
        print(f"Created contact ID {contact.id}")
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()


def _delete_contact(session):
    try:
        contact_id = int(input("Contact ID: ").strip())
        if delete_contact(session, contact_id):
            print(f"Deleted contact ID {contact_id}")
        else:
            print(f"Contact ID {contact_id} not found")
    except ValueError:
        print("Invalid ID")


def _print_menu():
    print("\nCommands:")
    print(" list    - List all contacts")
    print(" search  - Search contacts by name")
    print(" add     - Add new contact")
    print(" delete  - Delete contact by ID")
    print(" quit    - Exit shell")


def main():
    session = get_session()

    print("=" * 60)
    print("AUTOM8 DATABASE SHELL")
    print("=" * 60)

    commands = {
        "list": _list_contacts,
        "search": _search_contacts,
        "add": _add_contact,
        "delete": _delete_contact,
    }

    try:
        while True:
            _print_menu()
            cmd = input("\nEnter command: ").strip().lower()

            if cmd == "quit":
                print("Goodbye!")
                break

            if cmd in commands:
                commands[cmd](session)
            else:
                print("Unknown command")

    finally:
        session.close()


if __name__ == "__main__":
    main()
