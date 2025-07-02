from django.urls import path
from .views import (
    RegisterView, CustomObtainAuthToken, FaceVerificationView,
    PhoneVerificationView, PasswordResetRequestView, PasswordResetConfirmView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', CustomObtainAuthToken.as_view(), name='auth-login'),
    path('verify-face/', FaceVerificationView.as_view(), name='auth-verify-face'),
    path('verify-phone/', PhoneVerificationView.as_view(), name='auth-verify-phone'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]