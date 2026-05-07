import copy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def reset_activities_state():
    original = copy.deepcopy(activities)
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_returns_all_activities():
    # Arrange
    reset_activities_state()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()


def test_signup_for_activity_adds_participant():
    # Arrange
    reset_activities_state()
    activity_name = "Chess Club"
    email = "new_student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    reset_activities_state()
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_400():
    # Arrange
    reset_activities_state()
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_removes_participant():
    # Arrange
    reset_activities_state()
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    reset_activities_state()
    activity_name = "Chess Club"
    email = "missing_student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in this activity"
