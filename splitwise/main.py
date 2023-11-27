from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import SessionLocal, engine
from models import Base, User, Expense, ExpenseParticipant
from schemas import UserCreate, ExpenseCreate, ExpenseParticipantCreate, SplitType

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = User(**user.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered. Please use a different email.",
        )


@app.post("/expenses/")
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    if expense.split_type == SplitType.EQUAL:
        # Handle EQUAL split logic
        if not expense.participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="List of participants is required for EQUAL split.",
            )

        # Calculate equal shares
        num_participants = len(expense.participants)
        share_amount = expense.amount / num_participants

        # Create ExpenseParticipant objects for each participant
        for user_id in expense.participants:
            db_participant = ExpenseParticipant(user_id=user_id, share=share_amount)
            db.add(db_participant)

        db.commit()
    elif expense.split_type == SplitType.EXACT:
        # Handle EXACT split logic
        pass
    elif expense.split_type == SplitType.PERCENTAGE:
        # Handle PERCENTAGE split logic
        pass

    db_expense = Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.post("/expense-participants/")
def create_expense_participant(
    participant: ExpenseParticipantCreate, db: Session = Depends(get_db)
):
    db_participant = ExpenseParticipant(**participant.model_dump())
    db.add(db_participant)
    db.commit()
    db.refresh(db_participant)
    return db_participant


@app.get("/users/{user_id}/expenses/")
def get_user_expenses(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.expenses


@app.get("/users/{user_id}/balances/")
def get_user_balances(user_id: int, db: Session = Depends(get_db)):
    # Implement logic to calculate balances based on expenses and participants
    # Return a dictionary of balances
    pass
