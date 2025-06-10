import streamlit as st
import os
import glob
import pandas as pd
import json
from datetime import datetime, date

user_id = st.session_state.get("user_id", "default_user")

CARPETA_BORRADORES = "formularios_guardados"
CARPETA_HISTORIAL = "historial"
TIPOS_VALIDOS = [
    "speaking_services_paraguas",
    "speaking_services_merck",
    "consulting_services",
    "event",
    "advisory_board"
]
MAPEO_PAGINAS = {
    "speaking services paraguas": "./pages/speaking_services_page.py",
    "speaking services merck": "./pages/speaking_services_page.py",
    "consulting services": "./pages/consulting_services_page.py",
    "event": "./pages/event_page.py",
    "advisory board": "./pages/advisory_board_page.py"
}

def deserialize_dates(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                try:
                    obj[k] = date.fromisoformat(v)
                except ValueError:
                    pass
            elif isinstance(v, (dict, list)):
                obj[k] = deserialize_dates(v)
    elif isinstance(obj, list):
        obj = [deserialize_dates(i) for i in obj]
    return obj

def cargar_archivos(directorio, tipo):
    patron = os.path.join(directorio, f"{user_id}_*.json")
    archivos = glob.glob(patron)
    data = []
    for path in archivos:
        nombre = os.path.basename(path)
        tipo_form = next((t.replace("_", " ") for t in TIPOS_VALIDOS if t in nombre), "Desconocido")
        fecha = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
        data.append({
            "Tipo de formulario": tipo_form,
            "Fecha de guardado": fecha,
            "Acciones": path
        })
    return pd.DataFrame(data)

def manejar_accion(accion, path, tipo_formulario):
    with open(path, 'r') as f:
        form_data = json.load(f)
    form_data = deserialize_dates(form_data)

    if tipo_formulario in MAPEO_PAGINAS:
        clave = f"form_data_{tipo_formulario.replace(' ', '_')}"
        if "speaking services" in tipo_formulario:
            st.session_state["form_data_speaking_services"] = form_data
            st.session_state["participantes_ss"] = list(form_data.get("participantes_ss", {}).values())
        elif tipo_formulario == "advisory board":
            st.session_state[clave] = form_data
            st.session_state["participantes_ab"] = list(form_data.get("participantes_ab", {}).values())
        elif tipo_formulario == "consulting services":
            st.session_state[clave] = form_data
            st.session_state["participantes_cs"] = list(form_data.get("participantes_cs", {}).values())
        elif tipo_formulario == "event":
            st.session_state[clave] = form_data
            st.session_state["email_correcto"] = True
        else:
            st.session_state[clave] = form_data
        st.switch_page(MAPEO_PAGINAS[tipo_formulario])

# 📄 Borradores guardados
st.markdown(f"<h3>Borradores guardados ({user_id})</h3><hr>", unsafe_allow_html=True)
df_borradores = cargar_archivos(CARPETA_BORRADORES, "borradores")

for i, row in df_borradores.iterrows():
    cols = st.columns([4, 1, 1])
    with cols[0]:
        st.markdown(f"**{row['Tipo de formulario']}** — *{row['Fecha de guardado']}*")
    with cols[1]:
        if st.button("✏️", key=f"edit_{i}"):
            manejar_accion("editar", row["Acciones"], row["Tipo de formulario"])
    with cols[2]:
        if st.button("🗑️", key=f"delete_{i}"):
            os.remove(row["Acciones"])
            st.rerun()

# ✔️ Historial
st.markdown("<h3>Historial de formularios completos</h3><hr>", unsafe_allow_html=True)
df_historial = cargar_archivos(CARPETA_HISTORIAL, "historial")

for i, row in df_historial.iterrows():
    cols = st.columns([5, 1])
    with cols[0]:
        st.markdown(f"**{row['Tipo de formulario']}** — *{row['Fecha de guardado']}*")
    with cols[1]:
        if st.button("👁️", key=f"view_{i}"):
            manejar_accion("ver", row["Acciones"], row["Tipo de formulario"])
