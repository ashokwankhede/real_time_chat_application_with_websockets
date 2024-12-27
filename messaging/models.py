from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

class AppUsers(User):
    app_user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email_id = models.EmailField(max_length=30, unique=True, blank=True)
    mobile_no = models.CharField(max_length=15, unique=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)


    def __str__(self):
        return self.username



class RealTimeMessages(models.Model):
    message_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sender = models.ForeignKey(AppUsers, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(AppUsers, on_delete=models.CASCADE, related_name="received_messages", null=True, blank=True)  # Null for group messages
    group = models.ForeignKey('ChatGroup', on_delete=models.CASCADE, related_name="group_messages", null=True, blank=True)  # For group chat
    content = models.TextField()
    content_type = models.CharField(
        max_length=20, 
        choices=[('TEXT', 'Text'), ('IMAGE', 'Image'), ('FILE', 'File')], 
        default='TEXT'
    )
    status = models.CharField(
        max_length=20, 
        choices=[('SENT', 'Sent'), ('DELIVERED', 'Delivered'), ('FAILED', 'Failed'), ('RECEIVED', 'Received'), ('READ', 'Read')]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['sender', 'receiver', 'timestamp']),  
            models.Index(fields=['group', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.sender} to {self.receiver or self.group}: {self.content[:30]}"




class ChatGroup(models.Model):
    group_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    admin = models.ForeignKey(AppUsers, on_delete=models.CASCADE, related_name="admin_groups")
    members = models.ManyToManyField(AppUsers, related_name="chat_groups")  # Changed related_name
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name




class MessageStatus(models.Model):
    message = models.ForeignKey(RealTimeMessages, on_delete=models.CASCADE, related_name="statuses")
    user = models.ForeignKey(AppUsers, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, 
        choices=[('SENT', 'Sent'), ('DELIVERED', 'Delivered'), ('READ', 'Read')]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.status} at {self.timestamp}"
