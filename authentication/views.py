from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordChangeView,
)
from django.views.generic import CreateView, UpdateView

from .forms import (
    RegisterUserForm,
    LoginUserForm,
    ProfileUserForm,
    CPasswordResetForm,
    CPasswordResetConfirmForm,
    PasswordChangeUserForm,
    MasterPasswordForm,
)


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    template_name = "authentication/registration.html"
    success_url = reverse_lazy("authentication:login")


class LoginUserView(LoginView):
    form_class = LoginUserForm
    template_name = "authentication/login.html"


class ProfileUserView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = "authentication/profile.html"
    success_url = reverse_lazy("authentication:profile")

    def get_object(self, queryset=None):
        return self.request.user


class CPasswordResetView(PasswordResetView):
    form_class = CPasswordResetForm
    template_name = "authentication/password_reset_form.html"
    email_template_name = "authentication/password_reset_email.html"
    success_url = reverse_lazy("authentication:password_reset_done")


class CPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CPasswordResetConfirmForm
    template_name = "authentication/password_reset_confirm.html"
    success_url = reverse_lazy("authentication:password_reset_complete")


@login_required
def password_reset_complete(request):
    return render(request, "authentication/password_reset_complete.html")


class PasswordChangeUserView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeUserForm
    success_url = reverse_lazy("authentication:password_change_done")
    template_name = "authentication/password_change_form.html"


@login_required
def confirm_master_password(request):
    if request.method == "POST":
        form = MasterPasswordForm(request.POST)
        if form.is_valid():
            master_password = form.cleaned_data["master_password"]
            if check_password(master_password, request.user.master_password):
                request.session["master_password"] = master_password
                # Возвращаем пользователя к заполненной форме создания аккаунта
                return redirect(request.session.pop("next", "passfort:home"))
            else:
                form.add_error(field="master_password", error="Неверный мастер-пароль")

    else:
        form = MasterPasswordForm()

    return render(
        request, "authentication/confirm_master_password.html", {"form": form}
    )
