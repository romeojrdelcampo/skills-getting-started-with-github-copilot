import pytest
from fastapi.testclient import TestClient
from src.app import app

# Create a test client
client = TestClient(app)

# Original activities data for reset
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities data before each test"""
    from src.app import activities
    activities.clear()
    activities.update(ORIGINAL_ACTIVITIES)

def test_get_activities():
    """Test GET /activities endpoint"""
    # Arrange
    expected_keys = ["Chess Club", "Programming Class", "Gym Class"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert set(data.keys()) == set(expected_keys)
    for activity in data.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

def test_signup_success():
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]

    # Verify the participant was added
    get_response = client.get("/activities")
    activities = get_response.json()
    assert email in activities[activity_name]["participants"]

def test_signup_duplicate():
    """Test signup when student is already signed up"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_signup_invalid_activity():
    """Test signup for non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_remove_success():
    """Test successful removal of a participant"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/remove?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]

    # Verify the participant was removed
    get_response = client.get("/activities")
    activities = get_response.json()
    assert email not in activities[activity_name]["participants"]

def test_remove_not_signed_up():
    """Test removal when student is not signed up"""
    # Arrange
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/remove?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]

def test_remove_invalid_activity():
    """Test removal from non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/remove?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_root_redirect():
    """Test GET / redirects to static HTML"""
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert "location" in response.headers
    assert response.headers["location"] == "/static/index.html"