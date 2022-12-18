from django.urls import path
from .views import (
    send_sms_code1,
    send_sms_code2,
)

urlpatterns = [
    path('auth/send-code', send_sms_code1.view()),
    path('auth/send-code2', send_sms_code2.view()),
]