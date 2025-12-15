# finance/models.py
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils import timezone



class IncomeCategory(models.Model):
    id = models.AutoField(primary_key=True)
    incomeName = models.CharField(max_length=100)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name='income_categories'
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'income_category'
        ordering = ['is_default', 'incomeName']
        constraints = [
            models.UniqueConstraint(
                Lower('incomeName'),
                condition=Q(owner__isnull=True),
                name='uniq_income_default_name_ci'
            ),
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
    expenseName = models.CharField(max_length=100)
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
    CURRENCY_CHOICES = [
        ("KGS", "Сом (KGS)"),
        ("USD", "Доллар (USD)"),
        ("EUR", "Евро (EUR)"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField("ФИО", max_length=150, blank=True)
    currency = models.CharField(
        "Валюта",
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="KGS"
    )
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    class Meta:
        db_table = 'profile'
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.full_name or self.user.username


# ДОБАВЬТЕ ЭТУ МОДЕЛЬ В КОНЕЦ ФАЙЛА
class UserSubscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активная'),
        ('past_due', 'Просрочена'),
        ('canceled', 'Отменена'),
        ('unpaid', 'Не оплачена'),
        ('trialing', 'Пробный период'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_subscription'
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"Подписка {self.user.username} ({self.status})"

    @property
    def is_active(self):
        """Проверяет, активна ли подписка на данный момент"""
        if self.current_period_end and self.current_period_end > timezone.now():
            return self.status in ['active', 'trialing'] and not self.cancel_at_period_end
        return False


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

    def __str__(self):
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

    def __str__(self):
        return f"{self.date}: {self.amount} ({self.category})"


class SavingGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saving_goals")
    title = models.CharField("Цель", max_length=255)
    target_amount = models.DecimalField("Сумма цели", max_digits=12, decimal_places=2)
    current_amount = models.DecimalField("Накоплено", max_digits=12, decimal_places=2, default=0)
    created_at = models.DateField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Копилка"
        verbose_name_plural = "Копилки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.current_amount}/{self.target_amount})"

    @property
    def is_completed(self) -> bool:
        return self.current_amount >= self.target_amount

    @property
    def progress_percent(self) -> int:
        if self.target_amount and self.target_amount != 0:
            percent = int((self.current_amount / self.target_amount) * 100)
            if percent > 100:
                percent = 100
            return percent
        return 0


