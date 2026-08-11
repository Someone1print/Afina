# 💼 Afina — финансовый помощник

[![Django CI](https://github.com/Someone1print/Afina/actions/workflows/django.yml/badge.svg)](https://github.com/Someone1print/Afina/actions/workflows/django.yml)

**Afina** — Django-приложение для учёта доходов и расходов с персональными категориями и профилями пользователей.
Каждый пользователь имеет собственные записи и может добавлять свои категории поверх стандартных.

Групповой проект команды ПИ-4-23 (КГТУ им. И. Раззакова).

---

## 🧠 Основной функционал

- Регистрация и авторизация пользователей (сессии + JWT для API).
- Доходы и расходы, привязанные к каждому пользователю.
- 5 стандартных категорий по умолчанию:
  **Зарплата, Подарки, Проценты, Продажи, Другое** для доходов;
  **Еда, Транспорт, Жильё, Развлечения, Другое** для расходов.
- Свои категории поверх стандартных (уникальность без учёта регистра).
- Копилки (цели накоплений) с прогрессом.
- Подписки через **Stripe** (создание клиента, webhook, статусы подписки).
- Аналитика на дашборде: прогноз расходов (**Prophet**), поиск аномалий
  (**IsolationForest**), тренды (**LinearRegression**).
- REST API на **DRF**: фильтрация, поиск, пагинация, Swagger-документация
  на `/api/docs/` (drf-spectacular).

---

## 🚀 Установка и запуск (для любимого практиканта из КГТУ)

### 1. Клонировать репозиторий
```bash
git clone https://github.com/Someone1print/Afina.git
cd Afina
```

### 2. Создать виртуальное окружение
```bash
python -m venv .venv
```
Активировать:
- **Windows:** `.venv\Scripts\activate`
- **Linux/Mac:** `source .venv/bin/activate`

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Настроить окружение

Конфигурация читается из переменных окружения (см. `.env.example`).
База данных настраивается в **`afina/local_settings.py`** — файл в git, но
**защищён от коммитов** pre-commit hook'ом:

1. Установите git-хуки: `bash scripts/setup-hooks.sh` (Windows — Git Bash).
2. При необходимости поменяйте параметры подключения к БД — либо прямо в
   `local_settings.py`, либо через переменные `DJANGO_DB_*`.

### 5. Создать базу PostgreSQL
```bash
psql -U postgres -c "CREATE DATABASE afina;"
```

### 6. Применить миграции и запустить
```bash
python manage.py migrate
python manage.py runserver
```

Открыть: 👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🐳 Запуск в Docker

Поднимает PostgreSQL 16 и приложение одной командой:

```bash
docker compose up --build
```

Приложение: [http://localhost:8000](http://localhost:8000). Данные БД живут в
volume `postgres_data`.

---

## 🧪 Тесты

Тесты покрывают модели (копилки, подписки), сигналы (Stripe мокается,
переназначение категорий) и API (JWT, изоляция данных пользователей):

```bash
python manage.py test afina
```

Без локального PostgreSQL — на SQLite:

```bash
DJANGO_DB_ENGINE=sqlite3 python manage.py test afina
```

В CI (GitHub Actions) тесты гоняются на Python 3.12/3.13 против PostgreSQL 16
+ линт критических ошибок ruff.

---

## ⚙️ Переменные окружения

| Переменная | Назначение | Дефолт |
|---|---|---|
| `DJANGO_SECRET_KEY` | секретный ключ Django | dev-ключ (заменить в проде) |
| `DJANGO_DEBUG` | `1` — debug включён | `1` |
| `DJANGO_ALLOWED_HOSTS` | хосты через запятую | `localhost,127.0.0.1` |
| `DJANGO_DB_*` | подключение к PostgreSQL | локальные значения |
| `DJANGO_DB_ENGINE=sqlite3` | переключение на SQLite (тесты) | — |
| `STRIPE_SECRET_KEY` | секретный ключ Stripe | пусто |
| `STRIPE_PUBLISHABLE_KEY`, `STRIPE_PRICE_ID` | публичные параметры Stripe | тестовые |

---

## 📁 Структура проекта
```
afina/
├── afina/                # Django app (models, views, api_views, serializers, signals)
├── templates/            # HTML-шаблоны
├── static/               # CSS, JS, изображения
├── .github/workflows/    # CI (тесты + линт)
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── requirements.txt
```

---

## 🧑‍💻 Авторы

- **Команда Afina** (ПИ-4-23)

---
## TODO
1. Удалить лишнюю кнопку «Войти».
2. График доходов/расходов и статистика за период при входе в профиль.
3. Убрать кнопки «Изменить/Удалить» у дефолтных категорий.
4. Редирект на логин, если пользователь не авторизован.
