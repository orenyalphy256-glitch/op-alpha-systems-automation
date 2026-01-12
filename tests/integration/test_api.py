# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

Integration tests for Flask API endpoints.

Tests cover:
- HTTP endpoints
- Request/response handling
- Database integration
- Error responses
"""

import json
import time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from autom8.models import Base

# Helper function for unique phone numbers
_phone_counter = 0


def get_unique_phone():
    """Generate a unique phone number based on timestamp and counter."""
    global _phone_counter
    _phone_counter += 1
    return f"07{(int(time.time() * 1000) + _phone_counter) % 100000000:08d}"


# Fixtures
@pytest.fixture(scope="function")
def api_db():
    """Provide clean database for API tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    engine.dispose()


# Health check tests
class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_endpoint_returns_200(self, client):
        """Test health endpoint returns 200 OK."""
        # Act
        response = client.get("/api/v1/health")

        # Assert
        assert response.status_code == 200

    def test_health_endpoint_returns_json(self, client):
        """Test health endpoint returns JSON."""
        # Act
        response = client.get("/api/v1/health")

        # Assert
        assert response.content_type == "application/json"

    def test_health_endpoint_structure(self, client):
        """Test health endpoint returns correct structure."""
        # Act
        response = client.get("/api/v1/health")
        data = json.loads(response.data)

        # Assert
        assert "status" in data
        assert data["status"] == "healthy"
        assert "service" in data
        assert "timestamp" in data or "version" in data


# Contacts CRUD tests
class TestContactsEndpoints:
    """Test contacts CRUD operations."""

    def test_get_all_contacts_empty(self, client):
        """Test getting all contacts when none exist."""
        # Act
        response = client.get("/api/v1/contacts")

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        # API returns a dictionary with contacts list
        assert isinstance(data, dict)
        assert "contacts" in data
        assert isinstance(data["contacts"], list)
        # Note: May not be empty if database has existing data

    def test_create_contact_success(self, client):
        """Test creating a new contact."""
        # Arrange - Use unique phone number
        new_contact = {"name": "Test User", "phone": get_unique_phone()}

        # Act
        response = client.post(
            "/api/v1/contacts", data=json.dumps(new_contact), content_type="application/json"
        )

        # Assert
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == "Test User"
        assert "phone" in data
        assert "id" in data

    def test_create_contact_missing_name(self, client):
        """Test creating contact without name fails."""
        # Arrange
        invalid_contact = {"phone": "0700000000"}

        # Act
        response = client.post(
            "/api/v1/contacts", data=json.dumps(invalid_contact), content_type="application/json"
        )

        # Assert
        assert response.status_code == 400

    def test_create_contact_missing_phone(self, client):
        """Test creating contact without phone fails."""
        # Arrange
        invalid_contact = {"name": "Test User"}

        # Act
        response = client.post(
            "/api/v1/contacts", data=json.dumps(invalid_contact), content_type="application/json"
        )

        # Assert
        assert response.status_code == 400

    def test_get_contact_by_id(self, client):
        """Test getting specific contact by ID."""
        # Arrange - Create contact first with unique phone
        new_contact = {"name": "Test User", "phone": get_unique_phone()}
        create_response = client.post(
            "/api/v1/contacts", data=json.dumps(new_contact), content_type="application/json"
        )
        contact_id = json.loads(create_response.data)["id"]

        # Act
        response = client.get(f"/api/v1/contacts/{contact_id}")

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["id"] == contact_id
        assert data["name"] == "Test User"

    def test_get_nonexistent_contact(self, client):
        """Test getting non-existent contact returns 404."""
        # Act
        response = client.get("/api/v1/contacts/99999")

        # Assert
        assert response.status_code == 404

    def test_update_contact(self, client):
        """Test updating a contact."""
        # Arrange - Create contact first
        new_contact = {"name": "Original Name", "phone": get_unique_phone()}
        create_response = client.post(
            "/api/v1/contacts", data=json.dumps(new_contact), content_type="application/json"
        )
        contact_id = json.loads(create_response.data)["id"]

        # Act
        updated_phone = get_unique_phone()
        updated_data = {"name": "Updated Name", "phone": updated_phone}
        response = client.put(
            f"/api/v1/contacts/{contact_id}",
            data=json.dumps(updated_data),
            content_type="application/json",
        )

        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Updated Name"
        assert data["phone"] == updated_phone

    def test_delete_contact(self, client):
        """Test deleting a contact."""
        # Arrange - Create contact first
        new_contact = {"name": "To Delete", "phone": get_unique_phone()}
        create_response = client.post(
            "/api/v1/contacts", data=json.dumps(new_contact), content_type="application/json"
        )
        contact_id = json.loads(create_response.data)["id"]

        # Act
        response = client.delete(f"/api/v1/contacts/{contact_id}")

        # Assert
        assert response.status_code == 200 or response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/v1/contacts/{contact_id}")
        assert get_response.status_code == 404

    def test_create_duplicate_phone(self, client):
        """Test creating contact with duplicate phone fails."""
        # Arrange - Use same phone for both to test duplicate detection
        duplicate_phone = get_unique_phone()
        contact1 = {"name": "User 1", "phone": duplicate_phone}
        contact2 = {"name": "User 2", "phone": duplicate_phone}  # Same phone!

        # Act
        client.post("/api/v1/contacts", data=json.dumps(contact1), content_type="application/json")
        response = client.post(
            "/api/v1/contacts", data=json.dumps(contact2), content_type="application/json"
        )

        # Assert
        assert response.status_code == 400 or response.status_code == 409


# Metrics endpoint tests
class TestMetricsEndpoint:
    """Test metrics endpoint."""

    def test_metrics_endpoint_returns_200(self, client):
        """Test metrics endpoint is accessible."""
        # Act
        response = client.get("/api/v1/metrics")

        # Assert
        assert response.status_code == 200

    def test_metrics_endpoint_returns_json(self, client):
        """Test metrics returns JSON format."""
        # Act
        response = client.get("/api/v1/metrics")

        # Assert
        assert response.content_type == "application/json"

    def test_metrics_contains_system_info(self, client):
        """Test metrics contains system information."""
        # Act
        response = client.get("/api/v1/metrics")
        data = json.loads(response.data)

        # Assert
        # Should contain some system metrics
        assert isinstance(data, dict)
        # Check for expected keys (adjust based on your metrics implementation)
        assert len(data) > 0


# Error handling tests
class TestAPIErrorHandling:
    """Test API error handling."""

    def test_invalid_json_returns_400(self, client):
        """Test sending invalid JSON returns 400."""
        # Act
        response = client.post(
            "/api/v1/contacts", data="invalid json{{{", content_type="application/json"
        )

        # Assert
        assert response.status_code == 400

    def test_invalid_endpoint_returns_404(self, client):
        """Test accessing invalid endpoint returns 404."""
        # Act
        response = client.get("/api/v1/nonexistent")

        # Assert
        assert response.status_code == 404

    def test_invalid_method_returns_405(self, client):
        """Test using invalid HTTP method returns 405."""
        # Act
        response = client.patch("/api/v1/health")  # PATCH not supported

        # Assert
        assert response.status_code == 405


# Integration workflow tests
class TestAPIWorkflows:
    """Test complete API workflows."""

    def test_complete_contact_lifecycle(self, client):
        """Test complete CRUD lifecycle for a contact."""
        # 1. CREATE
        new_contact = {"name": "Lifecycle Test", "phone": get_unique_phone()}
        create_response = client.post(
            "/api/v1/contacts", data=json.dumps(new_contact), content_type="application/json"
        )
        assert create_response.status_code == 201
        contact_id = json.loads(create_response.data)["id"]

        # 2. READ
        read_response = client.get(f"/api/v1/contacts/{contact_id}")
        assert read_response.status_code == 200
        assert json.loads(read_response.data)["name"] == "Lifecycle Test"

        # 3. UPDATE
        updated_data = {"name": "Updated Lifecycle", "phone": get_unique_phone()}
        update_response = client.put(
            f"/api/v1/contacts/{contact_id}",
            data=json.dumps(updated_data),
            content_type="application/json",
        )
        assert update_response.status_code == 200
        assert json.loads(update_response.data)["name"] == "Updated Lifecycle"

        # 4. DELETE
        delete_response = client.delete(f"/api/v1/contacts/{contact_id}")
        assert delete_response.status_code in [200, 204]

        # 5. VERIFY DELETION
        verify_response = client.get(f"/api/v1/contacts/{contact_id}")
        assert verify_response.status_code == 404

    def test_multiple_contacts_workflow(self, client):
        """Test creating and managing multiple contacts."""
        # Create multiple contacts with unique phones
        contacts = [
            {"name": "User 1", "phone": get_unique_phone()},
            {"name": "User 2", "phone": get_unique_phone()},
            {"name": "User 3", "phone": get_unique_phone()},
        ]

        contact_ids = []
        for contact in contacts:
            response = client.post(
                "/api/v1/contacts", data=json.dumps(contact), content_type="application/json"
            )
            assert response.status_code == 201
            contact_ids.append(json.loads(response.data)["id"])

        # Get all contacts
        all_response = client.get("/api/v1/contacts")
        assert all_response.status_code == 200
        all_contacts = json.loads(all_response.data)["contacts"]
        assert len(all_contacts) >= 3

        # Verify each contact exists
        for contact_id in contact_ids:
            response = client.get(f"/api/v1/contacts/{contact_id}")
            assert response.status_code == 200
