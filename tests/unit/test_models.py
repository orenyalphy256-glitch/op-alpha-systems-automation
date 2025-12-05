"""
Unit tests for database models
"""
import pytest
from datetime import datetime
from autom8.models import Contact

# Contact Model Tests
class TestContactModel:
    """Test suite for Contact model."""

    def test_contact_creation(self, test_db):
        # Arrange
        contact = Contact(name="John Doe", phone="0700000000")

        # Act
        test_db.add(contact)
        test_db.commit()

        # Assert
        assert contact.id is not None
        assert contact.name == "John Doe"
        assert contact.phone == "0700000000"
        assert isinstance(contact.created_at, datetime)
        assert isinstance(contact.updated_at, datetime)

    def test_contact_string_representation(self):
        """Test string representation of Contact model."""
        # Arrange
        contact = Contact(name="Jane Smith", phone="0711111111")

        # Assert
        assert "Jane Smith" in str(contact)
        assert "0711111111" in str(contact)

    def test_contact_requires_name(self, test_db):
        """Test that a contact requires a name."""
        # Arrange
        contact = Contact(phone="0700000000")
        test_db.add(contact)

        # Act & Assert
        with pytest.raises(Exception):
            test_db.commit()
    
    def test_contact_requires_phone(self, test_db):
        """Test that a contact requires a phone number."""
        # Arrange
        contact = Contact(name="John Doe")
        test_db.add(contact)

        # Act & Assert
        with pytest.raises(Exception):
            test_db.commit()
    
    def test_contact_phone_unique(self, test_db):
        """Test that a contact's phone number is unique."""
        # Arrange
        contact1 = Contact(name="User 1", phone="0700000000")
        contact2 = Contact(name="User 2", phone="0700000000")

        test_db.add(contact1)
        test_db.commit()

        test_db.add(contact2)

        # Act & Assert
        with pytest.raises(Exception):
            test_db.commit()
    
    def test_contact_update(self, test_db):
        """Test updating a contact."""
        # Arrange
        contact = Contact(name="Old Name", phone="0700000000")
        test_db.add(contact)
        test_db.commit()

        # Act
        contact.name = "New Name"
        contact.phone = "0711111111"
        test_db.commit()

        # Assert
        updated = test_db.query(Contact).filter_by(id=contact.id).first()

        assert updated.name == "New Name"
        assert updated.phone == "0711111111"

    def test_contact_delete(self, test_db):
        """Test deleting a contact."""
        # Arrange
        contact = Contact(name="To Delete", phone="0700000000")
        test_db.add(contact)
        test_db.commit()
        contact_id = contact.id

        # Act
        test_db.delete(contact)
        test_db.commit()

        # Assert
        deleted = test_db.query(Contact).filter_by(id=contact.id).first()
        assert deleted is None
    
    def test_contact_query_all(self, test_db_with_data):
        """Test querying all contacts."""
        # Act
        contacts = test_db_with_data.query(Contact).all()
        
        # Assert
        assert len(contacts) == 3
        assert all(isinstance(c, Contact) for c in contacts)

    def test_contact_query_by_name(self, test_db_with_data):
        """Test querying contact by name."""
        # Act
        contact = test_db_with_data.query(Contact).filter_by(name="Alice Johnson").first()
        
        # Assert
        assert contact is not None
        assert contact.name == "Alice Johnson"
        assert contact.phone == "0700000001"

    def test_contact_query_by_phone(self, test_db_with_data):
        """Test querying contact by phone."""
        # Act
        contact = test_db_with_data.query(Contact).filter_by(phone="0711111111").first()
        
        # Assert
        assert contact is not None
        assert contact.name == "Bob Smith"
        assert contact.phone == "0711111111"
    
    def test_contact_created_at_auto_set(self, test_db):
        """Test that created_at is automatically set on contact creation."""
        # Arrange
        contact = Contact(name="Test", phone="0700000000")

        # Act
        test_db.add(contact)
        test_db.commit()

        # Assert
        assert contact.created_at is not None
        assert isinstance(contact.created_at, datetime)
        assert contact.created_at <= datetime.utcnow()

# Edge cases and validation
class TestContactValidation:
    """Test contact validation and edge cases."""

    def test_contact_empty_name(self, test_db):
        """Test contact with empty string name."""
        # Arrange
        contact = Contact(name="", phone="0700000000")
        test_db.add(contact)

        # Act & Assert
        # Should allow empty string (database level)
        # Application level validation should catch this
        test_db.commit()
        assert contact.name == ""

    def test_contact_very_long_name(self, test_db):
        """Test contact with very long name."""
        # Arrange
        long_name = "A" * 500  # 500 characters long name
        contact = Contact(name=long_name, phone="0700000000")
        test_db.add(contact)

        # Act
        test_db.commit()

        # Assert
        assert len(contact.name) == 500

    def test_contact_special_characters_in_name(self, test_db):
        """Test contact with special characters in name."""
        # Arrange
        special_name = "Test User™ © ® €"
        contact = Contact(name=special_name, phone="0700000000")
        test_db.add(contact)
        
        # Act
        test_db.commit()
        
        # Assert
        assert contact.name == special_name

    def test_contact_phone_formats(self, test_db):
        """Test various phone number formats."""
        # Test different formats
        formats = [
            "0700000000",
            "+254700000000",
            "254700000000",
            "0700-000-000",
            "(070) 000-0000"
        ]

        for idx, phone in enumerate(formats):
            contact = Contact(name=f"User {idx}", phone=phone)
            test_db.add(contact)
        
        test_db.commit()
        
        # Assert all were saved
        contacts = test_db.query(Contact).all()
        assert len(contacts) == len(formats)

# Parametrized tests (Testing multiple scenarios)

@pytest.mark.parametrize("name,phone,should_succeed", [
    ("Valid User", "0700000000", True),
    ("Another User", "0711111111", True),
    ("User Three", "+254722222222", True),
])
def test_contact_creation_parametrized(test_db, name, phone, should_succeed):
    """
    Parametrized test for contact creation.
    Tests multiple scenarios with one test function.
    """
    # Arrange
    contact = Contact(name=name, phone=phone)
    test_db.add(contact)
    
    # Act
    if should_succeed:
        test_db.commit()
        # Assert
        assert contact.id is not None
        assert contact.name == name
        assert contact.phone == phone
    else:
        with pytest.raises(Exception):
            test_db.commit()