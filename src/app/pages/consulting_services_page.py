import pandas as pd
import streamlit as st
from streamlit_searchbox import st_searchbox
from datetime import date
import unicodedata
import uuid
import auxiliar.aux_functions as af
import auxiliar.create_docx as cd
import traceback
import io

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

    
    return errores


# Lista de parámetros obligatorios
mandatory_fields = [
]

# Parámetros dependientes: por ejemplo, si 'alojamiento' es "Sí", se requiere que 'num_noches' y 'hotel' tengan valor.
dependendent_fields = {
    "alojamiento": {
        "condicion": lambda x: x == "Sí",
        "dependientes": ["num_noches", "hotel"] #si es si, serán estos campos
    },
    "tipo_evento": {
        "condicion": lambda x: x != "Virtual",
        "dependientes": ["sede", "ciudad"]
    }
}

def save_to_session_state(key, value, key_participante=None, field_participante=None):
    if key != "participantes_cs":
        st.session_state[key] = value
        st.session_state["form_data_consulting_services"][key] = value
    else:
        st.session_state[field_participante] = value
        st.session_state["form_data_consulting_services"][key][key_participante][field_participante] = value

def add_participant():
    # Añadir un nuevo participante con campos inicializados
    id_user = str(uuid.uuid4())
    new_participant = {
        "id": id_user,
        f"nombre_{id_user}": "",
        f"dni_{id_user}": "",
        f"tier_{id_user}": "0",
        f"centro_trabajo_{id_user}": "",
        f"email_{id_user}": "",
        f"cobra_sociedad_{id_user}": "No",
        f"nombre_sociedad_{id_user}": "",
        f"honorarios_{id_user}": 0.0,
        f"preparacion_horas_{id_user}": 0,
        f"preparacion_minutos_{id_user}": 0,
        f"ponencia_horas_{id_user}": 0,
        f"ponencia_minutos_{id_user}": 0,
    }
    
    st.session_state["participantes_cs"].append(new_participant)
    
    # Inicializar participantes_cs en form_data_consulting_services si no existe
    if "participantes_cs" not in st.session_state["form_data_consulting_services"]:
        st.session_state["form_data_consulting_services"]["participantes_cs"] = {}
        
    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user] = new_participant

# Inicializar estado del formulario en session_state
if "form_data_consulting_services" not in st.session_state:
    field_defaults = {
        "nombre_necesidades_cs": "",
        "start_date_cs": date.today(),
        "end_date_cs": date.today(),
        "presupuesto_estimado_cs": 0.0,
        "producto_asociado_cs": "",
        "estado_aprobacion_cs": "N/A",
        "necesidad_reunion_cs": "",
        "descripcion_servicio_cs": "",
        "numero_consultores_cs": 0,
        "justificacion_numero_participantes_cs": "",
        "criterios_seleccion_cs": []
    }

    st.session_state["form_data_consulting_services"] = {}
    
    st.session_state["download_enabled_cs"] = False
    st.session_state["path_doc_cs"] = None
    
    for key, value in field_defaults.items():
        save_to_session_state(key, value)

    if "participantes_cs" not in st.session_state:
        st.session_state.participantes_cs = [] 
        
    add_participant()
    
st.title("Formulario de Consulting Services")
st.header("1. Documentos a adjuntar", divider=True)
st.file_uploader("Agenda o Guión  del evento *", type=["pdf"], key="doc1", on_change=lambda: save_to_session_state("doc1", st.session_state["doc1"]))

st.header("2. Declaración de necesidades", divider=True)
col1, col2 = st.columns(2)

with col1:
    st.text_input("Nombre *",
                  max_chars=255,
                  key="nombre_necesidades_cs",
                  value= st.session_state["form_data_consulting_services"]["nombre_necesidades_cs"] if "nombre_necesidades_cs" in st.session_state["form_data_consulting_services"] else "",
                  on_change=lambda: save_to_session_state("nombre_necesidades_cs", st.session_state["nombre_necesidades_cs"]))
    
    st.date_input("Fecha de inicio *",
                  value=st.session_state["form_data_consulting_services"]["start_date_cs"],
                  key="start_date_cs",
                  on_change=lambda: save_to_session_state("start_date_cs", st.session_state["start_date_cs"]))
    
    st.text_input("Producto asociado *",
                  max_chars=255,
                  key="producto_asociado_cs",
                  value= st.session_state["form_data_consulting_services"]["producto_asociado_cs"] if "producto_asociado_cs" in st.session_state["form_data_consulting_services"] else "",
                  on_change=lambda: save_to_session_state("producto_asociado_cs", st.session_state["producto_asociado_cs"]))
    
    st.text_area("Necesidad de la reunión y resultados esperados *",
                 max_chars=4000,
                 key="necesidad_reunion_cs",
                 help="Describa la necesidad de obtener información de los consultores y el propósito para el cual se utilizará dicha información.",
                 value= st.session_state["form_data_consulting_services"]["necesidad_reunion_cs"] if "necesidad_reunion_cs" in st.session_state["form_data_consulting_services"] else "",
                 on_change=lambda: save_to_session_state("necesidad_reunion_cs", st.session_state["necesidad_reunion_cs"]))
    
with col2:
    st.number_input("Presupuesto total estimado *",
                    min_value=0.0,
                    step=100.00,
                    key="presupuesto_estimado_cs",
                    help="Ratio obligatorio (5 asistentes por ponente)",
                    value= st.session_state["form_data_consulting_services"]["presupuesto_estimado_cs"] if "presupuesto_estimado_cs" in st.session_state["form_data_consulting_services"] else 0.0,
                    on_change=lambda: save_to_session_state("presupuesto_estimado_cs", st.session_state["presupuesto_estimado_cs"]))
    
    st.date_input("Fecha de fin *",
                  value=st.session_state["form_data_consulting_services"]["end_date_cs"],
                  key="end_date_cs",
                  on_change=lambda: save_to_session_state("end_date_cs", st.session_state["end_date_cs"]))
    
    st.selectbox("Estado de la aprobación",
                 ["N/A", "Aprobado", "No Aprobado"],
                 key="estado_aprobacion_cs",
                 index= ["N/A", "Aprobado", "No Aprobado"].index(st.session_state["form_data_consulting_services"]["estado_aprobacion_cs"]) if "estado_aprobacion_cs" in st.session_state["form_data_consulting_services"] else 0,
                 on_change=lambda: save_to_session_state("estado_aprobacion_cs", st.session_state["estado_aprobacion_cs"]))
    
    st.text_area("Descripción del servicio *",
                 max_chars=4000,
                 key="descripcion_servicio_cs",
                 value= st.session_state["form_data_consulting_services"]["descripcion_servicio_cs"] if "descripcion_servicio_cs" in st.session_state["form_data_consulting_services"] else "",
                 on_change=lambda: save_to_session_state("descripcion_servicio_cs", st.session_state["descripcion_servicio_cs"]))

st.header("3. Criterios del destinatario", divider=True)
col3, col4 = st.columns(2)

with col3:
    st.number_input("Nº de consultores *", 
                    min_value=0, 
                    step=1, 
                    key="numero_consultores_cs",
                    value= st.session_state["form_data_consulting_services"]["numero_consultores_cs"] if "numero_consultores_cs" in st.session_state["form_data_consulting_services"] else 0,
                    on_change=lambda: (
                     save_to_session_state("numero_consultores_cs", st.session_state["numero_consultores_cs"]),
                     save_to_session_state("justificacion_numero_participantes_cs", ""),
                 ) if st.session_state["numero_consultores_cs"] <= 1 else 
                     save_to_session_state("numero_consultores_cs", st.session_state["numero_consultores_cs"])
                     )
    
with col4:
    st.multiselect(
        "Criterios de selección *",
        [
            "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Kol Global", "Experiencia como ponente", "Experiencia como consultor",
            "Experiencia como profesor", "Experiencia clínica en tema a tratar", "Especialista en tema a tratar",
            "Criterios adicionales: campo abierto"
        ],
        key="criterios_seleccion_cs",
        default=st.session_state["form_data_consulting_services"]["criterios_seleccion_cs"] if "criterios_seleccion_cs" in st.session_state["form_data_consulting_services"] else [],
        on_change=lambda: save_to_session_state("criterios_seleccion_cs", st.session_state["criterios_seleccion_cs"]))

st.text_area("Justificación de número de participantes_cs *", 
             max_chars=4000, 
             key="justificacion_numero_participantes_cs", 
             value="" if st.session_state["form_data_consulting_services"]["numero_consultores_cs"] <=1 else st.session_state["form_data_consulting_services"].get("justificacion_numero_participantes_cs", ""), 
             disabled=st.session_state["form_data_consulting_services"]["numero_consultores_cs"] <= 1, 
             on_change=lambda: save_to_session_state("justificacion_numero_participantes_cs", st.session_state["justificacion_numero_participantes_cs"]))


def participantes_section():
    st.header("6. Detalles de los participantes_cs del Advisory", divider=True)

    if st.button("Agregar participante", use_container_width=True, icon="➕", key="add_participant_button"):
        add_participant()

    index = 0
    # Renderizar los participantes_cs
    for info_user in st.session_state["participantes_cs"]:

        id_user = info_user["id"]

        col_participant, col_remove_participant_individual = st.columns([10,1])
        with col_participant:
            with st.expander(f"Participante {index + 1}", expanded=False, icon="👩‍⚕️"):
                nombre = st_searchbox(
                        #label="Buscador de HCO / HCP *",
                        search_function=af.search_function,
                        placeholder="Busca un HCO / HCP *",
                        key=f"nombre_{id_user}",
                        edit_after_submit="option",
                        default_searchterm=info_user.get(f"nombre_{id_user}", ""),
                        #submit_function=print(st.session_state[f"nombre_{id_user}"])
                        submit_function= lambda x: save_to_session_state("participantes_cs", af.handle_tier_from_name(st.session_state[f"nombre_{id_user}"]), id_user, f"tier_{id_user}")
                    )

                st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"nombre_{id_user}"] = nombre
                
                col1, col2 = st.columns(2)
                with col1:
                    
                    dni = st.text_input(
                        f"DNI del participante {index + 1} *", 
                        value=info_user.get(f"dni_{id_user}", ""), 
                        key=f"dni_{id_user}"
                    )
                    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"dni_{id_user}"] = dni

                    centro = st.text_input(
                        f"Centro de trabajo del participante {index + 1} *", 
                        value=info_user.get(f"centro_trabajo_{id_user}", ""), 
                        key=f"centro_trabajo_{id_user}"
                    )
                    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"centro_trabajo_{id_user}"] = centro

                    cobra = st.selectbox(
                        "¿Cobra a través de sociedad? *", 
                        ["No", "Sí"], 
                        key=f"cobra_sociedad_{id_user}",
                        index= ["No", "Sí"].index(st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"cobra_sociedad_{id_user}"]) if f"cobra_sociedad_{id_user}" in st.session_state["form_data_consulting_services"]["participantes_cs"][id_user] else 0

                    )
                    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"cobra_sociedad_{id_user}"] = cobra
                    
                    st.markdown('<p style="font-size: 14px;">Tiempo de preparación</p>', unsafe_allow_html=True)  
 
                    
                with col2:
                    tier = st.selectbox(
                        f"Tier del participante {index + 1} *", 
                        ["0", "1", "2", "3", "4"],
                        key=f"tier_{id_user}",
                        index= ["0", "1", "2", "3", "4"].index(st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"tier_{id_user}"]) if f"tier_{id_user}" in st.session_state["form_data_consulting_services"]["participantes_cs"][id_user] else 0,

                    )
                    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"tier_{id_user}"] = tier
                    
                    email = st.text_input(
                        f"Email del participante {index + 1} *", 
                        value=info_user.get(f"email_{id_user}", ""), 
                        key=f"email_{id_user}"
                    )
                    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"email_{id_user}"] = email
                    
                    nombre_sociedad = st.text_input(
                        "Nombre de la sociedad",
                        value = st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"nombre_sociedad_{id_user}"] if cobra == "Sí" else "",
                        key=f"nombre_sociedad_{id_user}",
                        disabled= cobra == "No"
                    )
                    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"nombre_sociedad_{id_user}"] = nombre_sociedad
                    
                    st.markdown('<p style="font-size: 14px;">Tiempo de ponencia</p>', unsafe_allow_html=True)  
                col_prep_horas, col_prep_minutos, col_ponencia_horas, col_ponencia_minutos = st.columns(4)

                with col_prep_horas:
                    tiempo_prep_horas = st.number_input(
                        label="Horas",
                        min_value=0,
                        step=1,
                        key=f"preparacion_horas_{id_user}",
                        value= st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"preparacion_horas_{id_user}"] if f"preparacion_horas_{id_user}" in st.session_state["form_data_consulting_services"]["participantes_cs"][id_user] else 0,  
                    )
                    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"preparacion_horas_{id_user}"] = tiempo_prep_horas
                    
                with col_prep_minutos:
                    
                    tiempo_prep_minutos = st.selectbox(
                        label="Minutos",
                        options=[0,15,30,45],
                        key=f"preparacion_minutos_{id_user}",
                        index= [0,15,30,45].index(st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"preparacion_minutos_{id_user}"]) if f"preparacion_minutos_{id_user}" in st.session_state["form_data_consulting_services"]["participantes_cs"][id_user] else 0,
                    )
                    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"preparacion_minutos_{id_user}"] = tiempo_prep_minutos
                    
                with col_ponencia_horas:
                    tiempo_ponencia_horas = st.number_input(
                        label="Horas",
                        min_value=0,
                        step=1,
                        key=f"ponencia_horas_{id_user}",
                        value= st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"ponencia_horas_{id_user}"] if f"ponencia_horas_{id_user}" in st.session_state["form_data_consulting_services"]["participantes_cs"][id_user] else 0,

                    )
                    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"ponencia_horas_{id_user}"] = tiempo_ponencia_horas
                    
                with col_ponencia_minutos:
                    tiempo_ponencia_minutos = st.selectbox(
                        label="Minutos",
                        options=[0,15,30,45],
                        key=f"ponencia_minutos_{id_user}",
                        index= [0,15,30,45].index(st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"ponencia_minutos_{id_user}"]) if f"ponencia_minutos_{id_user}" in st.session_state["form_data_consulting_services"]["participantes_cs"][id_user] else 0,
                    )
                    
                    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"ponencia_minutos_{id_user}"] = tiempo_ponencia_minutos
                        
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
                st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"honorarios_{id_user}"] = honorarios
        index +=1
        with col_remove_participant_individual:
            if st.button("🗑️", key=f"remove_participant_{id_user}", use_container_width=True, type="secondary"):
                if id_user in st.session_state["form_data_consulting_services"]["participantes_cs"].keys():
                    del st.session_state["form_data_consulting_services"]["participantes_cs"][id_user]
                    st.session_state["participantes_cs"] = list(filter(lambda x: x['id'] != id_user, st.session_state["participantes_cs"]))

                st.rerun()
participantes_section()

st.write(st.session_state["form_data_consulting_services"])