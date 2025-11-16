import time
import requests
from fastapi import FastAPI

app = FastAPI()

API_URL = "https://api.exchangerate.host/latest?base=XAU&symbols=USD"

data_cache = {"price": None, "timestamp": None}

def get_gold_price():
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        json_data = response.json()

        price = json_data["rates"]["USD"]
        return price
    except Exception as e:
        print("Error:", e)
        return None

@app.get("/price")
def price_endpoint():
    # If cache older than 10s → refresh
    now = time.time()
    if (
        data_cache["timestamp"] is None
        or now - data_cache["timestamp"] > 10
    ):
        new_price = get_gold_price()
        if new_price:
            data_cache["price"] = new_price
            data_cache["timestamp"] = now

    return {"gold_price_usd": data_cache["price"]}
