"""
Notification Center API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..database import get_db
from ..dependencies import get_current_user_optional

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=schemas.NotificationListOut)
def list_notifications(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional),
):
    user_id = current_user.user_id if current_user else None
    # Seed demo notifications on first visit
    if user_id:
        crud.seed_demo_notifications(db, user_id)
    total, unread, items = crud.get_notifications(db, user_id=user_id, limit=limit, offset=offset)
    return {
        "total": total,
        "unread_count": unread,
        "items": items,
    }


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional),
):
    user_id = current_user.user_id if current_user else None
    count = crud.get_unread_count(db, user_id=user_id)
    return {"unread_count": count}


@router.post("/{notification_id}/read", response_model=schemas.NotificationOut)
def mark_read(
    notification_id: str,
    db: Session = Depends(get_db),
):
    notif = crud.mark_notification_read(db, notification_id, is_read=True)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif


@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    crud.mark_all_notifications_read(db, current_user.user_id)
    return {"success": True}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: str,
    db: Session = Depends(get_db),
):
    ok = crud.delete_notification(db, notification_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"deleted": True}
