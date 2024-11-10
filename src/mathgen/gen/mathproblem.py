from typing import Annotated, Any, Literal, Optional, Tuple

from pydantic import AfterValidator, BaseModel, Field, TypeAdapter

PREFIXES = ["var", "condition", "question", "textquestion", "answer", "choices", "numchoices", "order", "key", "units"]


def split_prefix(line: str) -> Optional[Tuple[str, str]]:
    line = line.strip()
    for prefix in PREFIXES:
        if line.startswith(f"@{prefix} "):
            return prefix, line[len(prefix) + 2 :].strip()
    return None


def mathgen_validator(code: str) -> str:
    if code.strip().startswith("@group"):
        return code
    lines = (x for x in code.splitlines() if x.strip())
    for line in lines:
        if split_prefix(line) is None:
            raise ValueError(f"invalid line, must start with one of {PREFIXES}")
    return code


MathGenCode = Annotated[str, AfterValidator(mathgen_validator)]

type MathProblemFormat = Literal[
    "auto", "number", "decimal", "money", "fraction", "mixed", "multiplechoice"
]


class MathProblemModel(BaseModel):
    name: str
    code: MathGenCode
    format: MathProblemFormat = "auto"
    units: str = ""
    rtl: bool = False


MathProblemModelAdapter = TypeAdapter(MathProblemModel)


class MathProblem(BaseModel):
    name: str
    key: Optional[Any] = Field(None, exclude=True)
    question: str = ""
    choices: Optional[list[str]] = None
    numchoices: Optional[int] = Field(None, exclude=True)
    order: Optional[list[str]] = Field(None, exclude=True)
    answer: str = ""
    format: MathProblemFormat = "auto"
    units: str = ""
    rtl: bool = False
