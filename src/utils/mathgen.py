import random
from collections import Counter
from typing import List, Optional

from mathgen import MathProblem, MathProblemGenerator, MathProblemModel

from src.database.models import ProblemModel


def generate_multiple(
    model_id: Optional[str] = None,
    model: Optional[MathProblemModel] = None,
    count: int = 1,
    seed: Optional[int] = None,
):
    if model_id is None and model is None:
        raise ValueError("Must provide either model_id or model")
    if model_id is not None and model is not None:
        raise ValueError("Cannot provide both model_id and model")

    if model is None:
        model = ProblemModel.get(model_id).get_mathgen_model()  # type: ignore

    group_prefix = "@group "

    if not model.code.startswith(group_prefix):
        return MathProblemGenerator(model, seed=seed).generate_multiple(count)

    model_ids = model.code[len(group_prefix) :].strip().split()
    rng = random.Random(seed)
    chosen_model_ids = rng.choices(model_ids, k=count)
    counts = Counter(chosen_model_ids)
    problems: List[MathProblem] = []
    for model_id, count in counts.items():
        problems.extend(generate_multiple(model_id=model_id, count=count, seed=seed))
    rng.shuffle(problems)
    return problems
