from django.contrib.auth.views import (
    LogoutView,
    PasswordResetDoneView,
    PasswordChangeDoneView,
)
from django.urls import path, reverse_lazy

from . import views


app_name = "authentication"

urlpatterns = [
    path("logout/", LogoutView.as_view(), name="logout"),
    path("registration/", views.RegisterUserView.as_view(), name="registration"),
    path("login/", views.LoginUserView.as_view(), name="login"),
    path("profile/", views.ProfileUserView.as_view(), name="profile"),
    path("password-reset/", views.CPasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(
            template_name="authentication/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        views.CPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        views.password_reset_complete,
        name="password_reset_complete",
    ),
    path(
        "password-change/",
        views.PasswordChangeUserView.as_view(),
        name="password_change",
    ),
    path(
        "password-change/done/",
        PasswordChangeDoneView.as_view(
            template_name="authentication/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path("confirm-master-password/", views.confirm_master_password, name="confirm-master-password"),
]
