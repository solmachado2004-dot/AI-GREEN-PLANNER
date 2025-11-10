# reciclaje.py — sitio de reciclaje
import streamlit as st

st.set_page_config(page_title="Centro de Reciclaje", page_icon="♻️", layout="wide")

st.title("♻️ Centro de Reciclaje y Reutilización")
st.caption("Aprendé cómo transformar los residuos de tu evento en oportunidades sostenibles 🌱")

st.markdown("""
### 🌿 Reutilización creativa
- Fundí medallas para nuevas ediciones o souvenires.
- Transformá remeras viejas en bolsas o paños.
- Reutilizá carteles como cobertores o manteles.
- Usá botellas PET para fabricar señalética o macetas.

### 🗑️ Separación inteligente
- 📦 **Reciclables:** plástico, papel, aluminio.
- 🌱 **Compostables:** cáscaras, restos de frutas.
- 🚯 **No reciclables:** lo demás (buscar reducirlos).

### 💡 Economía circular
- Doná materiales a escuelas técnicas o talleres locales.
- Organizá concursos de diseño con residuos del evento.
- Mostrá tus resultados en redes y educá a la comunidad.

---
[⬅️ Volver al planificador](app)
""")
