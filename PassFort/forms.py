from urllib import request
from django.shortcuts import redirect
from django import forms
from .models import Account


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["username", "password", "url", "description"]
        widgets = {
            "username": forms.TextInput(
                attrs={"autofocus": "True", "placeholder": "joo.bidon | @example.com"}
            ),
            "url": forms.URLInput(attrs={"placeholder": "https://yandex.ru/"}),
            "password": forms.TextInput(
                attrs={"maxlength": "32", "placeholder": "************"}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Какой-нибудь коммент или заметка ...",
                    "style": "resize: none;",
                }
            ),
        }

    # def save(self, commit=True):

    #     user = super().save(commit=False)
    #     master_password = self.cleaned_data.get("master_password")
    #     if master_password:
    #         user.master_password = make_password(master_password)
    #     if commit:
    #         user.save()
    #     return user


class PasswordGenerateForm(forms.Form):
    password_length = forms.IntegerField(
        min_value=8, max_value=32, label="Длина пароля", initial=16
    )
    include_lowercase = forms.BooleanField(
        label="Строчные буквы [a-z]", required=False, initial=True
    )
    include_uppercase = forms.BooleanField(
        label="Заглавные буквы [A-Z]", required=False, initial=True
    )
    include_numbers = forms.BooleanField(
        label="Цифры [0-9]", required=False, initial=True
    )
    include_special = forms.BooleanField(
        label="Символы пунктуации", required=False, initial=False
    )
    user_simbols = forms.CharField(
        label="Ваши символы",
        required=False,
        help_text="Впишите символы, которые вы хотите использовать в пароле.",
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )
