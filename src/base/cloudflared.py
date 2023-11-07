
import atexit
import subprocess
from pathlib import Path

import psutil


def __fully_kill_process(process):
    if process is None: return
    for child_process in psutil.Process(process.pid).children(True):
        try:
            child_process.kill()
        except psutil.NoSuchProcess:
            pass
    process.kill()

def run_tunnel(tunnel_url, port, blocking=False):
    subprocess.run(f"cloudflared tunnel create {tunnel_url}", shell=True)
    subprocess.run(f"cloudflared tunnel route dns --overwrite-dns {tunnel_url} {tunnel_url}", shell=True)

    cred_file = f"_temp/{tunnel_url.replace(".", "_")}_creds.json"
    Path(cred_file).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(f"cloudflared tunnel token --cred-file {cred_file} {tunnel_url}", shell=True)
    
    run_cmd = f"cloudflared tunnel run --cred-file {cred_file} --url localhost:{port} {tunnel_url}"
    if blocking:
        process = subprocess.run(run_cmd, shell=True)
    else:
        process = subprocess.Popen(run_cmd, shell=True)
        atexit.register(lambda: __fully_kill_process(process))

if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv(".env.dev")
    run_tunnel(os.environ.get("TUNNEL_URL"), int(os.environ.get("PORT", "0")), blocking=True)
