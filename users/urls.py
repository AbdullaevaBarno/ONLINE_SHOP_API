# users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import RegisterView, UserProfileView, SetPasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),# Registraciya (Jańa paydalanıwshı qosıw)

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),# Login (JWT Token alıw - Access hám Refresh)

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),# Token jańalaw (Access token óshkende jańasın alıw ushın)

    path('profile/', UserProfileView.as_view(), name='user-profile'),# Paydalanıwshı profili (Kóriw hám maǵlıwmatlardı ózgertiw)

    path('profile/set-password/', SetPasswordView.as_view(), name='set-password'),
]