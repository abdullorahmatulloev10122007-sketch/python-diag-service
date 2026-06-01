import sys
import os

# Добавляем корневую папку проекта в пути поиска
# os.path.dirname(__file__) -> это папка tests
# os.path.dirname(...) еще раз -> это корень проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Только ПОСЛЕ этого импортируем app
from app.main import app
from app.database import engine, get_db
# ... остальные импорты
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, get_db
from app import models

models.Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()


def test_create_user():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


def test_analyze_code():
    code_data = {
        "code": "list = [1, 2, 3]\nif x == True:\n    pass",
        "user_id": None
    }
    response = client.post("/analyze/", json=code_data)
    assert response.status_code == 200
    data = response.json()
    assert "errors" in data
    assert "score" in data
    assert data["errors_count"] > 0


def test_analyze_clean_code():
    code_data = {
        "code": "def hello():\n    return 'world'",
        "user_id": None
    }
    response = client.post("/analyze/", json=code_data)
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 100.0


def test_get_nonexistent_user():
    response = client.get("/users/9999")
    assert response.status_code == 404