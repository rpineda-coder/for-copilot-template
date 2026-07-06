import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def preserve_activity_state():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


def test_get_activities_returns_known_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_adds_new_participant():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity_name}"
    assert email in data["participants"]
    assert any(p.lower() == email for p in activities[activity_name]["participants"])


def test_signup_duplicate_participant_returns_400():
    activity_name = "Programming Class"
    email = "emma@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Already signed up"


def test_signup_full_activity_returns_409():
    activity_name = "Art Studio"
    email = "extra@student.edu"

    original_max = activities[activity_name]["max_participants"]
    activities[activity_name]["max_participants"] = len(activities[activity_name]["participants"])

    try:
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        assert response.status_code == 409
        assert response.json()["detail"] == "Activity is full"
    finally:
        activities[activity_name]["max_participants"] = original_max


def test_signup_unknown_activity_returns_404():
    response = client.post("/activities/Unknown Club/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_from_activity():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 200
    data = response.json()
    assert email not in data["participants"]
    assert all(participant.lower() != email.lower() for participant in data["participants"])


def test_unregister_unknown_activity_returns_404():
    response = client.delete("/activities/Unknown Club/participants/student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_nonexistent_participant_returns_404():
    activity_name = "Swimming Club"
    email = "missing@student.edu"

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
