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
            return int((self.current_amount / self.target_amount) * 100)
        return 0