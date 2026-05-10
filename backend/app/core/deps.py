from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.db.models import Member, MemberRole
from app.db import crud

# tells FastAPI where the login endpoint is
# automatically extracts Bearer token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_member(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Member:
    """
    Extracts and validates JWT token from request header.
    Returns the logged in member.
    Raises 401 if token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    member_id: str = payload.get("sub")
    if member_id is None:
        raise credentials_exception

    member = crud.get_member_by_id(db, UUID(member_id))
    if member is None:
        raise credentials_exception

    if not member.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    return member


def get_current_active_member(
    current_member: Member = Depends(get_current_member)
) -> Member:
    """Basic auth — any active member"""
    return current_member


def require_approver(
    current_member: Member = Depends(get_current_member)
) -> Member:
    """Only approvers and admins can access this route"""
    if current_member.role not in [MemberRole.approver, MemberRole.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Approver or admin role required"
        )
    return current_member


def require_admin(
    current_member: Member = Depends(get_current_member)
) -> Member:
    """Only admins can access this route"""
    if current_member.role != MemberRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return current_member