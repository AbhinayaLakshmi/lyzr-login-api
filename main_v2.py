from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import requests

app = FastAPI()


class PortalRequest(BaseModel):
    portal_name: str
    api_url: str
    bearer_token: str


@app.post("/portal-extract")
def portal_extract(req: PortalRequest):
    try:
        # 🔐 Headers (mimic browser request)
        headers = {
            "Authorization": f"Bearer {req.bearer_token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://qms-uat.firstsource.com",
            "Referer": "https://qms-uat.firstsource.com/dashboard",
            "User-Agent": "Mozilla/5.0"
        }

        # 📡 API Call
        response = requests.get(req.api_url, headers=headers)

        # ❌ Handle failure
        if response.status_code != 200:
            return {
                "status": "access_denied",
                "portal_name": req.portal_name,
                "extracted_at": datetime.utcnow().isoformat() + "Z",
                "data": {"items": []},
                "message": f"API call failed with status {response.status_code}"
            }

        api_data = response.json()

        # 🎯 Extract required fields
        items = []

        for invoice in api_data.get("data", []):
            items.append({
                "invoice_id": invoice.get("invoiceNumber"),
                "customer": invoice.get("customerId"),
                "status": invoice.get("status"),
                "amount": invoice.get("totalAmount")
            })

        return {
            "status": "success",
            "portal_name": req.portal_name,
            "extracted_at": datetime.utcnow().isoformat() + "Z",
            "data": {
                "items": items
            },
            "message": "Data extracted via API successfully."
        }

    except Exception as e:
        return {
            "status": "parsing_error",
            "portal_name": req.portal_name,
            "extracted_at": datetime.utcnow().isoformat() + "Z",
            "data": {"items": []},
            "message": str(e)
        }
