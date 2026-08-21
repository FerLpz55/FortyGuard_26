from typing import Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

DataT = TypeVar("DataT")


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[DataT]):
    items: list[DataT]
    total: int
    page: int
    size: int
    pages: int


class ErrorResponse(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    errors: list[dict] = []


class MessageResponse(BaseModel):
    message: str