from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()


class LoginRequest(BaseModel):
    url: str
    username: str
    password: str


@app.post("/login")
def login(request: LoginRequest):
    try:
        session = requests.Session()

        # --- Handle test site ---
        if "the-internet.herokuapp.com" in request.url:
            login_url = "https://the-internet.herokuapp.com/authenticate"

            payload = {
                "username": request.username,
                "password": request.password
            }

            response = session.post(login_url, data=payload)

            if "You logged into a secure area!" in response.text:
                return {
                    "status": "success",
                    "message": "Login successful"
                }
            else:
                return {
                    "status": "failed",
                    "message": "Invalid username or password"
                }

        return {
            "status": "error",
            "message": "Unsupported website"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }