from dependency_injector import containers, providers
from valkey.asyncio import from_url

from app.auth.adapter.output.persistence.auth_token_repository_adapter import (
    AuthTokenRepositoryAdapter,
)
from app.auth.adapter.output.persistence.valkey.auth_token import (
    ValkeyAuthTokenRepository,
)
from app.auth.application.service.auth import AuthService
from app.user.adapter.output.persistence.repository_adapter import (
    UserRepositoryAdapter,
)
from app.user.adapter.output.persistence.sqlalchemy.user import (
    UserSQLAlchemyRepository,
)
from core.config import config


class AuthContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.auth.adapter.input.api.v1.auth"]
    )

    valkey_client = providers.Singleton(
        from_url,
        config.VALKEY_URL,
        decode_responses=True,
    )
    auth_token_persistence = providers.Singleton(
        ValkeyAuthTokenRepository,
        client=valkey_client,
    )
    auth_token_repository = providers.Factory(
        AuthTokenRepositoryAdapter,
        repository=auth_token_persistence,
    )
    user_sqlalchemy_repository = providers.Singleton(UserSQLAlchemyRepository)
    user_repository = providers.Factory(
        UserRepositoryAdapter,
        repository=user_sqlalchemy_repository,
    )
    service = providers.Factory(
        AuthService,
        user_repository=user_repository,
        auth_token_repository=auth_token_repository,
    )
