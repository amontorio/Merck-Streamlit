import streamlit as st
import pandas as pd
from datetime import date, datetime
import time
import traceback
import io
import re
import time

import auxiliar.create_docx as cd
import model.llm_sponsorship_event as llm_se
import auxiliar.aux_functions as af

from dotenv import load_dotenv
load_dotenv()

LARGE_MAX_CHARS = 4000
MEDIUM_MAX_CHARS = 255

def save_to_session_state(key, value):
    if key not in ["documentosubido_1_event", "documentosubido_2_event", "documentosubido_3_event"]:
        st.session_state[key] = value
    st.session_state["form_data_event"][key] = value
    
def handle_invoke_chain_event_description():
    print("Inicio Chain Event Description")
    res = llm_se.invoke_chain_event_description(st.session_state["form_data_event"]["event_name"],
                                          st.session_state["form_data_event"]["start_date"],
                                          st.session_state["form_data_event"]["end_date"],
                                          st.session_state["form_data_event"]["venue"],
                                          st.session_state["form_data_event"]["city"],
                                          st.session_state["form_data_event"]["organization_name"],
                                          st.session_state["form_data_event"]["event_objetive"])
    print("Fin Chain Event Description")
    st.session_state.res_generate_event_description = res  
    save_to_session_state("short_description", st.session_state.res_generate_event_description)


def validacion_completa_email():
        save_to_session_state("signer_email_copy", st.session_state["signer_email"])
        mail = st.session_state.get("signer_email", "")
        st.session_state["email_correcto"] = True
        try: 
            #patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            tlds_validos = ['com', 'org', 'net', 'es', 'edu', 'gov', 'info', 'biz']
            tlds_pattern = '|'.join(tlds_validos)
            patron = rf'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?:{tlds_pattern})$'

            matcheo = re.match(patron, mail) 
            if matcheo == None and mail !="":
                st.session_state["email_correcto"] = False

        except:
            if mail != "":
                st.session_state["email_correcto"] = False

        if st.session_state["email_correcto"] == True:
            save_to_session_state("signer_email", st.session_state["signer_email"])
        else:
            st.session_state["form_data_event"]["signer_email"] = ""


def handle_fecha_inicio():
    save_to_session_state("start_date", st.session_state["start_date"])
    if st.session_state["start_date"] >= st.session_state["end_date"]:
        save_to_session_state("end_date", st.session_state["start_date"]) 

# Inicializar estado del formulario en session_state
if "form_data_event" not in st.session_state:
    field_defaults = {
        "event_name": "",
        "event_type": "Virtual",
        "start_date": date.today(),
        "end_date": date.today(),
        "venue": "",
        "city": "",
        "num_attendees": 0,
        "attendee_profile": "",
        "event_objetive": "",
        "amount": 0.0,
        "payment_type": "Pago directo",
        "name_st": "",
        "associated_product": "",
        "short_description": "",
        "benefits": "",
        "exclusive_sponsorship": "No",
        "recurrent_sponsorship": "No",
        "recurrent_text": "",
        "organization_name": "",
        "organization_cif": "",
        "signer_first_name": "",
        "signer_position": "",
        "signer_email": "",
        "signer_email_copy": "",
        "documentosubido_1_event": None,
        "documentosubido_2_event": None,
        "documentosubido_3_event": None
    }
    
    st.session_state["form_data_event"] = {}
    
    for key, value in field_defaults.items():
        save_to_session_state(key, value)
        
    st.session_state["res_generate_event_description"] = ""
    st.session_state["download_enabled"] = False
    st.session_state["path_doc"] = None
    st.session_state["email_correcto"] = True
    st.session_state["signer_email"] = ""
    st.session_state["signer_email_copy"] = ""

mandatory_fields = [
    "event_name",
    "event_type",
    "start_date",
    "end_date",
    "num_attendees",
    "attendee_profile",
    "event_objetive",
    "amount",
    "payment_type",
    "short_description",
    "benefits",
    "exclusive_sponsorship",
    "recurrent_sponsorship",
    "organization_name",
    "organization_cif",
    "signer_first_name",
    "signer_position",
    "signer_email",
    "documentosubido_1_event",
    "documentosubido_2_event",
    "event_objetive"
]

dependendent_fields = {
    "payment_type": {
        "condicion": lambda x: x != "Pago directo",
        "dependientes": ["name_st"]
    },
    "recurrent_sponsorship": {
        "condicion": lambda x: x == "Sí",
        "dependientes": ["recurrent_text"]
    },
    "exclusive_sponsorship": {
        "condicion": lambda x: x != "No",
        "dependientes": ["documentosubido_3_event"]
    },
    "event_type": {
            "condicion": lambda x: x != "Virtual",
            "dependientes": ["city", "venue"]
        }
}

if "signer_email" not in st.session_state:
    if "signer_email" in st.session_state["form_data_event"]:
        st.session_state["signer_email"] = st.session_state["form_data_event"]["signer_email"]
    else:
        st.session_state["signer_email"] = ""

if "signer_email_copy" not in st.session_state:
    if "signer_email_copy" in st.session_state["form_data_event"]:
        st.session_state["signer_email_copy"] = st.session_state["form_data_event"]["signer_email_copy"] 
    else:
        st.session_state["signer_email_copy"] = ""
        st.session_state["form_data_event"]["signer_email_copy"] = ""

if "venue" not in st.session_state:
    if "venue" in st.session_state["form_data_event"]:
        st.session_state["venue"] = st.session_state["form_data_event"]["venue"]
    else:
        st.session_state["venue"] = ""

if "city" not in st.session_state:
    if "city" in st.session_state["form_data_event"]:
        st.session_state["city"] = st.session_state["form_data_event"]["city"]
    else:
        st.session_state["city"] = ""

if "errores_event" not in st.session_state:
    st.session_state.errores_event = False

if "errores_generales_event" not in st.session_state:
    st.session_state.errores_generales_event = []

if "avisos_ia_event" not in st.session_state:
    st.session_state.avisos_ia_event = {}

if "errores_ia_event" not in st.session_state:
    st.session_state.errores_ia_event = []

validar_ia ={
        "validar_sede_location": {"start_date":"start_date", 
                                  "end_date": "end_date", 
                                  "sede": "venue"},
        "validar_sede_venue": {"sede": "venue"}
    }

campos_avisos_ia ={
        "validar_contraprestaciones": {"contraprestaciones":"benefits"}
    }

def check_mandatory_fields():
    """Check if all mandatory fields have valid values and return missing fields"""
    fields_to_check = list(mandatory_fields)
    missing_fields = []
    error_messages = []

    # If virtual event, venue and city are not mandatory
    if st.session_state["form_data_event"].get("event_type", "") == "Virtual":
        fields_to_check.remove("venue") 
        fields_to_check.remove("city")
    else:
        # Validate venue and city fields for non-virtual events
        if not st.session_state["form_data_event"].get("venue") or not st.session_state["form_data_event"].get("city"):
            error_messages.append("Para eventos presenciales o híbridos, la sede y ciudad son obligatorias")

    # For payment type validation
    if st.session_state["form_data_event"]["payment_type"] == "Pago directo":
        # Remove ST fields from validation when payment is direct
        fields_to_check.remove("name_st")
    else:
        # Validate ST fields when payment is through ST
        if not st.session_state["form_data_event"].get("name_st"):
            error_messages.append("Falta el nombre y/o el correo de la secretaría técnica")
        
    if st.session_state["form_data_event"]["recurrent_sponsorship"] == "Sí":
        # Validate recurrent text is provided when sponsorship is recurrent
        if not st.session_state["form_data_event"].get("recurrent_text"):
            error_messages.append("Faltan los detalles del patrocinio recurrente")
    else:
        # Remove recurrent text validation when not recurrent
        fields_to_check.remove("recurrent_text")

    # Check each field and collect missing ones
    for field in fields_to_check:
        value = st.session_state["form_data_event"].get(field, "")
        if isinstance(value, (int, float)):
            value = str(value)
        if not value or not str(value).strip():
            missing_fields.append(field)

    # Add missing fields error if any
    if missing_fields:
        missing_fields_str = ", ".join(missing_fields)
        error_messages.append(f"Los siguientes campos son obligatorios: {missing_fields_str}")

    # Show all errors in a single message if there are any
    if error_messages:
        st.error("\n\n".join(error_messages), icon="🚨")
        return False

    return True

def save_form_data_event():
    """Saves form data into a DataFrame"""
    data = {
        "event_name": st.session_state["form_data_event"].get("event_name", ""),
        "event_type": st.session_state["form_data_event"].get("event_type", ""),
        "start_date": st.session_state["form_data_event"].get("start_date", ""),
        "end_date": st.session_state["form_data_event"].get("end_date", ""),
        "venue": st.session_state["form_data_event"].get("venue", ""),
        "city": st.session_state["form_data_event"].get("city", ""),
        "num_attendees": st.session_state["form_data_event"].get("num_attendees", 0),
        "attendee_profile": st.session_state["form_data_event"].get("attendee_profile", ""),
        "event_objetive": st.session_state["form_data_event"].get("event_objetive", ""),
        "amount": st.session_state["form_data_event"].get("amount", 0.0),
        "payment_type": st.session_state["form_data_event"].get("payment_type", ""),
        "name_st": st.session_state["form_data_event"].get("name_st", ""),
        "associated_product": st.session_state["form_data_event"].get("associated_product", ""),
        "short_description": st.session_state["form_data_event"].get("short_description", ""),
        "benefits": st.session_state["form_data_event"].get("benefits", ""),
        "exclusive_sponsorship": st.session_state["form_data_event"].get("exclusive_sponsorship", ""),
        "recurrent_sponsorship": st.session_state["form_data_event"].get("recurrent_sponsorship", ""),
        "recurrent_text": st.session_state["form_data_event"].get("recurrent_text", ""),
        "organization_name": st.session_state["form_data_event"].get("organization_name", ""),
        "organization_cif": st.session_state["form_data_event"].get("organization_cif", ""),
        "signer_first_name": st.session_state["form_data_event"].get("signer_first_name", ""),
        "signer_position": st.session_state["form_data_event"].get("signer_position", ""),
        "signer_email": st.session_state["form_data_event"].get("signer_email", ""),
        "submission_date": datetime.now(),
        "documentosubido_1_event": st.session_state["form_data_event"].get("documentosubido_1_event", None),
        "documentosubido_2_event": st.session_state["form_data_event"].get("documentosubido_2_event", None),
        "documentosubido_3_event": st.session_state["form_data_event"].get("documentosubido_3_event", None)
    }
    
    df = pd.DataFrame([data])
    return df


# Sección de documentos a adjuntar
af.show_main_title(title="Sponsorship of Event", logo_size=200)

# Sección Detalles del Evento
def crear_detalles_evento():
    crear_nombre_y_tipo()
    crear_fechas()
    crear_ubicacion()
    crear_asistentes()

def crear_nombre_y_tipo():
    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            "Nombre del evento *",
            placeholder="Escribe el nombre del evento",
            value=st.session_state["form_data_event"]["event_name"],
            help="Introduce el nombre del evento",
            max_chars=MEDIUM_MAX_CHARS,
            key="event_name",
            on_change=lambda: save_to_session_state("event_name", st.session_state["event_name"])
        )
    with col2:
        event = st.selectbox(
            "Tipo de evento *",
            options=["Virtual", "Presencial", "Híbrido"],
            help="""Selecciona el tipo de evento que deseas realizar. 
                \n- **Virtual**: Evento realizado completamente en línea.
                \n- **Presencial**: Evento llevado a cabo físicamente en una ubicación específica.
                \n- **Híbrido**: Combina elementos de eventos virtuales y presenciales.""",
            key="event_type",
            index = ["Virtual", "Presencial", "Híbrido"].index(st.session_state["form_data_event"]["event_type"]) if "event_type" in st.session_state["form_data_event"] else 0,
            on_change=lambda: (
                        save_to_session_state("event_type", st.session_state["event_type"]),
                        save_to_session_state("venue", ""),
                        save_to_session_state("city", "")
                    ) if st.session_state["event_type"] == "Virtual" else 
                        save_to_session_state("event_type", st.session_state["event_type"]))
        
        

def crear_fechas():
    col3, col4 = st.columns(2)
    with col3:
        st.date_input("Fecha de inicio del evento *", 
                                   value=st.session_state["form_data_event"]["start_date"], 
                                   key="start_date", 
                                   on_change= handle_fecha_inicio, 
                                   format = "DD/MM/YYYY")
    with col4:
        st.date_input("Fecha de fin del evento *", 
                      value= st.session_state["form_data_event"]["start_date"] if st.session_state["form_data_event"]["end_date"] < st.session_state["form_data_event"]["start_date"] else st.session_state["form_data_event"]["end_date"],
                      min_value = st.session_state["form_data_event"]["start_date"],
                      key="end_date", 
                      on_change=lambda: save_to_session_state("end_date", st.session_state["end_date"]),
                      format = "DD/MM/YYYY")

    # if st.session_state.start_date > st.session_state.end_date:
    #     st.error("La fecha de inicio debe ser menor o igual a la fecha de fin.")

def crear_ubicacion():
    is_virtual = st.session_state["form_data_event"]["event_type"] == "Virtual"
    venue_value = "" if is_virtual else st.session_state["form_data_event"]["venue"]
    city_value = "" if is_virtual else st.session_state["form_data_event"]["city"]
    
    st.text_input(
        "Sede",
        disabled=is_virtual,
        value=venue_value,
        help="Indica el nombre de la sede",
        max_chars=MEDIUM_MAX_CHARS,
        key="venue",
        on_change=lambda: save_to_session_state("venue", st.session_state["venue"])
    )
    st.text_input(
        "Ciudad", 
        disabled=is_virtual,
        value=city_value,
        help="Indica la ciudad en la que se encuentra la sede",
        max_chars=MEDIUM_MAX_CHARS, 
        key="city",
        on_change=lambda: save_to_session_state("city", st.session_state["city"])
    )

def crear_asistentes():
    col5, col6 = st.columns(2, vertical_alignment="center")
    with col5:
        st.number_input(
            "Número de asistentes *",
            min_value=0,
            step=1, 
            value=st.session_state["form_data_event"]["num_attendees"],
            key="num_attendees",
            on_change=lambda: save_to_session_state("num_attendees", st.session_state["num_attendees"])
        )
    with col6:
        st.text_area(
            "Perfil de los asistentes *",
            max_chars=MEDIUM_MAX_CHARS,
            value=st.session_state["form_data_event"]["attendee_profile"],
            key="attendee_profile",
            on_change=lambda: save_to_session_state("attendee_profile", st.session_state["attendee_profile"])
        )

     
@st.fragment()
def validate_event_objetive(objective_text):
    """Validate the event objective text."""
    if not objective_text:
        return ""
    
    time.sleep(3)  # Simulates validation
    has_event_name = "nombre del evento" in objective_text.lower()
    color = "green" if has_event_name else "red"
    message = "El texto es correcto." if has_event_name else "El objetivo debe incluir el nombre del evento."
    return f'<p style="color:{color};">{message}</p>'

@st.fragment()
def display_objective_field():
    """Display and handle the event objective text area."""
    if 'prev_event_objetive' not in st.session_state:
        st.session_state.prev_event_objetive = ""
    
    st.text_area(
        "Descripción y objetivo del evento *", 
        max_chars=LARGE_MAX_CHARS,
        value=st.session_state["form_data_event"]["event_objetive"],
        key="event_objetive",
        on_change=lambda: save_to_session_state("event_objetive", st.session_state["event_objetive"])
    )

    if False:
        if st.session_state.event_objetive != st.session_state.prev_event_objetive:
            with st.spinner("Revisando objetivo..."):
                message = validate_event_objetive(st.session_state.event_objetive)
                st.markdown(message, unsafe_allow_html=True)
            st.session_state.prev_event_objetive = st.session_state.event_objetive

st.header("1. Detalles del Evento", divider=True)
with st.container(border=True):     
    crear_detalles_evento()
    display_objective_field()


# Sección Información del Firmante
@st.fragment()
def crear_detalles_firmante():
    st.header("2. Detalles del Organizador", divider=True)
    with st.container(border=True):
        col13, col14 = st.columns(2)
        with col13:
            st.text_input("Nombre de la organización *", value=st.session_state["form_data_event"]["organization_name"], key="organization_name", on_change=lambda: save_to_session_state("organization_name", st.session_state["organization_name"]))
        with col14:
            st.text_input("CIF *", value=st.session_state["form_data_event"]["organization_cif"], key="organization_cif", on_change=lambda: save_to_session_state("organization_cif", st.session_state["organization_cif"]))
        
        st.text_input("Nombre y apellidos del firmante *", value=st.session_state["form_data_event"]["signer_first_name"], key="signer_first_name", on_change=lambda: save_to_session_state("signer_first_name", st.session_state["signer_first_name"]))

        col13_2, col14_2 = st.columns(2)
        with col13_2:
            st.text_input("Cargo del firmante *", value=st.session_state["form_data_event"]["signer_position"], key="signer_position", on_change=lambda: save_to_session_state("signer_position", st.session_state["signer_position"]))
        with col14_2:
            email = st.text_input("Email del firmante *", 
                        #value=st.session_state["form_data_event"]["signer_email"] if st.session_state["email_correcto"] == True else "",
                        value=st.session_state["form_data_event"]["signer_email_copy"], # if st.session_state["email_correcto"] == True else "",
                        key="signer_email", 
                        on_change= lambda: validacion_completa_email())
            
        if not st.session_state["email_correcto"]:
            st.warning("El email introducido no es correcto.", icon="❌")

crear_detalles_firmante()

# Sección Detalles del Patrocinio
def crear_descripción_ia():
    st.markdown("**Pulsa para generar:**")  # Texto encima del botón
    st.button("Generar", help="Genera una breve descripción con IA en base al resto de campos", icon="📄", use_container_width=True, type="primary", on_click=handle_invoke_chain_event_description)

@st.fragment
def crear_detalles_patrocinio():
    st.header("3. Detalles del Patrocinio", divider=True)
    st.text_input(
        "Nombre del evento",
        placeholder="Este se actualizará automáticamente",
        value=f"Sponsorship of Event/Activity {st.session_state.get('event_name', '')}",
        disabled=True 
    )
    with st.container(border=True):
        col7, col8 = st.columns(2)
        with col7:
            st.number_input("Importe (€) *", min_value=0.0, step=100.0, value=st.session_state["form_data_event"]["amount"], key="amount", on_change=lambda: save_to_session_state("amount", st.session_state["amount"]))
        with col8:
            payment = st.selectbox("Tipo de pago *", options=["Pago directo", "Pago a través de la secretaría técnica (ST)"],
                         index = ["Pago directo", "Pago a través de la secretaría técnica (ST)"].index(st.session_state["form_data_event"]["payment_type"]) if "payment_type" in st.session_state["form_data_event"] else 0,
                         key="payment_type", 
                         on_change=lambda: save_to_session_state("payment_type", st.session_state["payment_type"]))
            

        
        st.text_input("Nombre de la secretaría técnica (ST)", value=st.session_state["form_data_event"]["name_st"] if st.session_state["form_data_event"]["payment_type"] != "Pago directo" else "", max_chars=MEDIUM_MAX_CHARS, disabled= st.session_state["form_data_event"]["payment_type"] != "Pago a través de la secretaría técnica (ST)", key="name_st", on_change=lambda: save_to_session_state("name_st", st.session_state["name_st"]))
        

        st.text_input("Producto asociado", value=st.session_state["form_data_event"]["associated_product"], max_chars=MEDIUM_MAX_CHARS, key="associated_product", on_change=lambda: save_to_session_state("associated_product", st.session_state["associated_product"]))
        col20, col21 = st.columns([5,1], vertical_alignment="center")
        with col20:
            st.text_area("Descripción del evento *", placeholder="Incluye nombre, fecha, sede, ciudad, descripción, objetivos y organizador", value=st.session_state["form_data_event"]["short_description"], max_chars=LARGE_MAX_CHARS, key="short_description", on_change=lambda: save_to_session_state("short_description", st.session_state["short_description"]))
        with col21:
            crear_descripción_ia()
            
        st.text_area("Contraprestaciones *", value=st.session_state["form_data_event"]["benefits"], key="benefits", on_change=lambda: save_to_session_state("benefits", st.session_state["benefits"]))

        patrocinador = st.selectbox("Merck patrocinador único o mayoritario *", options=["No", "Sí"], key="exclusive_sponsorship", help="Si Merck es el único financiador, documente completamente el presupuesto detallado de la actividad y asegúrese de que los conceptos y los límites estén en línea con las políticas y los códigos aplicables. Confirme mediante documentos de respaldo si el Solicitante ha solicitado financiación o patrocinio de otros",
                     index = ["No", "Sí"].index(st.session_state["form_data_event"]["exclusive_sponsorship"]) if "exclusive_sponsorship" in st.session_state["form_data_event"] else 0,
                     on_change=lambda: (
                                    save_to_session_state("exclusive_sponsorship", st.session_state["exclusive_sponsorship"]),
                                    save_to_session_state("documentosubido_3_event", ""),
                                ) if st.session_state["form_data_event"]["exclusive_sponsorship"] == "Sí" else 
                                    save_to_session_state("exclusive_sponsorship", st.session_state["exclusive_sponsorship"]))

        if st.session_state["form_data_event"]["exclusive_sponsorship"] == "Sí":
            st.warning("Debes enviar el dossier comercial o presupuesto del organizador.")
            st.file_uploader("Adjuntar presupuesto desglosado o dossier comercial", type=["pdf", "docx", "xlsx", "ppt"], key="documentosubido_3_event", accept_multiple_files=False, 
                    on_change=lambda: save_to_session_state("documentosubido_3_event", st.session_state["documentosubido_3_event"] if st.session_state["documentosubido_3_event"] else "")) 


        col11, col12 = st.columns(2, vertical_alignment="center")
        with col11:
            recurr = st.selectbox("Patrocinio recurrente *", options=["No lo sé","Sí", "No"], 
                         index = ["No lo sé","Sí", "No"].index(st.session_state["form_data_event"]["recurrent_sponsorship"]) if "recurrent_sponsorship" in st.session_state["form_data_event"] else 0,
                         key="recurrent_sponsorship", help="¿Merck ha colaborado en ediciones anteriores de este evento?", on_change=lambda: save_to_session_state("recurrent_sponsorship", st.session_state["recurrent_sponsorship"]))
        with col12:
            #if st.session_state.recurrent_sponsorship == "Sí":
            st.text_area("Detalles del patrocinio recurrente", value="Colaboraciones anteriores" if st.session_state["form_data_event"]["recurrent_sponsorship"] == "Sí" else "", max_chars=LARGE_MAX_CHARS, disabled=st.session_state["form_data_event"]["recurrent_sponsorship"] != "Sí", key="recurrent_text", on_change=lambda: save_to_session_state("recurrent_text", st.session_state["recurrent_text"]))

crear_detalles_patrocinio()

st.header("4. Documentos", divider=True)

with st.expander("Ver documentos necesarios"):
    st.file_uploader("Adjuntar agenda del evento *", type=["pdf", "docx", "xlsx", "ppt"], key="documentosubido_1_event", accept_multiple_files=False, 
                     on_change=lambda: save_to_session_state("documentosubido_1_event", st.session_state["documentosubido_1_event"] if st.session_state["documentosubido_1_event"] else "")) 
    st.file_uploader("Adjuntar solicitud de patrocinio *", type=["pdf", "docx", "xlsx", "ppt"], key="documentosubido_2_event", accept_multiple_files=False,
                    on_change=lambda: save_to_session_state("documentosubido_2_event", st.session_state["documentosubido_2_event"] if st.session_state["documentosubido_2_event"] else "")) 


# Estado inicial para el botón de descargar
st.session_state.download_enabled = False

def generacion_errores():
    try:
        st.session_state.download_enabled = False
        errores_general, err = af.validar_campos(st.session_state["form_data_event"], mandatory_fields, dependendent_fields)
        errores_ia = af.validar_campos_ia(st.session_state["form_data_event"], validar_ia)
        avisos = af.avisos_campos_ia(st.session_state["form_data_event"], campos_avisos_ia)

        if not errores_general and not errores_ia:
            df = save_form_data_event()
            doc, st.session_state.path_doc = cd.crear_documento_sponsorship_of_event(df)
            st.session_state.download_enabled = True
    except Exception as e:
        traceback.print_exc()
        st.toast(f"Ha ocurrido un problema al generar el formulario -> {e}", icon="❌")

    return errores_general, errores_ia, avisos

def mostrar_errores(errores_general, errores_ia, avisos):
    if not errores_general and not errores_ia:
        st.session_state.download_enabled = True
    else:
        if len(errores_general) > 0 :
            msg_general = "\n**Errores Generales del Formulario**\n"
            for msg in errores_general:
                msg_general += f"\n* {msg}\n"
            st.error(msg_general)

        if len(errores_ia) != 0:
            msg_ia = "\n**Errores detectados con IA**\n"
            for msg in errores_ia:
                msg_ia += f"\n* {msg}\n"
            st.error(msg_ia)

    
    if len(avisos) > 0:
        msg_aviso = "\n**Warnings detectados con IA**\n"
        for msg in avisos:
            msg_aviso += f"\n* {msg}\n"
        st.warning(msg_aviso)
    


# Botón para enviar
def button_form():
    if st.button(label="Generar Plantilla", use_container_width=True, type="primary"):
        with st.status("Validando campos...", expanded=True, state = "running") as status:
            st.write("Validando información general del formulario...")
            time.sleep(1.5)
            st.write("Validando campos obligatorios y dependientes...")
            time.sleep(1.5)
            st.write("Validando contenido de campos con IA...")
            time.sleep(1.5)

        errores_general, errores_ia, avisos = generacion_errores()
        st.session_state.errores_general_event, st.session_state.errores_ia_event, st.session_state.avisos_ia_event = errores_general, errores_ia, avisos

        # Actualizo el estado
        if st.session_state.download_enabled == True:
            status.update(
                label="Validación completada!", state="complete", expanded=False
            )
            #st.session_state.errores_event = False
        else:
            status.update(
                label="Validación no completada. Se deben revisar los campos obligatorios faltantes.", state="error", expanded=False
            )
            #st.session_state.errores_event = True
            st.toast("Se deben corregir los errores", icon="❌")
        
        if st.session_state.download_enabled == True:
            st.toast("Formulario generado correctamente", icon="✔️")

    if st.session_state.errores_event == True:
        mostrar_errores(st.session_state.errores_general_event, st.session_state.errores_ia_event, st.session_state.avisos_ia_event)     

        

def download_document():
    if st.session_state.path_doc:
        with open(st.session_state.path_doc, "rb") as file:
            st.download_button(
                label="Descargar ZIP",
                data=file,
                file_name="Sponshorship_Event.zip",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                icon="📥",
                disabled=disabled
            )
    else:
        st.download_button(
            label="Descargar ZIP",
            data=io.BytesIO(),
            file_name="Sponshorship_Event.zip",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            icon="📥",
            disabled=True
        )
        
button_form()
# Botón de descarga
disabled =  not st.session_state.download_enabled
download_document()

#st.write(st.session_state["form_data_event"])