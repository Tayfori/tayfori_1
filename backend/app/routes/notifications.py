"""
Bildirim yönetimi route'ları
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.models.user import User
from app.utils.security import get_current_user, require_coordinator_or_admin

router = APIRouter()


class NotificationCreate(BaseModel):
    title: str
    message: str
    notification_type: NotificationType = NotificationType.INFO
    recipient_user_id: int | None = None
    target_role: str | None = None
    is_broadcast: bool = False
    disaster_id: int | None = None
    priority: int = 0
    send_email: bool = False
    send_sms: bool = False
    send_push: bool = True


@router.get("/")
async def list_notifications(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bildirimleri listele"""
    query = db.query(Notification).filter(
        (Notification.recipient_user_id == current_user.id)
        | (Notification.is_broadcast == True)
        | (Notification.target_role == current_user.role.value)
    )

    if unread_only:
        query = query.filter(Notification.status != NotificationStatus.READ)

    notifications = (
        query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    )
    return notifications


@router.get("/{notification_id}")
async def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bildirim detaylarını al"""
    notification = (
        db.query(Notification).filter(Notification.id == notification_id).first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Bildirim bulunamadı")
    return notification


@router.post("/", status_code=201)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: User = Depends(require_coordinator_or_admin),
    db: Session = Depends(get_db),
):
    """Yeni bildirim oluştur"""
    new_notification = Notification(
        **notification_data.model_dump(),
        sender_id=current_user.id,
        status=NotificationStatus.PENDING,
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    # TODO: Gerçek bildirim gönderimi (email, SMS, push)
    # Şimdilik sadece veritabanına kaydet
    new_notification.status = NotificationStatus.SENT
    new_notification.sent_at = datetime.utcnow()
    db.commit()

    return new_notification


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bildirimi okundu olarak işaretle"""
    notification = (
        db.query(Notification).filter(Notification.id == notification_id).first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Bildirim bulunamadı")

    notification.status = NotificationStatus.READ
    notification.read_at = datetime.utcnow()
    db.commit()

    return {"message": "Bildirim okundu olarak işaretlendi"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Bildirimi sil"""
    notification = (
        db.query(Notification).filter(Notification.id == notification_id).first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Bildirim bulunamadı")

    db.delete(notification)
    db.commit()
    return {"message": "Bildirim silindi"}


@router.get("/unread/count")
async def get_unread_count(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Okunmamış bildirim sayısı"""
    count = (
        db.query(Notification)
        .filter(
            (Notification.recipient_user_id == current_user.id)
            | (Notification.is_broadcast == True)
            | (Notification.target_role == current_user.role.value)
        )
        .filter(Notification.status != NotificationStatus.READ)
        .count()
    )
    return {"unread_count": count}
