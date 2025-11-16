"""
test_models.py - Unit tests for database models
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from autom8.models import Base, Contact, create_contact, get_contact_by_id
import pytest

# Test database (in-memory)
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture
def session():
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_contact(session):
    contact = create_contact(session, "Test User", "0700000000")
    assert contact.id is not None
    assert contact.name == "Test User"
    assert contact.phone == "0700000000"

def test_contact_unique_phone(session):
    create_contact(session, "User1", "0700000000")
    with pytest.raises(Exception):
        create_contact(session, "User2", "0700000000")

def test_get_contact_by_id(session):
    contact = create_contact(session, "Test", "0700000000")
    fetched = get_contact_by_id(session, contact.id)
    assert fetched.name == "Test"

def test_contact_to_dict(session):
    contact = create_contact(session, "Test", "0700000000", "test@email.com")
    data = contact.to_dict()
    assert data["name"] == "Test"
    assert data["phone"] == "0700000000"
    assert data["email"] == "test@email.com"
    assert "created_at" in data