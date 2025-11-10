# app.py — versión con chat lateral y botón al sitio de reciclaje
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------- CONFIGURACIÓN ----------
st.set_page_config(page_title="AI Green Planner | LEKT", page_icon="🌿", layout="wide")

st.title("🌿 AI Green Planner — LEKT | Correr con propósito")
st.caption("Prototipo funcional con cálculo de huella, plan verde y asistente inteligente.")

# ---------- CARGA API KEY ----------
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["general"]["OPENAI_API_KEY"]
    except Exception:
        api_key = None

# ---------- FUNCIONES ----------
def calcular_huella(participantes, movilidad_auto, movilidad_bus, movilidad_bici,
                    distancia_promedio, pasajeros_auto, energia_kwh, residuos_kg, materiales_medallas):
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

def generar_plan(resultados):
    total = resultados["total"]
    arboles = total / 21
    texto = f"""
    🌱 **Plan Verde Personalizado**
    - Huella total estimada: {total:,.2f} kg CO₂
    - Equivalente a {arboles:,.0f} árboles por año.

    **Acciones sugeridas:**
    1. Ofrecer transporte compartido o shuttles (reduce hasta 25 %).
    2. Usar energía solar temporal o LED (−15 % energía).
    3. Reutilizar medallas o materiales reciclados.
    4. Implementar puntos de reciclaje y compost.
    5. Comunicar los resultados ambientales post-evento.
    """
    return texto

def generar_respuesta_ia(pregunta):
    # Modo demo sin API
    lower = pregunta.lower()
    if "transporte" in lower:
        return "Podés organizar un sistema de carpooling o un bus gratuito para reducir la huella de CO₂ del traslado."
    elif "energía" in lower:
        return "Recomendación: usar generadores solares o iluminación LED. Reducen emisiones y consumo."
    elif "residuos" in lower:
        return "Separá residuos en tres categorías: reciclables, compost y desechos. Podés colocar carteles educativos."
    else:
        return "Podés contarme más sobre el tipo de evento o tus prioridades y te doy un plan más ajustado."

# ---------- FORMULARIO ----------
st.subheader("🧮 Calculá la huella de carbono del evento")
with st.form("form_evento"):
    nombre_evento = st.text_input("Nombre del evento", "LEKT Trail 2026")
    participantes = st.number_input("Participantes estimados", min_value=1, value=300)
    movilidad_auto = st.slider("Participantes que vienen en auto (%)", 0.0, 1.0, 0.5)
    movilidad_bus = st.slider("Participantes que vienen en bus (%)", 0.0, 1.0, 0.2)
    movilidad_bici = st.slider("Participantes que vienen en bici (%)", 0.0, 1.0, 0.05)
    distancia_promedio = st.number_input("Distancia promedio (km)", 0.0, 500.0, 40.0)
    pasajeros_auto = st.number_input("Promedio pasajeros por auto", 1.0, 5.0, 2.0)
    energia_kwh = st.number_input("Uso de energía (kWh)", 0.0, 10000.0, 500.0)
    residuos_kg = st.number_input("Residuos por persona (kg)", 0.0, 10.0, 0.4)
    materiales_medallas = st.number_input("Kg de medallas (total)", 0.0, 100.0, 10.0)
    calcular = st.form_submit_button("Calcular impacto")

# ---------- RESULTADOS ----------
if calcular:
    resultados = calcular_huella(participantes, movilidad_auto, movilidad_bus, movilidad_bici,
                                 distancia_promedio, pasajeros_auto, energia_kwh, residuos_kg, materiales_medallas)
    st.success("✅ Cálculo completado correctamente.")
    st.write(generar_plan(resultados))
    df = pd.DataFrame({
        "Categoría": ["Transporte", "Energía", "Residuos", "Materiales"],
        "Emisiones": [resultados["transporte"], resultados["energía"], resultados["residuos"], resultados["materiales"]]
    })
    fig = px.bar(df, x="Categoría", y="Emisiones", color="Categoría", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

# ---------- NUEVOS BOTONES ----------
col1, col2 = st.columns(2)
with col1:
    abrir_chat = st.button("💬 CHATEA AQUÍ")

with col2:
    abrir_reciclaje = st.button("♻️ CENTRO DE RECICLAJE")

# ---------- CHAT DESPLEGABLE ----------
if abrir_chat:
    with st.sidebar:
        st.header("🤖 Asistente Ambiental")
        st.write("Podés preguntarme cómo reducir emisiones o mejorar tu evento.")
        pregunta = st.text_input("Escribí tu consulta:")
        if st.button("Enviar"):
            if pregunta.strip() != "":
                respuesta = generar_respuesta_ia(pregunta)
                st.info(respuesta)

# ---------- REDIRECCIÓN AL SITIO DE RECICLAJE ----------
if abrir_reciclaje:
    js = "window.open('reciclaje', '_blank')"  # abre la página reciclaje.py
    st.markdown(f"<script>{js}</script>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Desarrollado por Moira Machado · AI Green Planner · Proyecto LEKT | MOT 2025")
