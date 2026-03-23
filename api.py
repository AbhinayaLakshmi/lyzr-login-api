from fastapi import FastAPI
from pydantic import BaseModel
from login_tool import login_to_portal

# ✅ THIS is what uvicorn is looking for
app = FastAPI()


class LoginRequest(BaseModel):
    url: str
    username: str
    password: str


@app.post("/login")
def login(request: LoginRequest):
    result = login_to_portal(
        request.url,
        request.username,
        request.password
    )
    return result