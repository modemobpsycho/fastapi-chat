from datetime import datetime
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import TIMESTAMP, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

metadata = Base.metadata


class User(SQLAlchemyBaseUserTable, Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)

    rooms = relationship("RoomMembership", back_populates="user")
    friends = relationship("Friend", back_populates="user")
    blocks = relationship("Block", back_populates="user")


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime)

    users = relationship("RoomMembership", back_populates="room")


class RoomMembership(Base):
    __tablename__ = "room_membership"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    room_id = Column(Integer, ForeignKey("room.id"))
    joined_at = Column(DateTime)

    user = relationship("User", back_populates="room")
    room = relationship("Room", back_populates="user")


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    sent_at = Column(DateTime)
    from_id = Column(Integer, ForeignKey("user.id"))
    to_id = Column(Integer, ForeignKey("user.id"))

    from_user = relationship("User", foreign_keys=[from_id])
    to_user = relationship("User", foreign_keys=[to_id])


class FriendRequest(Base):
    __tablename__ = "friend_request"

    id = Column(Integer, primary_key=True, index=True)
    from_id = Column(Integer, ForeignKey("user.id"))
    to_id = Column(Integer, ForeignKey("user.id"))
    sent_at = Column(DateTime)

    from_user = relationship("User", foreign_keys=[from_id])
    to_user = relationship("User", foreign_keys=[to_id])


class Friend(Base):
    __tablename__ = "friend"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    friend_id = Column(Integer, ForeignKey("user.id"))
    added_at = Column(DateTime)

    user = relationship("User", foreign_keys=[
                        user_id], back_populates="friend")
    friend = relationship("User", foreign_keys=[friend_id])


class Block(Base):
    __tablename__ = "block"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    blocked_user_id = Column(Integer, ForeignKey("user.id"))
    blocked_at = Column(DateTime)

    user = relationship("User", foreign_keys=[
                        user_id], back_populates="block")
    blocked_user = relationship("User", foreign_keys=[blocked_user_id])
