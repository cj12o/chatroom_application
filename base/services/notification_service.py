from django.db import transaction

from base.logger import logger
from base.models import Notification, PersonalNotification


def get_unread_notifications(user):
    """Return unread personal notifications for a user with related data prefetched."""
    return (
        user.personalnotification_user
        .filter(mark_read=False)
        .select_related('notification__room', 'notification__message')
    )


def mark_notifications_read(ids: list[int]) -> None:
    """Bulk-mark notifications as read."""
    PersonalNotification.objects.filter(id__in=ids).update(mark_read=True)


def get_unread_count(user) -> int:
    """Return count of unread notifications for a user."""
    return user.personalnotification_user.filter(mark_read=False).count()


def create_notification(room_id: int, message_id: int, notify_text: str) -> Notification:
    """
    Create a Notification and populate PersonalNotifications for all room members.
    Called from the Celery task.
    """
    from base.models import Room, Message

    with transaction.atomic():
        room = Room.objects.get(id=room_id)
        message = Message.objects.get(id=message_id)
        notification = Notification.objects.create(
            room=room, message=message, notify=notify_text
        )
        notification.populatePersonalNotification()

    return notification
