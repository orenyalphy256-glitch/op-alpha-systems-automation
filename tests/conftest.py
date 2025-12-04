"""
Shared pytest fixtures for all tests.
Available to all test files automatically.
"""
import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from autom8.models import Base, Contact
from autom8 import core

# Database Fixtures
@pytest.fixture(scope="function")
def test_db():
    """
    Provide a clean in-memory SQLite database for each test.
    
    Scope: function (new database for each test)
    Cleanup: Automatic after test completes
    """
    # Create in-memory database
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Yield session
    yield session

    # Close session
    session.close()
    engine.dispose()

@pytest.fixture(scope="function")
def test_db_with_data(test_db):
    """
    Provide a database pre-populated with test data.
    """
    # Add sample contacts
    contacts = [
        Contact(name="Alice Johnson", phone="0700000001"),
        Contact(name="Bob Smith", phone="0711111111"),
        Contact(name="Carol White", phone="0722222222")
    ]

    for contact in contacts:
        test_db.add(contact)

    # Commit changes
    test_db.commit()

    return test_db

# File system fixtures
@pytest.fixture(scope="function")
def temp_dir():
    """
    Provide a temporary directory that is cleaned up after the test
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture(scope="function")
def temp_file():
    """
    Provide a temporary file that is cleaned up after the test
    """
    fd, path = tempfile.mkstemp()
    os.close(fd)
    os.unlink(path)

# Application Fixtures
@pytest.fixture(scope="session")
def app_config():
    """
    Provide test configuration dictionary for the application.

    Scope: session (single instance for all tests)
    """
    return {
        "TESTING": True,
        "DEBUG": True,
        "DATABASE_URL": "sqlite:///:memory:",
        "LOG_LEVEL": "DEBUG"
    }

# Data fixtures
@pytest.fixture
def sample_contact():
    return {
        "name": "Test User",
        "phone": "0700000000",
    }

@pytest.fixture
def sample_contacts_list():
    return [
        {"name": "User 1", "phone": "0700000001"},
        {"name": "User 2", "phone": "0700000002"},
        {"name": "User 3", "phone": "0700000003"},
    ]

# Mock fixtures
@pytest.fixture
def mock_datetime(monkeypatch):
    """
    Mock the datetime module to return a fixed date.
    """
    from datetime import datetime

    class MockDatetime:
        @staticmethod
        def now():
            return datetime(2025, 1, 1, 12, 0, 0)
        
        @staticmethod
        def utcnow():
            return datetime(2025, 1, 1, 12, 0, 0)

    monkeypatch.setattr("datetime.datetime", MockDatetime)
    
    return MockDatetime

# Cleanup Hooks
@pytest.fixture(autouse=True)
def reset_logging():
    """
    Reset logging configuration after each test.
    
    autouse=True means this runs automatically for every test.
    """
    import logging
    
    yield

    # Cleanup
    logging.getLogger().handlers = []