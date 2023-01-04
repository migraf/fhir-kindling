from typing import Optional

from pydantic import root_validator
from sqlmodel import Field, SQLModel


class ServerCredentials(SQLModel):
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    token: Optional[str] = Field(default=None)

    @root_validator
    def validate_credentials(cls, values):
        if (
            values["username"] is None
            and values["password"] is None
            and values["token"] is None
        ):
            raise ValueError(
                "At least one of username, password or token must be provided"
            )
        return values


class Server(SQLModel):
    name: Optional[str] = None
    api_url: Optional[str] = None
    credentials: Optional[ServerCredentials] = None
