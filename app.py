# app.py — AI Green Planner (versión final corregida para Streamlit Cloud)
# Autora: Moira Machado
# Proyecto: LEKT | Correr con propósito — Prototipo funcional
# 2025

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ======================================================
# 🔹 CONFIGURACIÓN INICIAL DE LA APP
# ======================================================
st.set_page_config(
    page_title="AI Green Planner | LEKT",
    page_icon="🌿",
    layout="wide"
)

# ======================================================
# 🔹 ESTILO VISUAL
# ======================================================
st.markdown("""
    <style>
    body {
        background-color: #F4F5F2;
        font-family: 'Poppins', sans-serif;
    }
    .stButton>button {
        background-color: #3A5A40;
        color: white;
        border-radius: 10px;
        padding: 0.5em 1.2em;
    }
    .stButton>button:hover {
        background-color: #2F4A36;
        color: #DAD7CD;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 AI Green Planner — LEKT | Correr con propósito")
st.caption("Prototipo funcional para la planificación sostenible de eventos deportivos")

# ======================================================
# 🔹 CARGA DE API KEY (desde secrets TOML o variable local)
# ======================================================
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["general"]["OPENAI_API_KEY"]
        st.success("🔐 API Key cargada correctamente desde secrets.")
    except Exception:
        api_key = None
        st.warning("⚠️ No se encontró la API Key. Se usará modo demo (sin conexión a OpenAI).")

# ======================================================
# 🔹 FORMULARIO PRINCIPAL
# ======================================================
st.subheader("📝 Datos del evento")

with st.form("form_evento"):
    col1, col2 = st.columns(2)

    with col1:
        nombre_evento = st.text_input("Nombre del evento", "LEKT Trail 2026")
        fecha_evento = st.date_input("Fecha del evento")
        lugar = st.text_input("Lugar (ciudad o coordenadas)", "Lago Lolog, Neuquén")
        participantes = st.number_input("Participantes estimados", min_value=10, value=300, step=10)

        movilidad_auto = st.slider("Participantes que vienen en auto (%)", 0.0, 1.0, 0.5)
        distancia_promedio = st.number_input("Distancia promedio de viaje (km)", 0.0, 500.0, 40.0)
        pasajeros_auto = st.number_input("Promedio pasajeros por auto", 1.0, 5.0, 2.0)

    with col2:
        movilidad_bus = st.slider("Participantes que vienen en bus (%)", 0.0, 1.0, 0.2)
        movilidad_bici = st.slider("Participantes que vienen en bici (%)", 0.0, 1.0, 0.05)
        energia_kwh = st.number_input("Horas de uso de energía (kWh)", 0.0, 5000.0, 500.0)
        residuos_kg = st.number_input("Residuos estimados por persona (kg)", 0.0, 10.0, 0.4)
        materiales_medallas = st.number_input("Kg medallas (total)", 0.0, 100.0, 10.0)

    submitted = st.form_submit_button("Calcular impacto")

# ======================================================
# 🔹 FUNCIÓN DE CÁLCULO
# ======================================================
def calcular_huella(participantes, movilidad_auto, movilidad_bus, movilidad_bici,
                    distancia_promedio, pasajeros_auto, energia_kwh, residuos_kg, materiales_medallas):
    """Cálculo simplificado de huella ecológica total (en kg CO₂ eq)."""
    # Factores aproximados (kg CO₂ / km / persona)
    FE_AUTO = 0.180
    FE_BUS = 0.089
    FE_BICI = 0.0
    FE_ENERGIA = 0.475
    FE_RESIDUOS = 1.5
    FE_MATERIALES = 2.0

    transporte_auto = participantes * movilidad_auto * distancia_promedio * FE_AUTO / pasajeros_auto
    transporte_bus = participantes * movilidad_bus * distancia_promedio * FE_BUS
    transporte_bici = participantes * movilidad_bici * distancia_promedio * FE_BICI
    energia = energia_kwh * FE_ENERGIA
    residuos = participantes * residuos_kg * FE_RESIDUOS
    materiales = materiales_medallas * FE_MATERIALES

    total = transporte_auto + transporte_bus + transporte_bici + energia + residuos + materiales
    return {
        "transporte": transporte_auto + transporte_bus + transporte_bici,
        "energía": energia,
        "residuos": residuos,
        "materiales": materiales,
        "total": total
    }

# ======================================================
# 🔹 RESULTADOS Y VISUALIZACIÓN
# ======================================================
if submitted:
    resultados = calcular_huella(
        participantes, movilidad_auto, movilidad_bus, movilidad_bici,
        distancia_promedio, pasajeros_auto, energia_kwh, residuos_kg, materiales_medallas
    )

    st.success("✅ Cálculo completado correctamente.")

    total = resultados["total"]
    arboles = total / 21  # árboles equivalentes

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Huella total (kg CO₂ eq)", f"{total:,.2f}")
        st.metric("Equivalente árboles / año", f"{arboles:,.1f}")

    with col2:
        df = pd.DataFrame({
            "Categoría": ["Transporte", "Energía", "Residuos", "Materiales"],
            "Emisiones": [
                resultados["transporte"],
                resultados["energía"],
                resultados["residuos"],
                resultados["materiales"]
            ]
        })
        fig = px.bar(df, x="Categoría", y="Emisiones", color="Categoría", text_auto=True,
                     title="Distribución de emisiones por categoría (kg CO₂ eq)")
        st.plotly_chart(fig, use_container_width=True)

    # ======================================================
    # 🔹 GENERADOR DE PLAN VERDE (SIMULADO / IA)
    # ======================================================
    st.markdown("### 🌱 Plan Verde — Recomendaciones")
    if api_key:
        st.info("Sugerencia IA (demo): ofrecer shuttle desde ciudades cercanas, reducir plásticos de un solo uso, energía solar temporal, incentivar transporte compartido y separar residuos post-evento.")
    else:
        st.info("Sugerencia simulada: priorizar transporte compartido, energías limpias y reducción de residuos. (Modo demo sin API Key)")

# ======================================================
# 🔹 CHAT ASISTENTE
# ======================================================
st.markdown("---")
st.markdown("### 💬 Asistente / Chat")

consulta = st.text_input("Escribí una consulta (ej: ¿Cómo reduzco el transporte en un 20%?)")

if st.button("Preguntar al asistente"):
    if api_key:
        st.success("Respuesta IA (demo): promover carpooling, ajustar horarios de largada para compartir transporte y comunicar beneficios ambientales.")
    else:
        st.info("Sugerencia simulada: ofrecer transporte compartido o descuentos ecológicos (Modo demo sin IA).")

# ======================================================
# 🔹 PIE DE PÁGINA
# ======================================================
st.markdown("---")
st.caption("Desarrollado por Moira Machado · AI Green Planner — Proyecto LEKT | MOT 2025")

