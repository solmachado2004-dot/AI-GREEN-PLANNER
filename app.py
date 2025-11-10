# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import os
from datetime import datetime
import textwrap
import openai
from dotenv import load_dotenv

# Load .env if exists (for OPENAI_API_KEY)
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_KEY:
    openai.api_key = OPENAI_KEY

# ---------- Styling ----------
st.set_page_config(page_title="AI Green Planner - LEKT", page_icon="🌿", layout="wide")

# Custom CSS for fonts/colors (Streamlit allows limited CSS)
st.markdown(
    """
    <style>
    /* Font & card style */
    .stApp {
        background: linear-gradient(180deg, #F7F6F2 0%, #F0F3EE 100%);
    }
    .card {
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 2px 8px rgba(30,40,30,0.08);
        background: white;
    }
    .big-title {
        font-size:34px;
        font-weight:700;
        color:#334e3b;
    }
    .subtitle {
        font-size:16px;
        color:#5d6b57;
    }
    .small-muted {
        color:#7b8278;
        font-size:12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Colors / theme
PRIMARY = "#3A5A40"    # verde musgo
ACCENT = "#A3B18A"     # celeste-lago / soft green
NEUTRAL = "#DAD7CD"    # beige
TEXT = "#334e3b"

# ---------- Helper functions ----------
EMISSION_FACTORS = {
    "car_gCO2_per_km": 180,   # gCO2 per km per car (ejemplo)
    "bus_gCO2_per_km": 80,
    "bike_gCO2_per_km": 0,
    "kwh_kgCO2": 0.4,         # kgCO2 per kWh
    "waste_kgCO2_per_kg": 0.2 # kgCO2 per kg of waste (ejemplo)
}

def emissions_transport(participants, pct_car, avg_km, passengers_per_car=2, pct_bus=0, pct_bike=0):
    # participants * pct_car => number of participants by car
    n_car = participants * pct_car
    cars = n_car / passengers_per_car if passengers_per_car>0 else n_car
    gco2_cars = cars * avg_km * EMISSION_FACTORS["car_gCO2_per_km"]
    gco2_bus = participants * pct_bus * avg_km * EMISSION_FACTORS["bus_gCO2_per_km"]
    # bike considered 0
    return (gco2_cars + gco2_bus) / 1000  # kgCO2

def emissions_energy(kwh):
    return kwh * EMISSION_FACTORS["kwh_kgCO2"]

def emissions_materials(materials_list):
    # materials_list: list of tuples (kg, type_factor) => type_factor multiplier
    total = 0
    for kg, factor in materials_list:
        total += kg * factor
    return total

def emissions_waste(participants, waste_kg_per_person):
    total_kg = participants * waste_kg_per_person
    return total_kg * EMISSION_FACTORS["waste_kgCO2_per_kg"]

def human_readable_kg(kg):
    return f"{kg:,.0f} kgCO₂"

def estimate_tree_equivalent(kg_co2):
    # simple rule: 1 tree sequesters ~21 kg CO2/year (very approximate)
    return round(kg_co2 / 21, 1)

# ---------- LLM generator (optional) ----------
def generate_plan_with_openai(inputs: dict) -> str:
    """
    Uses OpenAI to create a 6-point plan. Requires OPENAI_API_KEY in env.
    If no key present, raise ValueError.
    """
    if not OPENAI_KEY:
        raise ValueError("OPENAI_API_KEY not set. Install into .env or set environment variable.")

    prompt = f"""
    You are an expert assistant that writes short, practical "Green Plan" recommendations
    for sporting events. Given the event data below, produce 6 prioritized recommendations,
    each with one-line impact estimate (approx % reduction) and a short note about difficulty/cost.

    Event data:
    {inputs}

    Output format:
    1) Recommendation - Impact: X% - Difficulty: low/med/high - Note: ...
    ... up to 6 recommendations.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini", # if not available, change to gpt-4o or gpt-4
        messages=[{"role":"user","content":prompt}],
        max_tokens=450,
        temperature=0.3
    )
    text = response["choices"][0]["message"]["content"]
    return text

# ---------- PDF Export ----------
class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.set_text_color(51,78,59)
        self.cell(0, 8, "AI Green Planner - Plan Verde", ln=True, align="L")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(120,120,120)
        self.cell(0, 10, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 0, "C")

def create_pdf_report(event_info: dict, total_kg: float, breakdown: dict, plan_text: str, filename="plan_verde.pdf"):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.set_text_color(51,78,59)
    pdf.cell(0, 8, event_info.get("name","Evento sin nombre"), ln=True)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(60,60,60)
    pdf.multi_cell(0, 6, f"Fecha: {event_info.get('date','-')}  |  Lugar: {event_info.get('location','-')}")
    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 7, f"Huella estimada: {human_readable_kg(total_kg)}", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.ln(2)
    pdf.cell(0, 6, "Desglose (kgCO₂):", ln=True)
    for k,v in breakdown.items():
        pdf.cell(0,6, f"- {k}: {v:,.1f} kgCO₂", ln=True)
    pdf.ln(6)
    pdf.set_font("Arial","B",11)
    pdf.cell(0,7,"Plan Verde sugerido:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0,6, plan_text)
    pdf.output(filename)
    return filename

# ---------- Layout ----------
st.markdown('<div class="big-title">AI Green Planner — Planificación sostenible</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">LEKT | Correr con propósito — prototipo funcional</div>', unsafe_allow_html=True)
st.write("")

# Two-column layout
with st.container():
    col1, col2 = st.columns([1,1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Datos del evento")
        with st.form("form_event"):
            event_name = st.text_input("Nombre del evento", "LEKT Trail 2026")
            event_date = st.date_input("Fecha", datetime.now())
            event_location = st.text_input("Lugar (ciudad o coordenadas)", "Lago Lolog, Neuquén")
            participants = st.number_input("Participantes estimados", min_value=1, value=300)
            st.write("Movilidad (ingresá porcentajes como 0.0 - 1.0)")
            pct_car = st.slider("Participantes que vienen en auto (%)", 0.0, 1.0, 0.5, step=0.05)
            avg_distance_km = st.number_input("Distancia promedio de viaje (km)", value=40)
            avg_passengers_per_car = st.number_input("Promedio pasajeros por auto", min_value=1.0, value=2.0, step=0.5)
            pct_bus = st.slider("Participantes que vienen en bus (%)", 0.0, 1.0, 0.2, step=0.05)
            pct_bike = st.slider("Participantes que vienen en bici (%)", 0.0, 1.0, 0.05, step=0.05)

            energy_kwh = st.number_input("Horas uso de energía (kWh)", min_value=0.0, value=500.0)
            waste_kg_per_person = st.number_input("Residuos estimados por persona (kg)", min_value=0.0, value=0.5)
            st.markdown("**Materiales** (ej: remeras, medallas) — indicá aproximado en kg")
            mat_shirts_kg = st.number_input("Kg remeras (total)", min_value=0.0, value=40.0)
            mat_medals_kg = st.number_input("Kg medallas (total)", min_value=0.0, value=10.0)
            submit = st.form_submit_button("Calcular impacto")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card" style="margin-top:16px">', unsafe_allow_html=True)
        st.subheader("Asistente / Chat (demo)")
        st.write("Escribí una consulta rápida y el asistente intentará responder (si configuraste OPENAI_API_KEY, usará la API; si no, respuesta simulada).")
        user_q = st.text_input("Consulta (ej: ¿Cómo reduzco el transporte en un 20%?)")
        if st.button("Preguntar al asistente"):
            if OPENAI_KEY:
                # simple completion
                try:
                    reply = openai.ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[{"role":"user","content":user_q}],
                        max_tokens=200,
                        temperature=0.3
                    )
                    assistant_text = reply["choices"][0]["message"]["content"]
                except Exception as e:
                    assistant_text = f"Error llamando a la API: {e}"
            else:
                # fallback simulated reply
                assistant_text = (
                    "Sugerencia: Ofrecer shuttle desde ciudades cercanas. "
                    "Comunicar incentivo (descuento en inscripción) para quienes usen transporte compartido. "
                    "Punto inmediato: contactar empresas de transporte local para 1-2 cotizaciones."
                )
            st.info(assistant_text)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Resultados y Plan Verde")
        if submit:
            # Calculations
            e_transport = emissions_transport(participants, pct_car, avg_distance_km, avg_passengers_per_car, pct_bus, pct_bike)
            e_energy = emissions_energy(energy_kwh)
            materials_list = [
                (mat_shirts_kg, 5.0),   # factor example: kgCO2 per kg (fabric)
                (mat_medals_kg, 15.0)
            ]
            e_materials = emissions_materials(materials_list)
            e_waste = emissions_waste(participants, waste_kg_per_person)
            total = e_transport + e_energy + e_materials + e_waste

            breakdown = {
                "Transporte": e_transport,
                "Energía": e_energy,
                "Materiales": e_materials,
                "Residuos": e_waste
            }

            st.metric("Huella estimada (kg CO₂)", f"{total:,.0f}")
            trees = estimate_tree_equivalent(total)
            st.write(f"Equivalente aproximado a árboles plantados (anual): {trees}")

            # Plot
            fig = go.Figure(go.Bar(
                x=list(breakdown.keys()),
                y=[v for v in breakdown.values()],
                text=[f"{v:,.0f}" for v in breakdown.values()],
                textposition='auto'
            ))
            fig.update_layout(title="Desglose de emisiones por fuente", plot_bgcolor="white",
                              title_font_color=TEXT)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.markdown("### Plan Verde (sugerido)")
            # Try LLM if key available
            inputs_for_llm = {
                "name": event_name,
                "date": str(event_date),
                "location": event_location,
                "participants": participants,
                "pct_car": pct_car,
                "avg_distance_km": avg_distance_km,
                "pct_bus": pct_bus,
                "energy_kwh": energy_kwh,
                "materials": {"shirts_kg": mat_shirts_kg, "medals_kg": mat_medals_kg},
                "waste_kg_per_person": waste_kg_per_person
            }
            try:
                if OPENAI_KEY:
                    plan_text = generate_plan_with_openai(inputs_for_llm)
                else:
                    # fallback: deterministic template recommendations
                    plan_text = textwrap.dedent(f"""
                    1) Implementar shuttle desde ciudades principales - Impacto: ~20% - Dificultad: media.
                    2) Ofrecer incentivos para uso de transporte compartido (descuento o prioridad de inscripción) - Impacto: ~8% - Dificultad: baja.
                    3) Reemplazar remeras por algodón orgánico o remeras recicladas - Impacto: ~6% - Dificultad: media.
                    4) Puntos de hidratación reutilizables (vasos/recipientes) para reducir residuos - Impacto: ~5% - Dificultad: baja.
                    5) Estación de reciclaje y señalética clara en llegada/meta - Impacto: ~4% - Dificultad: baja.
                    6) Comunicar la huella y compromiso (infografía) para atraer sponsors verdes - Impacto: indirecto - Dificultad: baja.
                    """).strip()
            except Exception as e:
                plan_text = f"Error generando plan automático: {e}"

            st.text_area("Plan Verde generado", value=plan_text, height=260)

            # Download PDF
            if st.button("Descargar Plan Verde (PDF)"):
                event_info = {"name": event_name, "date": str(event_date), "location": event_location}
                filename = f"plan_verde_{event_name.replace(' ','_')}.pdf"
                create_pdf_report(event_info, total, breakdown, plan_text, filename=filename)
                with open(filename, "rb") as f:
                    st.download_button("Descargar PDF", data=f, file_name=filename, mime="application/pdf")

        else:
            st.info("Completá el formulario a la izquierda y hacé click en 'Calcular impacto' para ver resultados.")
        st.markdown('</div>', unsafe_allow_html=True)

# Footer / gallery
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown('<div style="display:flex; gap:20px;">', unsafe_allow_html=True)
st.image("https://images.unsplash.com/photo-1508609349937-5ec4ae374ebf?auto=format&fit=crop&w=800&q=60", caption="Correr con propósito", width=240)
st.image("https://images.unsplash.com/photo-1526481280692-94a65f0f9b3d?auto=format&fit=crop&w=800&q=60", caption="Paisaje patagónico", width=240)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="small-muted">Prototipo construido para entrega académica. Valores de emisiones y factores son de ejemplo. Ver sección de anexos para fuentes y supuestos.</div>', unsafe_allow_html=True)
