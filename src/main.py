import socket
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from config import ENVIRONMENT
from routes.api import router as api_router
from routes.admin import router as admin_router

app = FastAPI(debug=ENVIRONMENT == "dev")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api_router)

@app.get("/ip")
def get_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return {
        "hostname": hostname,
        "ip_address": ip_address
    }

if ENVIRONMENT == "dev":
    app.include_router(admin_router)
    @app.get("/")
    def index():
        return RedirectResponse("/admin")