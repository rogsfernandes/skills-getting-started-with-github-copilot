import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


# Snapshot of original activities to restore between tests
original_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Reset in-memory database before each test to avoid cross-test pollution
    app_module.activities = copy.deepcopy(original_activities)
    yield
    app_module.activities = copy.deepcopy(original_activities)


def test_get_activities_contains_known_activity():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity check: Chess Club should be present
    assert "Chess Club" in data


def test_signup_and_duplicate_rejection():
    activity = "Chess Club"
    email = "test.student@mergington.edu"

    # Sign up should succeed
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Signing up again should fail with 400
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400


def test_unregister_and_not_registered():
    activity = "Programming Class"
    email = "not.registered@mergington.edu"

    # Unregistering a non-registered student should return 400
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 400

    # Register then unregister
    register_resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert register_resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    unregister_resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert unregister_resp.status_code == 200
    assert email not in app_module.activities[activity]["participants"]
