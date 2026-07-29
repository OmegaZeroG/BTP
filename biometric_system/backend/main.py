from fastapi import FastAPI
from pydantic import BaseModel

from auth import register, login

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

    fingerprint: str
    iris: str


# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------

@app.post("/generate")
def generate(data: UserInput):

    password = register(
        data.username,
        data.app,
        data.pin,
        data.fingerprint,
        data.iris
    )

    return {
        "status": "success",
        "password": password
    }


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------

@app.post("/login")
def login_user(data: UserInput):

    success, result = login(
        data.username,
        data.app,
        data.pin,
        data.fingerprint,
        data.iris
    )

    if success:

        return {
            "status": "success",
            "password": result
        }

    return {
        "status": "error",
        "message": result
    }