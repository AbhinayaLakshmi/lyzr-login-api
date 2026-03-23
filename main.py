from fastapi import FastAPI
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from datetime import datetime

app = FastAPI()


class ExtractRequest(BaseModel):
    portal_url: str
    username: str
    password: str


@app.post("/login-and-extract")
def login_and_extract(req: ExtractRequest):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # Open login page
            page.goto(req.portal_url, wait_until="networkidle")

            # Login using placeholders / input types
            page.locator(
                'input[placeholder*="firstsource.com"], input[type="email"], input[name="email"]'
            ).first.fill(req.username)
            page.locator(
                'input[type="password"], input[name="password"]'
            ).first.fill(req.password)
            page.get_by_role("button", name="Sign In").click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)

            # Extract total submitted
            total_label = page.locator("text=Total Submitted").first
            total_card = total_label.locator("xpath=ancestor::*[1]")
            total_text = total_card.inner_text()
            lines = [line.strip() for line in total_text.splitlines() if line.strip()]
            total_submitted = lines[0] if lines else ""

            # Extract submission names from dashboard
            submission_links = page.locator("text=/WE-[0-9]+/")
            submissions = []

            for i in range(submission_links.count()):
                text = submission_links.nth(i).inner_text().strip()
                if text:
                    submissions.append(text)

            browser.close()

            return {
                "status": "success",
                "portal_url": req.portal_url,
                "module": "dashboard",
                "user_role": "maker",
                "extracted_at": datetime.utcnow().isoformat() + "Z",
                "data": {
                    "total_submitted": total_submitted,
                    "submission_names": submissions
                },
                "message": "Dashboard data retrieved successfully."
            }

    except Exception as e:
        return {
            "status": "error",
            "portal_url": req.portal_url,
            "module": "dashboard",
            "user_role": "unknown",
            "extracted_at": datetime.utcnow().isoformat() + "Z",
            "data": {
                "total_submitted": "",
                "submission_names": []
            },
            "message": str(e)
        }