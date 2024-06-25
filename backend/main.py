import asyncio
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional, Annotated
import bcrypt
import models
from database import Base, engine, AsyncSession
from sqlalchemy.orm import Session
import schemas

app = FastAPI()


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


def get_db():
    db = AsyncSession()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[AsyncSession, Depends(get_db)]


@app.post("/login/")
def login(username: str, password: str, db: AsyncSession = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not bcrypt.checkpw(password.encode("utf-8"), user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return {"message": "Login successful"}


@app.post("/register/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
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
        hashed_password: bytes = bcrypt.hashpw(
            user.password.encode("utf-8"), salt)
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
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error saving user to database",
        )

    return new_user


@app.get("/profile/{user_id}/", response_model=schemas.User)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    profile = schemas.User(
        username=user.username,
        name=user.name,
        email=user.email
    )

    return profile


@app.websocket("/chat/{room_id}/{user_id}")
async def chat_endpoint(room_id: int, user_id: int, websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()

    room_membership = db.query(models.RoomMembership).filter(
        models.RoomMembership.room_id == room_id,
        models.RoomMembership.user_id == user_id
    ).first()

    if not room_membership:
        room_membership = models.RoomMembership(
            user_id=user_id,
            room_id=room_id
        )
        db.add(room_membership)
        db.commit()
        db.refresh(room_membership)

    while True:
        message = await websocket.receive_text()

        new_message = models.Message(
            content=message,
            from_id=user_id,
            to_id=room_id
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)

        room_memberships = db.query(models.RoomMembership).filter(
            models.RoomMembership.room_id == room_id,
            models.RoomMembership.user_id != user_id
        ).all()

        for membership in room_memberships:
            await send_message_to_user(websocket, new_message.content, membership.user_id)


async def send_message_to_user(websocket: WebSocket, message: str, user_id: int):
    await websocket.send_text(f"User {user_id}: {message}")


@app.get("/")
async def root():
    return {"message": "Hello World"}
