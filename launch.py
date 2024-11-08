import os
import subprocess
import sys

if __name__ == "__main__":
    if "tex2image" in sys.argv:
        args = sys.argv.copy()[1:]
        args.remove("tex2image")
        subprocess.run(f"python -m src.scripts.tex2image {" ".join(args)}", shell=True)
    elif "categories" in sys.argv:
        subprocess.run("cd src && python -m scripts.upsert_categories", shell=True)
    else:
        import uvicorn
        PORT = int(os.environ.get("PORT", 8000))
        RELOAD = os.environ.get("ENVIRONMENT") == "dev"
        uvicorn.run("main:app", app_dir="src", host="0.0.0.0", port=PORT, reload=RELOAD)