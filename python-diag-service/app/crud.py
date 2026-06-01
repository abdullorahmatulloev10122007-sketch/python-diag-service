from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas
from datetime import datetime


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_code_check(db: Session, check: schemas.CodeAnalysisRequest, errors: List):
    # Pydantic v2: используем .model_dump() вместо .dict()
    errors_as_dicts = [e.model_dump() for e in errors]

    db_check = models.CodeCheck(
        user_id=check.user_id,
        code_snippet=check.code,
        errors_found=len(errors),
        errors_details=errors_as_dicts
    )
    db.add(db_check)
    db.commit()
    db.refresh(db_check)

    # Обновляем статистику ТОЛЬКО если пользователь авторизован
    if check.user_id:
        for error in errors:
            update_error_statistic(db, check.user_id, error.type)

    return db_check


def get_user_checks(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.CodeCheck).filter(
        models.CodeCheck.user_id == user_id
    ).offset(skip).limit(limit).all()


def update_error_statistic(db: Session, user_id: int, error_type: str):
    stat = db.query(models.ErrorStatistic).filter(
        models.ErrorStatistic.user_id == user_id,
        models.ErrorStatistic.error_type == error_type
    ).first()
    
    if stat:
        stat.count += 1
        stat.last_seen = datetime.utcnow()
    else:
        stat = models.ErrorStatistic(
            user_id=user_id,
            error_type=error_type,
            count=1
        )
        db.add(stat)
    
    db.commit()


def get_user_statistics(db: Session, user_id: int) -> dict:
    checks = db.query(models.CodeCheck).filter(
        models.CodeCheck.user_id == user_id
    ).all()
    
    error_stats = db.query(models.ErrorStatistic).filter(
        models.ErrorStatistic.user_id == user_id
    ).all()
    
    total_errors = sum(check.errors_found for check in checks)
    
    return {
        "total_checks": len(checks),
        "total_errors": total_errors,
        "error_types": error_stats,
        "progress": {
            "last_check": checks[-1].created_at if checks else None,
            "average_errors": total_errors / len(checks) if checks else 0
        }
    }