import stripe
from django.conf import settings
from .models import UserSubscription

stripe.api_key = settings.STRIPE_SECRET_KEY

# def is_subscription_active(user):
#     """
#     Проверяет, есть ли у пользователя активная подписка в Stripe.
#     """
#     subscriptions = stripe.Subscription.list(customer=user.profile.stripe_customer_id).data
#     for subscription in subscriptions:
#         if subscription.status == 'active':
#             return True
#     return False

# finance/utils.py
from django.utils import timezone

def is_subscription_active(user):
    """Проверяет, есть ли у пользователя активная подписка"""
    try:
        # Импортируем модель здесь, чтобы избежать циклического импорта
        from .models import UserSubscription
        subscription = UserSubscription.objects.get(user=user)
        return subscription.is_active
    except UserSubscription.DoesNotExist:
        return False

def get_user_subscription(user):
    """Получает подписку пользователя или None"""
    try:
        # Импортируем модель здесь
        from .models import UserSubscription
        return UserSubscription.objects.get(user=user)
    except UserSubscription.DoesNotExist:
        return None