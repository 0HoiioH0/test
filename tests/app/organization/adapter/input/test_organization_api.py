from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.organization.application.exception import (
    OrganizationNotFoundException,
)
from app.organization.application.service import OrganizationService
from app.organization.domain.entity import (
    Organization,
    OrganizationAuthProvider,
)
from main import create_app

HANSUNG_ID = UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def make_organization() -> Organization:
    organization = Organization(
        code="univ_hansung",
        name="한성대학교",
        auth_provider=OrganizationAuthProvider.HANSUNG_SIS,
    )
    organization.id = HANSUNG_ID
    return organization


def test_list_organizations_returns_200(client, monkeypatch):
    async def list_stub_organizations(*_args, **_kwargs):
        return [make_organization()]

    monkeypatch.setattr(
        OrganizationService,
        "list_organizations",
        list_stub_organizations,
    )

    response = client.get("/api/organizations")

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["code"] == "univ_hansung"


def test_get_organization_returns_200(client, monkeypatch):
    async def get_stub_organization(*_args, **_kwargs):
        return make_organization()

    monkeypatch.setattr(
        OrganizationService,
        "get_organization",
        get_stub_organization,
    )

    response = client.get(f"/api/organizations/{HANSUNG_ID}")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["id"] == str(HANSUNG_ID)
    assert body["data"]["auth_provider"] == "hansung_sis"


def test_get_organization_not_found_returns_404(client, monkeypatch):
    async def raise_not_found(*_args, **_kwargs):
        raise OrganizationNotFoundException()

    monkeypatch.setattr(
        OrganizationService,
        "get_organization",
        raise_not_found,
    )

    response = client.get(f"/api/organizations/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error_code"] == "ORGANIZATION__NOT_FOUND"


def test_get_organization_invalid_id_returns_422(client):
    response = client.get("/api/organizations/invalid-uuid")

    assert response.status_code == 422
    assert response.json()["error_code"] == "SERVER__REQUEST_VALIDATION_ERROR"
