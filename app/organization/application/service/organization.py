from uuid import UUID

from app.organization.application.exception import (
    OrganizationNotFoundException,
)
from app.organization.domain.entity import Organization
from app.organization.domain.repository import OrganizationRepository
from app.organization.domain.usecase import OrganizationUseCase


class OrganizationService(OrganizationUseCase):
    def __init__(self, *, repository: OrganizationRepository):
        self.repository = repository

    async def get_organization(self, organization_id: UUID) -> Organization:
        organization = await self.repository.get_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundException()
        return organization

    async def list_organizations(self) -> list[Organization]:
        return list(await self.repository.list())
