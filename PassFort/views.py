from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import DeleteView, ListView, CreateView, UpdateView

from .models import Account
from .forms import AccountForm, PasswordGenerateForm

from secrets import choice as s_choice
from string import (
    ascii_uppercase,
    ascii_lowercase,
    digits as s_digits,
    punctuation as s_punctuation,
)


# Create your views here.
def landing(request):
    if request.user.is_authenticated:
        return redirect("passfort:home")
    return render(request, "landing.html")


class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    context_object_name = "accounts"

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).only(
            "url", "username", "description", "slug", "password"
        )


class AccountCreateView(LoginRequiredMixin, CreateView):
    model = Account
    form_class = AccountForm
    success_url = reverse_lazy("passfort:home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        master_password = self.request.user.get_master_password_from_session(
            self.request
        )
        if not master_password:
            # Сохраняем данные формы и URL возврата в сессии
            self.request.session["form_data"] = form.cleaned_data
            self.request.session["next"] = self.request.path
            self.request.session.modified = True
            return redirect("authentication:confirm-master-password")
        if master_password:
            form.instance.password = form.instance.encrypt_password(
                form.cleaned_data["password"], master_password
            )
        return super().form_valid(form)

    def get_initial(self):
        # Восстанавливаем данные формы из сессии, если они есть
        initial = super().get_initial()
        form_data = self.request.session.pop("form_data", None)
        if form_data:
            initial.update(form_data)
        return initial


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = Account
    slug_field = "slug"
    slug_url_kwarg = "slug"
    context_object_name = "account"
    success_url = reverse_lazy("passfort:home")

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = Account
    form_class = AccountForm
    success_url = reverse_lazy("passfort:home")
    master_password = None

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Действия, которые необходимо выполнить до обработки запроса
        self.master_password = self.request.user.get_master_password_from_session(
            self.request
        )
        if not self.master_password:
            # Сохраняем URL возврата в сессии
            self.request.session["next"] = self.request.path
            self.request.session.modified = True
            return redirect("authentication:confirm-master-password")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        account = self.get_object()
        decrypted_password = account.decrypt_password(
            account.password, self.master_password
        )
        initial["password"] = decrypted_password
        initial["url"] = f"https://{account.url}"
        return initial

    def form_valid(self, form):
        form.instance.password = form.instance.encrypt_password(
            form.cleaned_data["password"], self.master_password
        )
        return super().form_valid(form)


@login_required
def copy_password(request, slug):
    account = get_object_or_404(Account, slug=slug, user=request.user)
    master_password = request.session.get("master_password")

    if not master_password:
        return JsonResponse(
            {"redirect": True, "url": reverse("authentication:confirm-master-password")}
        )

    try:
        decrypted_password = account.decrypt_password(account.password, master_password)
        return JsonResponse({"redirect": False, "password": decrypted_password})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def generate_password(clean_data):
    characters = ""
    if clean_data["include_lowercase"]:
        characters += ascii_lowercase
    if clean_data["include_uppercase"]:
        characters += ascii_uppercase
    if clean_data["include_numbers"]:
        characters += s_digits
    if clean_data["include_special"]:
        characters += s_punctuation
    characters += "".join(set(clean_data["user_simbols"]))

    if characters == "":
        return "Выберите символы для пароля!"
    return "".join(
        s_choice(list(set(characters))) for _ in range(clean_data["password_length"])
    )


@login_required
def password_generator(request):
    password = None
    if request.method == "POST":
        form = PasswordGenerateForm(request.POST)
        if form.is_valid():
            password = generate_password(form.cleaned_data)
    else:
        form = PasswordGenerateForm()

    data = {"form": form, "password": password}
    return render(request, "Generator/password_generator.html", data)
