from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    "id": 1, "from": 1, "to": 2, "value": 10.0}, {"id": 2, "from": 2, "to": 3, "value": 20.0}, {"id": 3, "from": 3, "to": 1, "value": 30.0}, {
        "id": 4, "from": 1, "to": 3, "value": 40.0
}, {"id": 5, "from": 2, "to": 1, "value": 50.0}]


@app.get("/hello")
def hello():
    return {"message": "Hello World"}


@app.get("/")
def home():
    return {"AAAAAAAA": "ничего себе система"}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    for user in fake_users:
        if user["id"] == user_id:
            return user
        else:
            return {"message": "User not found"}


@app.get("/trades")
def get_trades(limit: int = 1, offset: int = 0):
    return fake_trades[offset:][:limit]
