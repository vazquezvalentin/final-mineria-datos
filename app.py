import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard Cripto", layout="wide")

st.title("💰 Dashboard de Análisis de Criptomonedas")
st.markdown("Análisis de tendencias utilizando **Suavizado Exponencial**.")

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    df = pd.read_csv("datos_dashboard.csv")
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

df = cargar_datos()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros")

# FILTRO 1: Selector de Moneda
lista_monedas = df['moneda'].unique()
moneda_seleccionada = st.sidebar.selectbox("1. Elige moneda:", lista_monedas)

# FILTRO 2: Slider de Días (MUCHO MÁS ESTABLE)
dias_visualizar = st.sidebar.slider("2. Días a visualizar:", min_value=30, max_value=900, value=180)

# --- LÓGICA DE FILTRADO ---
# Primero filtramos por moneda
df_filtrado = df[df['moneda'] == moneda_seleccionada]
# Luego tomamos solo los últimos X días seleccionados en el slider
df_filtrado = df_filtrado.iloc[-dias_visualizar:]

# --- MÉTRICAS ---
if df_filtrado.empty:
    st.stop()

ultimo_dato = df_filtrado.iloc[-1]
anteultimo_dato = df_filtrado.iloc[-2]

variacion_precio = ultimo_dato['precio_usd'] - anteultimo_dato['precio_usd']
variacion_modelo = ultimo_dato['modelo_mineria'] - anteultimo_dato['modelo_mineria']

col1, col2, col3 = st.columns(3)
col1.metric("Precio Actual", f"${ultimo_dato['precio_usd']:.2f}", f"{variacion_precio:.2f}")
col2.metric("Volatilidad", f"{ultimo_dato['volatilidad']:.4f}")
col3.metric("Predicción Tendencia", f"${ultimo_dato['modelo_mineria']:.2f}", f"{variacion_modelo:.2f}")

# --- GRÁFICOS ---
st.subheader(f"📈 Evolución de Precio (Últimos {dias_visualizar} días)")
fig_precio = px.line(df_filtrado, x='fecha', y=['precio_usd', 'modelo_mineria'], title="Precio Real vs Modelo")
st.plotly_chart(fig_precio, use_container_width=True)

col_izq, col_der = st.columns(2)
col_izq.plotly_chart(px.bar(df_filtrado, x='fecha', y='volumen', title="Volumen"), use_container_width=True)
col_der.plotly_chart(px.line(df_filtrado, x='fecha', y='tendencia_semanal', title="Tendencia Semanal"), use_container_width=True)

# --- HALLAZGOS ---
st.markdown("---")
diferencia = ultimo_dato['precio_usd'] - ultimo_dato['tendencia_mensual']

if diferencia > 0:
    st.success(f"✅ **Tendencia ALCISTA**: El precio (${ultimo_dato['precio_usd']:.2f}) supera el promedio mensual.")
else:
    st.warning(f"🔻 **Tendencia BAJISTA**: El precio (${ultimo_dato['precio_usd']:.2f}) está bajo el promedio mensual.")
