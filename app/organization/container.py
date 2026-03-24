from dependency_injector import containers, providers

from app.organization.adapter.output.persistence.sqlalchemy import (
    OrganizationSQLAlchemyRepository,
)
from app.organization.application.service import OrganizationService


class OrganizationContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.organization.adapter.input.api.v1.organization"]
    )

    repository = providers.Singleton(OrganizationSQLAlchemyRepository)
    service = providers.Factory(OrganizationService, repository=repository)
