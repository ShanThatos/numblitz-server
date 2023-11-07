import time

import jwt
from pydantic import BaseModel, Field, TypeAdapter

from src import config, utils


class UserToken(BaseModel):
    iat: int = Field(default_factory=lambda: int(time.time()))
    login_id: str = Field(default_factory=utils.random_string)
    user_id: int


UserTokenAdapter = TypeAdapter(UserToken)


def make_token(user_id: int) -> UserToken:
    return UserToken(user_id=user_id)


def jwt_encode(token: UserToken) -> str:
    return jwt.encode(token.model_dump(), config.get("SECRET_KEY"))


def jwt_decode(token: str) -> UserToken:
    return UserTokenAdapter.validate_python(
        jwt.decode(token, config.get("SECRET_KEY"), algorithms=["HS256"])
    )


__all__ = ["make_token", "jwt_encode", "jwt_decode"]
