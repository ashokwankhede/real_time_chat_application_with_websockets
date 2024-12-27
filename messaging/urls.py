from django.urls import path
from . import views
urlpatterns = [
    path('chat/', views.chat_page, name='chat_page')
]