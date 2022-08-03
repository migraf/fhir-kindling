from typing import List, Optional

from pydantic.fields import ModelField
from sqlmodel import SQLModel


class ResourceField(SQLModel):
    name: str
    type: str
    description: Optional[str] = None
    title: Optional[str] = None


class ResourceFields(SQLModel):
    resource: str
    fields: List[ResourceField]
