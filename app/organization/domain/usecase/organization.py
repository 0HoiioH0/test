from abc import ABC, abstractmethod
from uuid import UUID

from app.organization.domain.entity import Organization


class OrganizationUseCase(ABC):
    @abstractmethod
    async def get_organization(self, organization_id: UUID) -> Organization:
        """Get organization."""

    @abstractmethod
    async def list_organizations(self) -> list[Organization]:
        """List organizations."""
