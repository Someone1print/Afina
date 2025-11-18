from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api_views import (
    IncomeCategoryViewSet, ExpenseCategoryViewSet,
    IncomeViewSet, ExpenseViewSet,
    ProfileMeView, HealthView
)

router = DefaultRouter()
router.register(r'income-categories', IncomeCategoryViewSet, basename='income-category')
router.register(r'expense-categories', ExpenseCategoryViewSet, basename='expense-category')
router.register(r'incomes', IncomeViewSet, basename='income')
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    # auth (JWT)
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # profile (текущий пользователь)
    path('me/profile/', ProfileMeView.as_view(), name='profile_me'),

    # healthcheck
    path('health/', HealthView.as_view(), name='health'),

    # main resources
    path('', include(router.urls)),
]
