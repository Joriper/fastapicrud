from fastapi import FastAPI
from fastapi import *
from models_data import *
from datetime import *
from db import *
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
import uuid
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


SECRET_KEY = "abcdxyz"
ALGORITHM = "HS256"

app = FastAPI()


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",    
    "http://0.0.0.0:8001",
    "http://127.0.0.1:8001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="build/static"), name="static")

@app.get("/")
def index():
    return FileResponse("build/index.html")

@app.get("/signin")
def index():
    return FileResponse("build/index.html")

@app.get("/signup")
def index():
    return FileResponse("build/index.html")

@app.get("/notes")
def index():
    return FileResponse("build/index.html")

@app.post("/user/api/signup")
async def register_user(user:Register):
    data = user.dict()
    print(data)
    check = register_collection.find_one({"email":data['email']})
    if not check:
        register_collection.insert_one(data)
        login_collection.insert_one({"email":data['email'],"password":data['password']})
        return {"status":"OK","message":"User created successfully and redirecting to login..."}
    else:
        return {"status":"Failed","message":"Email already associate with different account"}


@app.post("/user/api/signin")
async def login_user(user:Login,response:Response):
    data = user.dict()
    check = login_collection.find_one({"email":data['email']},{"_id":0})
    register_check = register_collection.find_one({"email":data['email']},{"_id":0})
    if not check:
        return {"status":"Failed","message":"Invalid username or password"}
    else:
        print(check)
        token_data = {
            "email": data['email'],
            "types":register_check['types'],
            "exp": datetime.utcnow() + timedelta(hours=2)
        }        
        token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
        response.set_cookie(
            key="token",
            value=token,
            httponly=True,
            secure=False,
            samesite="Lax"
        )        
        return {"status":"OK","message":"Success","data":check,"token":token}



def check_token(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing header",
        )

    try:
        payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT token",
        )        
    return True

@app.post("/user/api/new",dependencies=[Depends(check_token)])
async def notes_data(request:Request,notes:Notes):
    data = notes.dict()
    token = request.headers.get("Authorization")

    random_uuid_id = uuid.uuid4()
    payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])    
    data['email'] = payload['email']
    data['custome_id'] = str(random_uuid_id)    

    check = notes_collection.insert_one(data)
    del data['_id']

    return {"status":"OK","message":"Note created successfully","data":data}



@app.put("/user/api/update",dependencies=[Depends(check_token)])
async def notes_data(request:Request,notes:Notes):
    data = notes.dict()
    token = request.headers.get("Authorization")

    random_uuid_id = uuid.uuid4()
    payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])    
    if payload['types'] == "admin":
        notes_collection.update_one({"custome_id":data['custome_id']},{"$set":{"title":data['title'],"description":data['description']}})
    else:
        notes_collection.update_one({"email":payload['email'],"custome_id":data['custome_id']},{"$set":{"title":data['title'],"description":data['description']}})
        
    return {"status":"OK","message":"Updated successfully"}


@app.get("/user/api/notes",dependencies=[Depends(check_token)])
async def fetch_notes(request:Request):
    token = request.headers.get("Authorization")

    payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
    if payload['types'] == "admin":
        data = notes_collection.find({},{"_id":0})
    else:
        data = notes_collection.find({"email":payload['email']},{"_id":0})
        
    result = [doc for doc in data]
    return {"status":"OK","messaage":"Available Notes","data":result}



@app.get("/user/api/notes",dependencies=[Depends(check_token)])
async def logout(request:Request):
    token = request.headers.get("Authorization")  

    payload = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
    if payload['types'] == "admin":
        data = notes_collection.find({},{"_id":0})
    else:
        data = notes_collection.find({"email":payload['email']},{"_id":0})
        
    result = [doc for doc in data]
    return {"status":"OK","messaage":"Available Notes","data":result}