from fastapi import FastAPI
from pydantic import BaseModel
from auth import register, login

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    username: str
    app: str
    pin: str = ""

# -------- REGISTER --------
@app.post("/generate")
def generate(data: UserInput):
    password = register(data.username, data.app, data.pin)
    return {
        "status": "success",
        "password": password
    }

# -------- LOGIN --------
@app.post("/login")
def login_user(data: UserInput):
    success, result = login(data.username, data.app, data.pin)

    if success:
        return {
            "status": "success",
            "password": result
        }
    else:
        return {
            "status": "error",
            "message": result
        }