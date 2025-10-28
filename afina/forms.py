from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import IncomeCategory, ExpenseCategory, Income, Expense, Profile
from datetime import date


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class IncomeCategoryForm(forms.ModelForm):
    incomeName = forms.CharField(label='Название категории', max_length=100)

    class Meta:
        model = IncomeCategory
        fields = ['incomeName']

class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ["expenseName"]

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
        super().__init__(*args, **kwargs)
        self.fields['date'].input_formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Разрешаем ввод разных форматов даты
        self.fields['date'].input_formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y']
        # По умолчанию — сегодняшняя дата
        self.fields['date'].initial = date.today()
        self.fields['category'].label_from_instance = lambda obj: getattr(obj, 'expenseName',
                                                                          getattr(obj, 'name', str(obj)))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "currency"]
        # fields = ["full_name", "currency", "avatar"]