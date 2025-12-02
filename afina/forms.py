from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import IncomeCategory, ExpenseCategory, Income, Expense, Profile, SavingGoal
from datetime import date
from django.db.models import Q


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class IncomeCategoryForm(forms.ModelForm):
    incomeName = forms.CharField(label='Категории доходов', max_length=100)

    class Meta:
        model = IncomeCategory
        fields = ['incomeName']

class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ["expenseName"]
        labels = {
            "expenseName": "Категория расходов",
        }

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['category', 'date', 'amount', 'note']
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',   # браузерный календарь
                    'class': 'form-control'
                },
                format='%Y-%m-%d'    # формат для Django
            ),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

    # чтобы Django понимал ввод '21.10.2025' и другие локальные варианты
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # форматы даты (оставляем как было)
        self.fields['date'].input_formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']
        self.fields['date'].initial = date.today()

        # --- категории ---
        if user is not None:
            # все категории пользователя + общие
            qs = (
                IncomeCategory.objects
                .filter(Q(owner=user) | Q(owner__isnull=True))
                .order_by('-is_default', 'incomeName')
            )
            self.fields['category'].queryset = qs

            # 🔹 дефолтная категория — “Другое”
            default_cat = qs.filter(incomeName__iexact="Другое").first()
            if default_cat:
                self.fields['category'].initial = default_cat
        else:
            # если user нет, пустой queryset (на всякий случай)
            self.fields['category'].queryset = IncomeCategory.objects.none()


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'date', 'amount', 'note']
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                },
                format='%Y-%m-%d'
            ),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
    # чтобы Django понимал ввод '21.10.2025' и другие локальные варианты
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # форматы даты (оставляем как было)
        self.fields['date'].input_formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']
        self.fields['date'].initial = date.today()

        # --- категории ---
        if user is not None:
            # все категории пользователя + общие
            qs = (
                ExpenseCategory.objects
                .filter(Q(owner=user) | Q(owner__isnull=True))
                .order_by('-is_default', 'expenseName')
            )
            self.fields['category'].queryset = qs

            # 🔹 дефолтная категория — “Другое”
            default_cat = qs.filter(expenseName__iexact="Другое").first()
            if default_cat:
                self.fields['category'].initial = default_cat
        else:
            # если user нет, пустой queryset (на всякий случай)
            self.fields['category'].label_from_instance = lambda obj: getattr(obj, 'expenseName',
                                                                              getattr(obj, 'name', str(obj)))


class ProfileForm(forms.ModelForm):
    # поля пользователя
    username = forms.CharField(label="Имя пользователя", max_length=150)
    email = forms.EmailField(label="Email", required=False)

    class Meta:
        model = Profile
        fields = ["full_name", "currency"]  # только поля из Profile!
        labels = {
            "full_name": "ФИО",
            "currency": "Валюта",
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "p-input-control"}),
            "currency": forms.Select(attrs={"class": "p-input-control"}),
        }

class SavingGoalForm(forms.ModelForm):
    class Meta:
        model = SavingGoal
        fields = ["title", "target_amount", "current_amount"]
        labels = {
            "title": "Цель",
            "target_amount": "Сумма цели (KGS)",
            "current_amount": "Уже накоплено (KGS)",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "target_amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "current_amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }