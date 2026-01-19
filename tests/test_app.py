import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestGetActivities:
    """Test cases for GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that get_activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_json(self):
        """Test that get_activities returns valid JSON"""
        response = client.get("/activities")
        assert response.headers["content-type"] == "application/json"

    def test_get_activities_has_expected_activities(self):
        """Test that get_activities returns all expected activities"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Tennis Club",
            "Basketball Team",
            "Art Club",
            "Drama Club",
            "Debate Team",
            "Robotics Club",
            "Chess Club",
            "Programming Class",
            "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_get_activities_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Tennis%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_adds_participant(self):
        """Test that signup adds participant to activity"""
        client.post("/activities/Basketball%20Team/signup?email=newstudent@mergington.edu")
        response = client.get("/activities")
        activities = response.json()
        
        assert "newstudent@mergington.edu" in activities["Basketball Team"]["participants"]

    def test_signup_duplicate_email_fails(self):
        """Test that duplicate signup fails"""
        # First signup
        client.post("/activities/Art%20Club/signup?email=duplicate@mergington.edu")
        
        # Attempt duplicate signup
        response = client.post(
            "/activities/Art%20Club/signup?email=duplicate@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self):
        """Test that signup for non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_returns_proper_message(self):
        """Test that signup returns the correct message"""
        response = client.post(
            "/activities/Drama%20Club/signup?email=actor@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up actor@mergington.edu for Drama Club" == data["message"]


class TestUnregisterFromActivity:
    """Test cases for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregister from an activity"""
        # First signup
        client.post("/activities/Robotics%20Club/signup?email=robot@mergington.edu")
        
        # Then unregister
        response = client.post(
            "/activities/Robotics%20Club/unregister?email=robot@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self):
        """Test that unregister removes participant from activity"""
        # First signup
        client.post("/activities/Chess%20Club/signup?email=chess@mergington.edu")
        
        # Verify signup
        response = client.get("/activities")
        activities = response.json()
        assert "chess@mergington.edu" in activities["Chess Club"]["participants"]
        
        # Unregister
        client.post("/activities/Chess%20Club/unregister?email=chess@mergington.edu")
        
        # Verify removal
        response = client.get("/activities")
        activities = response.json()
        assert "chess@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity_fails(self):
        """Test that unregister from non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_not_registered_fails(self):
        """Test that unregister for non-registered student fails"""
        response = client.post(
            "/activities/Programming%20Class/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_returns_proper_message(self):
        """Test that unregister returns the correct message"""
        # Signup first
        client.post("/activities/Gym%20Class/signup?email=gym@mergington.edu")
        
        # Unregister
        response = client.post(
            "/activities/Gym%20Class/unregister?email=gym@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered gym@mergington.edu from Gym Class" == data["message"]


class TestRootRoute:
    """Test cases for root route"""

    def test_root_redirects_to_static(self):
        """Test that root route redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
