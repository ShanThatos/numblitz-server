from urllib.parse import urlencode

from fastapi import Request
from fastapi.responses import RedirectResponse

from src.base.fastapi_instance import app
from src.base.oauth import AuthProvider, get_oauth_client
from src.database.main import db
from src.database.models import User

from ...utils.auth.token import *


@app.get("/login/{provider}")
async def auth_login(request: Request, provider: AuthProvider, redirect: str):
    request.session["final_redirect"] = redirect
    redirect_uri = request.url_for("auth_callback", provider=provider)
    return await get_oauth_client(provider).authorize_redirect(request, redirect_uri)


@app.get("/login/callback/{provider}")
async def auth_callback(request: Request, provider: AuthProvider):
    token = await get_oauth_client(provider).authorize_access_token(request)
    info = token["userinfo"]

    user: User = db.s.first(User, provider=provider, user_id=info.sub)
    if not user:
        user = db.s.create(
            User, provider=provider, name=info.name, email=info.email, user_id=info.sub
        )
    else:
        user.email = info.email

    db.s.commit()

    token = jwt_encode(make_token(user.id))
    base_url = request.session["final_redirect"]
    return RedirectResponse(base_url + "?" + urlencode({"token": token}))
