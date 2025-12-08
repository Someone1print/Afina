import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def is_subscription_active(user):
    """
    Проверяет, есть ли у пользователя активная подписка в Stripe.
    """
    subscriptions = stripe.Subscription.list(customer=user.profile.stripe_customer_id).data
    for subscription in subscriptions:
        if subscription.status == 'active':
            return True
    return False