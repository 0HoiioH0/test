from uuid import UUID, uuid4

import pytest

from app.organization.application.exception import (
    OrganizationNotFoundException,
)
from app.organization.application.service import OrganizationService
from app.organization.domain.entity import (
    Organization,
    OrganizationAuthProvider,
)
from app.organization.domain.repository import OrganizationRepository

HANSUNG_ID = UUID("11111111-1111-1111-1111-111111111111")


class InMemoryOrganizationRepository(OrganizationRepository):
    def __init__(self, organizations: list[Organization] | None = None):
        self.organizations = {
            organization.id: organization
            for organization in organizations or []
        }

    async def save(self, entity: Organization) -> Organization:
        self.organizations[entity.id] = entity
        return entity

    async def get_by_id(self, entity_id: UUID) -> Organization | None:
        return self.organizations.get(entity_id)

    async def get_by_code(self, code: str) -> Organization | None:
        return next(
            (
                organization
                for organization in self.organizations.values()
                if organization.code == code
            ),
            None,
        )

    async def list(self) -> list[Organization]:
        return list(self.organizations.values())


def make_organization() -> Organization:
    organization = Organization(
        code="univ_hansung",
        name="한성대학교",
        auth_provider=OrganizationAuthProvider.HANSUNG_SIS,
    )
    organization.id = HANSUNG_ID
    return organization


@pytest.mark.asyncio
async def test_list_organizations_returns_all_organizations():
    service = OrganizationService(
        repository=InMemoryOrganizationRepository([make_organization()])
    )

    organizations = await service.list_organizations()

    assert len(organizations) == 1
    assert organizations[0].code == "univ_hansung"


@pytest.mark.asyncio
async def test_get_organization_returns_organization():
    service = OrganizationService(
        repository=InMemoryOrganizationRepository([make_organization()])
    )

    organization = await service.get_organization(HANSUNG_ID)

    assert organization.name == "한성대학교"


@pytest.mark.asyncio
async def test_get_organization_not_found_raises():
    service = OrganizationService(repository=InMemoryOrganizationRepository())

    with pytest.raises(OrganizationNotFoundException):
        await service.get_organization(uuid4())
