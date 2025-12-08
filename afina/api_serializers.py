from rest_framework import serializers
from .models import IncomeCategory, ExpenseCategory, Income, Expense, Profile
from django.db.models.functions import Lower
from django.contrib.auth.models import User


# --- Общие валидаторы для "Другое" (дефолт) ---
def _forbid_default_change_or_delete(instance):
    """
    Возбуждать ValidationError при попытке модифицировать/удалять дефолтную "Другое".
    """
    name_field = 'incomeName' if isinstance(instance, IncomeCategory) else 'expenseName'
    name_val = getattr(instance, name_field, '').lower()
    if instance.is_default and name_val == 'другое':
        raise serializers.ValidationError("Нельзя изменять или удалять дефолтную категорию «Другое».")


# --- Категории доходов ---
class IncomeCategorySerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault(), required=False)

    class Meta:
        model = IncomeCategory
        fields = ['id', 'incomeName', 'owner', 'is_default']
        read_only_fields = ['is_default', 'owner']

    def validate(self, attrs):
        # уникальность имени внутри owner или среди общих (owner=None) уже обеспечена UniqueConstraint,
        # но дадим дружелюбное сообщение ещё на уровне сериализатора
        name = attrs.get('incomeName') or getattr(self.instance, 'incomeName', None)
        if not name:
            return attrs
        # запрет применять owner=None из API
        if 'owner' in attrs and attrs['owner'] is None:
            raise serializers.ValidationError("owner не может быть NULL через API.")
        return attrs

    def update(self, instance, validated_data):
        _forbid_default_change_or_delete(instance)
        return super().update(instance, validated_data)

    def delete(self):
        _forbid_default_change_or_delete(self.instance)
        return super().delete()


# --- Категории расходов ---
class ExpenseCategorySerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault(), required=False)

    class Meta:
        model = ExpenseCategory
        fields = ['id', 'expenseName', 'owner', 'is_default']
        read_only_fields = ['is_default', 'owner']

    def validate(self, attrs):
        name = attrs.get('expenseName') or getattr(self.instance, 'expenseName', None)
        if not name:
            return attrs
        if 'owner' in attrs and attrs['owner'] is None:
            raise serializers.ValidationError("owner не может быть NULL через API.")
        return attrs

    def update(self, instance, validated_data):
        _forbid_default_change_or_delete(instance)
        return super().update(instance, validated_data)

    def delete(self):
        _forbid_default_change_or_delete(self.instance)
        return super().delete()


# --- Доход ---
class IncomeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category_name = serializers.CharField(source='category.incomeName', read_only=True)

    class Meta:
        model = Income
        fields = ['id', 'user', 'category', 'category_name', 'date', 'amount', 'note']
        read_only_fields = ['user']

    def validate_category(self, category):
        # запрет выбирать чужую категорию или общую категорию — можно (owner=None) — на твое усмотрение
        if category.owner not in (None, self.context['request'].user):
            raise serializers.ValidationError("Нельзя указывать чужую категорию.")
        return category


# --- Расход ---
class ExpenseSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category_name = serializers.CharField(source='category.expenseName', read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'user', 'category', 'category_name', 'date', 'amount', 'note']
        read_only_fields = ['user']

    def validate_category(self, category):
        if category.owner not in (None, self.context['request'].user):
            raise serializers.ValidationError("Нельзя указывать чужую категорию.")
        return category


# --- Профиль (текущего пользователя) ---
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['full_name', 'currency']

# --- Register ---
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )
        return user

# --- Login ---
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)