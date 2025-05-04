# chatbot/models.py
from django.db import models
from django.conf import settings
from Profile.models import User
from Store.models import Order, Cart, Wishlist

class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    is_bot = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Contextual data snapshot
    order_context = models.JSONField(blank=True, null=True)
    cart_context = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"

    class Meta:
        ordering = ['timestamp']
