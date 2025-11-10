# afina
Group project for PI-4-23

## Setup

### Database Configuration

The project uses `afina/local_settings.py` for database settings. This file is tracked in git but **protected from commits** via a pre-commit hook.

**After cloning the repository:**

1. Install the git hooks by running:
   - **Windows (Git Bash):** `./scripts/setup-hooks.sh`
   - **Linux/Mac:** `bash scripts/setup-hooks.sh`
2. The `local_settings.py` file will be available in your working directory
3. Modify `local_settings.py` with your local database credentials as needed
4. **Note:** Any changes to `local_settings.py` will be blocked from being committed by the pre-commit hook 

TO do 
1. Инструкция для запуска проекта.
2. Интсрукция для создания БД.
3. Инструкция для подключения к проекту.
