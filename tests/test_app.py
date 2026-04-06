"""
Tests for the Mergington High School API backend
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


def test_get_activities(client):
    """Test that /activities returns the activity database"""
    # Arrange - No special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200

    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0

    # Check that each activity has the expected structure
    for name, details in activities.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Get initial participant count
    response = client.get("/activities")
    initial_activities = response.json()
    initial_count = len(initial_activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]
    assert activity_name in result["message"]

    # Verify the participant was added
    response = client.get("/activities")
    updated_activities = response.json()
    assert email in updated_activities[activity_name]["participants"]
    assert len(updated_activities[activity_name]["participants"]) == initial_count + 1


def test_signup_for_activity_duplicate(client):
    """Test that duplicate signup returns 400 error"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # This email is already signed up

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "already signed up" in result["detail"]


def test_signup_for_unknown_activity(client):
    """Test that signup for non-existent activity returns 404"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_remove_participant_success(client):
    """Test successful removal of a participant"""
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # This email exists in the initial data

    # Get initial participant count
    response = client.get("/activities")
    initial_activities = response.json()
    initial_count = len(initial_activities[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert email in result["message"]
    assert activity_name in result["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    updated_activities = response.json()
    assert email not in updated_activities[activity_name]["participants"]
    assert len(updated_activities[activity_name]["participants"]) == initial_count - 1


def test_remove_participant_not_found(client):
    """Test that removing a non-existent participant returns 404"""
    # Arrange
    activity_name = "Chess Club"
    email = "nonexistent@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Participant not found" in result["detail"]


def test_remove_participant_unknown_activity(client):
    """Test that removing from non-existent activity returns 404"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]