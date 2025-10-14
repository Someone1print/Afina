from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import IncomeCategory

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
