from typing import Any, Literal

from authlib.integrations.starlette_client import OAuth, StarletteOAuth2App

from .. import config

type AuthProvider = Literal["google"]

oauth = OAuth()
oauth.register(
    name="google",
    client_id=config.get("GOOGLE_CLIENT_ID"),
    client_secret=config.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def get_oauth_client(provider: AuthProvider) -> StarletteOAuth2App:
    return oauth.create_client(provider)  # type: ignore


__all__ = ("oauth", "get_oauth_client", "AuthProvider")
