# 🔍 Python Code Diagnostic Service

Сервис для анализа кода начинающих Python-разработчиков. Выявляет типичные ошибки, предоставляет объяснения и ссылки на обучающие материалы.

## 🎯 Возможности

- ✅ **Статический анализ кода** через AST (Abstract Syntax Tree)
- ✅ **15+ типичных ошибок** новичков:
  - Переопределение встроенных имен
  - Сравнение с True/False
  - Модификация списка во время итерации
  - Изменяемые аргументы по умолчанию
  - Bare except
  - Wildcard imports
  - Нарушение PEP 8
- ✅ **Оценка качества кода** (0-100)
- ✅ **Персонализированные рекомендации**
- ✅ **Ссылки на документацию** и обучающие материалы
- ✅ **История проверок** и статистика
- ✅ **REST API** с документацией (Swagger/OpenAPI)

## 🛠 Технологии

- **Backend**: FastAPI, SQLAlchemy
- **Database**: SQLite
- **Analysis**: Python AST module
- **Validation**: Pydantic
- **Tests**: pytest, coverage
- **Deployment**: Docker, Docker Compose

## 🚀 Быстрый старт

### Локальный запуск

```bash
# 1. Клонирование репозитория
git clone <your-repo-url>
cd PYTHON-DIAG-SERVICE

# 2. Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Установка зависимостей
pip install -r requirements.txt

# 4. Запуск сервера
uvicorn app.main:app --reload

# 5. Открыть в браузере
http://localhost:8000
http://localhost:8000/docs  # Swagger документация