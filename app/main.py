"""main file"""
from datetime import datetime
import uvicorn
from fastapi import FastAPI, Cookie, Response, HTTPException, Depends, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from models import models
import hashlib
import uuid
from jose import jwt



user = models.User(name="John Doe",age=1)
app = FastAPI()
security = HTTPBasic()
SECRET_KEY = "`d808e0c5dd4bd498fc52b1b50bc5a2bd8921dc9511818e413a160ceb38e00863`"
# hashlib.sha256(uuid.uuid4().bytes).hexdigest()
# print("secret key=", SECRET_KEY)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_jwt_token(username: str):
    payload = {"sub": username}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


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

def get_user(username):
    """get user"""
    if username in fake_db:
        return fake_db[username]
    return None


def verify_session_token(session_token: str = Cookie(None), user=Depends(get_user)):
    """check verify_ses"""
    if not session_token or session_token != user["session_token"]:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


def get_hashed_value(password):
    """get hashed"""
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(user, password):
    """check pass"""
    return user["password"] == get_hashed_value(password)

@app.post("/login2")
async def login(user: models.Login, response: Response):
    """login user"""
    client = get_user(user.username)
    if not client or not check_password(client, user.password):
        raise HTTPException(status_code=400, detail="Invalid data")

    session_token = str(uuid.uuid4())
    fake_db[user.username]["session_token"] = session_token

    response.set_cookie(key="session_token", value=session_token, secure=True)

    return {"message": "Successfully logged"}

@app.post("/register")
async def register_user(user: models.Login):
    """reg"""
    if get_user(user.username):
        raise HTTPException(status_code=400, detail="Username already exist in database")
    hashed_password = get_hashed_value(user.password)
    fake_db[user.username] = {"username": user.username, "password": hashed_password}
    return "Registration was successful, all 200 :D"


@app.get("/user")
async def get_user_data(user=Depends(verify_session_token)):
    """get"""
    return user

@app.get("/headers")
async def get_headers(request: Request):
    """headers"""
    user_agent = request.headers.get("user-agent")
    accept_language = request.headers.get("accept-language")

    if user_agent is None or accept_language is None:
        raise HTTPException(status_code=400, detail="Missing required headers")

    response_data = {
        "User-Agent": user_agent,
        "Accept-Language": accept_language
    }

    return response_data


USER_DATA = [models.User(**{"username": "user111", "password": "pass1"}), models.User(**{"username": "user2", "password": "pass2"})]

def authenticate_user(form_data: OAuth2PasswordRequestForm=Depends(security)):
    """auth"""
    user = get_user_from_db(form_data.username)
    if user is None or user.password != form_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
    token = create_jwt_token(user.username)
    return {"access_token": token, "token_type": "bearer"}

def get_user_from_db(username: str):
    """get user"""
    for user in USER_DATA:
        if user.username == username:
            return user
    return None

@app.get("/login")
def get_protected_resource(user: models.User = Depends(authenticate_user)):
    """g"""
    return {"message": "You got my secret, welcome", "user_info": user}




if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8000, reload=True, workers=3)
