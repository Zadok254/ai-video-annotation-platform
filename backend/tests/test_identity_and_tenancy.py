"""Critical integration coverage for tenant-scoped API behavior."""

from fastapi.testclient import TestClient


def register(client: TestClient, email: str, name: str) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correct-horse-battery-staple", "display_name": name},
    )
    assert response.status_code == 201, response.text


def headers_for(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": "correct-horse-battery-staple"},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_tenant_boundary_and_dataset_lifecycle(client: TestClient) -> None:
    register(client, "alice@acme-vision.com", "Alice")
    register(client, "bob@other-vision.com", "Bob")
    alice = headers_for(client, "alice@acme-vision.com")
    bob = headers_for(client, "bob@other-vision.com")
    organization = client.post(
        "/api/v1/organizations", headers=alice, json={"slug": "acme-vision", "name": "Acme Vision"}
    )
    assert organization.status_code == 201, organization.text
    organization_id = organization.json()["id"]
    assert (
        client.get(f"/api/v1/organizations/{organization_id}/projects", headers=bob).status_code
        == 403
    )
    project = client.post(
        f"/api/v1/organizations/{organization_id}/projects",
        headers=alice,
        json={"slug": "road-safety", "name": "Road safety"},
    )
    assert project.status_code == 201, project.text
    project_id = project.json()["id"]
    dataset = client.post(
        f"/api/v1/projects/{project_id}/datasets",
        headers=alice,
        json={"slug": "daytime-runs", "name": "Daytime runs"},
    )
    assert dataset.status_code == 201, dataset.text
    result = client.get(f"/api/v1/projects/{project_id}/datasets", headers=alice)
    assert result.status_code == 200
    assert [item["slug"] for item in result.json()] == ["daytime-runs"]


def test_duplicate_email_is_a_conflict(client: TestClient) -> None:
    register(client, "same@acme-vision.com", "First")
    duplicate = client.post(
        "/api/v1/auth/register",
        json={
            "email": "same@acme-vision.com",
            "password": "correct-horse-battery-staple",
            "display_name": "Second",
        },
    )
    assert duplicate.status_code == 409
