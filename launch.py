import subprocess
import sys

if __name__ == "__main__":
    if "categories" in sys.argv:
        subprocess.run("cd src && python -m scripts.upsert_categories", shell=True)
    else:
        import uvicorn
        uvicorn.run("main:app", app_dir="src", host="0.0.0.0", reload=True)