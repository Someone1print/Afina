# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # движок для PostgreSQL
        'NAME': 'afina',       # имя базы данных
        'USER': 'postgres',   # имя пользователя PostgreSQL
        'PASSWORD': '152535',  # пароль пользователя
        'HOST': 'localhost',  # хост сервера БД
        'PORT': '5432',       # порт PostgreSQL
    }
}

