from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_unregister_participant_from_activity():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    original_participants = activities[activity_name]["participants"][:]

    try:
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        assert response.status_code == 200
        data = response.json()
        assert email not in data["participants"]
        assert data["participants"] == [
            participant for participant in original_participants if participant != email
        ]
    finally:
        activities[activity_name]["participants"] = original_participants
