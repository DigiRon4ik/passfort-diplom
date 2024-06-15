from urllib.parse import urlparse
from django.db import models
from django.contrib.auth import get_user_model
from django_extensions.db.fields import AutoSlugField
from slugify import slugify
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import base64


class Account(models.Model):
    # title = models.CharField("Название", max_length=255, blank=True, null=True)
    url = models.URLField("URL-адрес", max_length=255)
    username = models.CharField("Имя пользователя", max_length=255)
    password = models.CharField("Пароль", max_length=1024)
    description = models.TextField("Заметки", max_length=255, blank=True)
    slug = AutoSlugField(
        "Слаг",
        max_length=255,
        unique=True,
        populate_from="username_hostname",
        overwrite=True,
    )
    time_created = models.DateTimeField("Время создания", auto_now_add=True)
    time_updated = models.DateTimeField("Время изменения", auto_now=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="accounts",
    )

    class Meta:
        verbose_name = "Аккаунт"
        verbose_name_plural = "Аккаунты"
        ordering = ["-time_created"]

    def generate_key(self, password, salt):
        return PBKDF2(password, salt, dkLen=32, count=1000000)

    def encrypt_password(self, raw_password, master_password):
        salt = get_random_bytes(16)
        key = self.generate_key(master_password, salt)
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(raw_password.encode())
        encrypted_data = base64.b64encode(
            salt + cipher.nonce + tag + ciphertext
        ).decode()
        return encrypted_data

    def decrypt_password(self, encrypted_password, master_password):
        encrypted_data = base64.b64decode(encrypted_password.encode())
        salt = encrypted_data[:16]
        nonce = encrypted_data[16:32]
        tag = encrypted_data[32:48]
        ciphertext = encrypted_data[48:]
        key = self.generate_key(master_password, salt)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        decrypted_text = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted_text.decode()

    @property
    def username_hostname(self):
        return slugify(f"{self.username}-{self.url}")

    def save(self, *args, **kwargs):
        if self.url:
            self.url = urlparse(self.url).hostname.replace("www.", "")
        if not self.slug:
            self.slug = slugify(f"{self.username}-{self.url}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}+{self.user}"
