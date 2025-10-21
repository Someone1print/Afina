
from django.contrib.messages.context_processors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from .models import IncomeCategory, ExpenseCategory, Income, Expense, Profile
from .forms import (IncomeCategoryForm, ExpenseCategoryForm,IncomeForm, ExpenseForm, ProfileForm)
from django.contrib.auth.decorators import login_required


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
def logout_view(request):
    logout(request)
    print("Вы вышли из системы")
    return redirect('login')

def home_view(request):
    return render(request, 'home.html')

# -------------------------
# IncomeCategory CRUD views
# -------------------------
def income_category_list(request):
    categories = IncomeCategory.objects.all().order_by('incomeName')
    return render(request, 'income_category_list.html', {'categories': categories})

def income_category_create(request):
    if request.method == 'POST':
        form = IncomeCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('income_category_list')
    else:
        form = IncomeCategoryForm()
    return render(request, 'income_category_form.html', {'form': form, 'title': 'Добавить категорию'})

def income_category_update(request, pk):
    category = get_object_or_404(IncomeCategory, pk=pk)
    if request.method == 'POST':
        form = IncomeCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('income_category_list')
    else:
        form = IncomeCategoryForm(instance=category)
    return render(request, 'income_category_form.html', {'form': form, 'title': 'Изменить категорию'})

def income_category_delete(request, pk):
    category = get_object_or_404(IncomeCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('income_category_list')
    return render(request, 'income_category_confirm_delete.html', {'category': category})

# -------- IncomeCategory (у тебя уже есть) --------
# оставь свои функции как есть:
# income_category_list, income_category_create, income_category_update, income_category_delete


# -------- ExpenseCategory CRUD --------
@login_required
def expense_category_list(request):
    categories = ExpenseCategory.objects.all().order_by('expenseName')
    return render(request, 'expense_category_list.html', {'categories': categories})

@login_required
def expense_category_create(request):
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expense_category_list')
    else:
        form = ExpenseCategoryForm()
    return render(request, 'expense_category_form.html', {'form': form, 'title': 'Добавить категорию расхода'})

@login_required
def expense_category_update(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('expense_category_list')
    else:
        form = ExpenseCategoryForm(instance=category)
    return render(request, 'expense_category_form.html', {'form': form, 'title': 'Изменить категорию расхода'})

@login_required
def expense_category_delete(request, pk):
    category = get_object_or_404(ExpenseCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
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
        form = IncomeForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('income_list')
    else:
        form = IncomeForm()
    return render(request, 'income_form.html', {'form': form, 'title': 'Добавить доход'})

@login_required
def income_update(request, pk):
    item = get_object_or_404(Income, pk=pk, user=request.user)
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('income_list')
    else:
        form = IncomeForm(instance=item)
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
        form = ExpenseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm()
    return render(request, 'expense_form.html', {'form': form, 'title': 'Добавить расход'})

@login_required
def expense_update(request, pk):
    item = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(instance=item)
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

@login_required(login_url='login')
def expense_category_create(request):
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно добавлена!')
            return redirect('expense_category_list')
        else:
            messages.error(request, 'Ошибка при добавлении категории. Попробуйте снова.')
    else:
        form = ExpenseCategoryForm()
    return render(request, 'expense_category_form.html', {'form': form, 'title': 'Добавить категорию'})

