from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import IncomeCategory, ExpenseCategory, Income, Expense, Profile

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
        fields = ["category", "date", "amount", "note"]

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["category", "date", "amount", "note"]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "currency"]
        # fields = ["full_name", "currency", "avatar"]