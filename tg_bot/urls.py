from django.urls import path
from tg_bot.views import (
    TelegramWebhookView,
    LoginWithCodeView
    
)

urlpatterns = [
   
    path('webhook/', TelegramWebhookView.as_view(), name='tg-webhook'),
    path('login-telegram/', LoginWithCodeView.as_view(), name='tg-login'),
]