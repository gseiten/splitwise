from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional, Dict


class SplitType(str, Enum):
    EQUAL = "EQUAL"
    EXACT = "EXACT"
    PERCENTAGE = "PERCENTAGE"


class UserCreate(BaseModel):
    name: str
    email: str
    mobile_number: str


class ExpenseSplitCreate(BaseModel):
    amount: float
    description: str
    payer_id: int
    split_type: SplitType
    participants: List[int]  # For all split types
    exact_amounts: Optional[Dict[int, float]] = None  # For EXACT split type
    percentages: Optional[Dict[int, float]] = None  # For PERCENTAGE split type


class ExpenseParticipantCreate(BaseModel):
    user_id: int
    expense_id: int
    share: float
