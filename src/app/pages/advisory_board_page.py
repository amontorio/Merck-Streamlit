import pandas as pd
import streamlit as st
from streamlit_searchbox import st_searchbox
from datetime import date
import unicodedata
import uuid
from datetime import time
import auxiliar.create_docx as cd
import traceback

# Diccionario de tarifas según el tier
tarifas = {
    "0": 50,  # Ejemplo de valores, cambia según tu lógica
    "1": 75,
    "2": 100,
    "3": 150,
    "4": 200
}

def validar_campos(input_data, parametros_obligatorios, parametros_dependientes):
    """
    Valida que los parámetros obligatorios y los parámetros dependientes (según su condición)
    tengan un valor en el input_data (por ejemplo, el diccionario obtenido de un JSON).

    Args:
        input_data (dict): Diccionario con los datos a validar.
        parametros_obligatorios (list): Lista de nombres de parámetros obligatorios.
        parametros_dependientes (dict): Diccionario con la estructura:
            {
                "parametro_principal": {
                    "condicion": función que recibe el valor del parametro_principal y retorna True/False,
                    "dependientes": [listado de parámetros dependientes]
                },
                ...
            }

    Returns:
        list: Lista de mensajes de error. Si está vacía, no se encontraron errores.
    """
    errores = []

    # Validar los parámetros obligatorios
    for param in parametros_obligatorios:
        # Se considera "sin valor" si no está presente, es None o es cadena vacía.
        if param not in input_data or input_data[param] is None or input_data[param] == "":
            errores.append(f"El parámetro '{param}' es obligatorio y no tiene valor.")

    # Validar los parámetros dependientes
    for parametro_principal, reglas in parametros_dependientes.items():
        # Obtener la función de condición y la lista de dependientes.
        condicion = reglas.get("condicion", lambda valor: False)
        dependientes = reglas.get("dependientes", [])

        # Solo se evalúa si el parámetro principal existe en input_data.
        if parametro_principal in input_data:
            valor_principal = input_data[parametro_principal]
            # Si la condición se cumple, se exigen los parámetros dependientes.
            if condicion(valor_principal):
                for dep in dependientes:
                    if dep not in input_data or input_data[dep] is None or input_data[dep] == "":
                        errores.append(
                            f"El parámetro dependiente '{dep}' es obligatorio cuando '{parametro_principal}' cumple la condición."
                        )
        else:
            # Opcional: Si se desea, se puede reportar que el parámetro principal falta.
            errores.append(f"El parámetro principal '{parametro_principal}' no se encontró en los datos.")

    return errores

def save_to_session_state(key, value, key_participante=None, field_participante=None):
    if key != "participantes":
        st.session_state[key] = value
        st.session_state["form_data_advisory_board"][key] = value
    else:
        st.session_state[field_participante] = value
        st.session_state["form_data_advisory_board"][key][key_participante][field_participante] = value

def add_participant():
    # Añadir un nuevo participante con campos inicializados
    id_user = str(uuid.uuid4())
    new_participant = {
        "id": id_user,
        f"nombre_{id_user}": "",
        f"apellidos_{id_user}": "",
        f"dni_{id_user}": "",
        f"tier_{id_user}": "0",
        f"centro_trabajo_{id_user}": "",
        f"email_contrato_{id_user}": "",
        f"cobra_sociedad_{id_user}": "",
        f"nombre_sociedad_{id_user}": "",
        f"honorarios_{id_user}": 0.0,
        f"preparacion_horas_{id_user}": 0,
        f"preparacion_minutos_{id_user}": 0,
        f"ponencia_horas_{id_user}": 0,
        f"ponencia_minutos_{id_user}": 0,
    }
    
    st.session_state["participantes"].append(new_participant)
    st.session_state["participant_index"] += 1
    st.session_state["id_participantes"].append(id_user)
    
    # Inicializar participantes en form_data_advisory_board si no existe
    if "participantes" not in st.session_state["form_data_advisory_board"]:
        st.session_state["form_data_advisory_board"]["participantes"] = {}
        
    st.session_state["form_data_advisory_board"]["participantes"][id_user] = new_participant
    
def remove_last_participant():
    # Eliminar el último participante
    if st.session_state["participantes"]:
        pos = len(st.session_state["participantes"])
        print(st.session_state["form_data_advisory_board"]["participantes"].pop(pos))

        st.session_state["participantes"].pop()

        st.session_state["participant_index"] -= 1
def get_form_data_advisory_boardby_key(key):
    return st.session_state["form_data_advisory_board"][key]


# Inicializar estado del formulario en session_state
if "form_data_advisory_board" not in st.session_state:
    field_defaults = {
        "start_date": date.today(),
        "end_date": date.today(),
        "estado_aprobacion": "N/A",
        "otra_actividad_departamento": "Sí", 
        "otra_actividad_otro_departamento": "Sí",
        "desplazamiento": "Sí",
        "alojamiento": "Sí", 
        "num_noches": 0,
        "hotel": "",
        "tipo_evento": "Virtual",
    }

    st.session_state["form_data_advisory_board"] = {}
    st.session_state["id_participantes"] = []
    
    for key, value in field_defaults.items():
        save_to_session_state(key, value)

if "participantes" not in st.session_state:
    st.session_state.participantes = [] 
if "participant_index" not in st.session_state:
    st.session_state["participant_index"] = 0
    add_participant()

st.title("Formulario de Advisory Board")
st.header("1. Documentos a adjuntar", divider=True)
st.file_uploader("Programa del evento *", type=["pdf"], key="doc1", on_change=lambda: save_to_session_state("doc1", st.session_state["doc1"]))

st.header("2. Detalles de la actividad", divider=True)
col1, col2 = st.columns(2)

with col1:
    st.text_input("Producto asociado *", max_chars=255, key="producto_asociado", on_change=lambda: save_to_session_state("producto_asociado", st.session_state["producto_asociado"]))

with col2:
    st.selectbox("Estado de la aprobación", ["N/A", "Aprobado", "No Aprobado"], key="estado_aprobacion", on_change=lambda: save_to_session_state("estado_aprobacion", st.session_state["estado_aprobacion"]))

col1, col2 = st.columns(2)

with col1:
    st.text_area("Descripción del servicio *", max_chars=4000, key="descripcion_servicio", help="Describa la necesidad de obtener información de los paticipantes y el propósito para el cual se utilizará dicha información.", on_change=lambda: save_to_session_state("descripcion_servicio", st.session_state["descripcion_servicio"]))
    st.selectbox("¿Otra actividad en el departamento en últimos 12 meses? *", ["No lo sé", "Sí", "No"], key="otra_actividad_departamento", on_change=lambda: save_to_session_state("otra_actividad_departamento", st.session_state["otra_actividad_departamento"]))
with col2:
    st.text_area("Necesidad de la reunión y resultados esperados *", max_chars=4000, key="necesidad_reunion", on_change=lambda: save_to_session_state("necesidad_reunion", st.session_state["necesidad_reunion"]))
    st.selectbox("¿Y en otro departamento? *", ["No lo sé", "Sí", "No"], key="otra_actividad_otro_departamento", on_change=lambda: save_to_session_state("otra_actividad_otro_departamento", st.session_state["otra_actividad_otro_departamento"]))

st.header("3. Logística de la actividad", divider=True)
col1, col2 = st.columns(2)
with col1:
    st.selectbox("¿Desplazamiento de participantes? *", ["No", "Sí"], key="desplazamiento", on_change=lambda: save_to_session_state("desplazamiento", st.session_state["desplazamiento"]))
with col2:
    st.selectbox("¿Alojamiento de participantes? *", ["No", "Sí"], key="alojamiento", 
                 on_change=lambda: (
                     save_to_session_state("alojamiento", st.session_state["alojamiento"]),
                     save_to_session_state("hotel", ""),
                     save_to_session_state("num_noches", 0)
                 ) if st.session_state["alojamiento"] == "No" else 
                     save_to_session_state("alojamiento", st.session_state["alojamiento"]))

with col1:
    st.text_input(
        "Hotel",
        max_chars=255,
        key="hotel",
        disabled=st.session_state["form_data_advisory_board"]["alojamiento"] == "No",
        value="" if st.session_state["form_data_advisory_board"]["alojamiento"] == "No" else st.session_state["form_data_advisory_board"].get("hotel", ""),
        on_change=lambda: save_to_session_state("hotel", st.session_state["hotel"])
    )
with col2:
    st.number_input(
        "Nº de noches", 
        min_value=0, 
        step=1, 
        key="num_noches", 
        disabled=st.session_state["form_data_advisory_board"]["alojamiento"] == "No",
        value=0 if st.session_state["form_data_advisory_board"]["alojamiento"] == "No" else st.session_state["form_data_advisory_board"].get("num_noches", 0),
        on_change=lambda: save_to_session_state("num_noches", st.session_state["num_noches"])
    )

def normalize_text(text):
    # Convertir a string y minúsculas
    text = str(text).lower()
    # Eliminar tildes y caracteres especiales
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')
    # Eliminar espacios adicionales
    text = text.strip()
    return text

def search_function(search_text):

    #df = pd.read_excel(r"C:\Users\AMONTORIOP002\Documents\Merck-Streamlit\src\app\database\Accounts with HCP tiering_ES_2025_01_29.xlsx")
    df = pd.read_excel(r"C:\Users\mcantabela001\Desktop\PROYECTOS\MERCK\Accounts with HCP tiering_ES_2025_01_29.xlsx")
    # Eliminar filas donde 'Nombre de la cuenta' sea NaN
    df = df.dropna(subset=['Nombre de la cuenta'])

    # Reemplazar NaN en 'Especialidad' con 'Ninguna'
    df['Especialidad'] = df['Especialidad'].fillna('Ninguna')

    # Reemplazar NaN en 'Tier' con 0
    df['Tier'] = df['Tier'].fillna(0)

    # Asegurarse de que la columna 'Tier' sea numérica
    df['Tier'] = pd.to_numeric(df['Tier'], errors='coerce').fillna(0)

    # Extraer las columnas necesarias y convertirlas a una lista de tuplas
    lista = list(df[['Nombre de la cuenta', 'Especialidad', 'Tier']].itertuples(index=False, name=None))
    
    # Normalizar el texto de búsqueda
    texto_normalizado = normalize_text(search_text)
    # Buscar coincidencias normalizando los elementos de la lista
    return [
        f"{elemento[0]} - {elemento[1]}" for elemento in lista
        if texto_normalizado in normalize_text(elemento[0])
    ]
    
st.header("4. Detalles del evento", divider=True)
st.text_input("Nombre *", max_chars=255, key="nombre_evento", on_change=lambda: save_to_session_state("descripcion_objetivo", st.session_state["descripcion_objetivo"]))
st.text_area("Descripción y objetivo *", max_chars=4000, key="descripcion_objetivo", on_change=lambda: save_to_session_state("descripcion_objetivo", st.session_state["descripcion_objetivo"]))

col1, col2 = st.columns(2)
with col1:
    start_date_ab = st.date_input("Fecha de inicio del evento *", value=st.session_state["form_data_advisory_board"]["start_date"], key="start_date", on_change=lambda: save_to_session_state("start_date", st.session_state["start_date"]))
with col2:
    st.date_input("Fecha de fin del evento *", value=st.session_state["form_data_advisory_board"]["end_date"], key="end_date", min_value = start_date_ab, on_change=lambda: save_to_session_state("end_date", st.session_state["end_date"]))


col1, col2 = st.columns(2)
with col1:
    st.selectbox("Tipo de evento *", ["Virtual", "Presencial", "Híbrido"], key="tipo_evento", 
                 on_change=lambda: (
                     save_to_session_state("tipo_evento", st.session_state["tipo_evento"]),
                     save_to_session_state("sede", ""),
                     save_to_session_state("ciudad", "")
                 ) if st.session_state["tipo_evento"] == "Virtual" else 
                     save_to_session_state("tipo_evento", st.session_state["tipo_evento"]))
with col2:
    st.number_input("Nº de participantes totales *", min_value=0, step=1, key="num_participantes_totales", help="Ratio obligatorio (5 asistentes por ponente)",
                    on_change=lambda: save_to_session_state("num_participantes_totales", st.session_state["num_participantes_totales"]))

col1, col2 = st.columns(2)
with col1:
    st.text_input(
        "Sede",
        max_chars=255,
        key="sede",
        disabled=st.session_state["form_data_advisory_board"]["tipo_evento"] == "Virtual",
        value="" if st.session_state["form_data_advisory_board"]["tipo_evento"] == "Virtual" else st.session_state["form_data_advisory_board"].get("sede", ""),
        on_change=lambda: save_to_session_state("sede", st.session_state["sede"])
    )
with col2:
    st.text_input(
        "Ciudad",
        max_chars=255,
        key="ciudad",
        disabled=st.session_state["form_data_advisory_board"]["tipo_evento"] == "Virtual",
        value="" if st.session_state["form_data_advisory_board"]["tipo_evento"] == "Virtual" else st.session_state["form_data_advisory_board"].get("ciudad", ""),
        on_change=lambda: save_to_session_state("ciudad", st.session_state["ciudad"])
    )

st.text_input(
        "Público objetivo del programa *",
        max_chars=255,
        key="publico_objetivo",
        on_change=lambda: save_to_session_state("publico_objetivo", st.session_state["publico_objetivo"])
    )

st.header("5. Participantes del Advisory", divider=True)
col1, col2 = st.columns(2)
with col1:
    st.number_input("Nº de participantes *", min_value=0, step=1, key="num_participantes", help="Asegúrese de que se contrate la cantidad necesaria de participantes para brindar los servicios que satisfacen las necesidades legítimas.", on_change=lambda: save_to_session_state("num_participantes", st.session_state["num_participantes"]))
with col2:
    st.multiselect(
        "Criterios de selección *",
        [
            "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Kol Global", "Experiencia como ponente", "Experiencia como Participante de Advisory",
            "Experiencia como profesor", "Experiencia clínica en tema a tratar", "Especialista en tema a tratar",
            "Criterios adicionales: campo abierto"
        ],
        key="criterios_seleccion",
        on_change=lambda: save_to_session_state("criterios_seleccion", st.session_state["criterios_seleccion"])
    )
st.text_area("Justificación de número de participantes *", max_chars=4000, key="justificacion_participantes", on_change=lambda: save_to_session_state("justificacion_participantes", st.session_state["justificacion_participantes"]))

def handle_tier_from_name(id_user, name):
    #df = pd.read_excel(r"C:\Users\AMONTORIOP002\Documents\Merck-Streamlit\src\app\database\Accounts with HCP tiering_ES_2025_01_29.xlsx")
    df = pd.read_excel(r"C:\Users\mcantabela001\Desktop\PROYECTOS\MERCK\Accounts with HCP tiering_ES_2025_01_29.xlsx")
    # Eliminar filas donde 'Nombre de la cuenta' sea NaN
    df = df.dropna(subset=['Nombre de la cuenta'])

    # Reemplazar NaN en 'Especialidad' con 'Ninguna'
    df['Especialidad'] = df['Especialidad'].fillna('Ninguna')

    # Reemplazar NaN en 'Tier' con 0
    df['Tier'] = df['Tier'].fillna(0)

    # Asegurarse de que la columna 'Tier' sea numérica
    df['Tier'] = pd.to_numeric(df['Tier'], errors='coerce').fillna(0)
    
    raw_name = name["result"].split("-")[0].strip()
    print(raw_name)
    tier = df.loc[df["Nombre de la cuenta"] == raw_name, "Tier"]
        
    if not tier.empty:
        return str(int(tier.values[0]))  # Devuelve el Tier encontrado
    return "0"  # Devuelve 0 si el nombre no está en los datos
    

def participantes_section():
    st.header("6. Detalles de los Participantes del Advisory", divider=True)

    if st.button("Agregar participante", use_container_width=True, icon="➕", key="add_participant_button"):
        add_participant()

    index = 0
    # Renderizar los participantes
    for info_user in st.session_state["participantes"]:

        id_user = info_user["id"]

        col_participant, col_remove_participant_individual = st.columns([10,1])
        with col_participant:
            with st.expander(f"Participante {index + 1}", expanded=False, icon="👩‍⚕️"):
                nombre = st_searchbox(
                        #label="Buscador de HCO / HCP *",
                        search_function=search_function,
                        placeholder="Busca un HCO / HCP *",
                        key=f"nombre_{id_user}",
                        edit_after_submit="option",
                        submit_function= lambda x: save_to_session_state("participantes", handle_tier_from_name(id_user, st.session_state[f"nombre_{id_user}"]), id_user, f"tier_{id_user}")
                    )
                
                st.session_state["form_data_advisory_board"]["participantes"][id_user][f"nombre_{id_user}"] = nombre
                    #st.session_state["form_data_advisory_board"]["participantes"][id_user][f"tier_{id_user}"] = handle_tier_from_name(id_user, nombre)
                
                col1, col2 = st.columns(2)
                with col1:
                    
                    dni = st.text_input(
                        f"DNI del participante {index + 1} *", 
                        value=info_user.get(f"dni_{id_user}", ""), 
                        key=f"dni_{id_user}"
                    )
                    st.session_state["form_data_advisory_board"]["participantes"][id_user][f"dni_{id_user}"] = dni

                    centro = st.text_input(
                        f"Centro de trabajo del participante {index + 1} *", 
                        value=info_user.get(f"centro_trabajo_{id_user}", ""), 
                        key=f"centro_trabajo_{id_user}"
                    )
                    st.session_state["form_data_advisory_board"]["participantes"][id_user][f"centro_trabajo_{id_user}"] = centro

                    cobra = st.selectbox(
                        "¿Cobra a través de sociedad? *", 
                        ["No", "Sí"], 
                        key=f"cobra_sociedad_{id_user}"
                    )
                    st.session_state["form_data_advisory_board"]["participantes"][id_user][f"cobra_sociedad_{id_user}"] = cobra
                    
                    st.markdown('<p style="font-size: 14px;">Tiempo de preparación</p>', unsafe_allow_html=True)  
 
                    
                with col2:
                    tier = st.selectbox(
                        f"Tier del participante {index + 1} *", 
                        ["0", "1", "2", "3", "4"], 
                        key=f"tier_{id_user}"
                    )
                    st.session_state["form_data_advisory_board"]["participantes"][id_user][f"tier_{id_user}"] = tier
                    
                    email = st.text_input(
                        f"Email del participante {index + 1} *", 
                        value=info_user.get(f"email_contrato_{id_user}", ""), 
                        key=f"email_{id_user}"
                    )
                    st.session_state["form_data_advisory_board"]["participantes"][id_user][f"email_{id_user}"] = email
                    
                    nombre_sociedad = st.text_input(
                        "Nombre de la sociedad",
                        value = st.session_state["form_data_advisory_board"]["participantes"][id_user][f"nombre_sociedad_{id_user}"] if cobra == "Sí" else "",
                        key=f"nombre_sociedad_{id_user}",
                        disabled= cobra == "No"
                    )
                    st.session_state["form_data_advisory_board"]["participantes"][id_user][f"nombre_sociedad_{id_user}"] = nombre_sociedad
                    
                    st.markdown('<p style="font-size: 14px;">Tiempo de ponencia</p>', unsafe_allow_html=True)  
                col_prep_horas, col_prep_minutos, col_ponencia_horas, col_ponencia_minutos = st.columns(4)

                with col_prep_horas:
                    tiempo_prep_horas = st.number_input(
                        label="Horas",
                        min_value=0,
                        step=1,
                        key=f"preparacion_horas_{id_user}"
                    )
                    st.session_state["form_data_advisory_board"]["participantes"][id_user][f"preparacion_horas_{id_user}"] = tiempo_prep_horas
                    
                with col_prep_minutos:
                    
                    tiempo_prep_minutos = st.selectbox(
                        label="Minutos",
                        options=[0,15,30,45],
                        key=f"preparacion_minutos_{id_user}"
                    )
                    st.session_state["form_data_advisory_board"]["participantes"][id_user][f"preparacion_minutos_{id_user}"] = tiempo_prep_minutos
                    
                with col_ponencia_horas:
                    tiempo_ponencia_horas = st.number_input(
                        label="Horas",
                        min_value=0,
                        step=1,
                        key=f"ponencia_horas_{id_user}"
                    )
                    st.session_state["form_data_advisory_board"]["participantes"][id_user][f"ponencia_horas_{id_user}"] = tiempo_ponencia_horas
                    
                with col_ponencia_minutos:
                    tiempo_ponencia_minutos = st.selectbox(
                        label="Minutos",
                        options=[0,15,30,45],
                        key=f"ponencia_minutos_{id_user}"
                    )
                    
                    st.session_state["form_data_advisory_board"]["participantes"][id_user][f"ponencia_minutos_{id_user}"] = tiempo_ponencia_minutos
                        
                # Obtener valores de tiempo en horas decimales
                tiempo_ponencia_horas = tiempo_ponencia_horas + tiempo_ponencia_minutos / 60
                tiempo_prep_horas = tiempo_prep_horas + tiempo_prep_minutos / 60

                # Obtener tarifa en función del tier
                tarifa = tarifas.get(tier, 0)  # Si no encuentra el tier, usa 0

                # Calcular honorarios
                honorarios = (tiempo_ponencia_horas + tiempo_prep_horas) * tarifa
                
                honorarios = st.number_input(
                    "Honorarios", 
                    value= float(honorarios), 
                    min_value=0.0, 
                    step=0.01, 
                    key=f"honorarios_{id_user}",
                    disabled=True
                )
                st.session_state["form_data_advisory_board"]["participantes"][id_user][f"honorarios_{id_user}"] = honorarios
        index +=1
        with col_remove_participant_individual:
            if st.button("🗑️", key=f"remove_participant_{id_user}", use_container_width=True, type="secondary"):
                if id_user in st.session_state["form_data_advisory_board"]["participantes"].keys():
                    del st.session_state["form_data_advisory_board"]["participantes"][id_user]
                    st.session_state["participantes"] = list(filter(lambda x: x['id'] != id_user, st.session_state["participantes"]))

                st.rerun()
participantes_section()

# Botón para enviar
def button_form():
    if st.button(label="Enviar", use_container_width=True, type="primary"):
        try:
            #if check_mandatory_fields():
            if True:
                doc, st.session_state.path_doc = cd.crear_documento_advisory(st.session_state["form_data_advisory_board"])
                st.toast("Formulario generado correctamente", icon="✔️")
            else:
                st.toast("Debes rellenar todos los campos obligatorios.", icon="❌")
            # Leer el archivo Word y prepararlo para descarga
        except Exception as e:
            traceback.print_exc()
            st.toast(f"Ha ocurrido un problema al generar el formulario -> {e}", icon="❌")

button_form()
st.header("Datos guardados")
st.write(st.session_state["form_data_advisory_board"])
