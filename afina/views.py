from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm, SavingGoalForm, ProfileForm
from .models import IncomeCategory, ExpenseCategory, Income, Expense, Profile, SavingGoal, UserSubscription
from .forms import (IncomeCategoryForm, ExpenseCategoryForm, IncomeForm, ExpenseForm, ProfileForm, SavingGoalForm)
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.db.models.functions import TruncMonth
from django.utils.dateparse import parse_date
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from datetime import datetime

# Регистрация
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
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
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# Логаут
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def home_view(request):
    user = request.user
    # Проверяем, есть ли у пользователя активная подписка
    try:
        subscription = UserSubscription.objects.get(user=user)
        has_active_subscription = subscription.is_active
    except UserSubscription.DoesNotExist:
        has_active_subscription = False

    # Рендерим главную страницу с информацией о подписке
    return render(request, 'home.html', {
        'has_active_subscription': has_active_subscription,
    })


# -------------------------
# IncomeCategory CRUD views
# -------------------------
@login_required
def income_category_list(request):
    qs = income_categories_for_user(request.user)
    paginator = Paginator(qs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    ctx = {
        'categories': page_obj.object_list,
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

    # Получаем подписку пользователя
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        has_active_subscription = subscription.is_active
    except UserSubscription.DoesNotExist:
        subscription = None
        has_active_subscription = False

    return render(request, 'profile_view.html', {
        'profile': profile,
        'has_active_subscription': has_active_subscription,
        'subscription': subscription,
    })


@login_required
def cancel_subscription_view(request):
    """Страница подтверждения отмены подписки"""
    try:
        subscription = UserSubscription.objects.get(user=request.user)

        if not subscription.is_active:
            messages.warning(request, "У вас нет активной подписки.")
            return redirect('profile_view')
    except UserSubscription.DoesNotExist:
        messages.warning(request, "У вас нет активной подписки.")
        return redirect('profile_view')

    context = {
        'subscription': subscription,
        'has_active_subscription': True,
    }
    return render(request, 'subscription_cancel_confirm.html', context)


@login_required
def cancel_subscription_confirm(request):
    """Подтверждение отмены подписки"""
    if request.method != 'POST':
        return redirect('profile_view')

    try:
        subscription = UserSubscription.objects.get(user=request.user)

        if not subscription.is_active:
            messages.warning(request, "У вас нет активной подписки.")
            return redirect('profile_view')
    except UserSubscription.DoesNotExist:
        messages.warning(request, "У вас нет активной подписки.")
        return redirect('profile_view')

    try:
        # Инициализируем Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Если есть stripe_subscription_id, отменяем в Stripe
        if subscription.stripe_subscription_id:
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )

            # Обновляем статус в базе данных
            subscription.cancel_at_period_end = True
            subscription.status = 'active'
            subscription.save()

            messages.success(
                request,
                f"✅ Подписка будет отменена {subscription.current_period_end.strftime('%d.%m.%Y')}. "
                f"Вы сохраните доступ до этой даты."
            )
        else:
            # Если нет Stripe ID, просто помечаем как отмененную
            subscription.cancel_at_period_end = True
            subscription.status = 'canceled'
            subscription.save()
            messages.success(request, "✅ Подписка отменена.")

    except stripe.error.StripeError as e:
        messages.error(request, f"❌ Ошибка Stripe: {str(e)}")
    except Exception as e:
        messages.error(request, f"❌ Произошла ошибка: {str(e)}")

    return redirect('profile_view')






@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)  # Обработка файлов

        if form.is_valid():
            # Сохраняем данные пользователя
            user = request.user
            user.username = form.cleaned_data["username"]
            user.email = form.cleaned_data["email"]
            user.save()

            # Сохраняем изменения профиля (включая фото)
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
        'title': 'Редактирование профиля',
    })




def expense_categories_for_user(user):
    return ExpenseCategory.objects.filter(Q(owner=user) | Q(owner__isnull=True)).order_by('-is_default', 'expenseName')


def income_categories_for_user(user):
    return IncomeCategory.objects.filter(Q(owner=user) | Q(owner__isnull=True)).order_by('-is_default', 'incomeName')


# Создание графиков для доходов
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

    labels = [row['m'].strftime('%b %Y') for row in agg]
    values = [float(row['total'] or 0) for row in agg]
    return JsonResponse({"labels": labels, "values": values})


# Создание графиков для расходов
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
        "stripe_public_key": settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, "stripe_test.html", context)


@csrf_exempt
@login_required
def create_checkout_session(request):
    email = request.user.email

    # Проверяем, существует ли клиент в Stripe
    existing_customers = stripe.Customer.list(email=email, limit=1).data

    if existing_customers:
        customer_id = existing_customers[0].id
    else:
        # Создаем нового клиента
        customer = stripe.Customer.create(
            email=email,
            name=request.user.username,
            metadata={
                'user_id': str(request.user.id),
                'username': request.user.username
            }
        )
        customer_id = customer.id

        # Сохраняем customer_id в профиль пользователя
        profile, created = Profile.objects.get_or_create(user=request.user)
        profile.stripe_customer_id = customer_id
        profile.save()

    try:
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            customer_update={
                'address': 'auto',
                'name': 'auto'
            },
            mode="subscription",
            line_items=[{
                "price": settings.STRIPE_PRICE_ID,
                "quantity": 1,
            }],
            metadata={
                'user_id': str(request.user.id),
                'username': request.user.username
            },
            success_url=request.build_absolute_uri(
                reverse("stripe_success")
            ) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse("stripe_cancel")),
        )

        return JsonResponse({"id": checkout_session.id})

    except stripe.error.StripeError as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def stripe_success_view(request):
    session_id = request.GET.get('session_id')

    # Проверяем текущую подписку пользователя
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        has_active_subscription = subscription.is_active
    except UserSubscription.DoesNotExist:
        subscription = None
        has_active_subscription = False

    if session_id:
        try:
            # Получаем информацию о сессии из Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(session_id)

            if session.mode == 'subscription' and session.payment_status == 'paid':
                # Получаем подписку из Stripe
                subscription_info = stripe.Subscription.retrieve(session.subscription)

                # Сохраняем customer_id в профиль
                profile, _ = Profile.objects.get_or_create(user=request.user)
                if session.customer:
                    profile.stripe_customer_id = session.customer
                    profile.save()

                # Определяем даты (30 дней от текущей даты)
                from datetime import datetime, timedelta
                now = datetime.now()
                period_end = now + timedelta(days=30)

                # Получаем price_id безопасно
                stripe_price_id = None
                if hasattr(subscription_info, 'items') and subscription_info.items:
                    # Если items это список
                    if isinstance(subscription_info.items, list) and len(subscription_info.items) > 0:
                        stripe_price_id = subscription_info.items[0].price.id
                    # Если items это объект с data
                    elif hasattr(subscription_info.items, 'data') and subscription_info.items.data:
                        stripe_price_id = subscription_info.items.data[0].price.id

                # Создаем или обновляем подписку пользователя
                user_subscription, created = UserSubscription.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'stripe_subscription_id': subscription_info.id,
                        'stripe_price_id': stripe_price_id,
                        'status': 'active',
                        'current_period_start': now,
                        'current_period_end': period_end,
                        'cancel_at_period_end': False,
                    }
                )

                messages.success(request, "✅ Подписка успешно активирована на 30 дней!")
                has_active_subscription = True
                subscription = user_subscription  # Обновляем переменную subscription

        except stripe.error.StripeError as e:
            messages.error(request, f"❌ Ошибка Stripe: {str(e)}")
        except Exception as e:
            messages.error(request, f"❌ Произошла ошибка: {str(e)}")

    return render(request, "stripe_success.html", {
        'has_active_subscription': has_active_subscription,
        'subscription': subscription,
    })


@login_required
def stripe_cancel_view(request):
    return render(request, "stripe_cancel.html")


@login_required
def savings_list(request):
    # Проверяем подписку напрямую
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        has_active_subscription = subscription.is_active
    except UserSubscription.DoesNotExist:
        has_active_subscription = False

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
    # Проверяем подписку напрямую
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        has_active_subscription = subscription.is_active
    except UserSubscription.DoesNotExist:
        has_active_subscription = False

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
    # Проверяем подписку напрямую
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        has_active_subscription = subscription.is_active
    except UserSubscription.DoesNotExist:
        has_active_subscription = False

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
    # Проверяем подписку напрямую (если нужно для логики)
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        has_active_subscription = subscription.is_active
    except UserSubscription.DoesNotExist:
        has_active_subscription = False

    goal = get_object_or_404(SavingGoal, pk=pk, user=request.user)

    if request.method == "POST":
        goal.delete()
        return redirect("savings_list")

    return redirect("savings_list")


# --- DASHBOARD API ---
def dashboard_expenses_by_day_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=6)

    expenses = Expense.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    ).values('date').annotate(total=Sum('amount')).order_by('date')

    day_data = {(start_date + timedelta(days=i)): 0 for i in range(7)}
    for item in expenses:
        day_data[item['date']] = float(item['total'])

    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    amounts = [day_data[start_date + timedelta(days=i)] for i in range(7)]

    return JsonResponse({
        "days": days,
        "amounts": amounts
    })


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
    total = 0.0

    for item in expenses:
        amount = float(item['total'] or 0)
        total += amount

    for item in expenses:
        name = item['category__expenseName'] or "Без категории"
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
        categories = ["Нет расходов"]
        amounts = [1]

    return JsonResponse({
        "categories": categories,
        "amounts": amounts
    })


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
@login_required
def savings_update(request, pk):
    goal = get_object_or_404(SavingGoal, pk=pk, user=request.user)

    if request.method == "POST":
        form = SavingGoalForm(request.POST, instance=goal)
        if form.is_valid():
            goal = form.save(commit=False)

            # Рассчитываем разницу между старой и новой суммой
            added_amount = goal.current_amount - goal._state.fields_cache.get('current_amount', 0)

            # Если сумма была добавлена, создаем расход
            if added_amount > 0:
                # Исправление: используем 'expenseName' вместо 'name'
                expense_category = ExpenseCategory.objects.get(expenseName="Накопление")  # Исправлено на expenseName

                # Создаем новый расход
                Expense.objects.create(
                    user=request.user,
                    category=expense_category,
                    amount=added_amount,
                    date=timezone.now(),
                    note="Пополнение цели накопления"
                )

            goal.save()
            return redirect("savings_list")
    else:
        form = SavingGoalForm(instance=goal)

    return render(
        request,
        "savings_form.html",
        {"form": form, "mode": "edit", "goal": goal}
    )
