from locale import currency
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="FastAPI Chat App with React JS",
              version="0.0.1 Ильюха чидор")

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fake_users = [{"id": 1, "role": "admin", "name": "Bob"}, {
    "id": 2, "role": "user", "name": "Alice"}, {"id": 3, "role": "user", "name": "John"}]

fake_trades = [{
    "id": 1, "user_id": 1, "currency": "BTC", "side": "buy", "price": 1000.0, "amount": 0.5}]


@app.get("/hello")
def hello():
    return {"message": "Hello World"}


@app.get("/")
def home():
    return {"AAAAAAAA": "ничего себе система"}


class User(BaseModel):
    id: int
    role: str
    name: str


@app.get("/users/{user_id}", response_model=List[User])
def get_user(user_id: int):
    for user in fake_users:
        if user["id"] == user_id:
            return [user]
        else:
            return {"message": "User not found"}


@app.post("/change_username/{user_id}")
def change_username(user_id: int, new_name: str):
    current_user = list(
        filter(lambda user: user.get("id") == user_id, fake_users))[0]

    current_user["name"] = new_name
    return {"status": "ok", "data": current_user}


@app.get("/users")
def get_users():
    return fake_users


class Trade(BaseModel):
    id: int
    user_id: int
    currency: str = Field(max_length=3)
    side: str
    price: float = Field(ge=0.0)
    amount: float


@app.get("/trades")
def get_trades(limit: int = 1, offset: int = 0):
    return fake_trades[offset:][:limit]


@app.post("/trades")
def add_trade(trades: List[Trade]):
    fake_trades.extend(trades)
    return {"status": "ok"}
