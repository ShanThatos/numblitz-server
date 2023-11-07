from collections import Counter
from pathlib import Path
from typing import List, Literal, Optional

from mathgen import MathGenCode
from pydantic import BaseModel, Field, model_validator

# class ProblemModel(BaseModel):
#     id: str
#     category_id: str = Field(default="")
#     name: str = Field(default="")
#     display: str = Field(default="")
#     difficulty: int = Field(default=1, ge=1, le=3)
#     locked: bool = Field(default=True)
#     code: MathGenCode = Field(default="")
#     explanation: str = Field(default="[]")
#     answer_format: Literal["auto", "number", "decimal", "money", "fraction", "mixed"] = Field(
#         default="auto"
#     )
#     ltr: bool = Field(default=True)
#     units: str = Field(default="")

#     def get_display_data(self, subscribed: bool = False):
#         data = self.model_dump(
#             include={"id", "category_id", "name", "display", "difficulty", "locked"}
#         )
#         if subscribed:
#             data["locked"] = False
#         return data


# class ProblemCategory(BaseModel):
#     id: str
#     name: str = Field(default="")
#     display: str = Field(default="")


# class ModelsData(BaseModel):
#     categories: List[ProblemCategory]
#     models: List[ProblemModel]

#     @model_validator(mode="after")
#     def validate(self):
#         for id, count in Counter(x.id for x in self.categories).items():
#             if count > 1:
#                 raise ValueError(f"Duplicate category id {id}")
#         for id, count in Counter(x.id for x in self.models).items():
#             if count > 1:
#                 raise ValueError(f"Duplicate model id {id}")
#         return self


# MGDATA = ModelsData.model_validate_json(Path("./models.json").read_bytes())


# def get_model(model_id: str) -> Optional[ProblemModel]:
#     return next((m for m in MGDATA.models if m.id == model_id), None)


# def save_models():
#     Path("./models.json").write_text(MGDATA.model_dump_json(indent=4, exclude_defaults=True))
