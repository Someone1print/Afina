
from django.contrib.messages.context_processors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from .models import IncomeCategory, ExpenseCategory, Income, Expense, Profile
from .forms import (IncomeCategoryForm, ExpenseCategoryForm,IncomeForm, ExpenseForm, ProfileForm)
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseForbidden



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
    categories = income_categories_for_user(request.user)
    return render(request, 'income_category_list.html', {'categories': categories})

@login_required
def income_category_create(request):
    if request.method == 'POST':
        form = IncomeCategoryForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.is_default = False
            obj.save()
            messages.success(request, 'Категория доходов добавлена.')
            return redirect('income_category_list')
    else:
        form = IncomeCategoryForm()
    return render(request, 'income_category_form.html', {'form': form, 'title': 'Добавить категорию доходов'})


@login_required
def income_category_update(request, pk):
    category = get_object_or_404(IncomeCategory, pk=pk)

    # запрещаем менять общие и чужие
    if category.owner is None or category.owner != request.user or (category.is_default and category.incomeName.lower() == 'другое'):
        return HttpResponseForbidden('Нельзя изменять общие или дефолтные категории.')

    if request.method == 'POST':
        form = IncomeCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория доходов обновлена.')
            return redirect('income_category_list')
    else:
        form = IncomeCategoryForm(instance=category)
    return render(request, 'income_category_form.html', {'form': form, 'title': 'Изменить категорию доходов'})

@login_required
def income_category_delete(request, pk):
    category = get_object_or_404(IncomeCategory, pk=pk)

    if category.owner != request.user or (category.is_default and category.incomeName.lower() == 'другое'):
        return HttpResponseForbidden('Нельзя удалять общие или дефолтные категории.')

    if request.method == 'POST':
        name = category.incomeName
        category.delete()  # 👈 сигнал переназначит связанные Income на «Другое»
        messages.success(request, f"Категория доходов «{name}» удалена, записи переназначены на «Другое».")
        return redirect('income_category_list')
    return render(request, 'income_category_confirm_delete.html', {'category': category})



# -------- ExpenseCategory CRUD --------
@login_required
def expense_category_list(request):
    categories = categories_for_user(request.user)
    return render(request, 'expense_category_list.html', {'categories': categories})

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
        return HttpResponseForbidden('Нельзя удалять общие или дефолтные категории.')

    if request.method == 'POST':
        name = category.expenseName
        category.delete()  # 👈 сигнал переназначит связанные Expense на «Другое»
        messages.success(request, f"Категория расходов «{name}» удалена, записи переназначены на «Другое».")
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