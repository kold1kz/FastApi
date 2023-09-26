from typing import Optional, Union
from .postgres import Base, String, Integer, Column, Boolean
from pydantic import BaseModel, EmailStr, PositiveInt

def main(user_id: str):
    return user_id

class User(BaseModel):
    username: Optional[str] = True
    password: Optional[str] = True
    


class Userresponse(BaseModel):
    name: Optional[str] = True
    age: Optional[int] = True
    is_adult: Optional[bool] = True

class FeedbackIn(BaseModel):
    name: Optional[str] = True
    message: Optional[str] = True

class Feedback(BaseModel):
    message: Optional[str] = True


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Union[PositiveInt, None] = None
    is_subscribed: Union[bool, None] = None


class Login(BaseModel):
    username: str
    password: str
    role: Optional[str] = None

class Bd_updated(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Bd_create_todo(BaseModel):
    title: str
    description: str
    completed: Optional[bool] = False

class Item(Base):
    __tablename__ = "FastApi"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    completed = Column(Boolean, index=False)
    

