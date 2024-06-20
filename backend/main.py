from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated
import bcrypt
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import schemas

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# app.include_router(users.router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        users = db.query(models.User).offset(skip).limit(limit).all()
        if users is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving users from database"
            )
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@app.post("/register/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db):
    if not user.email or not user.username or not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email, username, and password are required",
        )
    existing_user = db.query(models.User).filter(
        or_(models.User.email == user.email,
            models.User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists",
        )
    salt = bcrypt.gensalt()
    try:
        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), salt)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error hashing password",
        )

    new_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        avatar_url=user.avatar_url if user.avatar_url else None,
    )
    db.add(new_user)
    try:
        db.commit()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving user to database",
        )
    try:
        db.refresh(new_user)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing user from database",
        )

    return new_user


@app.get("/")
async def root():
    return {"message": "Hello World"}
