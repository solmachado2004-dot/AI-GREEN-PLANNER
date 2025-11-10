# app.py — AI Green Planner con chat estilo WhatsApp y centro de reciclaje funcional
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------- CONFIGURACIÓN ----------
st.set_page_config(page_title="AI Green Planner | LEKT", page_icon="🌿", layout="wide")

st.title("🌿 AI Green Planner — LEKT | Correr con propósito")
st.caption("Calculá la huella, obtené tu plan verde y conversá con el asistente ambiental.")

# ---------- API KEY ----------
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["general"]["OPENAI_API_KEY"]
    except Exception:
        api_key = None

# ---------- FUNCIÓN DE CÁLCULO ----------
def calcular_huella(participantes, movilidad_auto, movilidad_bus, movilidad_bici,
                    distancia_promedio, pasajeros_auto, energia_kwh, residuos_kg, materiales_medallas):
    FE_AUTO = 0.180
    FE_BUS = 0.089
    FE_ENERGIA = 0.475
    FE_RESIDUOS = 1.5
    FE_MATERIALES = 2.0

    transporte_auto = participantes * movilidad_auto * distancia_promedio * FE_AUTO / pasajeros_auto
    transporte_bus = participantes * movilidad_bus * distancia_promedio * FE_BUS
    energia = energia_kwh * FE_ENERGIA
    residuos = participantes * residuos_kg * FE_RESIDUOS
    materiales = materiales_medallas * FE_MATERIALES
    total = transporte_auto + transporte_bus + energia + residuos + materiales
    return {
        "transporte": transporte_auto + transporte_bus,
        "energía": energia,
        "residuos": residuos,
        "materiales": materiales,
        "total": total
    }

# ---------- RESPUESTAS DEMO ----------
def respuesta_demo(msg):
    m = msg.lower()
    if "transporte" in m:
        return "Podés organizar shuttles o promover carpooling entre participantes 🚐♻️"
    elif "energía" in m:
        return "Usá iluminación LED y paneles solares portátiles ☀️"
    elif "residuos" in m or "basura" in m:
        return "Implementá puntos verdes con separación de residuos 🗑️🌿"
    elif "agua" in m:
        return "Instalá dispensadores de agua y evitá botellas plásticas 💧"
    else:
        return "Buena pregunta 🌱. Contame más sobre lo que querés mejorar y te doy una sugerencia puntual."

# ---------- SESIÓN DE CHAT ----------
if "mensajes_chat" not in st.session_state:
    st.session_state.mensajes_chat = []  # lista de mensajes [{"emisor":"user"/"bot", "texto":"..." }]

# ---------- INTERFAZ PRINCIPAL ----------
col1, col2 = st.columns([2, 1])

# ----------- COLUMNA IZQUIERDA: FORMULARIO Y RESULTADOS -----------
with col1:
    st.subheader("🧮 Calculá la huella de carbono")
    with st.form("form_evento"):
        participantes = st.number_input("Participantes", 1, 10000, 300)
        movilidad_auto = st.slider("En auto (%)", 0.0, 1.0, 0.5)
        movilidad_bus = st.slider("En bus (%)", 0.0, 1.0, 0.2)
        movilidad_bici = st.slider("En bici (%)", 0.0, 1.0, 0.05)
        distancia_promedio = st.number_input("Distancia promedio (km)", 0.0, 500.0, 40.0)
        pasajeros_auto = st.number_input("Pasajeros por auto", 1.0, 5.0, 2.0)
        energia_kwh = st.number_input("Energía (kWh)", 0.0, 10000.0, 500.0)
        residuos_kg = st.number_input("Residuos (kg/persona)", 0.0, 10.0, 0.4)
        materiales_medallas = st.number_input("Medallas (kg total)", 0.0, 100.0, 10.0)
        calcular = st.form_submit_button("Calcular impacto")

    if calcular:
        resultados = calcular_huella(participantes, movilidad_auto, movilidad_bus, movilidad_bici,
                                     distancia_promedio, pasajeros_auto, energia_kwh, residuos_kg, materiales_medallas)
        st.success("✅ Cálculo completado")
        st.metric("Huella total (kg CO₂ eq)", f"{resultados['total']:,.2f}")
        df = pd.DataFrame({
            "Categoría": ["Transporte", "Energía", "Residuos", "Materiales"],
            "Emisiones": [resultados["transporte"], resultados["energía"], resultados["residuos"], resultados["materiales"]]
        })
        fig = px.bar(df, x="Categoría", y="Emisiones", color="Categoría", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
        st.info("🌱 Consejo: Reducí emisiones con transporte compartido y materiales reciclados.")

# ----------- COLUMNA DERECHA: CHAT ESTILO WHATSAPP -----------
with col2:
    st.subheader("💬 Chat Ambiental (tipo WhatsApp)")
    st.markdown("""
        <style>
        .chat-bubble-user {
            background-color: #DCF8C6;
            border-radius: 10px;
            padding: 8px 12px;
            margin-bottom: 5px;
            text-align: right;
        }
        .chat-bubble-bot {
            background-color: #E8F0FE;
            border-radius: 10px;
            padding: 8px 12px;
            margin-bottom: 5px;
            text-align: left;
        }
        </style>
    """, unsafe_allow_html=True)

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.mensajes_chat:
            if msg["emisor"] == "user":
                st.markdown(f"<div class='chat-bubble-user'>{msg['texto']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-bot'>{msg['texto']}</div>", unsafe_allow_html=True)

    with st.form("form_chat", clear_on_submit=True):
        user_msg = st.text_input("Escribí tu mensaje:")
        enviar = st.form_submit_button("Enviar")

    if enviar and user_msg:
        st.session_state.mensajes_chat.append({"emisor": "user", "texto": user_msg})
        respuesta = respuesta_demo(user_msg)
        st.session_state.mensajes_chat.append({"emisor": "bot", "texto": respuesta})
        st.experimental_rerun()

    st.markdown("---")
    st.write("Tus conversaciones se mantienen activas mientras la app esté abierta 🔒")

# ----------- BOTÓN DE RECICLAJE -----------
st.markdown("---")
if st.button("♻️ Abrir Centro de Reciclaje"):
    js = "window.open('reciclaje', '_blank')"
    st.markdown(f"<script>{js}</script>", unsafe_allow_html=True)

st.caption("Desarrollado por Moira Machado · Proyecto LEKT | MOT 2025")
