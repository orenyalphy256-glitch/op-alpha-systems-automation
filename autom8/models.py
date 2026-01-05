# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

models.py - SQLAlchemy Database Models
Defines: Contact model, database initialization, session management
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, create_engine, event, or_, Index
from sqlalchemy.orm import declarative_base, sessionmaker

from autom8.core import Config, log

# Database Configuration

# Database file path
DB_URL = Config.DATABASE_URL

# Create engine (connection pool)
# Optimized for high concurrency with SQLite
engine = create_engine(
    DB_URL,
    echo=Config.DB_ECHO,
    future=True,
    pool_size=100,
    max_overflow=200,
    pool_timeout=5,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "check_same_thread": False,
        "timeout": 5,  # Increase SQLite wait time for locks
        "isolation_level": None,
    },
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable WAL mode for SQLite to allow concurrent reads and writes."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=64000")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA mmap_size=268435456")
    cursor.close()


# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Base class for all models
Base = declarative_base()


# Model definitions
class Contact(Base):
    __tablename__ = "contacts"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Required fields
    name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=False, unique=True)

    # Optional fields
    email = Column(String(100), nullable=True, index=True)

    # Timestamps (auto-managed)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    __table_args__ = (
        Index('idx_contact_search', 'name', 'email', 'phone'),
    )

    def __repr__(self):
        """String representation for debugging."""
        return f"<Contact(id={self.id}, name='{self.name}', phone='{self.phone}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class TaskLog(Base):
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type = Column(String(50), nullable=False, index=True)
    task_name = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.now, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    result_data = Column(String(500), nullable=True)
    error_message = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<TaskLog(id={self.id}, type='{self.task_type}', status='{self.status}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "task_type": self.task_type,
            "task_name": self.task_name,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result_data": self.result_data,
            "error_message": self.error_message,
        }


# Database Initialization
def init_db():
    log.info(f"Initializing database at {DB_URL}")
    Base.metadata.create_all(bind=engine)
    log.info("Database tables created successfully")


def get_session():
    return SessionLocal()


# CRUD Helper Functions
def create_contact(session, name, phone, email=None):
    contact = Contact(name=name, phone=phone, email=email)
    session.add(contact)
    session.commit()
    session.refresh(contact)
    log.info(f"Created contact: {contact}")
    return contact


def get_contact_by_id(session, contact_id):
    return session.query(Contact).filter(Contact.id == contact_id).first()


def get_contact_by_phone(session, phone):
    return session.query(Contact).filter(Contact.phone == phone).first()


def list_contacts(session, limit=100, offset=0):
    return session.query(Contact).limit(limit).offset(offset).all()


def search_contacts(session, query):
    pattern = f"%{query}%"
    return session.query(Contact).filter(
        or_(
            Contact.name.ilike(pattern), 
            Contact.email.ilike(pattern), 
            Contact.phone.ilike(pattern)
            )
    ).all()


def update_contact(session, contact_id, **kwargs):
    contact = get_contact_by_id(session, contact_id)
    if contact:
        for key, value in kwargs.items():
            if hasattr(contact, key):
                setattr(contact, key, value)
        session.commit()
        session.refresh(contact)
        log.info(f"Updated contact: {contact}")
    return contact


def delete_contact(session, contact_id):
    contact = get_contact_by_id(session, contact_id)
    if contact:
        session.delete(contact)
        session.commit()
        log.info(f"Deleted contact ID {contact_id}")
        return True
    return False


# Modular Exports
__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "Contact",
    "TaskLog",
    "init_db",
    "get_session",
    "create_contact",
    "get_contact_by_id",
    "get_contact_by_phone",
    "list_contacts",
    "search_contacts",
    "update_contact",
    "delete_contact",
]
