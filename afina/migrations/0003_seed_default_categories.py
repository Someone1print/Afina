# afina/migrations/000X_seed_default_categories.py
from django.conf import settings
from django.db import migrations, models

def seed_defaults(apps, schema_editor):
    IncomeCategory = apps.get_model('afina', 'IncomeCategory')
    ExpenseCategory = apps.get_model('afina', 'ExpenseCategory')

    income_defaults = ['Зарплата', 'Подарки', 'Проценты', 'Продажи', 'Другое']
    expense_defaults = ['Еда', 'Транспорт', 'Жильё', 'Развлечения', 'Другое']

    for name in income_defaults:
        IncomeCategory.objects.get_or_create(
            incomeName=name, owner=None, defaults={'is_default': True}
        )
    for name in expense_defaults:
        ExpenseCategory.objects.get_or_create(
            expenseName=name, owner=None, defaults={'is_default': True}
        )

class Migration(migrations.Migration):
    dependencies = [
        ('afina', '0002_alter_expensecategory_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [migrations.RunPython(seed_defaults, migrations.RunPython.noop)]
