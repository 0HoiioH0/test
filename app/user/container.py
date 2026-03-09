from dependency_injector import containers, providers

from app.user.adapter.output.persistence.repository import UserPersistenceAdapter
from app.user.application.service.user import UserService


class UserContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.user.adapter.input.api.v1.user"])

    repository = providers.Factory(UserPersistenceAdapter)
    service = providers.Factory(UserService, user_repo=repository)
