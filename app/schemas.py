from datetime import date as date_type
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TransactionBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category: str = Field(min_length=1, max_length=100)
    date: date_type


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    amount: float | None = Field(default=None, gt=0)
    type: Literal["income", "expense"] | None = None
    category: str | None = Field(default=None, min_length=1, max_length=100)
    date: date_type | None = None


class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
