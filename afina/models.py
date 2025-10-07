from django.db import models
from django.contrib.auth.models import User


class Income(models.Model):
    TRANSACTION_TYPES = [
        ('salary', 'Заработная плата'),
        ('gift', 'Подарок'),
        ('dividend', 'Дивиденды'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        verbose_name="Тип транзакции"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    date = models.DateField(verbose_name="Дата")

    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} - {self.amount}"
