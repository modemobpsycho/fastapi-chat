from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    email: str
    username: str
    avatar_url: str
    is_active: bool

    class ConfigDict:
        from_attribute = True


class UserCreate(BaseModel):
    hashed_password: str

    class ConfigDict:
        from_attributes = True
