from fastapi import FastAPI
import time
import yfinance as yf

app = FastAPI()

data_cache = {"price": None, "timestamp": None}

# Ticker de XAUUSD en Yahoo Finance
TICKER = "XAUUSD=X"

def get_gold_price():
    try:
        ticker = yf.Ticker(TICKER)
        data = ticker.history(period="1d", interval="1m")

        if data.empty:
            return None

        price = float(data["Close"].iloc[-1])
        return price

    except:
        return None


@app.get("/price")
def price_endpoint():
    now = time.time()

    # actualizar cada 10s
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
