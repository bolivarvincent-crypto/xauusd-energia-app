# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
from datetime import datetime, timezone
import time

# -------------------------
# Config
# -------------------------
st.set_page_config(page_title="Volatilidad / Energía XAUUSD (Diario)", layout="wide", initial_sidebar_state="expanded")
st.title("📈 Volatilidad / Energía del Oro (XAUUSD) — Timeframe Diario")

# Auto-refresh (client-side JS reload) every N seconds
AUTO_REFRESH_SECONDS = 10  # you requested 10s
st.markdown(
    f"""
    <script>
        // auto-reload the page every {AUTO_REFRESH_SECONDS * 1000} ms
        setTimeout(function(){{ window.location.reload(); }}, {AUTO_REFRESH_SECONDS * 1000});
    </script>
    """,
    unsafe_allow_html=True,
)

# Small instructions
with st.expander("ℹ️ Cómo funciona (resumen)"):
    st.write("""
    - Datos: Yahoo Finance (ticker `XAUUSD=X` — precio spot oro vs USD).  
    - Frecuencia: la página se recarga automáticamente cada 10 segundos.  
    - Volatilidad (\"Energía\"): calculada como `High - Low` por día.  
    - Puedes cambiar la ventana de la media móvil y el umbral crítico en la barra lateral.
    """)

# -------------------------
# Sidebar controls
# -------------------------
st.sidebar.header("Controles")
st.sidebar.write("Fuente: Yahoo Finance (gratis).")

ticker = st.sidebar.text_input("Ticker para oro (si deseas cambiar):", value="XAUUSD=X")
days = st.sidebar.number_input("Días de histórico (máx 3650):", min_value=10, max_value=3650, value=365)
ma_window = st.sidebar.slider("Ventana MA (energía) — días:", min_value=1, max_value=60, value=10)
critical_level = st.sidebar.number_input("Nivel crítico de energía (dólares):", min_value=0.0, value=50.0, format="%.2f")
show_colorbar = st.sidebar.checkbox("Mostrar escala de colores (energía)", value=True)
show_ma = st.sidebar.checkbox("Mostrar media móvil de energía", value=True)

# -------------------------
# Fetch data (Yahoo Finance)
# -------------------------
@st.cache_data(ttl=30)  # cache por 30s para evitar demasiadas llamadas desde la interfaz
def fetch_ohlc(ticker_symbol: str, period_days: int):
    # yfinance period can be set as string like "365d"
    per = f"{max(1, int(period_days))}d"
    try:
        df = yf.download(tickers=ticker_symbol, period=per, interval="1d", progress=False, auto_adjust=False)
        # if empty, try another ticker fallback
        if df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        df = df.rename(columns={
            "Date": "Date",
            "Open": "Open",
            "High": "High",
            "Low": "Low",
            "Close": "Close",
            "Adj Close": "Adj Close",
            "Volume": "Volume"
        })
        # keep only needed columns
        df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
        return df
    except Exception as e:
        st.error(f"Error descargando datos: {e}")
        return pd.DataFrame()

df = fetch_ohlc(ticker, days)

if df.empty:
    st.warning("No se encontraron datos para el ticker. Revisa que 'XAUUSD=X' sea válido o intenta 'GC=F'.")
    st.stop()

# -------------------------
# Compute energy / volatility
# -------------------------
df["Volatilidad"] = df["High"] - df["Low"]
# Smoothed energy (ma)
df["MA_Energia"] = df["Volatilidad"].rolling(window=max(1, ma_window)).mean()

# Normalize energia for coloring (0..1)
max_e = df["Volatilidad"].max()
min_e = df["Volatilidad"].min()
if pd.isna(max_e) or max_e == 0:
    df["EnergiaNorm"] = 0.0
else:
    df["EnergiaNorm"] = (df["Volatilidad"] - min_e) / (max_e - min_e + 1e-12)

# Map to a color value for Plotly continuous scale (we'll use EnergiaNorm)
df["HoverText"] = df.apply(lambda r: f"Fecha: {r['Date'].date()}<br>Volatilidad: ${r['Volatilidad']:.2f}<br>Energía (norm): {r['EnergiaNorm']:.3f}", axis=1)

# -------------------------
# Layout: two columns / big charts
# -------------------------
col1, col2 = st.columns([3, 1], gap="large")

with col1:
    # Candlestick (plotly)
    fig_candle = go.Figure(data=[go.Candlestick(
        x=df["Date"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        increasing_line_color='white',
        decreasing_line_color='gray',
        hovertext=df["Date"].dt.strftime("%Y-%m-%d"),
        name="Precio"
    )])
    fig_candle.update_layout(
        template="plotly_dark",
        title=f"Precio XAUUSD (Daily) — {ticker}",
        xaxis_title="Fecha",
        yaxis_title="Precio (USD)",
        height=480,
        margin=dict(l=60, r=10, t=50, b=50),
    )

    st.plotly_chart(fig_candle, use_container_width=True)

    # Histogram / Energy
    # We'll color bars by EnergiaNorm (continuous)
    fig_hist = px.bar(
        df,
        x="Date",
        y="Volatilidad",
        color="EnergiaNorm",
        color_continuous_scale="Turbo",
        hover_data={"Volatilidad": ":.2f", "MA_Energia": ":.2f"},
        labels={"Volatilidad": "Volatilidad (USD)", "EnergiaNorm": "Energía (norm)"},
        title="Histograma de Volatilidad (Energía)",
        height=360,
    )
    fig_hist.update_layout(template="plotly_dark", margin=dict(l=60, r=10, t=50, b=50))
    # Add MA line on top if enabled
    if show_ma:
        fig_hist.add_trace(go.Scatter(
            x=df["Date"], y=df["MA_Energia"],
            mode="lines",
            name=f"MA ({ma_window}d)",
            line=dict(width=2, dash="dash", color="cyan"),
            hovertemplate="MA: %{y:.2f}"
        ))

    # Add critical level
    fig_hist.add_hline(y=critical_level, line_dash="dot", line_color="red",
                       annotation_text=f"Nivel crítico ${critical_level:.2f}", annotation_position="top right")

    if show_colorbar:
        fig_hist.update_coloraxes(colorbar_title="Energía (norm)")

    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.subheader("Detalles / Estado")
    st.markdown("**Últimas filas de datos:**")
    st.dataframe(df.tail(10)[["Date", "Open", "High", "Low", "Close", "Volatilidad"]].assign(
        Date=lambda d: d["Date"].dt.strftime("%Y-%m-%d")
    ), height=300)

    # Last update UTC
    last_update_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    st.write(f"**Última actualización (servidor):** {last_update_utc}")

    # Client local time (javascript)
    st.markdown(
        """
        <div>
            <strong>Hora local del navegador:</strong>
            <div id="local_time"></div>
        </div>
        <script>
            function updateLocalTime(){
                const el = document.getElementById('local_time');
                if (!el) return;
                el.innerText = new Date().toLocaleString();
            }
            updateLocalTime();
            setInterval(updateLocalTime, 1000);
        </script>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.write("Opciones rápidas:")
    st.write(f"- Ticker usado: `{ticker}`")
    st.write(f"- Histórico: {days} días")
    st.write(f"- Ventana MA: {ma_window} días")
    st.write(f"- Auto-refresh: cada {AUTO_REFRESH_SECONDS} segundos (recarga de página)")

    st.markdown("---")
    st.write("Consejos:")
    st.info("""
    - Si deseas cambiar el umbral crítico usa la casilla en la barra lateral.  
    - Si el gráfico no se actualiza, espera 10 segundos para la recarga automática o recarga manualmente la página.  
    - Para desplegar en Streamlit Cloud sigue las instrucciones provistas en el README.
    """)

# Footer: credits
st.markdown("---")
st.caption("App generada automáticamente. Datos por Yahoo Finance. No es asesoría financiera.")

