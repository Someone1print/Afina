# finance/models.py
from django.db import models

class IncomeCategory(models.Model):
    id = models.AutoField(primary_key=True)
    incomeName = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'income_category'  # имя твоей существующей таблицы
