"""Тесты Afina: модели, сигналы и REST API.

Stripe мокается во всех тестах: сигнал post_save(User) создаёт клиента Stripe,
поэтому реальные сетевые вызовы в тестах недопустимы.
"""
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import (
    Expense,
    ExpenseCategory,
    Income,
    IncomeCategory,
    Profile,
    SavingGoal,
    UserSubscription,
)
from .signals import FALLBACK_NAME


class StripeMockMixin:
    """Подменяет модуль stripe в afina.signals на мок для всех тестов класса."""

    def setUp(self):
        super().setUp()
        patcher = patch('afina.signals.stripe')
        self.mock_stripe = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_stripe.Customer.list.return_value = MagicMock(data=[])
        self.mock_stripe.Customer.create.return_value = MagicMock(id='cus_test_123')

    def make_user(self, username='user1', password='StrongPass123'):
        return User.objects.create_user(
            username=username, password=password, email=f'{username}@example.com',
        )


class SavingGoalModelTests(StripeMockMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = self.make_user()

    def _goal(self, target, current):
        return SavingGoal.objects.create(
            user=self.user, title='Ноутбук',
            target_amount=Decimal(target), current_amount=Decimal(current),
        )

    def test_progress_percent_partial(self):
        self.assertEqual(self._goal('1000', '250').progress_percent, 25)

    def test_progress_percent_capped_at_100(self):
        self.assertEqual(self._goal('1000', '1500').progress_percent, 100)

    def test_progress_percent_zero_target(self):
        self.assertEqual(self._goal('0', '500').progress_percent, 0)

    def test_is_completed(self):
        self.assertTrue(self._goal('1000', '1000').is_completed)
        self.assertFalse(self._goal('1000', '999.99').is_completed)


class UserSubscriptionModelTests(StripeMockMixin, TestCase):
    def _subscription(self, **kwargs):
        params = {
            'user': self.make_user(kwargs.pop('username', 'sub_user')),
            'status': 'active',
            'current_period_start': timezone.now() - timedelta(days=1),
            'current_period_end': timezone.now() + timedelta(days=29),
            'cancel_at_period_end': False,
        }
        params.update(kwargs)
        return UserSubscription.objects.create(**params)

    def test_active_subscription(self):
        self.assertTrue(self._subscription().is_active)

    def test_trialing_subscription_is_active(self):
        self.assertTrue(self._subscription(status='trialing').is_active)

    def test_expired_period_not_active(self):
        sub = self._subscription(current_period_end=timezone.now() - timedelta(days=1))
        self.assertFalse(sub.is_active)

    def test_canceled_status_not_active(self):
        self.assertFalse(self._subscription(status='canceled').is_active)

    def test_cancel_at_period_end_not_active(self):
        self.assertFalse(self._subscription(cancel_at_period_end=True).is_active)

    def test_missing_period_end_not_active(self):
        self.assertFalse(self._subscription(current_period_end=None).is_active)


class SignalTests(StripeMockMixin, TestCase):
    def test_profile_created_with_stripe_customer(self):
        user = self.make_user('newbie')
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.stripe_customer_id, 'cus_test_123')
        self.mock_stripe.Customer.list.assert_called_once()

    def test_existing_stripe_customer_reused(self):
        existing = MagicMock(id='cus_existing_42')
        self.mock_stripe.Customer.list.return_value = MagicMock(data=[existing])
        user = self.make_user('returning')
        self.assertEqual(user.profile.stripe_customer_id, 'cus_existing_42')
        self.mock_stripe.Customer.create.assert_not_called()

    def test_expenses_reassigned_to_fallback_on_category_delete(self):
        user = self.make_user('spender')
        category = ExpenseCategory.objects.create(expenseName='Кофе', owner=user)
        expense = Expense.objects.create(
            user=user, category=category, date=date.today(), amount=Decimal('150.00'),
        )
        category.delete()
        expense.refresh_from_db()
        self.assertIsNotNone(expense.category)
        self.assertEqual(expense.category.expenseName, FALLBACK_NAME)

    def test_incomes_reassigned_to_fallback_on_category_delete(self):
        user = self.make_user('earner')
        category = IncomeCategory.objects.create(incomeName='Подработка', owner=user)
        income = Income.objects.create(
            user=user, category=category, date=date.today(), amount=Decimal('5000.00'),
        )
        category.delete()
        income.refresh_from_db()
        self.assertEqual(income.category.incomeName, FALLBACK_NAME)


class CategoryConstraintTests(StripeMockMixin, TestCase):
    def test_duplicate_user_category_case_insensitive(self):
        # Латиница: LOWER() в SQLite не приводит кириллицу к нижнему регистру,
        # поэтому кейс с 'Транспорт'/'ТРАНСПОРТ' ловится только на PostgreSQL.
        user = self.make_user('dup_user')
        ExpenseCategory.objects.create(expenseName='Taxi', owner=user)
        with self.assertRaises(IntegrityError):
            ExpenseCategory.objects.create(expenseName='TAXI', owner=user)

    def test_same_name_allowed_for_different_users(self):
        first = self.make_user('first')
        second = self.make_user('second')
        ExpenseCategory.objects.create(expenseName='Транспорт', owner=first)
        created = ExpenseCategory.objects.create(expenseName='Транспорт', owner=second)
        self.assertIsNotNone(created.pk)


class ApiTests(StripeMockMixin, APITestCase):
    def authenticate(self, username='api_user', password='StrongPass123'):
        self.make_user(username, password)
        response = self.client.post(
            reverse('api:token_obtain_pair'),
            {'username': username, 'password': password},
            format='json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return User.objects.get(username=username)

    def test_health_endpoint_is_public(self):
        response = self.client.get(reverse('api:health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_incomes_require_authentication(self):
        response = self.client.get(reverse('api:income-list'))
        self.assertIn(response.status_code, (401, 403))

    def test_jwt_auth_and_income_list(self):
        user = self.authenticate()
        Income.objects.create(user=user, date=date.today(), amount=Decimal('1000.00'))
        response = self.client.get(reverse('api:income-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_users_do_not_see_each_others_expenses(self):
        stranger = self.make_user('stranger')
        Expense.objects.create(
            user=stranger, date=date.today(), amount=Decimal('999.00'),
        )
        self.authenticate('curious')
        response = self.client.get(reverse('api:expense-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
