from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    PasswordChangeForm,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from re import match as re__match

from core import settings


class RegisterUserForm(UserCreationForm):
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "placeholder": "************"}
        ),
    )
    password2 = forms.CharField(
        label="Повтор пароля",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "placeholder": "************"}
        ),
    )

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "email",
            "master_password",
            "password1",
            "password2",
        ]
        labels = {"email": "E-mail"}
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "JooBidon"}),
            "email": forms.EmailInput(attrs={"placeholder": "joo.bidon@example.ru"}),
            "master_password": forms.PasswordInput(
                attrs={"placeholder": "Это поле не изменяемое!"}
            ),
        }

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not re__match(r"^[A-Za-z][A-Za-z0-9._]*[A-Za-z]$", username):
            raise forms.ValidationError(
                "Имя пользователя должно начинаться и заканчиваться только буквой, и содержать только английские буквы, цифры, точки и подчеркивания."
            )
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Такой E-mail уже существует!")
        return email

    def clean_master_password(self):
        master_password = self.cleaned_data.get("master_password")
        if not master_password:
            raise forms.ValidationError("Мастер-пароль обязателен.")
        if not (8 <= len(master_password) <= 16):
            raise forms.ValidationError(
                "Мастер-пароль должен быть длиной от 8 до 16 символов."
            )
        if not re__match(r"^[A-Za-z0-9._!@#?+-]+$", master_password):
            raise forms.ValidationError(
                "Мастер-пароль должен состоять только из английских букв, цифр и специальных символов (+, -, _, !, @, #, ?, .)"
            )
        validate_password(master_password, self.instance)
        return master_password

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        # if not re__match(r"^[A-Za-z][A-Za-z0-9._!@#?]*[A-Za-z]$", password):
        if not re__match(r"^[A-Za-z0-9._!@#?+-]+$", password):
            raise forms.ValidationError(
                "Пароль должен состоять только из английских букв, цифр и специальных символов (+, -, _, !, @, #, ?, .)"
            )
        if password == self.cleaned_data.get("master_password"):
            raise forms.ValidationError("Пароль авторизации не должен совпадать с мастер-паролем.")
        return password

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     master_password = self.cleaned_data.get("master_password")
    #     if master_password:
    #         user.master_password = make_password(master_password)
    #     if commit:
    #         user.save()
    #     return user


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                "autofocus": True,
                "placeholder": "JooBidon",
            }
        )
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": "************",
            }
        ),
    )

    class Meta:
        model = get_user_model()
        fields = ["username", "password"]


class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(disabled=True, label="Логин", widget=forms.TextInput)
    email = forms.CharField(disabled=True, label="E-mail", widget=forms.EmailInput)

    class Meta:
        model = get_user_model()
        fields = ["img", "username", "email", "first_name", "last_name"]
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Joo"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Bidon"}),
            "img": forms.FileInput(
                attrs={"class": "profile_input_img", "accept": "image/*"}
            ),
        }

    def clean_img(self):
        img = self.cleaned_data.get("img")
        if hasattr(img, "content_type"):
            if img.size > settings.MAX_IMAGE_SIZE:
                raise forms.ValidationError(
                    "Файл изображения слишком большой (максимальный размер {0} МБ)".format(
                        settings.MAX_IMAGE_SIZE / (1024 * 1024)
                    )
                )
            if not img.content_type in settings.ALLOWED_IMAGE_TYPES:
                raise forms.ValidationError(
                    "Недопустимый тип файла. Разрешенные типы: {0}".format(
                        ", ".join(settings.ALLOWED_IMAGE_TYPES).replace("image/", "")
                    )
                )
        return img


class CPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="E-mail",
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "autofocus": True,
                "placeholder": "joo.bidon@example.ru",
            }
        ),
    )


class CPasswordResetConfirmForm(SetPasswordForm):
    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")
        # if not re__match(r"^[A-Za-z][A-Za-z0-9._!@#?]*[A-Za-z]$", password):
        if not re__match(r"^[A-Za-z0-9._!@#?+-]+$", password):
            raise forms.ValidationError(
                "Пароль должен состоять только из английских букв, цифр и специальных символов (+, -, _, !, @, #, ?, .)"
            )
        return password


class PasswordChangeUserForm(PasswordChangeForm):
    def clean_new_password1(self):
        password = self.cleaned_data.get("new_password1")
        # if not re__match(r"^[A-Za-z][A-Za-z0-9._!@#?]*[A-Za-z]$", password):
        if not re__match(r"^[A-Za-z0-9._!@#?+-]+$", password):
            raise forms.ValidationError(
                "Пароль должен состоять только из английских букв, цифр и специальных символов (+, -, _, !, @, #, ?, .)"
            )
        return password


class MasterPasswordForm(forms.Form):
    master_password = forms.CharField(
        label="Мастер-пароль",
        widget=forms.PasswordInput(
            attrs={
                "autofocus": True,
                "autocomplete": "current-password",
                "placeholder": "************",
            }
        ),
    )
