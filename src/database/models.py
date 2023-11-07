import json
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Self,
    Sequence,
    Set,
    Type,
    Unpack,
    override,
)

from sqlalchemy import ColumnExpressionArgument, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.types import JSON

from .main import db

# @cache
# def get_table_info(table: str):
#     return Base.metadata.tables[table].primary_key.columns[0]


# T = TypeVar("T")
class ModelExtensions:
    # @classmethod
    # async def get[T](cls: T, id: int) -> T:
    #     pk = get_table_info(table.__tablename__)
    #     return await fetch_one(select(table).where(pk == id))

    # @classmethod
    # async def first(table: T, *expressions, error=False) -> T:
    #     result = await fetch_one(select(table).where(*expressions))
    #     if result is None and error:
    #         raise CommonError(f"{table.__name__} Error", f"{table.__name__} not found")
    #     return result

    # @classmethod
    # async def filter(table: T, *expressions) -> List[T]:
    #     return await fetch_all(select(table).where(*expressions))

    # @classmethod
    # async def count(table: T, *expressions) -> int:
    #     return await execute(select(func.count()).select_from(table).where(*expressions))

    # @classmethod
    # async def insert(table: T, **kwargs):
    #     return await execute(insert(table).values(**kwargs))

    # @classmethod
    # async def update(table: T, id: int, **kwargs):
    #     pk = get_table_info(table.__tablename__)
    #     return await execute(update(table).where(pk == id).values(**kwargs))

    # @classmethod
    # def get[T](cls: T, id: int) -> T:
    #     ...

    @classmethod
    def get[T](cls: Type[T], id: int | str) -> T:
        return db.s.get_one(cls, id)

    @classmethod
    def get_or_none[T](cls: Type[T], id: int | str) -> T | None:
        return db.s.get(cls, id)

    @classmethod
    def all[T](cls: Type[T], *expressions: ColumnExpressionArgument[bool]) -> Sequence[T]:
        return db.s.execute(select(cls).where(*expressions)).scalars().all()

    @classmethod
    def all_as_dict(cls, *expressions: ColumnExpressionArgument[bool]) -> List[Dict]:
        return [x.as_dict() for x in cls.all(*expressions)]

    def get_all_fields(self) -> Set[str]:
        return set(c.name for c in self.__table__.columns)  # type: ignore

    def as_dict(
        self, include: Optional[Iterable[str]] = None, exclude: Optional[Iterable[str]] = None
    ) -> dict:
        columns = self.get_all_fields()
        if include is not None:
            columns = columns.intersection(include)
        if exclude is not None:
            columns = columns.difference(exclude)
        return {c: getattr(self, c) for c in columns}


class User(db.Model, ModelExtensions):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    user_id: Mapped[str]
    provider: Mapped[str]
    subscribed: Mapped[bool] = mapped_column(server_default="false")
    admin: Mapped[bool] = mapped_column(server_default="false")

    __table_args__ = (UniqueConstraint("user_id", "provider", name="unique_user_constraint"),)


class ModelProgress(db.Model, ModelExtensions):
    __tablename__ = "model_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    model_id: Mapped[int]
    progress: Mapped[int]

    __table_args__ = (
        UniqueConstraint("user_id", "model_id", name="unique_model_progress_constraint"),
    )


class Workbook(db.Model, ModelExtensions):
    __tablename__ = "workbooks"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int]
    name: Mapped[str]
    description: Mapped[str] = mapped_column(server_default="")
    data: Mapped[dict] = mapped_column(type_=JSON)


class ProblemCategory(db.Model, ModelExtensions):
    __tablename__ = "problem_categories"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(server_default="")
    display: Mapped[str] = mapped_column(server_default="")

    models: Mapped[Set["ProblemModel"]] = relationship(back_populates="category")


class ProblemModel(db.Model, ModelExtensions):
    __tablename__ = "problem_models"

    id: Mapped[str] = mapped_column(primary_key=True)
    category_id: Mapped[str] = mapped_column(ForeignKey(ProblemCategory.id))
    name: Mapped[str] = mapped_column(server_default="")
    display: Mapped[str] = mapped_column(server_default="")
    difficulty: Mapped[int] = mapped_column(server_default="1")
    unlocked: Mapped[bool] = mapped_column(server_default="false")
    code: Mapped[str] = mapped_column(server_default="")
    explanation: Mapped[str] = mapped_column(server_default="[]")
    answer_format: Mapped[str] = mapped_column(server_default="auto")
    rtl: Mapped[bool] = mapped_column(server_default="false")
    units: Mapped[str] = mapped_column(server_default="")

    category: Mapped["ProblemCategory"] = relationship(back_populates="models")

    @override
    def get_all_fields(self):
        return super().get_all_fields() | {"image_display"}

    @property
    def image_display(self):
        return json.loads(self.display)[1]

    def get_display_data(self, subscribed=False):
        data = self.as_dict(
            include=["id", "category_id", "name", "image_display", "difficulty", "unlocked"]
        )
        if subscribed:
            data["locked"] = False

        return data

    def allow_access(self, subscribed=False):
        return self.unlocked or subscribed


# future: WorkbookProgress

__all__ = ("User", "ModelProgress", "Workbook", "ProblemCategory", "ProblemModel")
