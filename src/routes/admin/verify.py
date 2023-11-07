from fastapi import HTTPException, Request


def verify_admin(request: Request):
    if request.session.get("admin", False) == False:
        raise HTTPException(302, detail="Not authorized", headers={"Location": "/admin/login"})
