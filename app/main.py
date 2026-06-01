from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from . import models, schemas, crud, analyzer
from .database import engine, get_db

# Создание таблиц
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Python Code Diagnostic Service",
    description="Сервис диагностики Python-кода новичка: типичные ошибки, объяснения, ссылки на материалы",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Создание нового пользователя"""
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Получение информации о пользователе"""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/analyze/", response_model=schemas.CodeAnalysisResponse)
def analyze_code(request: schemas.CodeAnalysisRequest, db: Session = Depends(get_db)):
    """Анализ Python-кода и выявление типичных ошибок"""
    try:
        # 1. Анализ кода
        code_analyzer = analyzer.PythonCodeAnalyzer()
        errors = code_analyzer.analyze(request.code)
        
        # 2. Расчёт метрик
        score = analyzer.calculate_score(errors)
        recommendations = analyzer.get_recommendations(errors)
        
        # 3. Сохранение в БД
        db_check = crud.create_code_check(db=db, check=request, errors=errors)
        
        # 4. 🔧 КЛЮЧЕВОЙ ФИКС: Конвертация analyzer.ErrorDetail → dict для Pydantic v2
        errors_as_dict = []
        for e in errors:
            errors_as_dict.append({
                "line": int(e.line),
                "type": str(e.type),
                "message": str(e.message),
                "fix": str(e.fix),
                "resource": str(e.resource),
                "severity": str(getattr(e, 'severity', 'warning'))
            })
        
        # 5. Возврат ответа (теперь словари, а не объекты!)
        return schemas.CodeAnalysisResponse(
            check_id=db_check.id,
            errors_count=len(errors),
            errors=errors_as_dict,  # ← Передаём list[dict], а не list[ErrorDetail]
            score=float(score),
            recommendations=[str(r) for r in recommendations],
            created_at=db_check.created_at
        )
        
    except Exception as ex:
        print(f"🔴 CRITICAL ERROR in /analyze/: {type(ex).__name__}: {ex}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(ex)}")

@app.get("/users/{user_id}/checks", response_model=List[schemas.CodeAnalysisResponse])
def get_user_checks(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Получение истории проверок пользователя"""
    checks = crud.get_user_checks(db, user_id=user_id, skip=skip, limit=limit)
    return [
        schemas.CodeAnalysisResponse(
            check_id=check.id,
            errors_count=check.errors_found,
            errors=[analyzer.ErrorDetail(**err) for err in (check.errors_details or [])],
            score=analyzer.calculate_score([analyzer.ErrorDetail(**err) for err in (check.errors_details or [])]),
            recommendations=analyzer.get_recommendations([analyzer.ErrorDetail(**err) for err in (check.errors_details or [])]),
            created_at=check.created_at
        )
        for check in checks
    ]


@app.get("/users/{user_id}/statistics")
def get_user_statistics(user_id: int, db: Session = Depends(get_db)):
    """Получение статистики пользователя"""
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return crud.get_user_statistics(db, user_id=user_id)


@app.get("/")
def root():
    """Информация о сервисе"""
    return {
        "service": "Python Code Diagnostic Service",
        "version": "1.0.0",
        "docs": "/docs",
        "description": "Сервис для анализа кода начинающих Python-разработчиков"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)