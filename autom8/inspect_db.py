"""
inspect_db.py - Display database statistics and info
"""

from autom8.models import Contact, TaskLog, engine, get_session


def main():
    session = get_session()

    print("\n" + "=" * 60)
    print("DATABASE INSPECTION Location:")
    print("=" * 60)

    # Database location
    print("\nDatabase Location:")
    print(f"    {engine.url}")

    # Table statistics
    print("\nTable Statistics:")

    # Contacts
    contact_count = session.query(Contact).count()
    print("\n  Contacts Table:")
    print(f"    - Total records: {contact_count}")

    if contact_count > 0:
        oldest = session.query(Contact).order_by(Contact.created_at).first()
        newest = session.query(Contact).order_by(Contact.created_at.desc()).first()
        print(f"    - Oldest: {oldest.name} ({oldest.created_at.date()})")
        print(f"    - Newest: {newest.name} ({newest.created_at.date()})")

    # Task Logs
    tasklog_count = session.query(TaskLog).count()
    print("\n  TaskLog Table:")
    print(f"    - Total records: {tasklog_count}")

    if tasklog_count > 0:
        completed = session.query(TaskLog).filter(TaskLog.status == "failed").count()
        failed = session.query(TaskLog).filter(TaskLog.status == "failed").count()
        print(f"    - Completed: {completed}")
        print(f"    - Failed: {failed}")

    # Sample records
    print("\nSample Contacts (first 3):")
    contacts = session.query(Contact).limit(3).all()
    for c in contacts:
        print(f"    [{c.id}] {c.name} - {c.phone}")

    print("\n" + "=" * 60)

    session.close()


if __name__ == "__main__":
    main()
