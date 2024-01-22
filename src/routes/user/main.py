from typing import Annotated

from fastapi import Depends

from src.base.fastapi_instance import app
from src.database.models import User
from src.utils.auth.depend import auth_user


@app.get("/user")
def user_index(user: Annotated[User, Depends(auth_user)]):
    return user.as_dict(include=["id", "name", "email"])
