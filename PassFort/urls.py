from django.urls import path

from . import views


app_name = "passfort"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("home/", views.AccountListView.as_view(), name="home"),
    path("accounts/new/", views.AccountCreateView.as_view(), name="account_create"),
    path(
        "accounts/delete/<slug:slug>/",
        views.AccountDeleteView.as_view(),
        name="account_delete",
    ),
    path(
        "accounts/update/<slug:slug>/",
        views.AccountUpdateView.as_view(),
        name="account_update",
    ),
    path("copy-password/<slug:slug>/", views.copy_password, name="copy_password"),
    path("generate-password/", views.password_generator, name="generate_password"),
]
