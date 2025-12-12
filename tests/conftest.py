"""
Shared pytest fixtures for all tests.
"""

import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from autom8.models import Base, Contact
from autom8 import core

# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def test_db():
    """
    Provide a clean in-memory SQLite database for each test.
    
    Scope: function (new database for each test)
    Cleanup: Automatic after test completes
    """
    # Create in-memory database
    engine = create_engine(
        "sqlite:///:memory:", 
        echo=False,
        connect_args={"check_same_thread": False}  # Important for SQLite
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()
    
    yield session
    
    # CRITICAL: Proper cleanup
    try:
        session.close()
        Session.remove()
        engine.dispose()
    except Exception as e:
        print(f"Warning: Error during database cleanup: {e}")


@pytest.fixture(scope="function")
def test_db_with_data(test_db):
    """
    Provide a database pre-populated with test data.
    """
    # Add sample contacts
    contacts = [
        Contact(name="Alice Johnson", phone="0700000001"),
        Contact(name="Bob Smith", phone="0711111111"),
        Contact(name="Carol White", phone="0722222222"),
    ]
    
    for contact in contacts:
        test_db.add(contact)
    
    test_db.commit()
    
    return test_db


# ============================================================================
# FILE SYSTEM FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def temp_dir():
    """
    Provide a temporary directory that's cleaned up after the test.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture(scope="function")
def temp_file():
    """
    Provide a temporary file that's cleaned up after the test.
    """
    fd, path = tempfile.mkstemp()
    yield path
    try:
        os.close(fd)
        os.unlink(path)
    except Exception:
        pass  # File might already be closed/deleted


# ============================================================================
# APPLICATION FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def app_config():
    """
    Provide test configuration.
    
    Scope: session (created once for all tests)
    """
    return {
        "TESTING": True,
        "DEBUG": True,
        "DATABASE_URL": "sqlite:///:memory:",
        "LOG_LEVEL": "DEBUG"
    }


# ============================================================================
# DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_contact():
    """Provide a sample contact dictionary."""
    return {
        "name": "Test User",
        "phone": "0700000000"
    }


@pytest.fixture
def sample_contacts_list():
    """Provide a list of sample contacts."""
    return [
        {"name": "User 1", "phone": "0700000001"},
        {"name": "User 2", "phone": "0700000002"},
        {"name": "User 3", "phone": "0700000003"},
    ]


# ============================================================================
# CLEANUP HOOKS
# ============================================================================

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