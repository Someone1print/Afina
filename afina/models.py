# finance/models.py
from django.db import models
from django.contrib.auth.models import User

class IncomeCategory(models.Model):
    id = models.AutoField(primary_key=True)
    incomeName = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'income_category'  # имя твоей существующей таблицы


    def __str__(self):
        return self.incomeName  # ← теперь в select будут имена


class ExpenseCategory(models.Model):
    id = models.AutoField(primary_key=True)
    expenseName = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'expense_category'
        ordering = ['expenseName']
        verbose_name = "Категория расхода"
        verbose_name_plural = "Категории расходов"

    def _str_(self):
        return self.expenseName


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

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    category = models.ForeignKey(IncomeCategory, on_delete=models.CASCADE, related_name='incomes')
    date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'income'
        ordering = ['-date', '-id']
        verbose_name = "Доход"
        verbose_name_plural = "Доходы"

    def _str_(self):
        return f"{self.date}: {self.amount} ({self.category})"


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'expense'
        ordering = ['-date', '-id']
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"

    def _str_(self):
        return f"{self.date}: {self.amount} ({self.category})"