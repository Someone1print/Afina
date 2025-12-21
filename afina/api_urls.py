from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Импортируем ВСЁ нужное из api_views.py
from .api_views import *
from .views import (
    dashboard_expenses_by_day_api,
    dashboard_expenses_by_category_pie_api,
    dashboard_income_by_day_api,
    dashboard_income_by_category_pie_api,
)

# Роутер для REST API
router = DefaultRouter()
router.register(r'income-categories', IncomeCategoryViewSet, basename='income-category')
router.register(r'expense-categories', ExpenseCategoryViewSet, basename='expense-category')
router.register(r'incomes', IncomeViewSet, basename='income')
router.register(r'expenses', ExpenseViewSet, basename='expense')

# Обязательно указываем app_name для {% url 'api:...' %}
app_name = 'api'

urlpatterns = [
    # JWT Авторизация
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Профиль и хелсчек
    path('me/profile/', ProfileMeView.as_view(), name='profile_me'),
    path('health/', HealthView.as_view(), name='health'),

    # Все CRUD (списки, создание, редактирование и т.д.)
    path('', include(router.urls)),

    # ГРАФИКИ ДЛЯ ДАШБОРДА — САМОЕ ВАЖНОЕ
    path('dashboard/expenses-by-day/', dashboard_expenses_by_day_api, name='dashboard_expenses_by_day'),
    path('dashboard/expenses-by-category/', dashboard_expenses_by_category_pie_api, name='dashboard_expenses_by_category'),
    path('dashboard/income-by-day/', dashboard_income_by_day_api, name='dashboard_income_by_day'),
    path('dashboard/income-by-category/', dashboard_income_by_category_pie_api, name='dashboard_income_by_category'),
]