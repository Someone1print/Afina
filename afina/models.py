# finance/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.functions import Lower

class IncomeCategory(models.Model):
    id = models.AutoField(primary_key=True)
    incomeName = models.CharField(max_length=100)              # убрали unique=True
    owner = models.ForeignKey(                                 # NULL = общая категория
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='income_categories'
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'income_category'
        ordering = ['is_default', 'incomeName']
        constraints = [
            # имя уникально среди общих (owner IS NULL), без учёта регистра
            models.UniqueConstraint(
                Lower('incomeName'),
                condition=Q(owner__isnull=True),
                name='uniq_income_default_name_ci'
            ),
            # имя уникально внутри пользователя (личные), без учёта регистра
            models.UniqueConstraint(
                Lower('incomeName'), 'owner',
                condition=Q(owner__isnull=False),
                name='uniq_income_user_name_ci'
            ),
        ]

    def __str__(self):
        return self.incomeName


class ExpenseCategory(models.Model):
    id = models.AutoField(primary_key=True)
    expenseName = models.CharField(max_length=100)             # убрали unique=True
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='expense_categories'
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'expense_category'
        ordering = ['is_default', 'expenseName']
        verbose_name = "Категория расхода"
        verbose_name_plural = "Категории расходов"
        constraints = [
            models.UniqueConstraint(
                Lower('expenseName'),
                condition=Q(owner__isnull=True),
                name='uniq_expense_default_name_ci'
            ),
            models.UniqueConstraint(
                Lower('expenseName'), 'owner',
                condition=Q(owner__isnull=False),
                name='uniq_expense_user_name_ci'
            ),
        ]

    def __str__(self):
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
    category = models.ForeignKey(
        'IncomeCategory',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='incomes'
    )
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
    category = models.ForeignKey(
        'ExpenseCategory',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='expenses'
    )
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