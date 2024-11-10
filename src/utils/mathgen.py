from typing import Dict, List, Optional

from config import logger
from config.clients import AsyncClient
from mathgen.gen.mathproblem import MathProblemModel

async def collect_models(supabase: AsyncClient, *model_names: str) -> Dict[str, MathProblemModel]:
    models_dict: Dict[str, MathProblemModel] = {}
    open_models = list(model_names)

    while open_models:
        model_name = open_models.pop()
        model = (await supabase.table("mathgen_models").select("*").eq("name", model_name).maybe_single().execute())
        if not model or not model.data:
            logger.warning(f"Model {model_name} not found")
            continue
        model = model.data

        groups = parse_groups(model["code"])
        if groups is not None:
            open_models.extend(groups)
        else:
            models_dict[model_name] = MathProblemModel(**model)
    
    return models_dict

def parse_groups(code: str) -> Optional[List[str]]:
    if not code.strip().startswith("@group"):
        return None
    return code.strip().split()[1:]
