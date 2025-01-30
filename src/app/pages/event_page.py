import streamlit as st
import pandas as pd
from datetime import date, datetime
import time
import traceback
import io

import auxiliar.create_docx as cd
import model.llm_sponsorship_event as llm_se

from dotenv import load_dotenv
load_dotenv()

LARGE_MAX_CHARS = 4000
MEDIUM_MAX_CHARS = 255

def save_to_session_state(key, value):
    st.session_state[key] = value
    st.session_state["form_data_event"][key] = value
    
def handle_invoke_chain_event_description():
    print("Inicio Chain Event Description")
    res = llm_se.invoke_chain_event_description(st.session_state.event_name,
                                          st.session_state.start_date,
                                          st.session_state.end_date,
                                          st.session_state.venue,
                                          st.session_state.city,
                                          st.session_state.organization_name,
                                          st.session_state.event_objetive)
    print("Fin Chain Event Description")
    st.session_state.res_generate_event_description = res  
    save_to_session_state("short_description", st.session_state.res_generate_event_description)

# Inicializar estado del formulario en session_state
if "form_data_event" not in st.session_state:
    field_defaults = {
        "event_name": "Sponsorship of Event/Activity ",
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
        "signer_last_name": "",
        "signer_position": "",
        "signer_email": "",
    }
    
    st.session_state["form_data_event"] = {}
    
    for key, value in field_defaults.items():
        save_to_session_state(key, value)
        
    st.session_state["res_generate_event_description"] = ""
    st.session_state["download_enabled"] = False
    st.session_state["path_doc"] = None

mandatory_fields = [
    "event_name",
    "event_type",
    "start_date",
    "end_date",
    "venue",
    "city",
    "num_attendees",
    "attendee_profile",
    "event_objetive",
    "amount",
    "payment_type",
    "name_st",
    "short_description",
    "benefits",
    "exclusive_sponsorship",
    "recurrent_sponsorship",
    "recurrent_text",
    "organization_name",
    "organization_cif",
    "signer_first_name",
    "signer_last_name",
    "signer_position",
    "signer_email",
]

def check_mandatory_fields():
    """Check if all mandatory fields have valid values and return missing fields"""
    fields_to_check = list(mandatory_fields)
    missing_fields = []
    error_messages = []

    # If virtual event, venue and city are not mandatory
    if st.session_state["form_data_event"]["event_type"] == "Virtual":
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
        "signer_last_name": st.session_state["form_data_event"].get("signer_last_name", ""),
        "signer_position": st.session_state["form_data_event"].get("signer_position", ""),
        "signer_email": st.session_state["form_data_event"].get("signer_email", ""),
        "submission_date": datetime.now()
    }
    
    df = pd.DataFrame([data])
    return df

# Sección de documentos a adjuntar
st.title("Formulario de Patrocinio de Evento")
st.header("Documentos a Adjuntar", divider=True)

with st.expander("Ver documentos necesarios"):
    st.file_uploader("Adjuntar agenda del evento (Obligatorio)", type=["pdf", "docx", "xlsx"], key="doc1", accept_multiple_files=False, on_change=lambda: save_to_session_state("doc1", st.session_state["doc1"]))
    st.file_uploader("Adjuntar solicitud de patrocinio (Obligatorio)", type=["pdf", "docx"], key="doc2", accept_multiple_files=False, on_change=lambda: save_to_session_state("doc2", st.session_state["doc2"]))
    st.file_uploader("Adjuntar presupuesto desglosado o dossier comercial (Solo si es patrocinador mayoritario)", type=["pdf", "docx"], key="doc3", accept_multiple_files=False, on_change=lambda: save_to_session_state("doc3", st.session_state["doc3"]))


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
            "Nombre del evento",
            placeholder="Escribe el nombre del evento",
            value=st.session_state.event_name,
            help="Introduce el nombre del evento",
            max_chars=MEDIUM_MAX_CHARS,
            key="event_name",
            on_change=lambda: save_to_session_state("event_name", st.session_state["event_name"])
        )
    with col2:
        st.selectbox(
            "Tipo de evento",
            options=["Virtual", "Presencial", "Híbrido"],
            help="""Selecciona el tipo de evento que deseas realizar. 
                \n- **Virtual**: Evento realizado completamente en línea.
                \n- **Presencial**: Evento llevado a cabo físicamente en una ubicación específica.
                \n- **Híbrido**: Combina elementos de eventos virtuales y presenciales.""",
            key="event_type",
            on_change=lambda: save_to_session_state("event_type", st.session_state["event_type"])
        )

def crear_fechas():
    col3, col4 = st.columns(2)
    with col3:
        st.date_input("Fecha de inicio del evento", value=st.session_state.start_date, key="start_date", on_change=lambda: save_to_session_state("start_date", st.session_state["start_date"]))
    with col4:
        st.date_input("Fecha de fin del evento", value=st.session_state.end_date, key="end_date", on_change=lambda: save_to_session_state("end_date", st.session_state["end_date"]))

    if st.session_state.start_date > st.session_state.end_date:
        st.error("La fecha de inicio debe ser menor o igual a la fecha de fin.")

def crear_ubicacion():
    is_virtual = st.session_state.event_type == "Virtual"
    venue_value = "" if is_virtual else st.session_state.venue
    city_value = "" if is_virtual else st.session_state.city
    
    st.text_input(
        "Sede (si aplica)",
        disabled=is_virtual,
        value=venue_value,
        help="Indica la dirección de la sede",
        max_chars=MEDIUM_MAX_CHARS,
        key="venue",
        on_change=lambda: save_to_session_state("venue", st.session_state["venue"])
    )
    st.text_input(
        "Ciudad (si aplica)", 
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
            "Número de asistentes",
            min_value=0,
            step=1, 
            value=st.session_state.num_attendees,
            key="num_attendees",
            on_change=lambda: save_to_session_state("num_attendees", st.session_state["num_attendees"])
        )
    with col6:
        st.text_area(
            "Perfil de los asistentes",
            max_chars=MEDIUM_MAX_CHARS,
            value=st.session_state.attendee_profile,
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
        "Objetivo del evento", 
        max_chars=LARGE_MAX_CHARS,
        value=st.session_state.get('event_objetive', ''), 
        key="event_objetive",
        on_change=lambda: save_to_session_state("event_objetive", st.session_state["event_objetive"])
    )

    if st.session_state.event_objetive != st.session_state.prev_event_objetive:
        with st.spinner("Revisando objetivo..."):
            message = validate_event_objetive(st.session_state.event_objetive)
            st.markdown(message, unsafe_allow_html=True)
        st.session_state.prev_event_objetive = st.session_state.event_objetive

st.header("Detalles del Evento", divider=True)
with st.container(border=True):     
    crear_detalles_evento()
    display_objective_field()

# Sección Detalles del Patrocinio


def crear_descripción_ia():
    st.markdown("**Pulsa para generar:**")  # Texto encima del botón
    st.button("Generar", help="Genera una breve descripción con IA en base al resto de campos", icon="📄", use_container_width=True, type="primary", on_click=handle_invoke_chain_event_description)
@st.fragment
def crear_detalles_patrocinio():
    st.header("Detalles del Patrocinio", divider=True)
    st.text_input(
        "Nombre del evento (copia automática)",
        placeholder="Este se actualizará automáticamente",
        value=st.session_state.get("event_name", ""),
        disabled=True 
    )
    with st.container(border=True):
        col7, col8 = st.columns(2)
        with col7:
            st.number_input("Importe (en euros)", min_value=0.0, step=100.0, value=st.session_state.amount, key="amount", on_change=lambda: save_to_session_state("amount", st.session_state["amount"]))
        with col8:
            st.selectbox("Tipo de pago", options=["Pago directo", "Pago a través de la secretaría técnica (ST)"], key="payment_type", on_change=lambda: save_to_session_state("payment_type", st.session_state["payment_type"]))

        
        st.text_input("Nombre de la secretaría técnica (ST)", value=st.session_state.name_st if st.session_state.payment_type != "Pago directo" else "", max_chars=MEDIUM_MAX_CHARS, disabled= st.session_state.payment_type != "Pago a través de la secretaría técnica (ST)", key="name_st", on_change=lambda: save_to_session_state("name_st", st.session_state["name_st"]))
        

        st.text_input("Producto asociado", value=st.session_state.associated_product, max_chars=MEDIUM_MAX_CHARS, key="associated_product", on_change=lambda: save_to_session_state("associated_product", st.session_state["associated_product"]))
        col20, col21 = st.columns([5,1], vertical_alignment="center")
        with col20:
            st.text_area("Descripción y objetivo del evento", placeholder="Incluye nombre, fecha, sede, ciudad, descripción, objetivos y organizador", value=st.session_state.short_description, max_chars=LARGE_MAX_CHARS, key="short_description", on_change=lambda: save_to_session_state("short_description", st.session_state["short_description"]))
        with col21:
            crear_descripción_ia()
            
        st.text_area("Contraprestaciones", value=st.session_state.benefits, key="benefits", on_change=lambda: save_to_session_state("benefits", st.session_state["benefits"]))

        st.selectbox("Merck único patrocinador o mayoritario", options=["Sí", "No"], key="exclusive_sponsorship", help="Si Merck es el único financiador, documente completamente el presupuesto detallado de la actividad y asegúrese de que los conceptos y los límites estén en línea con las políticas y los códigos aplicables. Confirme mediante documentos de respaldo si el Solicitante ha solicitado financiación o patrocinio de otros",on_change=lambda: save_to_session_state("exclusive_sponsorship", st.session_state["exclusive_sponsorship"]))
        if st.session_state.exclusive_sponsorship == "Sí":
            st.warning("Debes enviar el dossier comercial o presupuesto del organizador.")

        col11, col12 = st.columns(2, vertical_alignment="center")
        with col11:
            st.selectbox("Patrocinio recurrente", options=["No lo sé","Sí", "No"], key="recurrent_sponsorship", help="¿Merck ha colaborado en ediciones anteriores de este evento?", on_change=lambda: save_to_session_state("recurrent_sponsorship", st.session_state["recurrent_sponsorship"]))
        with col12:
            #if st.session_state.recurrent_sponsorship == "Sí":
            st.text_area("Detalles del patrocinio recurrente", value="Colaboraciones anteriores" if st.session_state.recurrent_sponsorship == "Sí" else "", max_chars=LARGE_MAX_CHARS, disabled=st.session_state.recurrent_sponsorship != "Sí", key="recurrent_text", on_change=lambda: save_to_session_state("recurrent_text", st.session_state["recurrent_text"]))

crear_detalles_patrocinio()

# Sección Información del Firmante
@st.fragment()
def crear_detalles_firmante():
    st.header("Detalles del Organizador", divider=True)
    with st.container(border=True):
        col13, col14 = st.columns(2)
        with col13:
            st.text_input("Nombre de la organización", value=st.session_state.organization_name, key="organization_name", on_change=lambda: save_to_session_state("organization_name", st.session_state["organization_name"]))
            st.text_input("Nombre del firmante", value=st.session_state.signer_first_name, key="signer_first_name", on_change=lambda: save_to_session_state("signer_first_name", st.session_state["signer_first_name"]))
            st.text_input("Cargo del firmante", value=st.session_state.signer_position, key="signer_position", on_change=lambda: save_to_session_state("signer_position", st.session_state["signer_position"]))
        with col14:
            st.text_input("CIF", value=st.session_state.organization_cif, key="organization_cif", on_change=lambda: save_to_session_state("organization_cif", st.session_state["organization_cif"]))
            st.text_input("Apellidos del firmante", value=st.session_state.signer_last_name, key="signer_last_name", on_change=lambda: save_to_session_state("signer_last_name", st.session_state["signer_last_name"]))
            st.text_input("Email del firmante", value=st.session_state.signer_email, key="signer_email", on_change=lambda: save_to_session_state("signer_email", st.session_state["signer_email"]))

crear_detalles_firmante()

# Estado inicial para el botón de descargar
st.session_state.download_enabled = False

# Botón para enviar
def button_form():
    if st.button(label="Enviar", use_container_width=True, type="primary"):
        try:
            if check_mandatory_fields():
                df = save_form_data_event()
                #st.dataframe(df)
                doc, st.session_state.path_doc = cd.crear_documento_sponsorship_of_event(df)
                ## Create a markdown string with bullet points for each column
                #markdown_text = "### Resumen de la solicitud:\n"
                #for column in df.columns:
                #    value = df[column].iloc[0]
                #    markdown_text += f"* **{column}**: {value}\n"
                #st.markdown(markdown_text)
                
                # Cambiar el estado del botón de descarga
                st.session_state.download_enabled = True
                
                #st.success("Formulario generado correctamente correctamente.")
                st.toast("Formulario generado correctamente", icon="✔️")
            else:
                st.toast("Debes rellenar todos los campos obligatorios.", icon="❌")
            # Leer el archivo Word y prepararlo para descarga
        except Exception as e:
            traceback.print_exc()
            st.toast(f"Ha ocurrido un problema al generar el formulario -> {e}", icon="❌")


def download_document():
    if st.session_state.path_doc:
        with open(st.session_state.path_doc, "rb") as file:
            st.download_button(
                label="Descargar documento Word",
                data=file,
                file_name="documento_sponsorship.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                icon="📥",
                disabled=disabled
            )
    else:
        st.download_button(
            label="Descargar documento Word",
            data=io.BytesIO(),
            file_name="documento_sponsorship.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            icon="📥",
            disabled=True
        )
        
button_form()
# Botón de descarga
disabled = not st.session_state.download_enabled
download_document()
