from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from core.config import config
from core.domain.types import TokenType


class TokenHelper:
    @classmethod
    def create_token(cls, payload: dict[str, Any], token_type: TokenType, expires_delta: int) -> str:
        """
        Create a JWT token.

        Args:
            payload: Data to include in the token.
            token_type: The type of token (access/refresh).
            expires_delta: Expiration time in minutes.
        """
        to_encode = payload.copy()
        expire = datetime.now(UTC) + timedelta(minutes=expires_delta)

        to_encode.update({"exp": expire, "type": token_type.value})
        return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

    @classmethod
    def decode_token(cls, token: str) -> dict[str, Any]:
        """
        Decode a JWT token.
        """
        return jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
