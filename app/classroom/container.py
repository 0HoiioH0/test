from dependency_injector import containers, providers

from app.classroom.adapter.output.persistence.sqlalchemy import (
    ClassroomSQLAlchemyRepository,
)
from app.classroom.application.service import ClassroomService


class ClassroomContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.classroom.adapter.input.api.v1.classroom"]
    )

    repository = providers.Singleton(ClassroomSQLAlchemyRepository)
    service = providers.Factory(ClassroomService, repository=repository)
