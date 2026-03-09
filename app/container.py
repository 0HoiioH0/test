from dependency_injector import containers, providers
from dependency_injector.containers import DeclarativeContainer

from app.user.container import UserContainer


class AppContainer(DeclarativeContainer):
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration(
        packages=[
            "app.user.adapter.input.api.v1",
        ]
    )

    user = providers.Container(UserContainer)
