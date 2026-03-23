import requests
from bs4 import BeautifulSoup


# ---------- Helper: Build payload (FIXED for this site) ----------
def build_payload(soup, username, password):
    payload = {}

    # Extract hidden fields (ASP.NET tokens)
    inputs = soup.find_all("input")
    for inp in inputs:
        name = inp.get("name")
        value = inp.get("value", "")
        field_type = inp.get("type")

        if name and field_type == "hidden":
            payload[name] = value

    # ✅ Correct login fields (based on your inspect)
    payload["ctl00$MainContent$txtUserAccount"] = username
    payload["ctl00$MainContent$txtPassword"] = password
    payload["ctl00$MainContent$btnSignIn"] = "Sign In"

    return payload


# ---------- Helper: Parse response ----------
def parse_response(response, url):
    soup = BeautifulSoup(response.text, "html.parser")

    # If password field still exists → login failed
    if soup.find("input", {"type": "password"}):
        return {
            "status": "failed",
            "message": "Login failed (still on login page)"
        }

    # If redirected → success
    if response.url != url:
        return {
            "status": "success",
            "message": f"Redirected to {response.url}"
        }

    return {
        "status": "unknown",
        "message": "Login attempted but result unclear"
    }


# ---------- MAIN FUNCTION ----------
def login_to_portal(url: str, username: str, password: str):
    try:
        session = requests.Session()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Referer": url
        }

        session.headers.update(headers)

        # STEP 1: GET login page
        res = session.get(url)

        print("\n--- DEBUG: GET Status ---")
        print(res.status_code)

        soup = BeautifulSoup(res.text, "html.parser")

        # STEP 2: Build payload
        payload = build_payload(soup, username, password)

        print("\n--- DEBUG: Payload Keys ---")
        print(list(payload.keys()))

        # STEP 3: POST login
        response = session.post(url, data=payload)

        print("\n--- DEBUG: POST Status ---")
        print(response.status_code)
        print("Final URL:", response.url)

        # STEP 4: Parse result
        return parse_response(response, url)

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ---------- TEST RUN ----------
if __name__ == "__main__":
    test_url = "https://www.sos.ks.gov/eforms/user_login.aspx?frm=BS"

    result = login_to_portal(test_url, "fake_user", "fake_password")

    print("\n--- FINAL RESULT ---")
    print(result)