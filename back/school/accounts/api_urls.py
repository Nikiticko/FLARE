from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import RegisterAPI, LoginAPI, AdminLoginAPI, MeAPI, VerifyPasswordAPI, ChangePasswordAPI, LogoutAPI

app_name = "accounts_api"

urlpatterns = [
    path("auth/register/", RegisterAPI.as_view(), name="register"),
    path("auth/login/", LoginAPI.as_view(), name="login"),
    path("auth/admin-login/", AdminLoginAPI.as_view(), name="admin_login"),
    path("auth/me/", MeAPI.as_view(), name="me"),
    path("auth/verify-password/", VerifyPasswordAPI.as_view(), name="verify_password"),
    path("auth/change-password/", ChangePasswordAPI.as_view(), name="change_password"),
    path("auth/logout/", LogoutAPI.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
