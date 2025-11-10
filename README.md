# afina
Group project for PI-4-23

## Setup
💼# 💼 Afina — финансовый помощник

**Afina** — это Django-приложение для учёта доходов и расходов с персональными категориями и профилями пользователей.  
Каждый пользователь имеет собственные записи и может добавлять свои категории поверх стандартных.
---

## 🚀 Установка и запуск проекта

### 1. Клонировать репозиторий
```bash
git clone https://github.com/username/afina.git
cd afina
```

### 2. Создать виртуальное окружение
```bash
python -m venv .venv
```
Активировать:
- **Windows:**  
  ```bash
  .venv\Scripts\activate
  ```
- **Linux/Mac:**  
  ```bash
  source .venv/bin/activate
  ```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

## 🧩 Настройка базы данных

## 🗂️ Настройка файла local_settings.py

Проект использует файл **`afina/local_settings.py`** для настройки базы данных.  
Этот файл находится под контролем git, но **защищён от коммитов** с помощью pre-commit hook’а.

**После клонирования репозитория:**

1. Установите git-хуки, выполнив команду:  
   - **Windows (Git Bash):** `./scripts/setup-hooks.sh`  
   - **Linux/Mac:** `bash scripts/setup-hooks.sh`
2. Файл `local_settings.py` появится в вашей рабочей директории  
3. Измените `local_settings.py`, указав свои локальные данные для подключения к базе данных  
4. **Важно:** любые изменения в `local_settings.py` будут заблокированы от коммита pre-commit hook’ом  


### 4. Создать базу PostgreSQL
Зайди в psql:
```bash
psql -U postgres
CREATE DATABASE afina;
```

### 5. Применить миграции
```bash
python manage.py makemigrations
python manage.py migrate
```

## ▶️ Запуск сервера
```bash
python manage.py runserver
```

Открой в браузере:
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🧠 Основной функционал

- Регистрация и авторизация пользователей.  
- Доходы и расходы, привязанные к каждому пользователю.  
- 5 стандартных категорий по умолчанию:  
  **Зарплата, Подарки, Проценты, Продажи, Другое** для доходов.  
  **Еда, Транспорт, Жильё, Развлечения, Другое** для расходов.  
- Возможность добавлять свои категории.  
- Профиль пользователя с валютой по умолчанию.

---

## 📁 Структура проекта
```
afina/
├── afina/                # Django app (models, views, forms, urls)
├── templates/            # HTML-шаблоны
├── static/               # CSS, JS, изображения
├── manage.py
└── requirements.txt
```

---

## ⚙️ Дополнительно

### Проверка кода:
```bash
python manage.py check
```

### Открыть shell:
```bash
python manage.py shell
```

### Сброс базы:
```bash
python manage.py flush
```

---

## 🧑‍💻 Авторы

- **Команда Afina**

---