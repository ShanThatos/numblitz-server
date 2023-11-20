from typing import Annotated

from fastapi import Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from src import config
from src.base.fastapi_instance import app
from src.database.models import ProblemCategory
from src.routes.admin.verify import verify_admin
from src.utils.jinja.jinja_utils import render_template


@app.get("/admin/login")
def admin_login():
    return HTMLResponse(render_template("admin/login.html"))


@app.post("/admin/login")
def admin_login_post(
    request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()]
):
    if username == config.get("ADMIN_USERNAME") and password == config.get("ADMIN_PASSWORD"):
        request.session["admin"] = True
    return Response(headers={"HX-Redirect": "/admin"})


@app.get("/admin/logout")
def admin_logout(request: Request):
    del request.session["admin"]
    return RedirectResponse("/admin")


@app.get("/admin", dependencies=[Depends(verify_admin)])
def admin_index():
    return HTMLResponse(render_template("admin/index.html", categories=ProblemCategory.all()))
