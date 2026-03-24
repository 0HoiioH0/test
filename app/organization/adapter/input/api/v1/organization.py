from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.auth.adapter.input.api.v1.deps import require_admin_user
from app.auth.domain.entity import CurrentUser
from app.organization.adapter.input.api.v1.request import (
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
)
from app.organization.adapter.input.api.v1.response import (
    OrganizationListResponse,
    OrganizationPayload,
    OrganizationResponse,
)
from app.organization.container import OrganizationContainer
from app.organization.domain.command import (
    CreateOrganizationCommand,
    UpdateOrganizationCommand,
)
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


@router.post("", response_model=OrganizationResponse)
@inject
async def create_organization(
    request: CreateOrganizationRequest,
    current_user: CurrentUser = Depends(require_admin_user),
    usecase: OrganizationUseCase = Depends(
        Provide[OrganizationContainer.service]
    ),
):
    del current_user
    organization = await usecase.create_organization(
        CreateOrganizationCommand(**request.model_dump())
    )
    return OrganizationResponse(data=_to_payload(organization))


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


@router.patch("/{organization_id}", response_model=OrganizationResponse)
@inject
async def update_organization(
    organization_id: UUID,
    request: UpdateOrganizationRequest,
    current_user: CurrentUser = Depends(require_admin_user),
    usecase: OrganizationUseCase = Depends(
        Provide[OrganizationContainer.service]
    ),
):
    del current_user
    organization = await usecase.update_organization(
        organization_id,
        UpdateOrganizationCommand(**request.model_dump(exclude_unset=True)),
    )
    return OrganizationResponse(data=_to_payload(organization))


@router.delete("/{organization_id}", response_model=OrganizationResponse)
@inject
async def delete_organization(
    organization_id: UUID,
    current_user: CurrentUser = Depends(require_admin_user),
    usecase: OrganizationUseCase = Depends(
        Provide[OrganizationContainer.service]
    ),
):
    del current_user
    organization = await usecase.delete_organization(organization_id)
    return OrganizationResponse(data=_to_payload(organization))
