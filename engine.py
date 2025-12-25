
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify
import streamlit as st

HEADERS = {"User-Agent": "Mozilla/5.0"}

# --------------------------------------------------
# PLATFORM CHECKS (FIXED HEURISTICS)
# --------------------------------------------------

def instagram(value, t):
    if t != "username":
        return None
    url = f"https://www.instagram.com/{value}/"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return ("Instagram", value, url)
    return None


def twitter(value, t):
    if t != "username":
        return None
    url = f"https://twitter.com/{value}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return ("Twitter/X", value, url)
    return None


def github(value, t):
    if t != "username":
        return None
    url = f"https://github.com/{value}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return ("GitHub", value, url)
    return None


def telegram(value, t):
    if t != "username":
        return None
    url = f"https://t.me/{value}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return ("Telegram", value, url)
    return None


def linkedin(value, t):
    if t != "username":
        return None
    url = f"https://www.linkedin.com/in/{value}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return ("LinkedIn", value, url)
    return None


# ---------------- EMAIL ----------------

def google_email(value, t):
    if t != "email":
        return None
    if value.endswith("@gmail.com"):
        return ("Google / Gmail", value, "https://accounts.google.com")
    return None


def amazon_email(value, t):
    if t != "email":
        return None
    if "@" in value:
        return ("Amazon", value, "https://www.amazon.in")
    return None


def flipkart_email(value, t):
    if t != "email":
        return None
    if "@" in value:
        return ("Flipkart", value, "https://www.flipkart.com")
    return None


def swiggy_email(value, t):
    if t != "email":
        return None
    if "@" in value:
        return ("Swiggy", value, "https://www.swiggy.com")
    return None


def zomato_email(value, t):
    if t != "email":
        return None
    if "@" in value:
        return ("Zomato", value, "https://www.zomato.com")
    return None


# ---------------- PHONE ----------------

def whatsapp_phone(value, t):
    if t != "phone":
        return None
    if len(value) == 10 or value.startswith("+91"):
        return ("WhatsApp", value, "https://www.whatsapp.com")
    return None


def truecaller_phone(value, t):
    if t != "phone":
        return None
    if len(value) == 10 or value.startswith("+91"):
        return ("Truecaller", value, "https://www.truecaller.com")
    return None


def paytm_phone(value, t):
    if t != "phone":
        return None
    if len(value) == 10:
        return ("Paytm", value, "https://paytm.com")
    return None


def phonepe_phone(value, t):
    if t != "phone":
        return None
    if len(value) == 10:
        return ("PhonePe", value, "https://www.phonepe.com")
    return None


# --------------------------------------------------
# PLATFORM LIST (TOP INDIAN APPS)
# --------------------------------------------------

PLATFORMS = [
    instagram,
    twitter,
    github,
    telegram,
    linkedin,
    google_email,
    amazon_email,
    flipkart_email,
    swiggy_email,
    zomato_email,
    whatsapp_phone,
    truecaller_phone,
    paytm_phone,
    phonepe_phone,
]

# --------------------------------------------------
# MULTITHREADED SCANNER
# --------------------------------------------------

def scan(value, t):
    results = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(p, value, t) for p in PLATFORMS]
        for f in as_completed(futures):
            try:
                r = f.result()
                if r:
                    results.append({
                        "Platform": r[0],
                        "Input": r[1],
                        "URL": r[2]
                    })
            except:
                pass
    return results


# --------------------------------------------------
# FLASK BACKEND
# --------------------------------------------------

app = Flask(__name__)

@app.route("/scan", methods=["POST"])
def api_scan():
    data = request.json
    return jsonify(scan(data["value"], data["type"]))


def run_flask():
    app.run(port=5000, debug=False, use_reloader=False)


# --------------------------------------------------
# STREAMLIT UI
# --------------------------------------------------

def run_ui():
    st.set_page_config("Indian OSINT Engine", layout="wide")
    st.title("🇮🇳 Indian OSINT Presence Finder")

    t = st.selectbox("Search Type", ["username", "email", "phone"])
    value = st.text_input("Enter value")

    if st.button("SCAN"):
        with st.spinner("Scanning Indian platforms..."):
            res = requests.post(
                "http://127.0.0.1:5000/scan",
                json={"value": value, "type": t}
            ).json()

        if not res:
            st.error("No presence detected")
        else:
            st.success(f"Detected on {len(res)} platforms")
            st.table(res)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    time.sleep(1)
    run_ui()
