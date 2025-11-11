# app.py — AI Green Planner con árboles equivalentes, consejos personalizados y reciclaje dinámico
import streamlit as st
import pandas as pd
import plotly.express as px
import random
import os
from openai import OpenAI

# --------------------------------------------------------
# 🧩 CONFIGURACIÓN INICIAL
# --------------------------------------------------------
st.set_page_config(page_title="AI Green Planner | LEKT", page_icon="🌿", layout="wide")

st.title("🌿 AI Green Planner — LEKT | Correr con propósito")
st.caption("Calculá la huella, conocé tu impacto en árboles equivalentes y conversá con el asistente ambiental inteligente.")

# --------------------------------------------------------
# 🧠 CONFIGURACIÓN OPENAI
# --------------------------------------------------------
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["general"]["OPENAI_API_KEY"]
    except Exception:
        api_key = None

client = OpenAI(api_key=api_key) if api_key else None

# --------------------------------------------------------
# 🔢 FUNCIÓN DE CÁLCULO
# --------------------------------------------------------
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
        "total": total,
        "arboles_eq": total / 21  # 1 árbol absorbe 21 kg CO₂/año
    }

# --------------------------------------------------------
# 🌱 CONSEJOS PERSONALIZADOS
# --------------------------------------------------------
def generar_consejo_personalizado(resultados):
    mayor_categoria = max(resultados, key=resultados.get)
    opciones = {
        "transporte": [
            "Implementá buses compartidos o carpooling entre los corredores 🚐",
            "Premiá con descuentos a quienes lleguen en bicicleta o transporte público 🚲",
            "Establecé puntos de partida desde ciudades cercanas para compartir movilidad 🌍"
        ],
        "energía": [
            "Usá iluminación LED y generadores solares portátiles ☀️",
            "Reducí el consumo eléctrico estableciendo zonas sin energía permanente ⚡",
            "Optimizá los horarios del evento para aprovechar la luz natural 🌤️"
        ],
        "residuos": [
            "Instalá puntos verdes con separación en origen ♻️",
            "Compostá los residuos orgánicos post-evento 🌿",
            "Eliminá plásticos de un solo uso y reemplazalos por materiales biodegradables 🌱"
        ],
        "materiales": [
            "Reutilizá medallas o trofeos fabricados con materiales reciclados 🥇",
            "Usá merchandising sustentable: remeras ecológicas, bolsas compostables 👕",
            "Reducí impresiones y priorizá comunicación digital 📱"
        ]
    }
    return random.choice(opciones.get(mayor_categoria, ["Continuá trabajando en tu plan verde 🌎"]))

# --------------------------------------------------------
# 🤖 CHATBOT
# --------------------------------------------------------
def obtener_respuesta_ia(mensaje):
    """Usa OpenAI GPT si hay API Key, o modo demo si no."""
    if client:
        try:
            respuesta = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Sos un asistente ambiental experto en sostenibilidad para eventos deportivos. Respondé de forma cálida, concreta y con consejos útiles."},
                    {"role": "user", "content": mensaje}
                ],
                max_tokens=200
            )
            return respuesta.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ Error al conectar con OpenAI: {e}"
    else:
        mensaje = mensaje.lower()
        if "transporte" in mensaje:
            return "Podés organizar shuttles o promover carpooling 🚐♻️"
        elif "energía" in mensaje:
            return "Usá iluminación LED y paneles solares portátiles ☀️"
        elif "residuos" in mensaje or "basura" in mensaje:
            return "Implementá puntos verdes con separación de residuos 🗑️🌿"
        elif "agua" in mensaje:
            return "Instalá dispensadores de agua y evitá botellas plásticas 💧"
        else:
            return "Buena pregunta 🌱. Contame más sobre lo que querés mejorar y te doy una sugerencia puntual."

# --------------------------------------------------------
# 🧠 SESIÓN DE ESTADO
# --------------------------------------------------------
if "mensajes_chat" not in st.session_state:
    st.session_state.mensajes_chat = []
if "resultados" not in st.session_state:
    st.session_state.resultados = None

# --------------------------------------------------------
# 🧾 INTERFAZ PRINCIPAL
# --------------------------------------------------------
col1, col2 = st.columns([2, 1])

# ----------- COLUMNA IZQUIERDA: CÁLCULO Y RESULTADOS -----------
with col1:
    st.subheader(" Calculá la huella de carbono")
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
        st.session_state.resultados = calcular_huella(participantes, movilidad_auto, movilidad_bus, movilidad_bici,
                                                      distancia_promedio, pasajeros_auto, energia_kwh, residuos_kg, materiales_medallas)

    if st.session_state.resultados:
        r = st.session_state.resultados
        st.success("✅ Cálculo completado correctamente")
        st.metric("Huella total (kg CO₂ eq)", f"{r['total']:,.2f}")
        st.metric("Equivalente en árboles", f"{r['arboles_eq']:.1f} 🌳")

        df = pd.DataFrame({
            "Categoría": ["Transporte", "Energía", "Residuos", "Materiales"],
            "Emisiones": [r["transporte"], r["energía"], r["residuos"], r["materiales"]]
        })
        fig = px.bar(df, x="Categoría", y="Emisiones", color="Categoría", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

        consejo = generar_consejo_personalizado(r)
        st.info(f"🌱 Consejo personalizado: {consejo}")

        st.divider()
        # --------------------------------------------------------
        # 🪴 SECCIÓN DE RECICLAJE (ADAPTATIVA)
        # --------------------------------------------------------
        st.header("♻️ Centro de Reciclaje y Reutilización")
        arboles = r['arboles_eq']
        if participantes < 200:
            tipo_evento = "pequeño"
        elif participantes < 600:
            tipo_evento = "mediano"
        else:
            tipo_evento = "grande"

        st.markdown(f"""
        ### 🌍 Análisis del evento
        - Tipo de evento: **{tipo_evento.capitalize()}**
        - Huella total: **{r['total']:.2f} kg CO₂ eq**
        - Equivalente a la absorción anual de **{arboles:.1f} árboles.**

        ### 🌿 Plan de acción propuesto
        - **1. Recuperación de residuos:** instalá contenedores diferenciados en meta, puestos y zonas de descanso.
        - **2. Educación ambiental:** capacitá a voluntarios como “eco-guías” para ayudar a separar correctamente.
        - **3. Reutilización creativa:** 
          - Fundí medallas para crear nuevos diseños o llaveros.
          - Transformá banderas o carteles en bolsos deportivos.
          - Convocá artistas locales para intervenir materiales reciclados.
        - **4. Compost y donación:** los restos orgánicos pueden convertirse en compost para viveros o escuelas.
        - **5. Comunicación:** compartí los datos del impacto y las acciones compensatorias en tus redes.

        ### 💡 Sugerencias específicas
        - Eventos **pequeños:** buscá alianzas con escuelas y cooperativas locales.
        - Eventos **medianos:** desarrollá un “punto verde móvil” con juegos educativos.
        - Eventos **grandes:** contratá una empresa de gestión ambiental y medí el impacto compensado.

        ### 🌲 Plan compensatorio
        - Por cada **21 kg CO₂** equivalentes, se recomienda **plantar un árbol nativo.**
        - En este caso, se sugiere plantar **{round(arboles)} árboles** para compensar la huella total.
        """)

# ----------- COLUMNA DERECHA: CHAT ----------- 
with col2:
    st.subheader("Chat Ambiental ")
    st.markdown("""
        <style>
        .chat-bubble-user {
            background-color: #008000 ;
            border-radius: 10px;
            padding: 8px 12px;
            margin-bottom: 5px;
            text-align: right;
        }
        .chat-bubble-bot {
            background-color: #228B22 ;
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

    user_msg = st.text_input("Escribí tu mensaje:", key="chat_input")
    if st.button("Enviar mensaje"):
        if user_msg.strip():
            st.session_state.mensajes_chat.append({"emisor": "user", "texto": user_msg})
            respuesta = obtener_respuesta_ia(user_msg)
            st.session_state.mensajes_chat.append({"emisor": "bot", "texto": respuesta})
            st.rerun()

    st.markdown("---")
    if api_key:
        st.success("IA activada ✅ (usando GPT-4o-mini)")
    else:
        st.warning("Modo demo sin conexión a OpenAI")

st.caption("Desarrollado por Moira Machado · Proyecto LEKT | MOT 2025")


