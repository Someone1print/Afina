# finance/signals.py
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ExpenseCategory, IncomeCategory, Expense, Income

FALLBACK_NAME = "Другое"

def get_fallback_expense_category(owner: User | None):
    """
    1) личное 'Другое' владельца категории (если есть),
    2) иначе общее 'Другое' (owner=None),
    3) если нет ни одного — создаём общее 'Другое'.
    """
    qs = ExpenseCategory.objects
    if owner:
        cat = qs.filter(owner=owner, expenseName__iexact=FALLBACK_NAME).first()
        if cat:
            return cat
    cat = qs.filter(owner__isnull=True, expenseName__iexact=FALLBACK_NAME).first()
    if cat:
        return cat
    # создать общее
    return qs.create(expenseName=FALLBACK_NAME, owner=None, is_default=True)

def get_fallback_income_category(owner: User | None):
    qs = IncomeCategory.objects
    if owner:
        cat = qs.filter(owner=owner, incomeName__iexact=FALLBACK_NAME).first()
        if cat:
            return cat
    cat = qs.filter(owner__isnull=True, incomeName__iexact=FALLBACK_NAME).first()
    if cat:
        return cat
    return qs.create(incomeName=FALLBACK_NAME, owner=None, is_default=True)

@receiver(pre_delete, sender=ExpenseCategory)
def reassign_expenses_on_category_delete(sender, instance: ExpenseCategory, using, **kwargs):
    fallback = get_fallback_expense_category(instance.owner)
    Expense.objects.filter(category=instance).update(category=fallback)

@receiver(pre_delete, sender=IncomeCategory)
def reassign_incomes_on_category_delete(sender, instance: IncomeCategory, using, **kwargs):
    fallback = get_fallback_income_category(instance.owner)
    Income.objects.filter(category=instance).update(category=fallback)
