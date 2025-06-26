from django.urls import path
from .views import RegisterView, CustomObtainAuthToken, FaceVerificationView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', CustomObtainAuthToken.as_view(), name='auth-login'),
    path('verify-face/', FaceVerificationView.as_view(), name='auth-verify-face'),
]