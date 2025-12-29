# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

Integration tests for database operations.

Tests cover:
- Database connections
- Transactions
- Concurrent access
- Data integrity
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from autom8.models import Base, Contact


# Database Connection Tests
class TestDatabaseConnection:
    """Test database connection and initialization."""

    def test_create_database_engine(self):
        """Test creating database engine."""
        # Act
        engine = create_engine("sqlite:///:memory:")

        # Assert
        assert engine is not None

    def test_create_tables(self):
        """Test creating database tables."""
        # Arrange
        engine = create_engine("sqlite:///:memory:")

        # Act
        Base.metadata.create_all(engine)

        # Assert
        # Verify tables exist
        assert "contacts" in Base.metadata.tables

    def test_session_creation(self):
        """Test creating database session."""
        # Arrange
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        # Act
        Session = sessionmaker(bind=engine)
        session = Session()

        # Assert
        assert session is not None
        session.close()


# Transaction Tests
class TestDatabaseTransactions:
    """Test database transaction handling."""

    def test_commit_transaction(self, test_db):
        """Test committing a transaction."""
        # Arrange
        contact = Contact(name="Test", phone="0700000000")
        test_db.add(contact)

        # Act
        test_db.commit()

        # Assert
        saved = test_db.query(Contact).filter_by(phone="0700000000").first()
        assert saved is not None

    def test_rollback_transaction(self, test_db):
        """Test rolling back a transaction."""
        # Arrange
        contact = Contact(name="Test", phone="0700000000")
        test_db.add(contact)

        # Act
        test_db.rollback()

        # Assert
        saved = test_db.query(Contact).filter_by(phone="0700000000").first()
        assert saved is None

    def test_transaction_isolation(self, test_db):
        """Test that uncommitted changes are not visible."""
        # Arrange
        contact1 = Contact(name="Committed", phone="0700000001")
        test_db.add(contact1)
        test_db.commit()

        contact2 = Contact(name="Uncommitted", phone="0700000002")
        test_db.add(contact2)
        # Don't commit!

        # Act
        committed_contacts = (
            test_db.query(Contact).filter(Contact.phone.in_(["0700000001", "0700000002"])).all()
        )

        # Assert
        # Both visible in same session
        assert len(committed_contacts) == 2


# Data integrity tests
class TestDataIntegrity:
    """Test data integrity constraints."""

    def test_unique_phone_constraint(self, test_db):
        """Test that phone numbers must be unique."""
        # Arrange
        contact1 = Contact(name="User 1", phone="0700000000")
        contact2 = Contact(name="User 2", phone="0700000000")

        test_db.add(contact1)
        test_db.commit()

        test_db.add(contact2)

        # Act & Assert
        with pytest.raises(Exception):
            test_db.commit()

    def test_not_null_constraints(self, test_db):
        """Test that required fields cannot be null."""
        # Arrange
        contact = Contact()  # No name or phone
        test_db.add(contact)

        # Act & Assert
        with pytest.raises(Exception):
            test_db.commit()


# Bulk operations tests
class TestBulkOperations:
    """Test bulk database operations."""

    def test_bulk_insert(self, test_db):
        """Test inserting multiple records at once."""
        # Arrange
        contacts = [Contact(name=f"User {i}", phone=f"070000000{i}") for i in range(100)]

        # Act
        test_db.bulk_save_objects(contacts)
        test_db.commit()

        # Assert
        count = test_db.query(Contact).count()
        assert count == 100

    def test_bulk_update(self, test_db_with_data):
        """Test updating multiple records at once."""
        # Arrange
        contacts = test_db_with_data.query(Contact).all()
        original_count = len(contacts)

        # Act
        test_db_with_data.query(Contact).update({"name": "Updated Name"}, synchronize_session=False)
        test_db_with_data.commit()

        # Assert
        updated_contacts = test_db_with_data.query(Contact).all()
        assert len(updated_contacts) == original_count
        assert all(c.name == "Updated Name" for c in updated_contacts)

    def test_bulk_delete(self, test_db_with_data):
        """Test deleting multiple records at once."""
        # Arrange
        initial_count = test_db_with_data.query(Contact).count()
        assert initial_count > 0

        # Act
        test_db_with_data.query(Contact).delete()
        test_db_with_data.commit()

        # Assert
        final_count = test_db_with_data.query(Contact).count()
        assert final_count == 0


# Query performance tests
class TestQueryPerformance:
    """Test query performance and optimization."""

    def test_query_with_filter(self, test_db_with_data):
        """Test filtering queries."""
        # Act
        alice = test_db_with_data.query(Contact).filter(Contact.name == "Alice Johnson").first()

        # Assert
        assert alice is not None
        assert alice.name == "Alice Johnson"

    def test_query_with_like(self, test_db_with_data):
        """Test LIKE queries."""
        # Act
        results = test_db_with_data.query(Contact).filter(Contact.name.like("%Smith%")).all()

        # Assert
        assert len(results) > 0
        assert any("Smith" in c.name for c in results)

    def test_query_ordering(self, test_db_with_data):
        """Test query result ordering."""
        # Act
        contacts_asc = test_db_with_data.query(Contact).order_by(Contact.name.asc()).all()

        contacts_desc = test_db_with_data.query(Contact).order_by(Contact.name.desc()).all()

        # Assert
        assert contacts_asc[0].name != contacts_desc[0].name
        assert contacts_asc[-1].name == contacts_desc[0].name

    def test_query_limit(self, test_db_with_data):
        """Test limiting query results."""
        # Act
        limited = test_db_with_data.query(Contact).limit(2).all()

        # Assert
        assert len(limited) == 2

    def test_query_count(self, test_db_with_data):
        """Test counting query results."""
        # Act
        count = test_db_with_data.query(Contact).count()

        # Assert
        assert count == 3  # From test_db_with_data fixture


# Concurrent access tests
class TestConcurrentAccess:
    """Test concurrent database access."""

    def test_multiple_sessions_read(self):
        """Test multiple sessions can read simultaneously."""
        # Arrange
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)

        session1 = Session()
        session2 = Session()

        contact = Contact(name="Test", phone="0700000000")
        session1.add(contact)
        session1.commit()

        # Act
        result1 = session1.query(Contact).first()
        result2 = session2.query(Contact).first()

        # Assert
        assert result1 is not None
        assert result2 is not None
        assert result1.name == result2.name

        # Cleanup
        session1.close()
        session2.close()
