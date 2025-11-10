from django.core.exceptions import ValidationError

def delete_model(self, request, obj):
    if getattr(obj, 'is_default', False) and \
       (getattr(obj, 'expenseName', None) == 'Другое' or getattr(obj, 'incomeName', None) == 'Другое'):
        raise ValidationError("Нельзя удалить дефолтную категорию 'Другое'.")
    return super().delete_model(request, obj)