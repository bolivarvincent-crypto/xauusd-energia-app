from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/status")
def status():
    return {"status": "Backend OK"}

@app.get("/price")
def price():
    try:
        r = requests.get("https://api.exchangerate.host/latest?base=XAU&symbols=USD")
        data = r.json()
        return {"gold_price_usd": data["rates"]["USD"]}
    except:
        return {"gold_price_usd": None}
