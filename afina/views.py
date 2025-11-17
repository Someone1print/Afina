
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from .models import IncomeCategory, ExpenseCategory, Income, Expense, Profile
from .forms import (IncomeCategoryForm, ExpenseCategoryForm,IncomeForm, ExpenseForm, ProfileForm)
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.db.models.functions import TruncMonth
from django.utils.dateparse import parse_date

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
    return render(request, 'home.html')

# -------------------------
# IncomeCategory CRUD views
# -------------------------
@login_required
def income_category_list(request):
    qs = IncomeCategory.objects.order_by('id')
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
    qs = ExpenseCategory.objects.order_by('id')
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
    items = Income.objects.filter(user=request.user).select_related('category').order_by('-date','-id')
    return render(request, 'income_list.html', {'items': items})

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
    items = Expense.objects.filter(user=request.user).select_related('category').order_by('-date','-id')
    return render(request, 'expense_list.html', {'items': items})

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


# -------- Profile (просмотр/редактирование) --------
@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'profile_view.html', {'profile': profile})

@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile_form.html', {'form': form, 'title': 'Профиль'})

from django.contrib import messages


def categories_for_user(user):
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
