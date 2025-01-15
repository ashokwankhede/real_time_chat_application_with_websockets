from django.contrib import admin
from .models import AppUsers, RealTimeMessages, ChatGroup, ReadRecipient

# Register your models here.

@admin.register(AppUsers)
class AppUsersAdmin(admin.ModelAdmin):
    list_display = ('app_user_id', 'username', 'mobile_no', 'profile_picture', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'mobile_no')
    list_filter = ('is_active', 'is_staff', 'date_joined')

@admin.register(RealTimeMessages)
class RealTimeMessagesAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'sender', 'receiver', 'group', 'content', 'content_type', 'status', 'timestamp')

    search_fields = ('content', 'content_type', 'status')
    list_filter = ('sender', 'receiver', 'group', 'content_type', 'timestamp', 'status')



@admin.register(ReadRecipient)
class MessageStatusAdmin(admin.ModelAdmin):
    list_display = ('message', 'recipient', 'status', 'timestamp')
    search_fields = ('message', 'recipient', 'status')
    list_filter = ('message',  'status')


@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by')
    list_filter = ('created_by',)
