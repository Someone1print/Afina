# finance/signals.py
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ExpenseCategory, IncomeCategory, Expense, Income, Profile
import stripe
from django.conf import settings

# Устанавливаем секретный ключ Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

FALLBACK_NAME = "Другое"

def get_fallback_expense_category(owner: User | None):
    qs = ExpenseCategory.objects
    if owner:
        cat = qs.filter(owner=owner, expenseName__iexact=FALLBACK_NAME).first()
        if cat:
            return cat
    cat = qs.filter(owner__isnull=True, expenseName__iexact=FALLBACK_NAME).first()
    if cat:
        return cat
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

# Новый сигнал для создания клиента в Stripe при регистрации пользователя
@receiver(post_save, sender=User)
def create_profile_and_stripe_customer(sender, instance, created, **kwargs):

    if created:  # Этот сигнал срабатывает только при создании нового пользователя
        # Проверяем, существует ли уже клиент с таким email
        existing_customer = stripe.Customer.list(email=instance.email).data
        if existing_customer:
            customer = existing_customer[0]  # Если клиент существует, используем его
        else:
            # Если клиента нет, создаем нового
            customer = stripe.Customer.create(
                email=instance.email,
                name=instance.username,
            )

        # Создаем или обновляем профиль пользователя
        profile, _ = Profile.objects.get_or_create(user=instance)
        profile.stripe_customer_id = customer.id
        profile.save()
