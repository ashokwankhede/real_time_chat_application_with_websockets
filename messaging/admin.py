from django.contrib import admin
from .models import AppUsers, RealTimeMessages, ChatGroup, MessageStatus

# Register your models here.

@admin.register(AppUsers)
class AppUsersAdmin(admin.ModelAdmin):
    list_display = ('app_user_id', 'username', 'email_id', 'mobile_no', 'profile_picture', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email_id', 'mobile_no')
    list_filter = ('is_active', 'is_staff', 'date_joined')

@admin.register(RealTimeMessages)
class RealTimeMessagesAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'sender', 'receiver', 'group', 'content', 'content_type', 'timestamp')

    search_fields = ('content', 'content_type')
    list_filter = ('sender', 'receiver', 'group', 'content_type', 'status', 'timestamp')


@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('group_id', 'name', 'created_at')
    search_fields = ('name',  'created_at')
    list_filter = ('name', 'created_at')



@admin.register(MessageStatus)
class MessageStatusAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'status', 'timestamp')
    search_fields = ('message', 'user', 'status')
    list_filter = ('message',  'status')
