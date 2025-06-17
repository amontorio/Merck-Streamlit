import streamlit as st
import os
import glob
import pandas as pd
import json
from datetime import datetime, date
import math

# === CONFIGURACIÓN DE PAGINACIÓN ===
PAGE_SIZE = 5  # número de ítems por página

# Inicializar páginas en session state
def init_pagination_state():
    if "page_borr" not in st.session_state:
        st.session_state.page_borr = 0
    if "page_hist" not in st.session_state:
        st.session_state.page_hist = 0

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

# Función para cargar archivos JSON y devolver DataFrame
def cargar_archivos(directorio, user_id, tipos_validos):
    patron = os.path.join(directorio, f"{user_id}_*.json")
    archivos = glob.glob(patron)
    data = []
    for path in archivos:
        nombre = os.path.basename(path)
        tipo_form = next((t.replace("_", " ") for t in tipos_validos if t in nombre), "Desconocido")
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

# Función para aplicar filtros
def aplicar_filtros(df, tipos, fecha_inicio, fecha_fin):
    if df.empty:
        return df
    df = df[df['Tipo de formulario'].isin(tipos)]
    df = df[(df['Fecha de guardado'].dt.date >= fecha_inicio) &
             (df['Fecha de guardado'].dt.date <= fecha_fin)]
    return df

# Función para manejar la acción de editar/ver con lógica original
def manejar_accion(path, tipo_formulario):
    with open(path, 'r') as f:
        form_data = json.load(f)
    form_data = deserialize_dates(form_data)
    clave = f"form_data_{tipo_formulario.replace(' ', '_').replace('_paraguas', '').replace('_merck', '')}"

    if "speaking services" in tipo_formulario:
        st.session_state[clave] = form_data
        st.session_state['participantes_ss'] = list(form_data.get('participantes_ss', {}).values())
        for user_elems in st.session_state['participantes_ss']:
            for key in user_elems.keys():
                st.session_state[clave]['participantes_ss'][user_elems['id']][key] = user_elems[key]

    elif tipo_formulario == "advisory board":
        st.session_state[clave] = form_data
        st.session_state['participantes_ab'] = list(form_data.get('participantes_ab', {}).values())
        for user_elems in st.session_state['participantes_ab']:
            for key in user_elems.keys():
                st.session_state[clave]['participantes_ab'][user_elems['id']][key] = user_elems[key]

    elif tipo_formulario == "consulting services":
        st.session_state[clave] = form_data
        st.session_state['participantes_cs'] = list(form_data.get('participantes_cs', {}).values())

    elif tipo_formulario == "event":
        st.session_state[clave] = form_data
        st.session_state['email_correcto'] = True

    else:
        st.session_state[clave] = form_data

    st.switch_page(MAPEO_PAGINAS[tipo_formulario])

# Callbacks de paginación
def borr_prev():
    if st.session_state.page_borr > 0:
        st.session_state.page_borr -= 1

def borr_next():
    max_borr = math.ceil(len(filtered_borr) / PAGE_SIZE) - 1
    if st.session_state.page_borr < max_borr:
        st.session_state.page_borr += 1

def hist_prev():
    if st.session_state.page_hist > 0:
        st.session_state.page_hist -= 1

def hist_next():
    max_hist = math.ceil(len(filtered_hist) / PAGE_SIZE) - 1
    if st.session_state.page_hist < max_hist:
        st.session_state.page_hist += 1

# Lógica principal

def main():
    user_id = st.session_state.get("user_id", "default_user")

    # CSS
    st.markdown(
        """
        <style>
        .expander { background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
        .action-button { width: 100%; padding: 0.5rem; border-radius: 0.5rem; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True
    )

    # Título y descripción
    st.title("📋 Gestión de Formularios")
    st.markdown("Selecciona, filtra y revisa tus borradores o formularios completos.")
    st.markdown(f"Usuario: **{user_id}**")

    # Configuración
    CARPETA_BORRADORES = "formularios_guardados"
    CARPETA_HISTORIAL = "historial"
    TIPOS_VALIDOS = [
        "speaking_services_paraguas",
        "speaking_services_merck",
        "consulting_services",
        "event",
        "advisory_board"
    ]
    global MAPEO_PAGINAS
    MAPEO_PAGINAS = {
        t.replace('_', ' '): f"./pages/{t.replace('_paraguas', '').replace('_merck', '')}_page.py" for t in TIPOS_VALIDOS
    }

    # Sidebar filtros
    st.sidebar.header("Filtros")
    opciones_tipos = [t.replace('_', ' ') for t in TIPOS_VALIDOS]
    filtro_tipos = st.sidebar.multiselect("Selecciona tipo(s)", opciones_tipos, default=opciones_tipos)
    hoy = date.today()
    fechas = st.sidebar.date_input("Rango de fechas", [hoy.replace(month=1, day=1), hoy], format="DD/MM/YYYY")
    # Validar selección de fechas
    if not (isinstance(fechas, (list, tuple)) and len(fechas) == 2):
        st.sidebar.warning("Por favor selecciona un rango de dos fechas.")
        fecha_inicio, fecha_fin = None, None
    else:
        fecha_inicio, fecha_fin = fechas

    # Cargar datos y aplicar filtros
    df_borr = cargar_archivos(CARPETA_BORRADORES, user_id, TIPOS_VALIDOS)
    df_hist = cargar_archivos(CARPETA_HISTORIAL, user_id, TIPOS_VALIDOS)
    global filtered_borr, filtered_hist
    filtered_borr = aplicar_filtros(df_borr, filtro_tipos, fecha_inicio, fecha_fin)
    filtered_hist = aplicar_filtros(df_hist, filtro_tipos, fecha_inicio, fecha_fin)

    # Iniciar paginación
    init_pagination_state()
    paginate = lambda df, page: df.iloc[page*PAGE_SIZE:(page+1)*PAGE_SIZE]

    # Función genérica de display
    def display_section(title, df, page_key, prev_cb, next_cb, action_btns):
        with st.expander(title, expanded=True):
            if df.empty:
                st.info(f"No hay {title.lower()} con esos filtros.")
                return
            page = st.session_state[page_key]
            page_df = paginate(df, page)
            for idx, row in page_df.iterrows():
                cols = st.columns([4] + [1]*len(action_btns))
                cols[0].markdown(f"**{row['Tipo de formulario'].title()}** — *{row['Fecha de guardado'].strftime('%Y-%m-%d %H:%M:%S')}*")
                for i, (label, cb) in enumerate(action_btns.items(), start=1):
                    if cols[i].button(label, key=f"{label}_{page_key}_{idx}", use_container_width=True):
                        cb(row['Acciones'], row['Tipo de formulario'])
            total = max(math.ceil(len(df)/PAGE_SIZE), 1)
            pcol, mcol, ncol = st.columns([1,8,1])
            with pcol:
                st.button("←", key=f"prev_{page_key}", disabled=page==0, on_click=prev_cb)
            with mcol:
                st.markdown(f"<div style='text-align:center'>Página {page+1} de {total}</div>", unsafe_allow_html=True)
            with ncol:
                st.button("→", key=f"next_{page_key}", disabled=page>=total-1, on_click=next_cb)

    # Mostrar secciones
    display_section(
        "Borradores guardados", filtered_borr, "page_borr",
        borr_prev, borr_next,
        {"✏️ Editar": manejar_accion, "🗑️ Eliminar": lambda p, t: (os.remove(p), st.rerun())}
    )
    display_section(
        "Historial de formularios", filtered_hist, "page_hist",
        hist_prev, hist_next,
        {"👁️ Ver": manejar_accion}
    )

if __name__ == '__main__':
    main()