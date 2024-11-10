import os

from subprocess import check_output

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from config import ENVIRONMENT
from config.clients import supabase
from routes.api import router as api_router
from routes.admin import router as admin_router

app = FastAPI(debug=ENVIRONMENT == "dev")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api_router)

@app.middleware("http")
async def ping_supabase(request: Request, call_next):
    for i in range(5):
        try:
            supabase.rpc("health").execute()
            break
        except Exception as e:
            if i < 4:
                print("Supabase health check failed, retrying...")
            else:
                raise e
    return await call_next(request)

if os.name != "nt":
    @app.get("/ip")
    def get_ip():
        hostname = check_output("hostname", shell=True, text=True).strip()
        ip_address = check_output("hostname -I", shell=True, text=True).strip()
        return {
            "hostname": hostname,
            "ip_address": ip_address
        }

if ENVIRONMENT == "dev":
    app.include_router(admin_router)
    @app.get("/")
    def index():
        return RedirectResponse("/admin")