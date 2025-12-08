from django.db.models import Q
from rest_framework import viewsets, mixins, generics, permissions, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from .models import IncomeCategory, ExpenseCategory, Income, Expense, Profile
from .api_serializers import (
    IncomeCategorySerializer, ExpenseCategorySerializer,
    IncomeSerializer, ExpenseSerializer, ProfileSerializer,RegisterSerializer,LoginSerializer
)
from .api_permissions import IsOwnerOrReadOnly
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth import logout


# --- Healthcheck ---
class HealthView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, *args, **kwargs):
        return Response({"status": "ok"})


# --- Базовый Mixin для списков "мои + общие" ---
class OwnerOrPublicQuerysetMixin:
    """
    Для категорий: показываем свои и общие (owner is null)
    Для транзакций: только свои
    """
    public_owner_field = 'owner'  # имя поля owner в модели

    def get_owner_filter(self):
        user = self.request.user
        return Q(**{f"{self.public_owner_field}": user}) | Q(**{f"{self.public_owner_field}__isnull": True})

    def get_queryset(self):
        qs = super().get_queryset()
        # для категорий фильтруем "мои + общие"
        if self.queryset.model in (IncomeCategory, ExpenseCategory):
            return qs.filter(self.get_owner_filter())
        # для транзакций только мои
        if self.queryset.model in (Income, Expense):
            return qs.filter(user=self.request.user)
        return qs


# --- Категории доходов ---
class IncomeCategoryViewSet(OwnerOrPublicQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = IncomeCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = IncomeCategory.objects.all().order_by('-is_default', 'incomeName')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['incomeName']
    ordering_fields = ['incomeName', 'id']

    def perform_create(self, serializer):
        # создаем личную категорию
        serializer.save(owner=self.request.user, is_default=False)

    def perform_destroy(self, instance):
        # запрет удалять дефолтную «Другое»
        name = (instance.incomeName or '').lower()
        if instance.is_default and name == 'другое':
            raise ValidationError("Нельзя удалять дефолтную категорию «Другое».")
        # здесь можно переназначать связанные записи на «Другое» сигналом или прямо здесь
        super().perform_destroy(instance)


# --- Категории расходов ---
class ExpenseCategoryViewSet(OwnerOrPublicQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = ExpenseCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = ExpenseCategory.objects.all().order_by('-is_default', 'expenseName')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['expenseName']
    ordering_fields = ['expenseName', 'id']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, is_default=False)

    def perform_destroy(self, instance):
        name = (instance.expenseName or '').lower()
        if instance.is_default and name == 'другое':
            raise ValidationError("Нельзя удалять дефолтную категорию «Другое».")
        super().perform_destroy(instance)


# --- Доходы ---
class IncomeViewSet(viewsets.ModelViewSet):
    serializer_class = IncomeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Income.objects.select_related('category').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['note']
    ordering_fields = ['date', 'amount', 'id']
    ordering = ['-date', '-id']

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        # простые фильтры через query params: ?date_from=2025-01-01&date_to=2025-12-31&category=5
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        category_id = self.request.query_params.get('category')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# --- Расходы ---
class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Expense.objects.select_related('category').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['note']
    ordering_fields = ['date', 'amount', 'id']
    ordering = ['-date', '-id']

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        category_id = self.request.query_params.get('category')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# --- Профиль текущего пользователя ---
class ProfileMeView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


# 1. Расходы по дням (последние 7 дней)
def dashboard_expenses_by_day_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)

    expenses = Expense.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).values('date').annotate(total=Sum('amount')).order_by('date')

    # Словарь: день недели → сумма
    day_data = {(start_date + timedelta(days=i)): 0 for i in range(7)}
    for item in expenses:
        day_data[item['date']] = float(item['total'])

    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    amounts = [day_data[start_date + timedelta(days=i)] for i in range(7)]

    return JsonResponse({
        "days": days,
        "amounts": amounts
    })


# 2. Расходы по категориям (круговая диаграмма)
# 2. Расходы по категориям (круговая диаграмма) — ИСПРАВЛЕНО РАБОТАЕТ
def dashboard_expenses_by_category_pie_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)

    expenses = Expense.objects.filter(
        user=request.user,
        date__gte=first_day_of_month
    ).values('category__expenseName') \
     .annotate(total=Sum('amount')) \
     .order_by('-total')

    categories = []
    amounts = []
    other_amount = 0.0

    # ← важно: float!
    total = 0.0             # ← тоже float

    # Переводим Decimal → float
    for item in expenses:
        amount = float(item['total'] or 0)
        total += amount

    # Теперь безопасно делим
    for item in expenses:
        name = item['category__expenseName'] or "Без категории"
        amount = float(item['total'] or 0)
        if total > 0 and (amount / total) < 0.03:  # < 3% → в "Другое"
            other_amount += amount
        else:
            categories.append(name)
            amounts.append(amount)

    if other_amount > 0:
        categories.append("Другое")
        amounts.append(other_amount)

    # Если вообще нет расходов — покажем красивую заглушку
    if total == 0:
        categories = ["Нет расходов"]
        amounts = [1]

    return JsonResponse({
        "categories": categories,
        "amounts": amounts
    })
# 3. Доходы по дням (последние 7 дней)
def dashboard_income_by_day_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)

    incomes = Income.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).values('date').annotate(total=Sum('amount')).order_by('date')

    day_data = {(start_date + timedelta(days=i)): 0 for i in range(7)}
    for item in incomes:
        day_data[item['date']] = float(item['total'] or 0)

    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    amounts = [day_data[start_date + timedelta(days=i)] for i in range(7)]

    return JsonResponse({
        "days": days,
        "amounts": amounts
    })


# 4. Доходы по категориям (текущий месяц)
def dashboard_income_by_category_pie_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)

    incomes = Income.objects.filter(
        user=request.user,
        date__gte=first_day_of_month
    ).values('category__incomeName') \
     .annotate(total=Sum('amount')) \
     .order_by('-total')

    categories = []
    amounts = []
    other_amount = 0.0
    total = 0.0

    for item in incomes:
        amount = float(item['total'] or 0)
        total += amount

    for item in incomes:
        name = item['category__incomeName'] or "Без категории"
        amount = float(item['total'] or 0)
        if total > 0 and (amount / total) < 0.03:
            other_amount += amount
        else:
            categories.append(name)
            amounts.append(amount)

    if other_amount > 0:
        categories.append("Другое")
        amounts.append(other_amount)

    if total == 0:
        categories = ["Нет доходов за месяц"]
        amounts = [1]

    return JsonResponse({
        "categories": categories,
        "amounts": amounts
    })

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                return Response({"message": "Login successful"}, status=200)
            return Response({"message": "Invalid credentials"}, status=401)
        return Response(serializer.errors, status=400)

class LogoutView(APIView):
    def post(self, request):
        logout(request)  # Завершаем сессию пользователя
        return Response({"message": "Logged out successfully."}, status=200)