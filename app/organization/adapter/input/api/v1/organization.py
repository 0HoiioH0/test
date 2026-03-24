from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.organization.adapter.input.api.v1.response import (
    OrganizationListResponse,
    OrganizationPayload,
    OrganizationResponse,
)
from app.organization.container import OrganizationContainer
from app.organization.domain.entity import Organization
from app.organization.domain.usecase import OrganizationUseCase

router = APIRouter(prefix="/organizations", tags=["organizations"])


def _to_payload(organization: Organization) -> OrganizationPayload:
    return OrganizationPayload(
        id=str(organization.id),
        code=organization.code,
        name=organization.name,
        auth_provider=organization.auth_provider.value,
        is_active=organization.is_active,
    )


@router.get("", response_model=OrganizationListResponse)
@inject
async def list_organizations(
    usecase: OrganizationUseCase = Depends(
        Provide[OrganizationContainer.service]
    ),
):
    organizations = await usecase.list_organizations()
    return OrganizationListResponse(
        data=[_to_payload(organization) for organization in organizations]
    )


@router.get("/{organization_id}", response_model=OrganizationResponse)
@inject
async def get_organization(
    organization_id: UUID,
    usecase: OrganizationUseCase = Depends(
        Provide[OrganizationContainer.service]
    ),
):
    organization = await usecase.get_organization(organization_id)
    return OrganizationResponse(data=_to_payload(organization))
