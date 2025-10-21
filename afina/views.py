
from django.contrib.messages.context_processors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm, IncomeCategoryForm
from .models import IncomeCategory

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
