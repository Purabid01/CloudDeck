from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import (
    verify_password, create_access_token, create_refresh_token
)
from app.db import crud
from app.db.schemas import (
    MemberCreate, MemberResponse, MemberLogin, Token, MessageResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=MemberResponse, status_code=201)
def register(data: MemberCreate, db: Session = Depends(get_db)):
    # check if email already exists
    existing = crud.get_member_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    member = crud.create_member(db, data)
    return member


@router.post("/login", response_model=Token)
def login(data: MemberLogin, db: Session = Depends(get_db)):
    # find member
    member = crud.get_member_by_email(db, data.email)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    # check password
    if not verify_password(data.password, member.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    # check active
    if not member.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabled"
        )
    # create tokens
    return Token(
        access_token=create_access_token(member.id),
        refresh_token=create_refresh_token(member.id)
    )


@router.post("/logout", response_model=MessageResponse)
def logout():
    # stateless JWT — client just deletes the token
    # in production you'd add token to a Redis blocklist
    return MessageResponse(message="Logged out successfully")