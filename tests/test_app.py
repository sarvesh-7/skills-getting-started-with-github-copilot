"""
Comprehensive test suite for the Mergington High School API

Tests cover:
- Get activities endpoint
- Signup endpoint with valid and error cases
- Delete participant endpoint with valid and error cases
- Edge cases and validation
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

# Create a test client for the FastAPI app
client = TestClient(app)


class TestGetActivities:
    """Test cases for GET /activities endpoint"""

    def test_get_activities_success(self):
        """Test successfully retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()

        # Verify response is a dictionary
        assert isinstance(data, dict)

        # Verify all expected activities are present
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Tennis Club", "Art Studio",
            "Drama Club", "Debate Team", "Science Club"
        ]
        for activity in expected_activities:
            assert activity in data

    def test_get_activities_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()

        required_fields = ["description", "schedule", "max_participants", "participants"]

        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity {activity_name} missing {field}"

    def test_get_activities_participants_is_list(self):
        """Test that participants field is a list"""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), f"Participants for {activity_name} is not a list"

    def test_get_activities_max_participants_is_int(self):
        """Test that max_participants is an integer"""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int), f"max_participants for {activity_name} is not an int"


class TestSignupEndpoint:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successful signup"""
        # Use an activity that exists
        response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "test@example.com" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        response = client.post("/activities/NonExistent/signup?email=test@example.com")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email(self):
        """Test signing up twice with same email"""
        # First signup
        client.post("/activities/Programming%20Class/signup?email=duplicate@example.com")

        # Second signup should fail
        response = client.post("/activities/Programming%20Class/signup?email=duplicate@example.com")
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_different_activities_same_email(self):
        """Test same email can sign up for different activities"""
        # Sign up for two different activities
        response1 = client.post("/activities/Gym%20Class/signup?email=multi@example.com")
        response2 = client.post("/activities/Basketball%20Team/signup?email=multi@example.com")

        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_signup_updates_participants_list(self):
        """Test that signup actually adds email to participants list"""
        email = "verify@example.com"

        # Get initial participants
        response = client.get("/activities")
        initial_participants = response.json()["Tennis Club"]["participants"]

        # Sign up
        client.post("/activities/Tennis%20Club/signup?email=" + email)

        # Check participants again
        response = client.get("/activities")
        updated_participants = response.json()["Tennis Club"]["participants"]

        assert email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1


class TestDeleteParticipantEndpoint:
    """Test cases for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_delete_participant_success(self):
        """Test successful participant removal"""
        email = "delete@example.com"

        # First sign up
        client.post("/activities/Art%20Studio/signup?email=" + email)

        # Then delete
        response = client.delete(f"/activities/Art%20Studio/participants/{email}")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Art Studio" in data["message"]

    def test_delete_participant_activity_not_found(self):
        """Test deleting from non-existent activity"""
        response = client.delete("/activities/NonExistent/participants/test@example.com")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_delete_participant_not_signed_up(self):
        """Test deleting participant who is not signed up"""
        response = client.delete("/activities/Drama%20Club/participants/notsignedup@example.com")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]

    def test_delete_participant_removes_from_list(self):
        """Test that delete actually removes email from participants list"""
        email = "remove@example.com"

        # Sign up
        client.post("/activities/Debate%20Team/signup?email=" + email)

        # Verify added
        response = client.get("/activities")
        assert email in response.json()["Debate Team"]["participants"]

        # Delete
        client.delete(f"/activities/Debate%20Team/participants/{email}")

        # Verify removed
        response = client.get("/activities")
        assert email not in response.json()["Debate Team"]["participants"]


class TestRootEndpoint:
    """Test cases for root endpoint"""

    def test_root_redirect(self):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/")
        assert response.status_code == 200
        # FastAPI redirects are handled, but in test client it might return the HTML
        # The redirect response should contain the HTML content or redirect status


class TestDataIntegrity:
    """Test data integrity and business rules"""

    def test_activities_data_structure_preserved(self):
        """Test that activities data structure is not corrupted by operations"""
        # Get initial state
        response = client.get("/activities")
        initial_data = response.json()

        # Perform some operations
        client.post("/activities/Chess%20Club/signup?email=temp@example.com")
        client.delete("/activities/Chess%20Club/participants/temp@example.com")

        # Get final state
        response = client.get("/activities")
        final_data = response.json()

        # Structure should be the same (though participants may differ)
        assert set(initial_data.keys()) == set(final_data.keys())

        for activity in initial_data:
            assert "description" in final_data[activity]
            assert "schedule" in final_data[activity]
            assert "max_participants" in final_data[activity]
            assert "participants" in final_data[activity]
            assert isinstance(final_data[activity]["participants"], list)

    def test_concurrent_operations_isolation(self):
        """Test that operations on different activities don't interfere"""
        # Sign up for different activities
        client.post("/activities/Science%20Club/signup?email=user1@example.com")
        client.post("/activities/Chess%20Club/signup?email=user2@example.com")

        # Check both activities
        response = client.get("/activities")
        activities = response.json()

        assert "user1@example.com" in activities["Science Club"]["participants"]
        assert "user2@example.com" in activities["Chess Club"]["participants"]
        assert "user1@example.com" not in activities["Chess Club"]["participants"]
        assert "user2@example.com" not in activities["Science Club"]["participants"]