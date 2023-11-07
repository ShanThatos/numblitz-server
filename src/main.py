from .base import cloudflared, fastapi_instance
from .routes import *

app = fastapi_instance.app


if __name__ == "__main__":
    import uvicorn

    from . import config

    ENVIRONMENT = config.get("ENVIRONMENT")
    PORT = int(config.get("PORT"))

    HOT_RELOAD = ENVIRONMENT == "dev"

    if config.get("RUN_TUNNEL", "no") == "yes" and not HOT_RELOAD:
        cloudflared.run_tunnel(config.get("TUNNEL_URL"), PORT)

    uvicorn.run("src.main:app", port=PORT, reload=HOT_RELOAD)
