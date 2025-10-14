"""
URL configuration for afina project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # IncomeCategory CRUD
    path('income-categories/', views.income_category_list, name='income_category_list'),
    path('income-categories/add/', views.income_category_create, name='income_category_create'),
    path('income-categories/<int:pk>/edit/', views.income_category_update, name='income_category_update'),
    path('income-categories/<int:pk>/delete/', views.income_category_delete, name='income_category_delete'),
]

