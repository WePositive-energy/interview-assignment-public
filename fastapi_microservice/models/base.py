from sqlmodel import (
    Field,  # pyright:ignore[reportUnknownVariableType]
    SQLModel,
)


class BaseModel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
