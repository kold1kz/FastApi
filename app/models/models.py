from typing import Optional, Union
from pydantic import BaseModel, EmailStr, PositiveInt

def main(user_id: str):
    return user_id

class User(BaseModel):
    name: Optional[str] = True
    age: Optional[int] = True


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


