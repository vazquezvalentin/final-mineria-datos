import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard Cripto", layout="wide")

# Título y Descripción del Proyecto
st.title("💰 Dashboard de Análisis de Criptomonedas")
st.markdown("""
Este proyecto analiza la evolución de precios de criptomonedas utilizando **Series Temporales**.
Se aplicaron técnicas de suavizado exponencial para identificar tendencias.
""")

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    # Leemos el CSV que generamos en la etapa anterior
    df = pd.read_csv("datos_dashboard.csv")
    df['fecha'] = pd.to_datetime(df['fecha']) # Convertimos fecha para que se grafique bien
    return df

df = cargar_datos()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros")

# Filtro 1: Selector de Moneda
lista_monedas = df['moneda'].unique()
moneda_seleccionada = st.sidebar.selectbox("1. Elige una moneda:", lista_monedas)

# Filtro 2: Rango de Fechas (CORREGIDO)
# Definimos las fechas mínima y máxima permitidas según los datos
min_date = df['fecha'].min().date()
max_date = df['fecha'].max().date()

rango_fechas = st.sidebar.date_input(
    "2. Selecciona rango de fechas:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# --- LÓGICA DE FILTRADO ---
# Aquí validamos que el usuario haya elegido las dos fechas
if len(rango_fechas) == 2:
    start_date, end_date = rango_fechas
    
    # Aplicamos filtro maestro: Moneda Y Fechas
    df_filtrado = df[
        (df['moneda'] == moneda_seleccionada) & 
        (df['fecha'].dt.date >= start_date) & 
        (df['fecha'].dt.date <= end_date)
    ]
else:
    # Si falta una fecha, mostramos aviso y DETENEMOS la ejecución
    st.info("👋 Por favor, selecciona la fecha final en el calendario para actualizar los gráficos.")
    st.stop() 


# --- SECCIÓN DE MÉTRICAS (KPIs) ---
# Verificamos que queden datos después del filtro
if df_filtrado.empty:
    st.warning("No hay datos para el rango seleccionado.")
    st.stop()

ultimo_dato = df_filtrado.iloc[-1]

# Intentamos calcular la variación con el dato anterior (si existe)
if len(df_filtrado) > 1:
    anteultimo_dato = df_filtrado.iloc[-2]
    variacion_precio = ultimo_dato['precio_usd'] - anteultimo_dato['precio_usd']
    variacion_modelo = ultimo_dato['modelo_mineria'] - anteultimo_dato['modelo_mineria']
else:
    variacion_precio = 0
    variacion_modelo = 0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Precio Actual", f"${ultimo_dato['precio_usd']:.2f}", f"{variacion_precio:.2f}")
with col2:
    st.metric("Volatilidad (Riesgo)", f"{ultimo_dato['volatilidad']:.4f}")
with col3:
    st.metric("Predicción Modelo", f"${ultimo_dato['modelo_mineria']:.2f}", f"{variacion_modelo:.2f}")

# --- GRÁFICO PRINCIPAL: SERIE TEMPORAL ---
st.subheader(f"📈 Evolución de Precio vs Modelo ({moneda_seleccionada})")

fig_precio = px.line(df_filtrado, x='fecha', y=['precio_usd', 'modelo_mineria'],
                     labels={'value': 'Precio (USD)', 'fecha': 'Fecha', 'variable': 'Métrica'},
                     title="Comparación: Precio Real vs Suavizado Exponencial")
st.plotly_chart(fig_precio, use_container_width=True)

# --- GRÁFICOS SECUNDARIOS ---
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("📊 Volumen de Operaciones")
    fig_volumen = px.bar(df_filtrado, x='fecha', y='volumen', color_discrete_sequence=['#ffaa00'])
    st.plotly_chart(fig_volumen, use_container_width=True)

with col_der:
    st.subheader("📉 Tendencia Semanal")
    fig_tendencia = px.line(df_filtrado, x='fecha', y='tendencia_semanal', color_discrete_sequence=['green'])
    st.plotly_chart(fig_tendencia, use_container_width=True)

# --- CONCLUSIONES (HALLAZGOS) ---
st.markdown("---")
st.subheader("📝 Hallazgos y Conclusiones")

# Calculamos diferencia para el texto automático
diferencia = ultimo_dato['precio_usd'] - ultimo_dato['tendencia_mensual']

if diferencia > 0:
    # Caso Positivo
    with st.container(border=True):
        st.success("✅ **Tendencia ALCISTA (Bullish)**")
        st.write(f"El precio actual de **{moneda_seleccionada}** es: **${ultimo_dato['precio_usd']:.2f}**")
        st.write(f"Supera su promedio mensual de: **${ultimo_dato['tendencia_mensual']:.2f}**")
        st.info("💡 Interpretación: El mercado muestra optimismo. El precio está por encima de la tendencia.")

else:
    # Caso Negativo
    with st.container(border=True):
        st.warning("🔻 **Tendencia BAJISTA (Bearish)**")
        st.write(f"El precio actual de **{moneda_seleccionada}** es: **${ultimo_dato['precio_usd']:.2f}**")
        st.write(f"Ha caído por debajo de su promedio mensual de: **${ultimo_dato['tendencia_mensual']:.2f}**")
        st.error("⚠️ Interpretación: El mercado está corrigiendo o bajando. Precaución.")
