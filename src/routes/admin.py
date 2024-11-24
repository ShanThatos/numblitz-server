import time
from typing import List

from fastapi import APIRouter, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from mathgen.gen.generate import MathProblemGenerator
from mathgen.gen.mathproblem import MathProblemModel
from config import logger
from config.clients import SupabaseClientDep, SupabaseAsyncClientDep
from utils.jinja import render_macro, render_template
from utils.mathgen import collect_models, parse_groups

router = APIRouter(prefix="/admin")

class MathgenModelData(BaseModel):
    name: str
    display_name: str
    category_name: str
    code: str
    format: str
    units: str
    rtl: bool = False
    hidden: bool = False
    difficulty: int
    display_image: str
    display_image_equation: str
    explanation: str

@router.get("/")
def index(supabase: SupabaseClientDep):
    models = supabase.table("mathgen_models").select("*").execute().data
    categories = supabase.table("mathgen_categories").select("*").execute().data
    return HTMLResponse(render_template("index.html", models=models, categories=categories))

@router.get("/models/{name}")
def model(supabase: SupabaseClientDep, name: str):
    model = supabase.table("mathgen_models").select("*").eq("name", name).maybe_single().execute()
    if not model:
        return RedirectResponse(router.prefix)
    model = model.data
    model["display_name"] = model.get("display_name", "").replace("\n", "\\n")
    categories = supabase.table("mathgen_categories").select("*").execute().data
    return HTMLResponse(render_template("model.html", model=model, categories=categories))

@router.post("/models/{name}")
async def model_update(supabase: SupabaseClientDep, name: str, model: MathgenModelData):
    model.display_name = model.display_name.replace("\\n", "\n")
    supabase.table("mathgen_models").update(model.model_dump()).eq("name", name).execute()
    return HTMLResponse("", headers={"HX-Redirect": f"{router.prefix}/models/{model.name}"})

@router.post("/models/{name}/preview")
async def model_preview(supabase: SupabaseAsyncClientDep, name: str, model_data: MathgenModelData):
    try:
        base_model = MathProblemModel(**model_data.model_dump())
        models = [base_model]
        if (groups := parse_groups(model_data.code)) is not None:
            models = list((await collect_models(supabase, *groups)).values())

        problems = MathProblemGenerator.generate_multiple(models, 20, 1)
        return HTMLResponse("\n".join(render_macro("macros.html:render_problem_preview", p) for p in problems))
    except Exception as e:
        logger.exception(f"Error generating preview {str(e)}")
        return HTMLResponse(str(e), headers={"HX-Retarget": "#previewerror"})

@router.get("/models/{name}/duplicate")
def model_duplicate(supabase: SupabaseClientDep, name: str):
    model = supabase.table("mathgen_models").select("*").eq("name", name).maybe_single().execute()
    if not model:
        return RedirectResponse(router.prefix)
    model = model.data
    model["name"] = f"{model['name']}_copy_{int(time.time())}"
    model["hidden"] = True
    del model["id"]
    del model["created_at"]
    del model["order"]
    supabase.table("mathgen_models").insert(model).execute()
    return RedirectResponse(f"{router.prefix}/models/{model['name']}")

@router.post("/models/{name}/delete")
def model_delete(supabase: SupabaseClientDep, name: str):
    supabase.table("mathgen_models").delete().eq("name", name).execute()
    return Response(headers={"HX-Refresh": "true"})

@router.get("/categories")
def categories(supabase: SupabaseClientDep):
    categories = supabase.table("mathgen_categories").select("*").execute().data
    return HTMLResponse(render_template("categories.html", categories=categories))

@router.get("/categories/{name}")
def category(supabase: SupabaseClientDep, name: str):
    category = supabase.table("mathgen_categories").select("*").eq("name", name).maybe_single().execute()
    if not category:
        return RedirectResponse(router.prefix)
    models = supabase.table("mathgen_models").select("name, display_name, display_image, hidden, order").eq("category_name", name).eq("hidden", False).order("order").execute().data
    return HTMLResponse(render_template("category.html", category=category.data, models=models))

@router.post("/categories/{name}")
def category_update(supabase: SupabaseClientDep, name: str, order: List[str]):
    upsert_vals = [{"name": name, "order": i} for i, name in enumerate(order)]
    supabase.table("mathgen_models").upsert(upsert_vals, on_conflict="name").execute()
    return {}