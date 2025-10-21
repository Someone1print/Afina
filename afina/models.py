# finance/models.py
from django.db import models
from django.contrib.auth.models import User

class IncomeCategory(models.Model):
    id = models.AutoField(primary_key=True)
    incomeName = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'income_category'  # имя твоей существующей таблицы

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    category = models.ForeignKey(IncomeCategory, on_delete=models.PROTECT, related_name='incomes')
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

