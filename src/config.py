import os
import sys
from typing import Optional

from dotenv import load_dotenv

args = sys.argv[1:]
is_dev = "--dev" in args
is_prod = "--prod" in args
if not (is_dev ^ is_prod):
    print("Please specify either --dev or --prod")
    sys.exit(1)


load_dotenv(verbose=True, override=True)
load_dotenv(f".env.{"dev" if is_dev else "prod"}", verbose=True, override=True)

os.environ["ENVIRONMENT"] = "dev" if is_dev else "prod"

def get(key: str, default = "") -> str:
    return os.environ.get(key, default)
