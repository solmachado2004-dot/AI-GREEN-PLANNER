# app.py
# AI Green Planner + Chatbot conversacional integrado
# Autor: Moira Machado (adaptado por Besti)
# 2025

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import textwrap
from datetime import datetime

# Try import OpenAI; if not installed the app will still run (modo demo)
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

# ---------- Page config & style ----------
st.set_page_config(page_title="AI Green Planner — Chatbot", page_icon="🌿", layout="wide")

st.markdown("""
    <style>
    body { background-color: #F7F6F2; font-family: 'Poppins', sans-serif; }
    .stButton>button { background-color: #3A5A40; color: white; border-radius: 8px; }
    .stButton>button:hover { background-color: #2F4A36; }
    .message-user { background:#DFF2E1; padding:8px 12px; border-radius:12px; margin-bottom:6px; }
    .message-bot { background:#E8F4FF; padding:8px 12px; border-radius:12px; margin-bottom:6px; }
    </style>
""", unsafe_allow_html=True)

st.title("🌿 AI Green Planner — Chatbot conversacional")
st.caption("Calculá la huella y hablá con un asistente que te propone un plan de acción concreto.")

# ---------- Load API key from env or Streamlit secrets (TOML) ----------
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["general"]["OPENAI_API_KEY"]
    except Exception:
        api_key = None

# If OpenAI python package is available and key present, configure it
if OPENAI_AVAILABLE and api_key:
    openai.api_key = api_key

# ---------- Session state for chat ----------
if "chat_messages" not in st.session_state:
    # store messages as list of dicts: {"role": "system/user/assistant", "content": "...", "time": ...}
    st.session_state.chat_messages = []

if "last_plan_inputs" not in st.session_state:
    st.session_state.last_plan_inputs = None

# ---------- Helper functions ----------
def calcular_huella(participantes, movilidad_auto, movilidad_bus, movilidad_bici,
                    distancia_promedio, pasajeros_auto, energia_kwh, residuos_kg, materiales_medallas):
    FE_AUTO = 0.180
    FE_BUS = 0.089
    FE_BICI = 0.0
    FE_ENERGIA = 0.475
    FE_RESIDUOS = 1.5
    FE_MATERIALES = 2.0

    transporte_auto = participantes * movilidad_auto * distancia_promedio * FE_AUTO / max(pasajeros_auto,1)
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

def format_plan_from_template(inputs, results):
    # deterministic plan text (fallback/demo)
    total = results["total"]
    plan = textwrap.dedent(f"""
    1) Shuttle desde ciudades cercanas — Impacto estimado: ~{min(30, int(30 + (inputs['pct_car']-0.4)*50))}% si se implementa correctamente.
       Nota: negociar 1-2 cotizaciones y ofrecer incentivos.

    2) Incentivos para carpooling — Impacto estimado: ~10%.
       Nota: descuento en inscripción o prioridad en largada para quienes viajen compartiendo.

    3) Puntos de hidratación reutilizables — Impacto estimado: ~5-8%.
       Nota: reducir vasos/vasijas desechables y ofrecer botellas reutilizables.

    4) Reemplazo de remeras por material reciclado/algodón orgánico — Impacto estimado: ~5-8%.
       Nota: cotizar con dos proveedores locales.

    5) Estaciones de reciclaje y compostaje — Impacto estimado: ~3-6%.
       Nota: señalética clara y voluntariado para acompañamiento.

    6) Comunicación transparente del impacto — Impacto indirecto.
       Nota: generar infografías para sponsors y redes, mostrar objetivos y resultados.
    """)
    return plan.strip()

def generate_plan_openai(inputs, results):
    """Usa la API de OpenAI para generar un plan conversacional. Devuelve texto."""
    if not (OPENAI_AVAILABLE and api_key):
        return format_plan_from_template(inputs, results)

    # Construir prompt/consulta para modelo conversacional
    system_prompt = (
        "Eres AI Green Planner, asistente experto en eventos deportivos sostenibles. "
        "Generá un Plan Verde con 6 acciones priorizadas, cada una con impacto estimado (porcentaje) "
        "y una breve nota sobre implementación y costos aproximados. Sé conciso y práctico."
    )

    user_prompt = f"Inputs del evento:\n{inputs}\nResultados de emisiones (kg CO2):\n{results}\nGenerá el plan."

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system", "content": system_prompt},
                {"role":"user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.25
        )
        text = resp["choices"][0]["message"]["content"].strip()
        return text
    except Exception as e:
        # fallback
        return format_plan_from_template(inputs, results) + f"\n\n(Nota: OpenAI API error: {e})"

def openai_chat_reply(user_message):
    """Responde usando OpenAI (con historial)."""
    if not (OPENAI_AVAILABLE and api_key):
        # modo demo: respuestas simples basadas en keywords
        lower = user_message.lower()
        if "transporte" in lower or "shuttle" in lower or "auto" in lower:
            return "Sugerencia práctica: ofrecer 2 shuttles desde las ciudades más pobladas y un formulario para coordinar carpooling. Incentivo: 10% de descuento o kit ecológico."
        if "remeras" in lower or "camiseta" in lower:
            return "Podés cotizar remeras recicladas con 2 proveedores locales: pedí muestras y calcula coste por unidad. Considerá reducir cantidad promocional."
        if "residuos" in lower or "basura" in lower:
            return "Implementá 3 estaciones de reciclaje y compostaje (meta: 80% de residuos correctamente separados). Usa señalética clara y voluntariado formador."
        if "costo" in lower or "presupuesto" in lower:
            return "Prioriza medidas de alto impacto/bajo costo (carpooling, señalética, puntos de hidratación reutilables). Posteriormente negocia proveedores para remeras recicladas."
        # default:
        return "¡Buena pregunta! Podés darme más detalles (presupuesto, prioridad rápida o compromiso a largo plazo) y te doy un plan concreto."
    # If OpenAI available, call chat completion including conversation history
    messages = []
    # system message
    messages.append({"role":"system", "content":"Eres AI Green Planner, asistente útil, conciso y empático. Responde con acciones prácticas y claras para reducir la huella de eventos deportivos."})
    # include history from session_state
    for m in st.session_state.chat_messages:
        # map our roles to openai roles
        if m["role"] == "assistant":
            messages.append({"role":"assistant", "content": m["content"]})
        elif m["role"] == "user":
            messages.append({"role":"user", "content": m["content"]})
    # add user's current message
    messages.append({"role":"user", "content": user_message})

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=400,
            temperature=0.3
        )
        reply = resp["choices"][0]["message"]["content"].strip()
        return reply
    except Exception as e:
        return f"(Error al conectar con OpenAI: {e})"

# ---------- Layout: Left = form, Right = chat & results ----------
left_col, right_col = st.columns([1.1, 1])

with left_col:
    st.subheader("📝 Datos del evento")
    with st.form("form_event2"):
        nombre_evento = st.text_input("Nombre del evento", value="LEKT Trail 2026")
        fecha_evento = st.date_input("Fecha del evento", value=datetime.now())
        lugar = st.text_input("Lugar", value="Lago Lolog, Neuquén")
        participantes = st.number_input("Participantes estimados", min_value=1, value=300, step=10)
        movilidad_auto = st.slider("Participantes en auto (%)", 0.0, 1.0, 0.5)
        distancia_promedio = st.number_input("Distancia promedio (km)", value=40.0, step=1.0)
        pasajeros_auto = st.number_input("Promedio pasajeros por auto", min_value=1.0, value=2.0, step=0.5)
        movilidad_bus = st.slider("Participantes en bus (%)", 0.0, 1.0, 0.2)
        movilidad_bici = st.slider("Participantes en bici (%)", 0.0, 1.0, 0.05)
        energia_kwh = st.number_input("Horas uso de energía (kWh)", value=500.0)
        residuos_kg = st.number_input("Residuos estimados por persona (kg)", value=0.4)
        materiales_medallas = st.number_input("Kg medallas (total)", value=10.0)
        calcular_btn = st.form_submit_button("Calcular impacto y generar plan")

with right_col:
    st.subheader("💬 Chatbot conversacional")
    # Display conversation messages
    chat_box = st.empty()
    def render_chat():
        with chat_box.container():
            st.markdown("**Conversación:**")
            for m in st.session_state.chat_messages:
                if m["role"] == "user":
                    st.markdown(f"<div class='message-user'><b>Tú:</b> {m['content']}</div>", unsafe_allow_html=True)
                elif m["role"] == "assistant":
                    st.markdown(f"<div class='message-bot'><b>AI:</b> {m['content']}</div>", unsafe_allow_html=True)
    render_chat()

    # Input for user messages
    user_input = st.text_input("Escribí tu mensaje aquí y presioná Enter (o usá el botón):", key="user_msg_input")
    send = st.button("Enviar mensaje")

# ---------- Actions on calcular_btn ----------
if calcular_btn:
    results = calcular_huella(
        participantes, movilidad_auto, movilidad_bus, movilidad_bici,
        distancia_promedio, pasajeros_auto, energia_kwh, residuos_kg, materiales_medallas
    )
    st.session_state.last_plan_inputs = {
        "name": nombre_evento,
        "date": str(fecha_evento),
        "location": lugar,
        "participants": participantes,
        "pct_car": round(movilidad_auto,2),
        "avg_distance_km": distancia_promedio,
        "pct_bus": round(movilidad_bus,2),
        "energy_kwh": energia_kwh,
        "materials": {"medals_kg": materiales_medallas},
        "waste_kg_per_person": residuos_kg
    }

    # display quick summary under left column (we're in same run)
    with left_col:
        st.success("✅ Cálculo completado")
        st.metric("Huella total (kg CO₂ eq)", f"{results['total']:,.2f}")
        df_vis = pd.DataFrame({
            "Categoría": ["Transporte", "Energía", "Residuos", "Materiales"],
            "Emisiones": [results["transporte"], results["energía"], results["residuos"], results["materiales"]]
        })
        fig = px.pie(df_vis, names="Categoría", values="Emisiones", title="Desglose de emisiones")
        st.plotly_chart(fig, use_container_width=True)

    # generate initial plan using OpenAI or template
    plan_text = generate_plan_openai(st.session_state.last_plan_inputs, results)

    # Add initial messages to chat (assistant)
    # Clear previous chat? We'll append; if you want to reset, user can press a Clear button (not included)
    intro_user_msg = f"Calculé la huella para {nombre_evento} con {participantes} participantes. Generá un plan de acción."
    # append user message and assistant reply to session_state
    st.session_state.chat_messages.append({"role":"user", "content": intro_user_msg, "time": str(datetime.now())})
    st.session_state.chat_messages.append({"role":"assistant", "content": plan_text, "time": str(datetime.now())})

    # re-render chat
    render_chat()

# ---------- Actions on send (user message) ----------
if send and st.session_state.get("user_msg_input", "").strip() != "":
    message = st.session_state.user_msg_input.strip()
    # append user message to history
    st.session_state.chat_messages.append({"role":"user", "content": message, "time": str(datetime.now())})
    render_chat()

    # get assistant reply
    reply = openai_chat_reply(message)
    st.session_state.chat_messages.append({"role":"assistant", "content": reply, "time": str(datetime.now())})

    # clear input box
    st.session_state.user_msg_input = ""
    # re-render chat with new message
    render_chat()

# ---------- Optional: Button to clear chat ----------
st.sidebar.markdown("### Opciones")
if st.sidebar.button("🔄 Reiniciar conversación"):
    st.session_state.chat_messages = []
    st.session_state.last_plan_inputs = None
    st.experimental_rerun()

# ---------- Footer ----------
st.markdown("---")
st.caption("Prototipo AI Green Planner · Chatbot integrado · Modo demo si no hay OpenAI Key.")
