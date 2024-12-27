from django.urls import path
from . import views
urlpatterns = [
    path('home/', views.chat_page, name='home'),
    path('register/', views.register_user_view, name='register'),
    path('', views.login_view, name='login'),
]