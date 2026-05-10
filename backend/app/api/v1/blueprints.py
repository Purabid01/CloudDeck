from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_member, require_approver
from app.db import crud
from app.db.models import Member
from app.db.schemas import ReviewResponse, ReviewDecision

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/pending", response_model=list[ReviewResponse])
def get_pending_reviews(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_member: Member = Depends(require_approver)  # approver only
):
    return crud.get_pending_reviews(db, skip, limit)


@router.post("/{task_id}/decide", response_model=ReviewResponse)
def decide_review(
    task_id: UUID,
    decision: ReviewDecision,
    db: Session = Depends(get_db),
    current_member: Member = Depends(require_approver)
):
    review = crud.decide_review(db, task_id, current_member.id, decision)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review