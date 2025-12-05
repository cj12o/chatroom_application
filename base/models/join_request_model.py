from django.db import models
from django.contrib.auth.models import User
from .room_model import Room

class RequestStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    REJECTED = 'REJECTED', 'Rejected'

class JoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='join_requests')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='join_requests')
    status = models.CharField(
        max_length=10,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'room')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} -> {self.room.name} ({self.status})"
