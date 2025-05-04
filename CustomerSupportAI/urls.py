# chatbot/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_interface, name='chat_interface'),
    path('send/', views.send_message, name='send_message'),
    path('clear/', views.clear_chat, name='clear_chat'),
]
