from fastapi import FastAPI
from fastapi.responses import FileResponse
from models import models
from pydantic import BaseModel
import uvicorn


user = models.User(name="John Doe",age=1)
app = FastAPI()


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


@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/calulate/{num1;num2}")
async def calculate(num1:int, num2:int):
    return {"result": num1+num2}

@app.get("/custom")
async def read_custom_message():
    return {"message": "This is a custom message!"}


@app.get("/users", response_model=models.User)
async def getusers():
    return user

@app.post("/user")
async def getuser(user: models.User, response_model=models.Userresponse):
    return {"age": user.age, "name": user.name, "is_adult": user.age>=18}

@app.post("/feedback", response_model=models.Feedback)
async def response(user: models.FeedbackIn):
    with open('user.txt','a') as f:
        f.writelines(f'name: {user.name} - message: {user.message}\n')
        f.close()
    return {"message": f'Feedback received. Thank you, {user.name}!'}


@app.post('/create_user', response_model=models.UserCreate)
async def create_user(user: models.UserCreate):
    return user


@app.get('/products/{product_id}')
async def products(product_id: int):
    product = [item for item in sample_products if item["product_id"]==product_id]
    if not product:
        return {"message": f'Product with id: {product_id} not found!'}
    return product[0]


@app.get('/products/search')
async def search(keyword: str, category: str, limit: int):
    result = list(filter(lambda item: keyword.lower() in item['name'].lower(), sample_products))
    if category:
        result = list(filter(lambda item: item["category"] == category, result))
    return result[:limit]
    

if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True, workers=3)
