# # finance/webhooks.py
# import stripe
# from django.conf import settings
# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import UserSubscription, Profile
# from datetime import datetime
#
#
# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
#     endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Добавьте в settings.py
#
#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, endpoint_secret
#         )
#     except ValueError as e:
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError as e:
#         return HttpResponse(status=400)
#
#     # Обработка успешной подписки
#     if event['type'] == 'checkout.session.completed':
#         session = event['data']['object']
#
#         if session.mode == 'subscription':
#             subscription_id = session.subscription
#             customer_id = session.customer
#
#             try:
#                 # Получаем подписку из Stripe
#                 subscription = stripe.Subscription.retrieve(subscription_id)
#
#                 # Находим пользователя по customer_id в профиле
#                 profile = Profile.objects.get(stripe_customer_id=customer_id)
#                 user = profile.user
#
#                 # Создаем или обновляем подписку
#                 UserSubscription.objects.update_or_create(
#                     user=user,
#                     defaults={
#                         'stripe_subscription_id': subscription.id,
#                         'stripe_price_id': subscription.items.data[0].price.id,
#                         'status': subscription.status,
#                         'current_period_start': datetime.fromtimestamp(subscription.current_period_start),
#                         'current_period_end': datetime.fromtimestamp(subscription.current_period_end),
#                         'cancel_at_period_end': subscription.cancel_at_period_end,
#                     }
#                 )
#             except (Profile.DoesNotExist, stripe.error.StripeError) as e:
#                 print(f"Webhook error: {e}")
#
#     # Обработка обновления подписки
#     elif event['type'] == 'customer.subscription.updated':
#         subscription = event['data']['object']
#
#         try:
#             user_subscription = UserSubscription.objects.get(
#                 stripe_subscription_id=subscription.id
#             )
#             user_subscription.status = subscription.status
#             user_subscription.current_period_end = datetime.fromtimestamp(subscription.current_period_end)
#             user_subscription.cancel_at_period_end = subscription.cancel_at_period_end
#             user_subscription.save()
#         except UserSubscription.DoesNotExist:
#             pass
#
#     # Обработка отмены подписки
#     elif event['type'] == 'customer.subscription.deleted':
#         subscription = event['data']['object']
#
#         try:
#             user_subscription = UserSubscription.objects.get(
#                 stripe_subscription_id=subscription.id
#             )
#             user_subscription.status = 'canceled'
#             user_subscription.save()
#         except UserSubscription.DoesNotExist:
#             pass
#
#     return HttpResponse(status=200)