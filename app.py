from fastapi import FastAPI
import requests
import time

app = FastAPI()

# API de oro (gratis)
API_URL = "https://api.metals.live/v1/spot"

data_cache = {"price": None, "timestamp": None}


def get_gold_price():
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        json_data = response.json()

        # metals.live devuelve una lista [[precio]]
        price = json_data[0][0]
        return price
    except:
        return None


@app.get("/price")
def price_endpoint():
    now = time.time()

    # refrescar cada 10 segundos
    if (
        data_cache["timestamp"] is None
        or now - data_cache["timestamp"] > 10
    ):
        new_price = get_gold_price()
        if new_price:
            data_cache["price"] = new_price
            data_cache["timestamp"] = now

    return {"gold_price_usd": data_cache["price"]}


@app.get("/")
def root():
    return {"status": "Backend OK"}
