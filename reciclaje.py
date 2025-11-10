# reciclaje.py — mini sitio de reciclaje y reutilización
import streamlit as st

st.set_page_config(page_title="Centro de Reciclaje | AI Green Planner", page_icon="♻️", layout="wide")

st.title("♻️ Centro de Reciclaje y Reutilización — AI Green Planner")
st.caption("Ideas para transformar residuos del evento en recursos útiles y sostenibles.")

st.markdown("""
### 🌱 Reutilización de materiales
- **Medallas recicladas:** fundir o reacondicionar para ediciones futuras.  
- **Remeras viejas:** convertir en bolsos o pañuelos para runners.  
- **Cartelería de lona:** reutilizar como cobertores o bolsas de entrenamiento.  
- **Botellas PET:** transformarlas en señalética o recipientes para plantines.  

### 🗑️ Separación inteligente
- Implementá **puntos verdes** con tres secciones:  
  - ♻️ Reciclables (plástico, papel, aluminio)  
  - 🌿 Compostables (restos orgánicos)  
  - 🚯 No reciclables  
- Sumá señalética educativa y voluntarios que orienten a los corredores.

### 💡 Economía circular
- Asociate con artesanos o escuelas locales para donar materiales reutilizables.  
- Creá un concurso post-evento con objetos hechos a partir de residuos.  

### 🌍 Acción a largo plazo
- Mantené registro anual de los materiales recuperados.  
- Difundí los resultados en redes para inspirar a otros eventos.  

---
[⬅️ Volver al Planificador Principal](app)
""")
