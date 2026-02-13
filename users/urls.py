from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, UserProfileView, SetPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('profile/', UserProfileView.as_view(), name='user-profile'),

    path('profile/set-password/', SetPasswordView.as_view(), name='set-password'),
]