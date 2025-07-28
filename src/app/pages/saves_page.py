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

def extraer_fecha_evento(contenido, tipo_form):
    if "speaking services" in tipo_form:
        start_date = contenido.get("start_date_ss", "")
        end_date = contenido.get("end_date_ss", "")
    elif tipo_form == "advisory board":
        start_date = contenido.get("start_date_ab", "")
        end_date = contenido.get("end_date_ab", "")
    elif tipo_form == "consulting services":
        start_date = contenido.get("start_date_cs", "")
        end_date = contenido.get("end_date_cs", "")
    elif tipo_form == "event":
        start_date = contenido.get("start_date", "")
        end_date = contenido.get("end_date", "")
    else:
        return "—"
    
    if start_date and end_date:
        if start_date == end_date:
            return start_date
        else:
            return f"{start_date} - {end_date}"
    elif start_date:
        return start_date
    elif end_date:
        return end_date
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
                fecha_evento = extraer_fecha_evento(contenido, tipo_form)
        except Exception:
            event_name = "—"
            fecha_evento = "—"
        data.append({
            "Tipo de formulario": tipo_form,
            "Fecha de guardado": pd.to_datetime(fecha_mod),
            "Nombre del evento": event_name,
            "Fecha del evento": fecha_evento,
            "Acciones": path
        })
    df = pd.DataFrame(data, columns=["Tipo de formulario", "Fecha de guardado", "Nombre del evento", "Fecha del evento", "Acciones"])
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
                f"<span style='font-size:20px; font-weight:bold;'>{row['Tipo de formulario'].title()}</span><br>"
                f"💾 <span style='font-size:14px; color: #666;'><strong>Guardado:</strong> {row['Fecha de guardado'].strftime('%Y-%m-%d %H:%M:%S')}</span><br>"
                f"📌 <strong>Evento:</strong> {row['Nombre del evento']}<br>"
                f"📅 <strong>Fecha del evento:</strong> {row['Fecha del evento']}",
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

def fecha_evento_en_rango(fecha_evento_str, fecha_inicio_filtro, fecha_fin_filtro):
    """
    Verifica si las fechas del evento se superponen con el rango de filtro.
    fecha_evento_str puede ser una fecha simple o un rango "fecha1 - fecha2"
    """
    if fecha_evento_str == "—" or not fecha_evento_str:
        return False
    
    try:
        if " - " in fecha_evento_str:
            # Es un rango de fechas
            start_str, end_str = fecha_evento_str.split(" - ")
            evento_inicio = date.fromisoformat(start_str.strip())
            evento_fin = date.fromisoformat(end_str.strip())
        else:
            # Es una sola fecha
            evento_inicio = date.fromisoformat(fecha_evento_str.strip())
            evento_fin = evento_inicio
        
        # Verificar si hay superposición entre los rangos
        # Hay superposición si: evento_inicio <= fecha_fin_filtro AND evento_fin >= fecha_inicio_filtro
        return evento_inicio <= fecha_fin_filtro and evento_fin >= fecha_inicio_filtro
    
    except (ValueError, AttributeError):
        return False

def aplicar_filtros(df, tipos, fecha_inicio, fecha_fin, nombre_evento, fecha_evento_rango):
    if df.empty:
        return df
    df = df[df['Tipo de formulario'].isin(tipos)]
    df = df[(df['Fecha de guardado'].dt.date >= fecha_inicio) &
            (df['Fecha de guardado'].dt.date <= fecha_fin)]
    if nombre_evento:
        df = df[df['Nombre del evento'].str.contains(nombre_evento, case=False, na=False)]
    
    # Filtrar por rango de fechas del evento
    if fecha_evento_rango and isinstance(fecha_evento_rango, (list, tuple)) and len(fecha_evento_rango) == 2:
        fecha_inicio_evento, fecha_fin_evento = fecha_evento_rango
        # Aplicar el filtro usando la nueva función
        df = df[df['Fecha del evento'].apply(
            lambda x: fecha_evento_en_rango(x, fecha_inicio_evento, fecha_fin_evento)
        )]
    
    return df

def reset_filtros():
    # Valores por defecto para los filtros
    hoy = date.today()
    TIPOS_VALIDOS = [
        "speaking_services_paraguas",
        "speaking_services_merck",
        "consulting_services",
        "event",
        "advisory_board"
    ]
    
    # Restablecer cada filtro a su valor por defecto
    st.session_state['filtro_tipos'] = [t.replace('_', ' ') for t in TIPOS_VALIDOS]
    st.session_state['fecha_rango'] = [hoy.replace(month=1, day=1), hoy]
    st.session_state['filtro_evento'] = ""
    st.session_state['filtro_fecha_evento'] = [hoy.replace(month=1, day=1), hoy]
    
    # Reiniciar paginación
    st.session_state['page_borr'] = 0
    st.session_state['page_hist'] = 0

def generar_id_borrador(contenido, tipo_form):
    """
    Genera un identificador único para el borrador basado en:
    - Nombre del evento
    - Fecha de inicio 
    - Fecha de fin
    """
    nombre_evento = extraer_nombre_evento(contenido, tipo_form)
    
    # Extraer fechas según el tipo de formulario
    if "speaking services" in tipo_form:
        start_date = contenido.get("start_date_ss", "")
        end_date = contenido.get("end_date_ss", "")
    elif tipo_form == "advisory board":
        start_date = contenido.get("start_date_ab", "")
        end_date = contenido.get("end_date_ab", "")
    elif tipo_form == "consulting services":
        start_date = contenido.get("start_date_cs", "")
        end_date = contenido.get("end_date_cs", "")
    elif tipo_form == "event":
        start_date = contenido.get("start_date", "")
        end_date = contenido.get("end_date", "")
    else:
        start_date = ""
        end_date = ""
    
    # Normalizar el nombre del evento para usarlo como ID
    nombre_normalizado = ""
    if nombre_evento and nombre_evento != "—":
        import re
        # Eliminar caracteres especiales y espacios, convertir a minúsculas
        nombre_normalizado = re.sub(r'[^a-zA-Z0-9]', '_', nombre_evento.lower())
        # Limitar la longitud para evitar nombres de archivo muy largos
        nombre_normalizado = nombre_normalizado[:50]
    
    # Crear ID único combinando nombre y fechas
    id_unico = f"{nombre_normalizado}_{start_date}_{end_date}".replace("-", "").replace(":", "")
    
    return id_unico

def encontrar_borrador_existente(user_id, tipo_form, contenido):
    """
    Busca si ya existe un borrador con el mismo identificador único
    """
    id_borrador = generar_id_borrador(contenido, tipo_form)
    # Buscar archivos que contengan el tipo de formulario y el ID único
    patron = os.path.join("formularios_guardados", f"{user_id}_{tipo_form.replace(' ', '_')}_*{id_borrador}*.json")
    archivos_existentes = glob.glob(patron)
    
    return archivos_existentes[0] if archivos_existentes else None

def guardar_borrador_inteligente(datos_formulario, tipo_formulario, user_id):
    """
    Guarda o actualiza un borrador de manera inteligente:
    - Si ya existe un borrador con el mismo nombre y fechas, lo sobrescribe
    - Si no existe, crea uno nuevo
    
    Retorna: (ruta_archivo, es_actualizacion)
    """
    import copy
    from datetime import datetime
    
    # Crear una copia de los datos para no modificar el original
    datos = copy.deepcopy(datos_formulario)
    
    # Buscar si ya existe un borrador con el mismo identificador
    archivo_existente = encontrar_borrador_existente(user_id, tipo_formulario, datos)
    
    if archivo_existente:
        # Actualizar el borrador existente
        ruta_archivo = archivo_existente
        es_actualizacion = True
    else:
        # Crear un nuevo borrador
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        id_borrador = generar_id_borrador(datos, tipo_formulario)
        nombre_archivo = f"{user_id}_{tipo_formulario.replace(' ', '_')}_{id_borrador}_{fecha_actual}.json"
        ruta_archivo = os.path.join("formularios_guardados", nombre_archivo)
        es_actualizacion = False
    
    # Preparar los datos para guardar
    def serialize_dates(obj):
        """Convierte objetos datetime.date a cadenas para la serialización JSON."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (datetime, date)):
                    obj[key] = value.isoformat()
                elif isinstance(value, dict):
                    obj[key] = serialize_dates(value)
                elif isinstance(value, list):
                    obj[key] = [serialize_dates(item) for item in value]
        elif isinstance(obj, list):
            obj = [serialize_dates(item) for item in obj]
        return obj
    
    datos_ser = serialize_dates(datos)
    datos_ser["user_id"] = user_id
    datos_ser["formulario_tipo"] = tipo_formulario
    
    # Limpiar documentos para no guardarlos en el borrador
    campos_documentos = [
        "documentosubido_1_event", "documentosubido_2_event", "documentosubido_3_event", 
        "documentosubido_4_event", "documentosubido_5_event",
        "documentosubido_1_ab", "documentosubido_2_ab", "documentosubido_3_ab", "documentosubido_4_ab",
        "documentosubido_1_cs", "documentosubido_2_cs", "documentosubido_3_cs", "documentosubido_4_cs",
        "documentosubido_1_ss", "documentosubido_2_ss", "documentosubido_3_ss", "documentosubido_4_ss"
    ]
    
    for campo in campos_documentos:
        if campo in datos_ser:
            datos_ser[campo] = ""
    
    # Guardar el archivo
    with open(ruta_archivo, "w") as f:
        json.dump(datos_ser, f, indent=2)
    
    return ruta_archivo, es_actualizacion

# Función para ser importada desde otros archivos
def guardar_borrador_desde_formulario(datos_formulario, tipo_formulario, user_id="default_user"):
    """
    Función para ser llamada desde otros archivos de formularios.
    Guarda o actualiza un borrador de manera inteligente.
    
    Args:
        datos_formulario: Los datos del formulario a guardar
        tipo_formulario: El tipo de formulario (event, advisory_board, etc.)
        user_id: ID del usuario
        
    Returns:
        tuple: (mensaje_exito, es_actualizacion)
    """
    try:
        print(f"[DEBUG] Guardando borrador: tipo={tipo_formulario}, user_id={user_id}")
        print(f"[DEBUG] Datos del formulario: {list(datos_formulario.keys())}")
        
        ruta_archivo, es_actualizacion = guardar_borrador_inteligente(datos_formulario, tipo_formulario, user_id)
        
        print(f"[DEBUG] Archivo guardado en: {ruta_archivo}")
        print(f"[DEBUG] Es actualización: {es_actualizacion}")
        
        if es_actualizacion:
            mensaje = "Borrador actualizado exitosamente!"
        else:
            mensaje = "Borrador guardado exitosamente!"
            
        return mensaje, es_actualizacion
        
    except Exception as e:
        print(f"[ERROR] Error al guardar el borrador: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al guardar el borrador: {str(e)}", False

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

    st.sidebar.subheader("🗓️ Filtros por fecha de guardado")
    hoy = date.today()
    valor_fecha_default = [hoy.replace(month=1, day=1), hoy]

    fecha_rango = st.sidebar.date_input(
        "Rango de fechas de guardado",
        key='fecha_rango',
        value=valor_fecha_default,
        format="DD/MM/YYYY",
        help="Filtra los formularios por la fecha en que fueron guardados"
    )

    if not (isinstance(fecha_rango, (list, tuple)) and len(fecha_rango) == 2):
        st.sidebar.warning("Por favor selecciona un rango de dos fechas.")
        st.info("Por favor selecciona un rango de dos fechas para mostrar resultados.")
        return

    st.sidebar.subheader("🔍 Filtros por contenido")
    filtro_evento = st.sidebar.text_input("📌 Filtrar por nombre de evento", key='filtro_evento')
    
    # Filtro de rango de fechas del evento
    hoy_evento = date.today()
    valor_fecha_evento_default = [hoy_evento.replace(month=1, day=1), hoy_evento]
    
    filtro_fecha_evento = st.sidebar.date_input(
        "📅 Rango de fechas del evento",
        key='filtro_fecha_evento',
        value=valor_fecha_evento_default,
        format="DD/MM/YYYY",
        help="Filtra eventos que tengan al menos un día dentro del rango seleccionado"
    )

    st.sidebar.button("Limpiar filtros", on_click=reset_filtros, icon="🧹", use_container_width=True, type="secondary")

    fecha_inicio, fecha_fin = fecha_rango

    # Validar que el filtro de fecha del evento tenga el formato correcto
    if not (isinstance(filtro_fecha_evento, (list, tuple)) and len(filtro_fecha_evento) == 2):
        # Si no hay un rango válido, pasar None para que no filtre por fecha de evento
        filtro_fecha_evento = None

    df_borr = cargar_archivos("formularios_guardados", user_id, TIPOS_VALIDOS)
    df_hist = cargar_archivos("historial", user_id, TIPOS_VALIDOS)

    filtered_borr = aplicar_filtros(df_borr, filtro_tipos, fecha_inicio, fecha_fin, filtro_evento, filtro_fecha_evento)
    filtered_hist = aplicar_filtros(df_hist, filtro_tipos, fecha_inicio, fecha_fin, filtro_evento, filtro_fecha_evento)

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
        {"👁️ Ver": manejar_accion, "🗑️ Eliminar": lambda p, t: (os.remove(p), st.rerun())}
    )

if __name__ == '__main__':
    main()
