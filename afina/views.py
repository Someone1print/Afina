
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from .models import IncomeCategory, ExpenseCategory, Income, Expense, Profile, SavingGoal
from .forms import (IncomeCategoryForm, ExpenseCategoryForm,IncomeForm, ExpenseForm, ProfileForm, SavingGoalForm)
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.db.models.functions import TruncMonth
from django.utils.dateparse import parse_date
import stripe
from django.db.models.functions import ExtractWeekDay
from django.db.models import Sum
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.shortcuts import render
from .utils import is_subscription_active  # Импортируем функцию для проверки подписки
from django.utils import timezone
from datetime import timedelta

# Регистрация
# metodi bystroy razrabotki
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # автоматически залогинивает
            return redirect('home')  # куда хочешь после регистрации
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

# Логин
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            print("Successfully logged in")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Логаут
@login_required
def logout_view(request):
    logout(request)
    print("Вы вышли из системы")
    return redirect('login')


def home_view(request):
    user = request.user
    # Проверяем, есть ли у пользователя активная подписка
    has_active_subscription = is_subscription_active(user)

    # Рендерим главную страницу с информацией о подписке
    return render(request, 'home.html', {
        'has_active_subscription': has_active_subscription,  # Передаем переменную в шаблон
    })
# -------------------------
# IncomeCategory CRUD views
# -------------------------
@login_required
def income_category_list(request):
    qs = income_categories_for_user(request.user)
    paginator = Paginator(qs, 6)               # по 8 записей на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) # безопасно: сам обрабатывает мусорные значения

    ctx = {
        'categories': page_obj.object_list,    # чтобы твой шаблон продолжал работать
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'income_category_list.html', ctx)

@login_required
def income_category_create(request):
    if request.method == 'POST':
        form = IncomeCategoryForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.is_default = False
            obj.save()
            messages.success(request, '✅ Категория доходов добавлена.')
            return redirect('income_category_list')
    else:
        form = IncomeCategoryForm()
    return render(request, 'income_category_form.html', {'form': form, 'title': 'Добавить категорию доходов'})


@login_required
def income_category_update(request, pk):
    category = get_object_or_404(IncomeCategory, pk=pk)
    if category.owner is None or category.owner != request.user or (category.is_default and category.incomeName.lower() == 'другое'):
        messages.error(request, '❌ Нельзя изменять общие или дефолтные категории.')
        return redirect('income_category_list')

    if request.method == 'POST':
        form = IncomeCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Категория доходов обновлена.')
            return redirect('income_category_list')
    else:
        form = IncomeCategoryForm(instance=category)
    return render(request, 'income_category_form.html', {'form': form, 'title': 'Изменить категорию доходов'})


@login_required
def income_category_delete(request, pk):
    category = get_object_or_404(IncomeCategory, pk=pk)

    if category.owner != request.user or (category.is_default and category.incomeName.lower() == 'другое'):
        messages.error(request, "❌ Нельзя удалить общие или дефолтные категории.")
        return redirect('income_category_list')

    if request.method == 'POST':
        name = category.incomeName
        category.delete()
        messages.success(request, f"✅ Категория доходов «{name}» удалена, записи переназначены на «Другое».")
        return redirect('income_category_list')

    return render(request, 'income_category_confirm_delete.html', {'category': category})




# -------- ExpenseCategory CRUD --------
@login_required
def expense_category_list(request):
    qs = expense_categories_for_user(request.user)
    paginator = Paginator(qs, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    ctx = {
        'categories': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'expense_category_list.html', ctx)
@login_required
def expense_category_create(request):
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.is_default = False
            obj.save()
            messages.success(request, 'Категория расходов добавлена.')
            return redirect('expense_category_list')
    else:
        form = ExpenseCategoryForm()
    return render(request, 'expense_category_form.html', {'form': form, 'title': 'Добавить категорию расходов'})

@login_required
def expense_category_update(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)

    if category.owner is None or category.owner != request.user or (category.is_default and category.expenseName.lower() == 'другое'):
        return HttpResponseForbidden('Нельзя изменять общие или дефолтные категории.')

    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория расходов обновлена.')
            return redirect('expense_category_list')
    else:
        form = ExpenseCategoryForm(instance=category)
    return render(request, 'expense_category_form.html', {'form': form, 'title': 'Изменить категорию расходов'})

@login_required
def expense_category_delete(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)

    # Проверяем: если дефолтная или не твоя — просто показываем всплывающее сообщение и возвращаемся
    if category.owner != request.user or (category.is_default and category.expenseName.lower() == 'другое'):
        messages.error(request, "❌ Нельзя удалить общие или дефолтные категории.")
        return redirect('expense_category_list')

    if request.method == 'POST':
        name = category.expenseName
        category.delete()
        messages.success(request, f"✅ Категория «{name}» удалена, записи переназначены на «Другое».")
        return redirect('expense_category_list')

    return render(request, 'expense_category_confirm_delete.html', {'category': category})



# -------- Income CRUD --------
@login_required
def income_list(request):
    qs = Income.objects.filter(user=request.user) \
                       .select_related('category') \
                       .order_by('-date')

    paginator = Paginator(qs, 7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'items': page_obj.object_list,
        'page_obj': page_obj,
    }
    return render(request, 'income_list.html', context)
@login_required
def income_create(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('income_list')
    else:
        form = IncomeForm(user=request.user)
    return render(request, 'income_form.html', {'form': form, 'title': 'Добавить доход'})

@login_required
def income_update(request, pk):
    item = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=item, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('income_list')
    else:
        form = IncomeForm(instance=item, user=request.user)
    return render(request, 'income_form.html', {'form': form, 'title': 'Изменить доход'})

@login_required
def income_delete(request, pk):
    item = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        item.delete()
        return redirect('income_list')
    return render(request, 'income_confirm_delete.html', {'item': item})

# -------- Expense CRUD --------
@login_required
def expense_list(request):
    qs = Expense.objects.filter(user=request.user) \
                        .select_related('category') \
                        .order_by('-date')

    paginator = Paginator(qs, 7)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'items': page_obj.object_list,
        'page_obj': page_obj,
    }
    return render(request, 'expense_list.html', context)
@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)
    return render(request, 'expense_form.html', {'form': form, 'title': 'Добавить расход'})

@login_required
def expense_update(request, pk):
    item = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=item, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=item, user=request.user)
    return render(request, 'expense_form.html', {'form': form, 'title': 'Изменить расход'})

@login_required
def expense_delete(request, pk):
    item = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        item.delete()
        return redirect('expense_list')
    return render(request, 'expense_confirm_delete.html', {'item': item})


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile_view.html', {
        'profile': profile,
    })


@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)

        if form.is_valid():
            # сначала обновляем User
            user = request.user
            user.username = form.cleaned_data["username"]
            user.email = form.cleaned_data["email"]
            user.save()

            # потом профиль
            form.save()

            messages.success(request, "✅ Профиль успешно обновлён.")
            return redirect('profile_view')
        else:
            messages.error(request, "❌ Проверьте правильность заполнения формы.")
    else:
        form = ProfileForm(
            instance=profile,
            initial={
                "username": request.user.username,
                "email": request.user.email,
            }
        )

    return render(request, 'profile_form.html', {
        'form': form,
        'title': 'Профиль',
    })


def expense_categories_for_user(user):
    return ExpenseCategory.objects.filter(Q(owner=user) | Q(owner__isnull=True)).order_by('-is_default', 'expenseName')

def income_categories_for_user(user):
    return IncomeCategory.objects.filter(Q(owner=user) | Q(owner__isnull=True)).order_by('-is_default', 'incomeName')

#Создание графиков для доходов

@login_required
def expense_by_category_api(request):
    qs = Expense.objects.filter(user=request.user)
    start = request.GET.get('start')
    end = request.GET.get('end')
    if start:
        qs = qs.filter(date__gte=parse_date(start))
    if end:
        qs = qs.filter(date__lte=parse_date(end))

    agg = (qs.values('category__expenseName')
             .annotate(total=Sum('amount'))
             .order_by('-total'))

    labels = [row['category__expenseName'] for row in agg]
    values = [float(row['total'] or 0) for row in agg]
    return JsonResponse({"labels": labels, "values": values})

@login_required
def expense_by_month_api(request):
    qs = Expense.objects.filter(user=request.user)
    start = request.GET.get('start')
    end = request.GET.get('end')
    if start:
        qs = qs.filter(date__gte=parse_date(start))
    if end:
        qs = qs.filter(date__lte=parse_date(end))

    agg = (qs.annotate(m=TruncMonth('date'))
             .values('m')
             .annotate(total=Sum('amount'))
             .order_by('m'))

    labels = [row['m'].strftime('%b %Y') for row in agg]  # например: "Ноя 2025"
    values = [float(row['total'] or 0) for row in agg]
    return JsonResponse({"labels": labels, "values": values})

#Создание графиков для расходов

@login_required
def income_by_category_api(request):
    qs = Income.objects.filter(user=request.user)
    start = request.GET.get('start')
    end = request.GET.get('end')
    if start:
        qs = qs.filter(date__gte=parse_date(start))
    if end:
        qs = qs.filter(date__lte=parse_date(end))

    agg = (qs.values('category__incomeName')
             .annotate(total=Sum('amount'))
             .order_by('-total'))

    labels = [row['category__incomeName'] for row in agg]
    values = [float(row['total'] or 0) for row in agg]
    return JsonResponse({"labels": labels, "values": values})

@login_required
def income_by_month_api(request):
    qs = Income.objects.filter(user=request.user)
    start = request.GET.get('start')
    end = request.GET.get('end')
    if start:
        qs = qs.filter(date__gte=parse_date(start))
    if end:
        qs = qs.filter(date__lte=parse_date(end))

    agg = (qs.annotate(m=TruncMonth('date'))
             .values('m')
             .annotate(total=Sum('amount'))
             .order_by('m'))

    labels = [row['m'].strftime('%b %Y') for row in agg]
    values = [float(row['total'] or 0) for row in agg]
    return JsonResponse({"labels": labels, "values": values})

@login_required
def stripe_test_view(request):
    context = {
        "stripe_public_key": settings.STRIPE_PUBLISHABLE_KEY,  # <-- имя такое
    }
    return render(request, "stripe_test.html", context)



@csrf_exempt
@login_required
# Когда происходит создание платежа
def create_checkout_session(request):
    email = request.user.email  # Получаем email текущего пользователя

    # Проверяем, существует ли клиент в Stripe
    existing_customer = stripe.Customer.list(email=email).data
    if existing_customer:
        customer_id = existing_customer[0].id  # Используем ID существующего клиента
    else:
        # Создаем нового клиента, если не найден
        customer = stripe.Customer.create(
            email=email,
            name=request.user.username,
        )
        customer_id = customer.id

    # Продолжаем с созданием сессии на основе найденного или созданного клиента
    checkout_session = stripe.checkout.Session.create(
        customer=customer_id,  # Используем customer_id
        mode="subscription",
        line_items=[{
            "price": settings.STRIPE_PRICE_ID,  # price_xxx из Stripe
            "quantity": 1,
        }],
        success_url=request.build_absolute_uri(reverse("stripe_success")) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(reverse("stripe_cancel")),
    )

    return JsonResponse({"id": checkout_session.id})

@login_required
def stripe_success_view(request):
    return render(request, "stripe_success.html")


@login_required
def stripe_cancel_view(request):
    return render(request, "stripe_cancel.html")

@login_required
def savings_list(request):
    has_active_subscription = is_subscription_active(request.user)

    qs = SavingGoal.objects.filter(user=request.user)
    active_goals = qs.filter(current_amount__lt=F("target_amount"))
    completed_goals = qs.filter(current_amount__gte=F("target_amount"))

    context = {
        "active_goals": active_goals,
        "completed_goals": completed_goals,
        "has_active_subscription": has_active_subscription,
    }
    return render(request, "savings_list.html", context)



@login_required
def savings_create(request):
    has_active_subscription = is_subscription_active(request.user)

    if request.method == "POST":
        form = SavingGoalForm(request.POST)
        if form.is_valid():
            goal: SavingGoal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect("savings_list")
    else:
        form = SavingGoalForm(initial={"current_amount": 0})

    return render(
        request,
        "savings_form.html",
        {"form": form, "mode": "create", "has_active_subscription": has_active_subscription},
    )


@login_required
def savings_update(request, pk):
    has_active_subscription = is_subscription_active(request.user)

    goal = get_object_or_404(SavingGoal, pk=pk, user=request.user)

    if request.method == "POST":
        form = SavingGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect("savings_list")
    else:
        form = SavingGoalForm(instance=goal)

    return render(
        request,
        "savings_form.html",
        {"form": form, "mode": "edit", "goal": goal, "has_active_subscription": has_active_subscription},
    )


@login_required
def savings_delete(request, pk):
    has_active_subscription = is_subscription_active(request.user)

    goal = get_object_or_404(SavingGoal, pk=pk, user=request.user)

    if request.method == "POST":
        goal.delete()
        return redirect("savings_list")

    return redirect("savings_list")
    # в шаблон тут не рендерим, так что флаг не нужен
# --- DASHBOARD API (новые эндпоинты) ---

from datetime import datetime

# 1. Расходы по дням (последние 7 дней)
@login_required
def dashboard_expenses_by_day_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    # Получаем расходы пользователя
    expenses = Expense.objects.filter(user=request.user)

    # Составляем список дней недели (Пн, Вт, Ср, Чт, Пт, Сб, Вс)
    days_of_week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    amounts = [0] * 7  # 7 дней недели, начинаем с нулей

    # Заполняем массив с суммами по дням недели
    for expense in expenses:
        # Используем метод weekday() для получения дня недели (Пн=0, Вт=1, Ср=2 и т.д.)
        day_of_week = expense.date.weekday()  # 0 - Понедельник, 6 - Воскресенье
        amounts[day_of_week] += float(expense.amount)

    return JsonResponse({
        "days": days_of_week,
        "amounts": amounts
    })



# 2. Расходы по категориям (круговая диаграмма)
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

    total = 0.0  # общая сумма

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

    # Если вообще нет расходов — покажем заглушку
    if total == 0:
        categories = ["Нет расходов"]
        amounts = [1]

    return JsonResponse({
        "categories": categories,
        "amounts": amounts
    })


# 3. Доходы по дням (последние 7 дней)
@login_required
def dashboard_income_by_day_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    # Получаем доходы пользователя
    incomes = Income.objects.filter(user=request.user)

    # Составляем список дней недели (Пн, Вт, Ср, Чт, Пт, Сб, Вс)
    days_of_week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    amounts = [0] * 7  # 7 дней недели, начинаем с нулей

    # Заполняем массив с суммами по дням недели
    for income in incomes:
        # Используем метод weekday() для получения дня недели (Пн=0, Вт=1, Ср=2 и т.д.)
        day_of_week = income.date.weekday()  # 0 - Понедельник, 6 - Воскресенье
        amounts[day_of_week] += float(income.amount)

    return JsonResponse({
        "days": days_of_week,
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
