from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException

from src.database import User, db
from src.utils.auth.token import jwt_decode


class AuthUser:
    def __init__(self, authorization: Annotated[Optional[str], Header()] = None):
        self.jwt = authorization
        self.token = None
        self.__user = None
        if self.jwt:
            self.token = jwt_decode(self.jwt)

    @property
    def user(self) -> User:
        if self.token is None:
            raise Exception("User is not authenticated")
        if self.__user is None:
            self.__user = db.s.first(User, id=self.token.user_id)
        return self.__user

    @property
    def is_guest(self):
        return self.token is None

    @property
    def subscribed(self):
        if self.is_guest:
            return False
        return self.user.subscribed


def any_user(auser: Annotated[AuthUser, Depends(AuthUser)]):
    return auser


def auth_user(auser: Annotated[AuthUser, Depends(AuthUser)]):
    if auser.is_guest:
        raise HTTPException(401, "User is not authenticated")
    return auser.user
