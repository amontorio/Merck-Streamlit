import pandas as pd
import streamlit as st
from streamlit_searchbox import st_searchbox
from datetime import date
import unicodedata
import uuid
from datetime import time
import auxiliar.create_docx as cd
import traceback
import auxiliar.aux_functions as af
import io


tarifas = {
    "0": 50,  # Ejemplo de valores, cambia según tu lógica
    "1": 75,
    "2": 100,
    "3": 150,
    "4": 200
}


def save_to_session_state(key, value, key_participante=None, field_participante=None):
    """
    Saves a value to the Streamlit session state.

    Parameters:
        key (str): The key under which the value will be saved in the session state.
        value (any): The value to be saved in the session state.
        key_participante (str, optional): The key for the participant, used only if key is "participantes_ss".
        field_participante (str, optional): The field for the participant, used only if key is "participantes_ss".

    Returns:
        None
    """
    if key != "participantes_ss":
        st.session_state[key] = value
        st.session_state["form_data_speaking_services"][key] = value
    else:
        st.session_state[field_participante] = value
        st.session_state["form_data_speaking_services"][key][key_participante][field_participante] = value


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
    return "0" 


def add_ponente():
    id_user = str(uuid.uuid4())
    new_participant = {
        "id": id_user,
        f"nombre_{id_user}": "",
        f"dni_{id_user}": "",
        f"tier_{id_user}": "0",
        f"centro_trabajo_{id_user}": "",
        f"email_{id_user}": "",
        f"cobra_sociedad_{id_user}": "",
        f"nombre_sociedad_{id_user}": "",
        f"honorarios_{id_user}": 0.0,
        f"preparacion_horas_{id_user}": 0,
        f"preparacion_minutos_{id_user}": 0,
        f"ponencia_horas_{id_user}": 0,
        f"ponencia_minutos_{id_user}": 0,
    }
    
    st.session_state["participantes_ss"].append(new_participant)
    st.session_state["id_participantes_ss"].append(id_user)
        

    st.session_state["form_data_speaking_services"]["participantes_ss"][id_user] = new_participant

def remove_last_participant():
    # Eliminar el último participante
    if st.session_state["participantes_ss"]:
        pos = len(st.session_state["participantes_ss"])
        print(st.session_state["form_data_speaking_services"]["participantes_ss"].pop(pos))

        st.session_state["participantes_ss"].pop()

        #st.session_state["participant_index_ss"] -= 1


def ponentes_section():

        if st.button("Agregar ponente", use_container_width=True, icon="➕", key="add_ponente_button"):
            add_ponente()
            print(st.session_state["form_data_speaking_services"]["participantes_ss"])


        index = 0
        # Renderizar los participantes
        for info_user in st.session_state["participantes_ss"]:
            id_user = info_user["id"]
            print(id_user)
            col_participant, col_remove_participant_individual = st.columns([10,1])
            with col_participant:
                with st.expander(f"Ponente {index + 1}", expanded=False, icon="👩‍⚕️"):
                    nombre = st_searchbox(
                            #label="Buscador de HCO / HCP *",
                            search_function=search_function,
                            placeholder="Busca un HCO / HCP *",
                            key=f"nombre_{id_user}",
                            edit_after_submit="option",
                            submit_function= lambda x: (save_to_session_state("participantes_ss", handle_tier_from_name(id_user, st.session_state[f"nombre_{id_user}"]), id_user, f"tier_{id_user}"))                    )

                    st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"nombre_{id_user}"] = nombre
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        
                        dni = st.text_input(
                            f"DNI del participante {index + 1} *", 
                            value=info_user.get(f"dni_{id_user}", ""), 
                            key=f"dni_{id_user}"
                        )
                        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"dni_{id_user}"] = dni

                        centro = st.text_input(
                            f"Centro de trabajo del participante {index + 1} *", 
                            value=info_user.get(f"centro_trabajo_{id_user}", ""), 
                            key=f"centro_trabajo_{id_user}"
                        )
                        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"centro_trabajo_{id_user}"] = centro

                        cobra = st.selectbox(
                            "¿Cobra a través de sociedad? *", 
                            ["No", "Sí"], 
                            key=f"cobra_sociedad_{id_user}"
                        )
                        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"cobra_sociedad_{id_user}"] = cobra
                        
                        st.markdown('<p style="font-size: 14px;">Tiempo de preparación</p>', unsafe_allow_html=True)  
    
                        
                    with col2:
                        tier = st.selectbox(
                            f"Tier del participante {index + 1} *", 
                            ["0", "1", "2", "3", "4"], 
                            key=f"tier_{id_user}"
                        )
                        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"tier_{id_user}"] = tier
                        
                        email = st.text_input(
                            f"Email del participante {index + 1} *", 
                            value=info_user.get(f"email_{id_user}", ""), 
                            key=f"email_{id_user}"
                        )
                        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"email_{id_user}"] = email
                        
                        nombre_sociedad = st.text_input(
                            "Nombre de la sociedad",
                            value = st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"nombre_sociedad_{id_user}"] if cobra == "Sí" else "",
                            key=f"nombre_sociedad_{id_user}",
                            disabled= cobra == "No"
                        )
                        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"nombre_sociedad_{id_user}"] = nombre_sociedad
                        
                        st.markdown('<p style="font-size: 14px;">Tiempo de ponencia</p>', unsafe_allow_html=True)  
                    col_prep_horas, col_prep_minutos, col_ponencia_horas, col_ponencia_minutos = st.columns(4)

                    with col_prep_horas:
                        tiempo_prep_horas = st.number_input(
                            label="Horas",
                            min_value=0,
                            step=1,
                            key=f"preparacion_horas_{id_user}"
                        )
                        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"preparacion_horas_{id_user}"] = tiempo_prep_horas
                        
                    with col_prep_minutos:
                        
                        tiempo_prep_minutos = st.selectbox(
                            label="Minutos",
                            options=[0,15,30,45],
                            key=f"preparacion_minutos_{id_user}"
                        )
                        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"preparacion_minutos_{id_user}"] = tiempo_prep_minutos
                        
                    with col_ponencia_horas:
                        tiempo_ponencia_horas = st.number_input(
                            label="Horas",
                            min_value=0,
                            step=1,
                            key=f"ponencia_horas_{id_user}"
                        )
                        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"ponencia_horas_{id_user}"] = tiempo_ponencia_horas
                        
                    with col_ponencia_minutos:
                        tiempo_ponencia_minutos = st.selectbox(
                            label="Minutos",
                            options=[0,15,30,45],
                            key=f"ponencia_minutos_{id_user}"
                        )
                        
                        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"ponencia_minutos_{id_user}"] = tiempo_ponencia_minutos
                            
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
                    st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"honorarios_{id_user}"] = honorarios
            index +=1
            with col_remove_participant_individual:
                if st.button("🗑️", key=f"remove_participant_ss_{id_user}", use_container_width=True, type="secondary"):
                    if id_user in st.session_state["form_data_speaking_services"]["participantes_ss"].keys():
                        del st.session_state["form_data_speaking_services"]["participantes_ss"][id_user]
                        st.session_state["participantes_ss"] = list(filter(lambda x: x['id'] != id_user, st.session_state["participantes_ss"]))

                    st.rerun()

def button_form(tipo):
        if st.button(label="Enviar", use_container_width=True, type="primary"):
            try:
                #if check_mandatory_fields():
                validacion = af.validar_campos(st.session_state["form_data_speaking_services"], mandatory_fields, dependendent_fields)
                if len(validacion)==0:
                    if tipo == "Reunión Merck Program":
                        doc, st.session_state.path_doc_ss = cd.crear_documento_speaking(st.session_state["form_data_speaking_services"])
                    else:
                        doc, st.session_state.path_doc_ss = cd.crear_documento_speaking_reducido(st.session_state["form_data_speaking_services"])
                    st.session_state.download_enabled_ss = True
                    st.toast("Formulario generado correctamente", icon="✔️")
                else:
                    st.toast("Debes rellenar todos los campos obligatorios.", icon="❌")
                    for msg in validacion:
                    #st.info(msg)
                        st.toast(msg, icon="❌")
                # Leer el archivo Word y prepararlo para descarga
            except Exception as e:
                traceback.print_exc()
                st.toast(f"Ha ocurrido un problema al generar el formulario -> {e}", icon="❌")


def download_document(disabled):
    if st.session_state.path_doc_ss:
        with open(st.session_state.path_doc_ss, "rb") as file:
            st.download_button(
                label="Descargar documento Word",
                data=file,
                file_name="documento_speaking_service.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                icon="📥",
                disabled=disabled
            )
    else:
        st.download_button(
            label="Descargar documento Word",
            data=io.BytesIO(),
            file_name="documento_speaking_service.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            icon="📥",
            disabled=True
        )



################################################################################################################################
### ver si quitar o no
# if "participantes_ss" not in st.session_state:
#     st.session_state["participantes_ss"] = []

# if "id_participantes_ss" not in st.session_state:
#     st.session_state["id_participantes_ss"] = []

# Inicializar estado del formulario en session_state
if "form_data_speaking_services" not in st.session_state:
    field_defaults = {
        "start_date_ss": date.today(),
        "end_date_ss": date.today(),
        "tipo_evento_ss": "Virtual",
        "alojamiento_ponentes": "No",
        "num_noches_ss": 0,
        "hotel_ss": "",
        "desplazamiento_ponentes_ss": "No"
    }

    st.session_state["form_data_speaking_services"] = {}
    #st.session_state["participantes_ss"] = []
    st.session_state["id_participantes_ss"] = []

    st.session_state["download_enabled_ss"] = False
    st.session_state["path_doc_ss"] = None


    for key, value in field_defaults.items():
        save_to_session_state(key, value)

    if "participantes_ss" not in st.session_state:
        st.session_state.participantes_ss = [] 

    # Inicializar participantes en form_data_speaking_services si no existe
    if "participantes_ss" not in st.session_state["form_data_speaking_services"]:
        st.session_state["form_data_speaking_services"]["participantes_ss"] = {}

    # if "participant_index_ss" not in st.session_state:
    #     st.session_state["participant_index_ss"] = 0
    add_ponente()




st.title("Formulario de Speaking Services")

st.header("Reunión Merck", divider=True)
meeting_type = st.selectbox("Tipo de reunión",["Reunión Merck Program", "Paragüas iniciado"])

if meeting_type == "Reunión Merck Program":

    # Lista de parámetros obligatorios
    mandatory_fields = [
    "start_date_ss",
    "end_date_ss",
    "presupuesto_estimado",
    "necesidad_reunion_ss",
    "descripcion_objetivo_ss",
    "desplazamiento_ponentes_ss",
    "alojamiento_ponentes",
    "nombre_evento_ss",
    "descripcion_objetivo_ss",
    "tipo_evento_ss",
    "num_asistentes_totales_ss",
    "publico_objetivo_ss",
    "num_ponentes",
    "criterios_seleccion_ss"
    ]

    # Parámetros dependientes: por ejemplo, si 'alojamiento_ab' es "Sí", se requiere que 'num_noches_ab' y 'hotel_ab' tengan valor.
    dependendent_fields = {
        "alojamiento_ponentes": {
            "condicion": lambda x: x == "Sí",
            "dependientes": ["num_noches_ss", "hotel_ss"]
        },
        "tipo_evento_ss": {
            "condicion": lambda x: x != "Virtual",
            "dependientes": ["sede_ss", "ciudad_ss"]
        }
    }


    st.header("1. Documentos", divider=True)
    st.file_uploader("Agenda del evento *", type=["pdf"], key="doc1_ss", on_change=lambda: save_to_session_state("doc1_ss", st.session_state["doc1_ss"])) 
    st.file_uploader("Contratos inferiores a 1000€: MINUTA reunión previa con Compliance *", type=["pdf"], key="doc2_ss", on_change=lambda: save_to_session_state("doc2_ss", st.session_state["doc2_ss"])) 


    st.header("2. Detalles de la actividad", divider=True)
    col1, col2 = st.columns(2)

    with col1:
        st.number_input("Presupuesto total estimado *", min_value=0, step=1, key="presupuesto_estimado", on_change=lambda: save_to_session_state("presupuesto_estimado", st.session_state["presupuesto_estimado"]))
    with col2:
        st.text_input("Producto asociado", max_chars=255, key="producto_asociado_ss", on_change=lambda: save_to_session_state("producto_asociado_ss", st.session_state["producto_asociado_ss"]))


    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Necesidad de la reunión y resultados esperados *", max_chars=4000, key="necesidad_reunion_ss", help = "Describa la necesidad detectada para organizar esta reunión de la mano de los profesionales seleccionados y cuál el resultado que se espera obtener esperado.", on_change=lambda: save_to_session_state("necesidad_reunion_ss", st.session_state["necesidad_reunion_ss"]))
    with col2:
        st.text_input("Descripción del servicio *", max_chars=4000, key="servicio_ss", on_change=lambda: save_to_session_state("servicio_ss", st.session_state["servicio_ss"]),
                    help = "Ponencia [nombre del evento]")
        ####### meter campo consideraciones!!!!


    st.header("3. Detalles del evento", divider=True)
    col1, col2 = st.columns(2)
    st.text_input("Nombre del evento *", max_chars=255, key="nombre_evento_ss", on_change=lambda: save_to_session_state("nombre_evento_ss", st.session_state["nombre_evento_ss"]))
    st.text_area("Descripción y objetivo *", max_chars=4000, key="descripcion_objetivo_ss", on_change=lambda: save_to_session_state("descripcion_objetivo_ss", st.session_state["descripcion_objetivo_ss"]))

    col1, col2 = st.columns(2)

    with col1:
        start_date_ss = st.date_input("Fecha de inicio del evento *", 
                    value=st.session_state["form_data_speaking_services"]["start_date_ss"],
                    key="start_date_ss", 
                    on_change=lambda: save_to_session_state("start_date_ss", st.session_state["start_date_ss"]))
    with col2:
        st.date_input("Fecha de fin del evento *", 
                    value= start_date_ss if st.session_state["form_data_speaking_services"]["end_date_ss"] < start_date_ss else  st.session_state["form_data_speaking_services"]["end_date_ss"],
                    key="end_date_ss", 
                    min_value = start_date_ss,
                    on_change=lambda: save_to_session_state("end_date_ss", st.session_state["end_date_ss"]))


    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Tipo de evento *", ["Virtual", "Presencial", "Híbrido"], key="tipo_evento_ss", 
                    on_change=lambda: (
                        save_to_session_state("tipo_evento_ss", st.session_state["tipo_evento_ss"]),
                        save_to_session_state("sede_ss", ""),
                        save_to_session_state("ciudad_ss", "")
                    ) if st.session_state["tipo_evento_ss"] == "Virtual" else 
                        save_to_session_state("tipo_evento_ss", st.session_state["tipo_evento_ss"]))
    with col2:
        st.number_input("Nº de asistentes totales *", min_value=0, step=1, key="num_asistentes_totales_ss", help="Ratio obligatorio (5 asistentes por ponente)",
                        on_change=lambda: save_to_session_state("num_asistentes_totales_ss", st.session_state["num_asistentes_totales_ss"]))

        
    col1, col2 = st.columns(2)
    with col1:

            st.text_input(
            "Sede",
            max_chars=255,
            key="sede_ss",
            disabled=st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual",
            value="" if st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual" else st.session_state["form_data_speaking_services"].get("sede_ss", ""),
            on_change=lambda: save_to_session_state("sede_ss", st.session_state["sede_ss"])
        )
    with col2:
        st.text_input(
            "Ciudad",
            max_chars=255,
            key="ciudad_ss",
            disabled=st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual",
            value="" if st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual" else st.session_state["form_data_speaking_services"].get("ciudad_ss", ""),
            on_change=lambda: save_to_session_state("ciudad_ss", st.session_state["ciudad_ss"])
        )

    st.text_input(
            "Público objetivo del programa *",
            max_chars=4000,
            key="publico_objetivo_ss",
            on_change=lambda: save_to_session_state("publico_objetivo_ss", st.session_state["publico_objetivo_ss"])
        )





    st.header("4. Logística de la actividad", divider=True)
    col1, col2 = st.columns(2)

    with col1:
        st.selectbox("¿Desplazamiento de ponentes? *", ["Sí", "No"], key="desplazamiento_ponentes_ss", on_change=lambda: save_to_session_state("desplazamiento_ponentes_ss", st.session_state["desplazamiento_ponentes_ss"]))
    with col2:
        st.selectbox("¿Alojamiento de ponentes? *", ["Sí", "No"], 
                    key="alojamiento_ponentes", 
                    on_change=lambda: (
                                        save_to_session_state("alojamiento_ponentes", st.session_state["alojamiento_ponentes"]),
                                        save_to_session_state("num_noches_ss", 0),
                                        save_to_session_state("hotel_ss", "")
                                    ) if st.session_state["alojamiento_ponentes"] == "No" else 
                                        save_to_session_state("alojamiento_ponentes", st.session_state["alojamiento_ponentes"]))

    col1, col2 = st.columns(2)


    with col1:
        st.number_input("Nº de noches *", 
                        min_value=0, 
                        step=1, 
                        key="num_noches_ss", 
                        disabled=st.session_state["form_data_speaking_services"]["alojamiento_ponentes"] == "No",
                        value= 0 if st.session_state["form_data_speaking_services"]["alojamiento_ponentes"] == "No" else st.session_state["form_data_speaking_services"].get("num_noches_ss", 0),
                        on_change=lambda: save_to_session_state("num_noches_ss", st.session_state["num_noches_ss"]))
                        
    with col2:
        st.text_input("Hotel *", 
                    max_chars=255, 
                    key="hotel_ss",
                    disabled=st.session_state["form_data_speaking_services"]["alojamiento_ponentes"] == "No", 
                    value="" if st.session_state["form_data_speaking_services"]["alojamiento_ponentes"] == "No" else st.session_state["form_data_speaking_services"].get("hotel_ss", ""),
                    on_change=lambda: save_to_session_state("hotel_ss", st.session_state["hotel_ss"]))






    st.header("5. Criterios de selección (Ponentes)", divider=True)
    col1, col2 = st.columns(2)
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Nº de ponentes *", min_value=0, step=1, key="num_ponentes", help="Asegúrese de que  se contrate la cantidad necesaria de ponentes para brindar los servicios que satisfacen las necesidades comerciales legítimas.", on_change=lambda: save_to_session_state("num_ponentes", st.session_state["num_ponentes"]))
    with col2:
        st.multiselect(
            "Criterios de selección *",
            [
                "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Kol Global", "Experiencia como ponente", "Experiencia como profesor",
                "Experiencia clínica en tema a tratar", "Especialista en tema a tratar",
                "Criterios adicionales: campo abierto"
            ],
            key="criterios_seleccion_ss",
            on_change=lambda: save_to_session_state("criterios_seleccion_ss", st.session_state["criterios_seleccion_ss"])
        )


    #### seccion última
    st.header("6. Detalles de Ponentes", divider=True)
    ponentes_section()

    # Estado inicial para el botón de descargar
    st.session_state.download_enabled_ss = False
    button_form(meeting_type)


else:

    mandatory_fields = [
        "start_date_ss",
        "end_date_ss",
        "nombre_evento_ss",
        "tipo_evento_ss"
    ]

    # Parámetros dependientes: por ejemplo, si 'alojamiento_ab' es "Sí", se requiere que 'num_noches_ab' y 'hotel_ab' tengan valor.
    dependendent_fields = {
        "tipo_evento_ss": {
            "condicion": lambda x: x != "Virtual",
            "dependientes": ["sede_ss", "ciudad_ss"]
        }
    }

    #st.header("Caso Paragüas", divider=True)
    st.header("Detalles del Evento", divider=True)
    col1, col2 = st.columns(2)
    st.text_input("Nombre del evento *", max_chars=255, key="nombre_evento_ss", on_change=lambda: save_to_session_state("nombre_evento_ss", st.session_state["nombre_evento_ss"]))
    #st.text_area("Descripción y objetivo *", max_chars=4000, key="descripcion_objetivo_ss", on_change=lambda: save_to_session_state("descripcion_objetivo_ss", st.session_state["descripcion_objetivo_ss"]))

    col1, col2 = st.columns(2)

    with col1:
        start_date_ss = st.date_input("Fecha de inicio del evento *", 
                    value=st.session_state["form_data_speaking_services"]["start_date_ss"],
                    key="start_date_ss", 
                    on_change=lambda: save_to_session_state("start_date_ss", st.session_state["start_date_ss"]))
    with col2:
        st.date_input("Fecha de fin del evento *", 
                    value= start_date_ss if st.session_state["form_data_speaking_services"]["end_date_ss"] < start_date_ss else  st.session_state["form_data_speaking_services"]["end_date_ss"],
                    key="end_date_ss", 
                    min_value = start_date_ss,
                    on_change=lambda: save_to_session_state("end_date_ss", st.session_state["end_date_ss"]))
        
    st.selectbox("Tipo de evento *", ["Virtual", "Presencial", "Híbrido"], key="tipo_evento_ss", 
                    on_change=lambda: (
                        save_to_session_state("tipo_evento_ss", st.session_state["tipo_evento_ss"]),
                        save_to_session_state("sede_ss", ""),
                        save_to_session_state("ciudad_ss", "")
                    ) if st.session_state["tipo_evento_ss"] == "Virtual" else 
                        save_to_session_state("tipo_evento_ss", st.session_state["tipo_evento_ss"]))

        
    col1, col2 = st.columns(2)
    with col1:

            st.text_input(
            "Sede",
            max_chars=255,
            key="sede_ss",
            disabled=st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual",
            value="" if st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual" else st.session_state["form_data_speaking_services"].get("sede_ss", ""),
            on_change=lambda: save_to_session_state("sede_ss", st.session_state["sede_ss"])
        )
    with col2:
        st.text_input(
            "Ciudad",
            max_chars=255,
            key="ciudad_ss",
            disabled=st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual",
            value="" if st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual" else st.session_state["form_data_speaking_services"].get("ciudad_ss", ""),
            on_change=lambda: save_to_session_state("ciudad_ss", st.session_state["ciudad_ss"])
        )

    st.header("Detalles de Ponentes", divider=True)
    ponentes_section()
    st.session_state.download_enabled_ss = False
    button_form(meeting_type)
    disabled = not st.session_state.download_enabled_ss
    download_document(disabled)


st.write(st.session_state["form_data_speaking_services"])