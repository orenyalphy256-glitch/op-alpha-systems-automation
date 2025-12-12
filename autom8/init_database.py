"""
init_database.py - Database initialization script
Run once to create tables
"""

from autom8.models import init_db, engine


def main():
    print("Initializing database...")
    init_db()
    print(f"Database ready at: {engine.url}")
    print("\nTables created:")
    print("  - contacts")
    print("  - task_logs")


if __name__ == "__main__":
    main()
