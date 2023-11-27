from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from collections import defaultdict


from database import SessionLocal, engine
from models import Base, User, ExpenseSplit, ExpenseParticipant, ShareStatus
from schemas import UserCreate, ExpenseSplitCreate, ExpenseParticipantCreate, SplitType
from email_utils import send_expense_notification

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
def create_expense(expense: ExpenseSplitCreate, db: Session = Depends(get_db)):
    if not expense.participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="List of participants is required for split.",
        )

    db_expense = ExpenseSplit(
        amount=expense.amount,
        description=expense.description,
        split_type=expense.split_type,
        payer_id=expense.payer_id,
    )

    if expense.split_type == SplitType.EQUAL:
        num_participants = len(expense.participants) + 1
        share_amount = expense.amount / num_participants

        # Create ExpenseParticipant objects for each participant
        for user_id in expense.participants:
            user_instance = db.query(User).get(user_id)
            db_participant = ExpenseParticipant(
                user=user_instance,
                expense=db_expense,
                share=share_amount,
            )
            db.add(db_participant)

        db.commit()
        db.refresh(db_expense)
    elif expense.split_type == SplitType.EXACT:
        if len(expense.participants) != len(expense.exact_amounts):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exact amounts should be specified for all participants.",
            )

        if sum(expense.exact_amounts.values()) > expense.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exact amounts should not be more than the total expense amount.",
            )

        for user_id, exact_amount in expense.exact_amounts.items():
            print(user_id, exact_amount)
            user_instance = db.query(User).get(int(user_id))
            db_participant = ExpenseParticipant(
                user=user_instance,
                expense=db_expense,
                share=exact_amount,
            )
            db.add(db_participant)

        db.commit()
    elif expense.split_type == SplitType.PERCENTAGE:
        if len(expense.participants) != len(expense.percentages):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Percentages should be specified for all participants.",
            )

        if sum(expense.percentages.values()) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Percentages add up to more than 100%.",
            )

        # Create ExpenseParticipant objects for each participant with PERCENTAGE amounts
        for user_id, percentage in expense.percentages.items():
            user_instance = db.query(User).get(user_id)
            share_amount = (percentage / 100) * expense.amount
            db_participant = ExpenseParticipant(user=user_instance, share=share_amount)
            db.add(db_participant)

        db.commit()

    # Send expense notification emails to participants
    for user_id in expense.participants:
        user_instance = db.query(User).get(user_id)
        total_simplified_owed, total_simplified_owe = simplify_expenses(user_id)
        send_expense_notification(
            user_instance.email,
            total_amount_owed=expense.amount,
        )

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@app.post("/simplify-expenses/")
def simplify_expenses(user_id: int, db: Session = Depends(get_db)):
    expenses = (
        db.query(ExpenseSplit)
        .options(joinedload(ExpenseSplit.participants))
        .filter(
            or_(
                ExpenseSplit.payer_id == user_id,
                ExpenseParticipant.user_id == user_id,
            )
        )
        .all()
    )

    balances = defaultdict(float)
    for expense in expenses:
        if expense.payer_id == user_id:
            for participant in expense.participants:
                balances[participant.user_id] -= participant.share
        else:
            balances[expense.payer_id] += expense.amount

    simplified_balances = defaultdict(float)
    for user, balance in balances.items():
        if balance != 0:
            simplified_balances[user] += balance

    for debtor, amount in simplified_balances.items():
        print(f"User {user_id} owes {amount} to User {debtor}")

    return simplified_balances
