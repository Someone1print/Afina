# finance/models.py
from django.db import models
from django.contrib.auth.models import User

class IncomeCategory(models.Model):
    id = models.AutoField(primary_key=True)
    incomeName = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'income_category'  # имя твоей существующей таблицы

    class Profile(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
        full_name = models.CharField("ФИО", max_length=150, blank=True)
        currency = models.CharField("Валюта по умолчанию", max_length=10, default="KGS")

        # avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)  # если нужно

        class Meta:
            db_table = 'profile'
            verbose_name = "Профиль"
            verbose_name_plural = "Профили"

        def _str_(self):
            return self.full_name or self.user.username