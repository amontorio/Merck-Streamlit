import streamlit as st
import os
import glob
import pandas as pd
import json
from datetime import datetime, date

user_id = st.session_state.get("user_id", "default_user")

# Estilos CSS personalizados
st.markdown(
    """
    <style>
    .expander {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .action-button {
        width: 100%;
        padding: 0.5rem;
        border-radius: 0.5rem;
        font-weight: bold;
    }
    .edit-button { background-color: #e0f7fa; }
    .delete-button { background-color: #ffebee; }
    .view-button { background-color: #e8f5e9; }
    </style>
    """, unsafe_allow_html=True
)

# Título y descripción de la página
st.title("📋 Gestión de Formularios")
st.markdown("Selecciona, filtra y revisa tus borradores o formularios completos.")
st.markdown(f"Usuario: **{user_id}**")

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

# Función para deserializar fechas ISO

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

# Función para cargar archivos JSON y devolver un DataFrame con columnas fijas

def cargar_archivos(directorio):
    patron = os.path.join(directorio, f"{user_id}_*.json")
    archivos = glob.glob(patron)
    data = []
    for path in archivos:
        nombre = os.path.basename(path)
        tipo_form = next((t.replace("_", " ") for t in TIPOS_VALIDOS if t in nombre), "Desconocido")
        fecha_mod = datetime.fromtimestamp(os.path.getmtime(path))
        data.append({
            "Tipo de formulario": tipo_form,
            "Fecha de guardado": pd.to_datetime(fecha_mod),
            "Acciones": path
        })
    df = pd.DataFrame(data, columns=["Tipo de formulario", "Fecha de guardado", "Acciones"])
    if not df.empty:
        df = df.sort_values("Fecha de guardado", ascending=False)
    return df

# Manejo de acciones (editar/ver)

def manejar_accion(path, tipo_formulario):
    with open(path, 'r') as f:
        form_data = json.load(f)
    form_data = deserialize_dates(form_data)
    clave = f"form_data_{tipo_formulario.replace(' ', '_').replace('_paraguas', '').replace('_merck', '')}"
    
    if "speaking services" in tipo_formulario:
        st.session_state[clave] = form_data
        st.session_state['participantes_ss'] = list(form_data.get('participantes_ss', {}).values())
        print(f"#########################")
        print(st.session_state['participantes_ss'])
        for user_elems in st.session_state['participantes_ss']:
            for key in user_elems.keys():
                st.session_state[clave]['participantes_ss'][user_elems["id"]][key] = user_elems[key]

    elif tipo_formulario == "advisory board":
        st.session_state[clave] = form_data
        st.session_state['participantes_ab'] = list(form_data.get('participantes_ab', {}).values())

        for user_elems in st.session_state['participantes_ab']:
            for key in user_elems.keys():
                st.session_state[clave]['participantes_ab'][user_elems["id"]][key] = user_elems[key]

        print(st.session_state['participantes_ab'] )
    elif tipo_formulario == "consulting services":
        st.session_state[clave] = form_data
        st.session_state['participantes_cs'] = list(form_data.get('participantes_cs', {}).values())
    elif tipo_formulario == "event":
        st.session_state[clave] = form_data
        st.session_state['email_correcto'] = True
    else:
        st.session_state[clave] = form_data

    
    st.switch_page(MAPEO_PAGINAS[tipo_formulario])
# ===== INTERFAZ DE FILTROS =====
st.sidebar.header("Filtros")
opciones_tipos = [t.replace('_', ' ') for t in TIPOS_VALIDOS]
filtro_tipos = st.sidebar.multiselect(
    "Selecciona tipo(s)", opciones_tipos, default=opciones_tipos
)
hoy = date.today()
fecha_inicio, fecha_fin = st.sidebar.date_input(
    "Rango de fechas", [hoy.replace(month=1, day=1), hoy],
    format="DD/MM/YYYY"
)

# ===== CARGAR Y FILTRAR DATOS =====

df_borradores = cargar_archivos(CARPETA_BORRADORES)
df_historial = cargar_archivos(CARPETA_HISTORIAL)

def aplicar_filtros(df):
    if df.empty:
        return df
    df = df[df['Tipo de formulario'].isin(filtro_tipos)]
    df = df[(df['Fecha de guardado'].dt.date >= fecha_inicio) & (df['Fecha de guardado'].dt.date <= fecha_fin)]
    return df

filtered_borr = aplicar_filtros(df_borradores)
filtered_hist = aplicar_filtros(df_historial)

# ===== MOSTRAR EN ACORDEÓN =====

with st.expander(f"Borradores guardados", expanded=True):
    if filtered_borr.empty:
        st.info("No hay borradores con esos filtros.")
    else:
        for i, row in filtered_borr.iterrows():
            c0, c1, c2 = st.columns([4, 1, 1])
            with c0:
                st.markdown(f"**{row['Tipo de formulario'].title()}** — *{row['Fecha de guardado'].strftime('%Y-%m-%d %H:%M:%S')}*")
            with c1:
                if st.button("✏️ Editar", key=f"edit_b_{i}", use_container_width=True):
                    manejar_accion(row['Acciones'], row['Tipo de formulario'])
            with c2:
                if st.button("🗑️ Eliminar", key=f"del_b_{i}", use_container_width=True):
                    os.remove(row['Acciones'])
                    st.rerun()

with st.expander("Historial de formularios", expanded=True):
    if filtered_hist.empty:
        st.info("No hay formularios completos con esos filtros.")
    else:
        for i, row in filtered_hist.iterrows():
            c0, c1 = st.columns([5, 1])
            with c0:
                st.markdown(f"**{row['Tipo de formulario'].title()}** — *{row['Fecha de guardado'].strftime('%Y-%m-%d %H:%M:%S')}*")
            with c1:
                if st.button("👁️ Ver", key=f"view_h_{i}", use_container_width=True):
                    manejar_accion(row['Acciones'], row['Tipo de formulario'])
