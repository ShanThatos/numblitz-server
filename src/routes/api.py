import random
import time

from fastapi import APIRouter, HTTPException
from typing import List, Optional

from mathgen.gen.generate import MathProblemGenerator
from mathgen.gen.mathproblem import MathProblem
from utils.mathgen import collect_models

router = APIRouter(prefix="/api")

@router.get("/")
def index():
    return {"message": "lol hi what are you doing here?"}

@router.get("/generate/model/{model_name}")
def generate(model_name: str, amount: int = 10, seed: Optional[int] = None):
    print(f"Generating {amount} problems for {model_name}")
    models = collect_models(model_name)
    if not models:
        raise HTTPException(status_code=404, detail="Model not found")
    
    problems = MathProblemGenerator.generate_multiple(models.values(), amount, seed)
    return {"problems": problems}
