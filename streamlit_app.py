import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, date

# URL de tu backend FastAPI en Render (aún no desplegado)
BACKEND_URL = "https://your-backend.onrender.com/price"

# ---- FUNCIONES -----------------------------------------------------

def get_price():
    """Consulta el backend FastAPI que devuelve el precio del oro."""
    try:
        r = requests.get(BACKEND_URL, timeout=5)
        r.raise_for_status()
        return r.json()["gold_price_usd"]
    except:
        return None

def init_session_state():
    """Crea variables para almacenar datos del día."""
    if "prices" not in st.session_state:
        st.session_state.prices = []
    if "timestamps" not in st.session_state:
        st.session_state.timestamps = []
    if "today" not in st.session_state:
        st.session_state.today = date.today()

def reset_if_new_day():
    """Al llegar un nuevo día, reiniciar datos."""
    if st.session_state.today != date.today():
        st.session_state.prices = []
        st.session_state.timestamps = []
        st.session_state.today = date.today()

# ---- INICIO APP -----------------------------------------------------

st.title("📈 XAUUSD Energía / Volatilidad (Tiempo Real)")

st.write("Actualiza cada vez que entras. Basado en datos gratuitos.")

init_session_state()
reset_if_new_day()

price = get_price()

if price:
    st.session_state.prices.append(price)
    st.session_state.timestamps.append(datetime.now())

# ---- CÁLCULO DE ENERGÍA DIARIA -------------------------------------

if len(st.session_state.prices) > 1:
    max_p = max(st.session_state.prices)
    min_p = min(st.session_state.prices)
    energia = max_p - min_p
else:
    energia = 0

st.subheader("🔋 Energía (Volatilidad del día)")
st.metric("Energía actual", f"{energia:.3f}")

# ---- GRÁFICA --------------------------------------------------------

if len(st.session_state.prices) > 1:
    df = pd.DataFrame({
        "Fecha": st.session_state.timestamps,
        "Precio": st.session_state.prices
    })
    st.line_chart(df, x="Fecha", y="Precio")

st.write("Último precio:", price)
