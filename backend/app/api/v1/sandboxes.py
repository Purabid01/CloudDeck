from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_member
from app.db import crud
from app.db.models import Member
from app.db.schemas import StageResponse

router = APIRouter(prefix="/stages", tags=["stages"])


@router.get("/", response_model=list[StageResponse])
def get_my_stages(
    db: Session = Depends(get_db),
    current_member: Member = Depends(get_current_active_member)
):
    return crud.get_stages_for_member(db, current_member.id)