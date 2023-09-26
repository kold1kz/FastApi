"""main file"""
from datetime import datetime, timedelta
import uvicorn
from typing import Annotated
from fastapi import FastAPI, Cookie, Response, HTTPException, Depends, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from passlib.context import CryptContext
from models import models, postgres
from databases import Database
import hashlib
import uuid
import jwt





user = models.User(name="John Doe",age=1)
app = FastAPI()
security = HTTPBasic()
SECRET_KEY = "`d808e0c5dd4bd498fc52b1b50bc5a2bd8921dc9511818e413a160ceb38e00863`"
# hashlib.sha256(uuid.uuid4().bytes).hexdigest()
# print("secret key=", SECRET_KEY)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.on_event("startup")
async def startup_database():
    await postgres.database.connect()

@app.on_event("shutdown")
async def shutdown_database():
    await postgres.database.disconnect()




sample_product_1 = {
    "product_id": 123,
    "name": "Smartphone",
    "category": "Electronics",
    "price": 599.99
}

sample_product_2 = {
    "product_id": 456,
    "name": "Phone Case",
    "category": "Accessories",
    "price": 19.99
}

sample_product_3 = {
    "product_id": 789,
    "name": "Iphone",
    "category": "Electronics",
    "price": 1299.99
}

sample_product_4 = {
    "product_id": 101,
    "name": "Headphones",
    "category": "Accessories",
    "price": 99.99
}

sample_product_5 = {
    "product_id": 202,
    "name": "Smartwatch",
    "category": "Electronics",
    "price": 299.99
}

sample_products = [sample_product_1, sample_product_2, sample_product_3, sample_product_4, sample_product_5]

fake_db={"username": "Jhoni",
         "password": 1234}


@app.get("/")
async def root():
    """root"""
    return FileResponse("index.html")

@app.get("/calulate/{num1;num2}")
async def calculate(num1:int, num2:int):
    """calculat"""
    return {"result": num1+num2}

@app.get("/custom")
async def read_custom_message():
    """red mes"""
    return {"message": "This is a custom message!"}


@app.get("/users", response_model=models.User)
async def getusers():
    """get userS"""
    return user


@app.post("/feedback", response_model=models.Feedback)
async def response(user: models.FeedbackIn):
    """response"""
    with open('user.txt','a') as file:
        file.writelines(f'name: {user.name} - message: {user.message}\n')
        file.close()
    return {"message": f'Feedback received. Thank you, {user.name}!'}


@app.post('/create_user', response_model=models.UserCreate)
async def create_user(user: models.UserCreate):
    """create user"""
    return user


@app.get('/products/{product_id}')
async def products(product_id: int):
    """products"""
    product = [item for item in sample_products if item["product_id"]==product_id]
    if not product:
        return {"message": f'Product with id: {product_id} not found!'}
    return product[0]


@app.get('/products/search')
async def search(keyword: str, category: str, limit: int):
    """search"""
    result = list(filter(lambda item: keyword.lower() in item['name'].lower(), sample_products))
    if category:
        result = list(filter(lambda item: item["category"] == category, result))
    return result[:limit]

def get_user1(username):
    """get user"""
    if username in fake_db:
        return fake_db[username]
    return None


USERS_DATA = {
    "admin": {"username": "admin", "password": "adminpass", "role": "admin"},
    "user": {"username": "user", "password": "userpass", "role": "user"},
    "guest": {"username": "guest", "password": "guestpass", "role": "guest"}
} 




# Функция для создания JWT токена
def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)



def get_user_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("payload 151 = ", payload) # декодируем токен
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )



def get_user(username: str):
    if username in USERS_DATA:
        user_data = USERS_DATA[username]
        return models.Login(**user_data)
    return None



@app.post("/token/")
def login(user_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_data_from_db = get_user(user_data.username)
    if user_data_from_db is None or user_data.password != user_data_from_db.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_jwt_token({"sub": user_data.username})} # тут мы добавляем полезную нагрузку в токен, и говорим, что "sub" содержит значение username


# Защищенный роут для админов, когда токен уже получен
@app.get("/admin/")
def get_admin_info(current_user: str = Depends(get_user_from_token)):
    user_data = get_user(current_user)
    if user_data.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return {"message": "Welcome Admin!"}


# Защищенный роут для обычных пользователей, когда токен уже получен
@app.get("/user/")
def get_user_info(current_user: str = Depends(get_user_from_token)):
    user_data = get_user(current_user)
    if user_data.role != "user":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return {"message": "Hello User!"}

@app.get("/guest/")
def get_user_info(current_user: str = Depends(get_user_from_token)):
    user_data = get_user(current_user)
    if user_data.role != "guest":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return {"message": "Hello User!"}


@app.get('/todos/{todo_id}/')
async def get_todo_id(todo_id: int, db = Depends(postgres.get_db)):
    """get todo by id"""
    item = db.query(models.Item).filter(models.Item.id == todo_id).first()
    
    if item is None:
        raise HTTPException(status_code=404, detail="Объект не найден")
    
    return item

@app.put("/todos/{todo_id}/", response_model=models.Bd_updated)
async def update_todo(todo_id: int, new_data:models.Bd_updated, db = Depends(postgres.get_db)):
    item = db.query(models.Item).filter(models.Item.id == todo_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    for key, value in new_data.dict().items():  # Используйте .dict() для преобразования Pydantic-модели в словарь
        if key is not None:
            setattr(item, key, value)
    db.commit()
    db.refresh(item) 
    return item

@app.delete("/todos/{todo_id}/", response_model=str)
async def delete_todo(todo_id: int,  db = Depends(postgres.get_db)):
    try:
        item = db.query(models.Item).filter(models.Item.id == todo_id).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Объект не найден")
        db.delete(item)
        db.commit()
        return "Объект удален успешно"
    except Exception as e:
        raise HTTPException(status_code=500, detail="Произошла ошибка при удалении объекта")


@app.post("/todos/")
async def add_todo(user_data: models.Bd_create_todo, db = Depends(postgres.get_db)):
    try:
        item=models.Item(title=user_data.title, description=user_data.description, completed=False)
        if item is None:
            raise HTTPException(status_code=404, detail="Объект не определен")
        
        async with db.begin() as transaction:
            db.add(item)
            await transaction.commit()
            await db.flush()

        return item
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Произошла ошибка при добавлении объекта")



if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True, workers=3)
