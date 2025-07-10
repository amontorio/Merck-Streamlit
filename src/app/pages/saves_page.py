import streamlit as st
import os
import glob
import pandas as pd
import json
from datetime import datetime, date
import math

PAGE_SIZE = 5

def init_pagination_state():
    if "page_borr" not in st.session_state:
        st.session_state.page_borr = 0
    if "page_hist" not in st.session_state:
        st.session_state.page_hist = 0

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

def extraer_nombre_evento(contenido, tipo_form):
    if "speaking services" in tipo_form:
        return contenido.get("nombre_evento_ss", "—")
    elif tipo_form == "advisory board":
        return contenido.get("nombre_evento_ab", "—")
    elif tipo_form == "consulting services":
        return contenido.get("nombre_necesidades_cs", "—")
    elif tipo_form == "event":
        return contenido.get("event_name", "—")
    else:
        return "—"

def extraer_owner(contenido, tipo_form):
    if "speaking services" in tipo_form:
        return contenido.get("owner_ss", "—")
    elif tipo_form == "advisory board":
        return contenido.get("owner_ab", "—")
    elif tipo_form == "consulting services":
        return contenido.get("owner_cs", "—")
    elif tipo_form == "event":
        return contenido.get("owner", "—")
    else:
        return "—"

def cargar_archivos(directorio, user_id, tipos_validos):
    patron = os.path.join(directorio, f"{user_id}_*.json")
    archivos = glob.glob(patron)
    data = []
    for path in archivos:
        nombre = os.path.basename(path)
        tipo_form = next((t.replace("_", " ") for t in tipos_validos if t in nombre), "Desconocido")
        fecha_mod = datetime.fromtimestamp(os.path.getmtime(path))
        try:
            with open(path, 'r') as f:
                contenido = json.load(f)
                event_name = extraer_nombre_evento(contenido, tipo_form)
                owner = extraer_owner(contenido, tipo_form)
        except Exception:
            event_name = "—"
            owner = "—"
        data.append({
            "Tipo de formulario": tipo_form,
            "Fecha de guardado": pd.to_datetime(fecha_mod),
            "Nombre del evento": event_name,
            "Owner": owner,
            "Acciones": path
        })
    df = pd.DataFrame(data, columns=["Tipo de formulario", "Fecha de guardado", "Nombre del evento", "Owner", "Acciones"])
    if not df.empty:
        df = df.sort_values("Fecha de guardado", ascending=False)
    return df

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

def display_section(title, df, page_key, prev_cb, next_cb, action_btns):
    with st.expander(title, expanded=True):
        if df.empty:
            st.info(f"No hay {title.lower()} con esos filtros.")
            return
        st.markdown(f"<div style='margin-top: 1px; margin-bottom: 5px;  font-size: 16px; color: gray;'>🔎 Resultados encontrados: <strong>{len(df)}</strong></div>", unsafe_allow_html=True)

        page = st.session_state[page_key]
        page_df = df.iloc[page*PAGE_SIZE:(page+1)*PAGE_SIZE]
        for idx, row in page_df.iterrows():
            cols = st.columns([4] + [1]*len(action_btns))
            cols[0].markdown(
                f"<span style='font-size:20px; font-weight:bold;'>{row['Tipo de formulario'].title()}</span> — "
                f"<span style='font-size:16px; font-style:italic;'>{row['Fecha de guardado'].strftime('%Y-%m-%d %H:%M:%S')}</span><br>"
                f"📌 <strong>Evento:</strong> {row['Nombre del evento']}<br>👤 <strong>Owner:</strong> {row['Owner']}",
                unsafe_allow_html=True
            )
            for i, (label, cb) in enumerate(action_btns.items(), start=1):
                if cols[i].button(label, key=f"{label}_{page_key}_{idx}", use_container_width=True):
                    cb(row['Acciones'], row['Tipo de formulario'])
        total = max(math.ceil(len(df)/PAGE_SIZE), 1)
        pcol, mcol, ncol = st.columns([1,8,1])
        with pcol:
            st.button("←", key=f"prev_{page_key}", disabled=page==0, on_click=prev_cb)
        with mcol:
            st.markdown(f"<div style='text-align:center; font-size:18px;'>Página {page+1} de {total}</div>", unsafe_allow_html=True)
        with ncol:
            st.button("→", key=f"next_{page_key}", disabled=page>=total-1, on_click=next_cb)

def aplicar_filtros(df, tipos, fecha_inicio, fecha_fin, nombre_evento, owner):
    if df.empty:
        return df
    df = df[df['Tipo de formulario'].isin(tipos)]
    df = df[(df['Fecha de guardado'].dt.date >= fecha_inicio) &
            (df['Fecha de guardado'].dt.date <= fecha_fin)]
    if nombre_evento:
        df = df[df['Nombre del evento'].str.contains(nombre_evento, case=False, na=False)]
    if owner:
        df = df[df['Owner'].str.contains(owner, case=False, na=False)]
    return df

def reset_filtros():
    for k in ["filtro_tipos", "fecha_rango", "filtro_evento", "filtro_owner", "page_borr", "page_hist"]:
        if k in st.session_state:
            del st.session_state[k]

def main():
    user_id = st.session_state.get("user_id", "default_user")
    init_pagination_state()

    TIPOS_VALIDOS = [
        "speaking_services_paraguas",
        "speaking_services_merck",
        "consulting_services",
        "event",
        "advisory_board"
    ]
    global MAPEO_PAGINAS
    MAPEO_PAGINAS = {t.replace('_', ' '): f"./pages/{t.replace('_paraguas', '').replace('_merck', '')}_page.py" for t in TIPOS_VALIDOS}

    # CSS para aumentar tamaño en acordeones
    st.markdown(
        """
        <style>
        div[role="region"] {
            font-size: 16px !important;
        }
        div[role="region"] > div {
            padding: 1rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("📋 Gestión de Formularios")
    st.markdown(f"Usuario: {st.session_state.first_name} {st.session_state.last_name} (**{user_id}**)")

    st.sidebar.header("Filtros")

    filtro_tipos = st.sidebar.multiselect(
        "Selecciona tipo(s)",
        [t.replace('_', ' ') for t in TIPOS_VALIDOS],
        key='filtro_tipos',
        default=[t.replace('_', ' ') for t in TIPOS_VALIDOS]
    )

    hoy = date.today()
    valor_fecha_default = [hoy.replace(month=1, day=1), hoy]

    fecha_rango = st.sidebar.date_input(
        "Rango de fechas",
        key='fecha_rango',
        value=valor_fecha_default,
        format="DD/MM/YYYY"
    )

    if not (isinstance(fecha_rango, (list, tuple)) and len(fecha_rango) == 2):
        st.sidebar.warning("Por favor selecciona un rango de dos fechas.")
        st.info("Por favor selecciona un rango de dos fechas para mostrar resultados.")
        return

    filtro_evento = st.sidebar.text_input("📌 Filtrar por nombre de evento", key='filtro_evento')
    filtro_owner = st.sidebar.text_input("👤 Filtrar por owner", key='filtro_owner')

    st.sidebar.button("Limpiar filtros", on_click=reset_filtros, icon="🧹", use_container_width=True, type="secondary")

    fecha_inicio, fecha_fin = fecha_rango

    df_borr = cargar_archivos("formularios_guardados", user_id, TIPOS_VALIDOS)
    df_hist = cargar_archivos("historial", user_id, TIPOS_VALIDOS)

    filtered_borr = aplicar_filtros(df_borr, filtro_tipos, fecha_inicio, fecha_fin, filtro_evento, filtro_owner)
    filtered_hist = aplicar_filtros(df_hist, filtro_tipos, fecha_inicio, fecha_fin, filtro_evento, filtro_owner)

    display_section(
        "Borradores guardados", filtered_borr, "page_borr",
        lambda: setattr(st.session_state, 'page_borr', max(st.session_state.page_borr - 1, 0)),
        lambda: setattr(st.session_state, 'page_borr', min(st.session_state.page_borr + 1, math.ceil(len(filtered_borr) / PAGE_SIZE) - 1)),
        {"✏️ Editar": manejar_accion, "🗑️ Eliminar": lambda p, t: (os.remove(p), st.rerun())}
    )
    display_section(
        "Historial de formularios", filtered_hist, "page_hist",
        lambda: setattr(st.session_state, 'page_hist', max(st.session_state.page_hist - 1, 0)),
        lambda: setattr(st.session_state, 'page_hist', min(st.session_state.page_hist + 1, math.ceil(len(filtered_hist) / PAGE_SIZE) - 1)),
        {"👁️ Ver": manejar_accion}
    )

if __name__ == '__main__':
    main()
