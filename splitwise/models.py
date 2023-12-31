# models.py

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum
from sqlalchemy.orm import relationship
import enum

from database import Base


class SplitType(enum.Enum):
    EQUAL = "EQUAL"
    EXACT = "EXACT"
    PERCENTAGE = "PERCENTAGE"


class ShareStatus(enum.Enum):
    PAID = "PAID"
    PENDING = "PENDING"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    mobile_number = Column(String)


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    description = Column(String)
    split_type = Column(Enum(SplitType))
    payer_id = Column(Integer, ForeignKey("users.id"))

    payer = relationship("User", back_populates="expenses")
    participants = relationship("ExpenseParticipant", back_populates="expense")


class ExpenseParticipant(Base):
    __tablename__ = "expense_participants"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expense_id = Column(
        Integer, ForeignKey("expense_splits.id")
    )  # Corrected ForeignKey
    share = Column(Float)
    status = Column(Enum(ShareStatus), default=ShareStatus.PENDING)

    user = relationship("User", back_populates="expense_participations")
    expense = relationship("ExpenseSplit", back_populates="participants")


User.expenses = relationship("ExpenseSplit", back_populates="payer")
User.expense_participations = relationship("ExpenseParticipant", back_populates="user")
