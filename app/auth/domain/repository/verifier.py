from abc import ABC, abstractmethod

from app.auth.domain.entity import AuthenticatedIdentity
from app.organization.domain.entity import Organization


class IdentityVerifier(ABC):
    @abstractmethod
    async def verify(
        self,
        *,
        organization: Organization,
        login_id: str,
        password: str,
    ) -> AuthenticatedIdentity:
        """Verify user credentials against an organization identity system."""
