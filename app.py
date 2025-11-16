import time
import streamlit as st
import requests
import pandas as pd

# URL del backend (FastAPI)
API_URL = "https://xauusd-backend.onrender.com/price"

st.title("Precio XAU/USD en tiempo real")
st.subheader("Actualización cada 10 segundos")

placeholder = st.empty()
historico = []

def obtener_precio():
    try:
        r = requests.get(API_URL, timeout=5)
        r.raise_for_status()
        precio = r.json().get("gold_price_usd")
        return precio
    except Exception as e:
        st.error(f"Error obteniendo precio: {e}")
        return None

while True:
    precio = obtener_precio()
    if precio:
        timestamp = pd.Timestamp.now()

        historico.append({"time": timestamp, "price": precio})
        df = pd.DataFrame(historico)

        with placeholder.container():
            st.metric("Precio actual", f"{precio} USD")
            st.line_chart(df.set_index("time"))

    time.sleep(10)
