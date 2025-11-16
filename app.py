import streamlit as st
import requests
import pandas as pd
import time

API_URL = "https://xauusd-backend.onrender.com/price"   # <-- AQUÍ VA TU ENLACE CORRECTO

st.title("Precio XAU/USD en tiempo real")
st.subheader("Actualización cada 10 segundos")

placeholder = st.empty()
data = []

while True:
    try:
        response = requests.get(API_URL)
        price = response.json()["price"]

        timestamp = pd.Timestamp.now()
        data.append({"time": timestamp, "price": price})

        df = pd.DataFrame(data)

        with placeholder.container():
            st.line_chart(df.set_index("time"))

        time.sleep(10)

    except Exception as e:
        st.error(f"Error: {e}")
        time.sleep(5)
