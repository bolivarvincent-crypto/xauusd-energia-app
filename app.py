import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="XAU/USD en tiempo real", layout="wide")

st.title("Precio del Oro (XAU/USD) en Tiempo Real")
st.subheader("Actualización automática cada 10 segundos")

backend_url = "https://xauusd-backend.onrender.com/precio"

placeholder_price = st.empty()
placeholder_chart = st.empty()

historical = []

def obtener_precio():
    try:
        res = requests.get(backend_url, timeout=5).json()

        if "gold_price_usd" in res and res["gold_price_usd"]:
            return float(res["gold_price_usd"])
        return None

    except Exception as e:
        st.error(f"Error al obtener precio: {e}")
        return None


# Loop en Streamlit
while True:
    price = obtener_precio()

    if price:
        timestamp = pd.Timestamp.now()
        historical.append({"time": timestamp, "price": price})
        df = pd.DataFrame(historical)

        # Mostrar precio
        placeholder_price.metric("Precio actual", f"{price:.2f} USD")

        # Mostrar gráfica
        placeholder_chart.line_chart(df.set_index("time"))

    time.sleep(10)
