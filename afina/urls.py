"""
URL configuration for afina project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from django.urls import path, include


urlpatterns = [
    path('', views.home_view, name='home'),
    path('api/', include('afina.api_urls')),  # все API вынесем в afina/api_urls.py
    # Auth
    # urls.py
    path('api/auth/', include('rest_framework.urls')),  # логин/логаут для браузера


    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('accounts/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # IncomeCategory CRUD
    path('income-categories/', views.income_category_list, name='income_category_list'),
    path('income-categories/add/', views.income_category_create, name='income_category_create'),
    path('income-categories/<int:pk>/edit/', views.income_category_update, name='income_category_update'),
    path('income-categories/<int:pk>/delete/', views.income_category_delete, name='income_category_delete'),
# ExpenseCategory
    path('expense-categories/', views.expense_category_list, name='expense_category_list'),
    path('expense-categories/create/', views.expense_category_create, name='expense_category_create'),
    path('expense-categories/<int:pk>/edit/', views.expense_category_update, name='expense_category_update'),
    path('expense-categories/<int:pk>/delete/', views.expense_category_delete, name='expense_category_delete'),

    # Incomes
    path('incomes/', views.income_list, name='income_list'),
    path('incomes/create/', views.income_create, name='income_create'),
    path('incomes/<int:pk>/edit/', views.income_update, name='income_update'),
    path('incomes/<int:pk>/delete/', views.income_delete, name='income_delete'),
    # API для Plotly-графиков доходов
    path('api/incomes/by-category/', views.income_by_category_api, name='income_by_category_api'),
    path('api/incomes/by-month/', views.income_by_month_api, name='income_by_month_api'),
    # Expenses
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_update, name='expense_update'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    # Plotly API
    path('expenses/by-category/', views.expense_by_category_api, name='expense_by_category_api'),
    path('expenses/by-month/', views.expense_by_month_api, name='expense_by_month_api'),

    # Profile
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # ✅ Swagger / schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    #Stripe
    path('stripe-test/', views.stripe_test_view, name='stripe_test'),
    path('stripe/create-checkout-session/', views.create_checkout_session,
         name='create_checkout_session'),
    path('stripe/success/', views.stripe_success_view, name='stripe_success'),
    path('stripe/cancel/', views.stripe_cancel_view, name='stripe_cancel'),

    path("savings/", views.savings_list, name="savings_list"),
    path("savings/new/", views.savings_create, name="savings_create"),
    path("savings/<int:pk>/edit/", views.savings_update, name="savings_update"),
    path("savings/<int:pk>/delete/", views.savings_delete, name="savings_delete"),

# Подписка
    path('subscription/cancel/', views.cancel_subscription_view, name='cancel_subscription'),
    path('subscription/cancel/confirm/', views.cancel_subscription_confirm, name='cancel_subscription_confirm'),
    #path('stripe/webhook/', webhooks.stripe_webhook, name='stripe_webhook'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

