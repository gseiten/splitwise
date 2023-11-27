from pydantic import BaseModel, Field
from enum import Enum
from typing import List


class SplitType(str, Enum):
    EQUAL = "EQUAL"
    EXACT = "EXACT"
    PERCENTAGE = "PERCENTAGE"


class UserCreate(BaseModel):
    name: str
    email: str
    mobile_number: str


class ExpenseCreate(BaseModel):
    amount: float
    description: str
    payer_id: int
    split_type: SplitType
    participants: List[int] = Field(..., title="List of participant IDs")


class ExpenseParticipantCreate(BaseModel):
    user_id: int
    expense_id: int
    share: float
