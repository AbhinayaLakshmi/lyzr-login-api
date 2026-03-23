from fastapi import FastAPI
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from datetime import datetime

app = FastAPI()


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/test-login")
def test_login(req: LoginRequest):
    try:
        portal_name = "Kansas eForms"
        login_url = "https://www.sos.ks.gov/eforms/user_login.aspx?frm=BS"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Open page
            page.goto(login_url)

            # Wait for full load
            page.wait_for_timeout(6000)

            # 👇 CLICK somewhere on page to focus
            page.mouse.click(300, 300)

            # 👇 TYPE username
            page.keyboard.type(req.username)

            # TAB → go to password
            page.keyboard.press("Tab")

            # 👇 TYPE password
            page.keyboard.type(req.password)

            # ENTER → submit
            page.keyboard.press("Enter")

            # Wait for response
            page.wait_for_timeout(4000)

            # Try to capture error text
            error_message = ""

            try:
                error_message = page.locator("body").inner_text()
            except:
                pass

            browser.close()

            # crude but effective check
            if "Please" in error_message or "Invalid" in error_message:
                return {
                    "status": "login_failed",
                    "portal": portal_name,
                    "extracted_at": datetime.utcnow().isoformat() + "Z",
                    "error_message": error_message[:200],  # limit text
                    "data": {}
                }

            return {
                "status": "success",
                "portal": portal_name,
                "extracted_at": datetime.utcnow().isoformat() + "Z",
                "error_message": "",
                "data": {"message": "login done"}
            }

    except Exception as e:
        return {
            "status": "error",
            "portal": portal_name,
            "extracted_at": datetime.utcnow().isoformat() + "Z",
            "error_message": str(e),
            "data": {}
        }