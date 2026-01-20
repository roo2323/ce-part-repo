"""
Tests for emergency contacts API endpoints.

This module contains tests for CRUD operations on emergency contacts
including validation, business rules, and edge cases.
"""
import pytest
from fastapi.testclient import TestClient

from src.contacts.models import EmergencyContact


class TestContactsList:
    """Tests for GET /api/v1/contacts endpoint."""

    def test_get_contacts_empty(self, client: TestClient, auth_headers: dict):
        """Test getting contacts when none exist."""
        response = client.get("/api/v1/contacts", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["max_contacts"] == 3
        assert data["current_count"] == 0

    def test_get_contacts_with_data(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
        test_user,
    ):
        """Test getting contacts when contacts exist."""
        # Create a contact directly in the database
        contact = EmergencyContact(
            user_id=test_user.id,
            name="Emergency Contact",
            contact_type="email",
            contact_value="emergency@example.com",
            priority=1,
            is_verified=False,
        )
        db_session.add(contact)
        db_session.commit()

        response = client.get("/api/v1/contacts", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Emergency Contact"
        assert data["current_count"] == 1

    def test_get_contacts_unauthorized(self, client: TestClient):
        """Test getting contacts without authentication."""
        response = client.get("/api/v1/contacts")

        assert response.status_code == 401


class TestCreateContact:
    """Tests for POST /api/v1/contacts endpoint."""

    def test_create_contact_success_email(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test successful contact creation with email."""
        payload = {
            "name": "Mom",
            "contact_type": "email",
            "contact_value": "mom@example.com",
            "priority": 1,
        }

        response = client.post(
            "/api/v1/contacts",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Mom"
        assert data["contact_type"] == "email"
        assert data["contact_value"] == "mom@example.com"
        assert data["priority"] == 1
        assert data["is_verified"] is False
        assert "id" in data
        assert "created_at" in data

    def test_create_contact_success_sms(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test successful contact creation with SMS."""
        payload = {
            "name": "Dad",
            "contact_type": "sms",
            "contact_value": "010-1234-5678",
            "priority": 2,
        }

        response = client.post(
            "/api/v1/contacts",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Dad"
        assert data["contact_type"] == "sms"

    def test_create_contact_max_exceeded(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
        test_user,
    ):
        """Test creating contact when maximum reached."""
        # Create 3 contacts directly
        for i in range(3):
            contact = EmergencyContact(
                user_id=test_user.id,
                name=f"Contact {i+1}",
                contact_type="email",
                contact_value=f"contact{i+1}@example.com",
                priority=i + 1,
                is_verified=False,
            )
            db_session.add(contact)
        db_session.commit()

        # Try to create a 4th contact
        payload = {
            "name": "Contact 4",
            "contact_type": "email",
            "contact_value": "contact4@example.com",
            "priority": 1,
        }

        response = client.post(
            "/api/v1/contacts",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["code"] == "CONTACT001"

    def test_create_contact_duplicate(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
        test_user,
    ):
        """Test creating contact with duplicate value."""
        # Create a contact first
        contact = EmergencyContact(
            user_id=test_user.id,
            name="Existing Contact",
            contact_type="email",
            contact_value="existing@example.com",
            priority=1,
            is_verified=False,
        )
        db_session.add(contact)
        db_session.commit()

        # Try to create with same contact value
        payload = {
            "name": "New Contact",
            "contact_type": "email",
            "contact_value": "existing@example.com",
            "priority": 2,
        }

        response = client.post(
            "/api/v1/contacts",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["code"] == "CONTACT002"

    def test_create_contact_invalid_email(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test creating contact with invalid email format."""
        payload = {
            "name": "Invalid",
            "contact_type": "email",
            "contact_value": "not-an-email",
            "priority": 1,
        }

        response = client.post(
            "/api/v1/contacts",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_create_contact_invalid_priority(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test creating contact with invalid priority."""
        payload = {
            "name": "Invalid Priority",
            "contact_type": "email",
            "contact_value": "valid@example.com",
            "priority": 5,  # Invalid: must be 1-3
        }

        response = client.post(
            "/api/v1/contacts",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_create_contact_unauthorized(self, client: TestClient):
        """Test creating contact without authentication."""
        payload = {
            "name": "Test",
            "contact_type": "email",
            "contact_value": "test@example.com",
            "priority": 1,
        }

        response = client.post("/api/v1/contacts", json=payload)

        assert response.status_code == 401


class TestUpdateContact:
    """Tests for PUT /api/v1/contacts/{contact_id} endpoint."""

    def test_update_contact_name(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
        test_user,
    ):
        """Test updating contact name."""
        contact = EmergencyContact(
            user_id=test_user.id,
            name="Original Name",
            contact_type="email",
            contact_value="test@example.com",
            priority=1,
            is_verified=False,
        )
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)

        payload = {"name": "Updated Name"}

        response = client.put(
            f"/api/v1/contacts/{contact.id}",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["priority"] == 1  # Unchanged

    def test_update_contact_priority(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
        test_user,
    ):
        """Test updating contact priority."""
        contact = EmergencyContact(
            user_id=test_user.id,
            name="Test Contact",
            contact_type="email",
            contact_value="test@example.com",
            priority=1,
            is_verified=False,
        )
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)

        payload = {"priority": 3}

        response = client.put(
            f"/api/v1/contacts/{contact.id}",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["priority"] == 3
        assert data["name"] == "Test Contact"  # Unchanged

    def test_update_contact_not_found(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test updating non-existent contact."""
        payload = {"name": "Updated"}

        response = client.put(
            "/api/v1/contacts/non-existent-id",
            json=payload,
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_contact_unauthorized(
        self,
        client: TestClient,
        db_session,
        test_user,
    ):
        """Test updating contact without authentication."""
        contact = EmergencyContact(
            user_id=test_user.id,
            name="Test Contact",
            contact_type="email",
            contact_value="test@example.com",
            priority=1,
            is_verified=False,
        )
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)

        payload = {"name": "Updated"}

        response = client.put(f"/api/v1/contacts/{contact.id}", json=payload)

        assert response.status_code == 401


class TestDeleteContact:
    """Tests for DELETE /api/v1/contacts/{contact_id} endpoint."""

    def test_delete_contact_success(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
        test_user,
    ):
        """Test successful contact deletion."""
        contact = EmergencyContact(
            user_id=test_user.id,
            name="To Delete",
            contact_type="email",
            contact_value="delete@example.com",
            priority=1,
            is_verified=False,
        )
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)

        response = client.delete(
            f"/api/v1/contacts/{contact.id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deletion
        response = client.get("/api/v1/contacts", headers=auth_headers)
        assert response.json()["current_count"] == 0

    def test_delete_contact_not_found(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test deleting non-existent contact."""
        response = client.delete(
            "/api/v1/contacts/non-existent-id",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_delete_contact_unauthorized(
        self,
        client: TestClient,
        db_session,
        test_user,
    ):
        """Test deleting contact without authentication."""
        contact = EmergencyContact(
            user_id=test_user.id,
            name="Test Contact",
            contact_type="email",
            contact_value="test@example.com",
            priority=1,
            is_verified=False,
        )
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)

        response = client.delete(f"/api/v1/contacts/{contact.id}")

        assert response.status_code == 401


class TestVerifyContact:
    """Tests for POST /api/v1/contacts/{contact_id}/verify endpoint."""

    def test_verify_contact_success(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
        test_user,
    ):
        """Test successful verification request."""
        contact = EmergencyContact(
            user_id=test_user.id,
            name="To Verify",
            contact_type="email",
            contact_value="verify@example.com",
            priority=1,
            is_verified=False,
        )
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)

        response = client.post(
            f"/api/v1/contacts/{contact.id}/verify",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["contact_id"] == contact.id
        assert data["sent_to"] == "verify@example.com"
        assert "message" in data

    def test_verify_contact_not_found(
        self,
        client: TestClient,
        auth_headers: dict,
    ):
        """Test verification for non-existent contact."""
        response = client.post(
            "/api/v1/contacts/non-existent-id/verify",
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestContactOrdering:
    """Tests for contact priority ordering."""

    def test_contacts_ordered_by_priority(
        self,
        client: TestClient,
        auth_headers: dict,
        db_session,
        test_user,
    ):
        """Test that contacts are returned ordered by priority."""
        # Create contacts in reverse order
        for priority in [3, 1, 2]:
            contact = EmergencyContact(
                user_id=test_user.id,
                name=f"Contact {priority}",
                contact_type="email",
                contact_value=f"contact{priority}@example.com",
                priority=priority,
                is_verified=False,
            )
            db_session.add(contact)
        db_session.commit()

        response = client.get("/api/v1/contacts", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 3
        assert data["data"][0]["priority"] == 1
        assert data["data"][1]["priority"] == 2
        assert data["data"][2]["priority"] == 3
