import streamlit as st
import pandas as pd
from datetime import date, datetime
import time
import traceback
import io

import auxiliar.create_docx as cd
import model.llm_sponsorship_event as llm_se

from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
load_dotenv()
LARGE_MAX_CHARS = 4000
MEDIUM_MAX_CHARS = 255


def handle_invoke_chain_event_description():
    res = llm_se.invoke_chain_event_description(st.session_state.event_name,
                                          st.session_state.start_date,
                                          st.session_state.end_date,
                                          st.session_state.venue,
                                          st.session_state.city,
                                          st.session_state.organization_name)
    
    st.session_state.res_generate_event_description = res  
  
    st.session_state.short_description = st.session_state.res_generate_event_description

# Initialize session state variables
if "event_name" not in st.session_state:
    #fields
    st.session_state.event_name = "Sponsorship of Event/Activity "
    st.session_state.event_type = "Virtual"
    st.session_state.start_date = date.today()
    st.session_state.end_date = date.today()
    st.session_state.venue = ""
    st.session_state.city = ""
    st.session_state.num_attendees = 0
    st.session_state.attendee_profile = ""
    st.session_state.event_objective = ""
    st.session_state.amount = 0.0
    st.session_state.payment_type = "Pago directo"
    st.session_state.name_st = ""
    st.session_state.email_st = ""
    st.session_state.associated_product = ""
    st.session_state.short_description = ""
    st.session_state.benefits = ""
    st.session_state.exclusive_sponsorship = "No"
    st.session_state.recurrent_sponsorship = "No"
    st.session_state.recurrent_text = ""
    st.session_state.organization_name = ""
    st.session_state.organization_cif = ""
    st.session_state.signer_first_name = ""
    st.session_state.signer_last_name = ""
    st.session_state.signer_position = ""
    st.session_state.signer_email = ""
    
    #extra
    st.session_state.res_generate_event_description = ""
    st.session_state.download_enabled = False
    st.session_state.path_doc = None


mandatory_fields = [
    st.session_state.event_name,
    st.session_state.event_type,
    st.session_state.start_date,
    st.session_state.end_date,
    st.session_state.venue,
    st.session_state.city,
    st.session_state.num_attendees,
    st.session_state.attendee_profile,
    st.session_state.event_objective,
    st.session_state.amount,
    st.session_state.payment_type,
    st.session_state.name_st,
    st.session_state.email_st,
    st.session_state.associated_product,
    st.session_state.short_description,
    st.session_state.benefits,
    st.session_state.exclusive_sponsorship,
    st.session_state.recurrent_sponsorship,
    st.session_state.recurrent_text,
    st.session_state.organization_name,
    st.session_state.organization_cif,
    st.session_state.signer_first_name,
    st.session_state.signer_last_name,
    st.session_state.signer_position,
    st.session_state.signer_email,
]

def check_mandatory_fields():
    """Check if all mandatory fields have valid values"""
    # First check base fields except special cases
    fields_to_check = list(mandatory_fields)

    # If virtual event, venue and city are not mandatory
    if st.session_state.event_type == "Virtual":
        fields_to_check.remove(st.session_state.venue)
        fields_to_check.remove(st.session_state.city)

    if st.session_state.payment_type == "Pago directo":
        fields_to_check.remove(st.session_state.name_st)
        fields_to_check.remove(st.session_state.email_st)
        
    if st.session_state.recurrent_sponsorship == "No":
        fields_to_check.remove(st.session_state.recurrent_text)
    # Check if any required field is empty
    if any(not str(field).strip() for field in fields_to_check):
        return False

    return True

def save_form_data():
    """Saves form data into a DataFrame"""
    data = {
        "event_name": st.session_state.get("event_name", ""),
        "event_type": st.session_state.get("event_type", ""),
        "start_date": st.session_state.get("start_date", ""),
        "end_date": st.session_state.get("end_date", ""),
        "venue": st.session_state.get("venue", ""),
        "city": st.session_state.get("city", ""),
        "num_attendees": st.session_state.get("num_attendees", 0),
        "attendee_profile": st.session_state.get("attendee_profile", ""),
        "event_objective": st.session_state.get("event_objective", ""),
        "amount": st.session_state.get("amount", 0.0),
        "payment_type": st.session_state.get("payment_type", ""),
        "name_st": st.session_state.get("name_st", ""),
        "email_st": st.session_state.get("email_st", ""),
        "associated_product": st.session_state.get("associated_product", ""),
        "short_description": st.session_state.get("short_description", ""),
        "benefits": st.session_state.get("benefits", ""),
        "exclusive_sponsorship": st.session_state.get("exclusive_sponsorship", ""),
        "recurrent_sponsorship": st.session_state.get("recurrent_sponsorship", ""),
        "recurrent_text": st.session_state.get("recurrent_text", ""),
        "organization_name": st.session_state.get("organization_name", ""),
        "organization_cif": st.session_state.get("organization_cif", ""),
        "signer_first_name": st.session_state.get("signer_first_name", ""),
        "signer_last_name": st.session_state.get("signer_last_name", ""),
        "signer_position": st.session_state.get("signer_position", ""),
        "signer_email": st.session_state.get("signer_email", ""),
        "submission_date": datetime.now()
    }
    
    df = pd.DataFrame([data])
    return df

# Sección de documentos a adjuntar
st.title("Formulario de Patrocinio de Evento")
st.header("Documentos a Adjuntar", divider=True)

with st.expander("Ver documentos necesarios"):
    st.file_uploader("Adjuntar agenda del evento (Obligatorio)", type=["pdf", "docx", "xlsx"], key="doc1", accept_multiple_files=False)
    st.file_uploader("Adjuntar solicitud de patrocinio (Obligatorio)", type=["pdf", "docx"], key="doc2", accept_multiple_files=False)
    st.file_uploader("Adjuntar presupuesto desglosado o dossier comercial (Solo si es patrocinador mayoritario)", type=["pdf", "docx"], key="doc3", accept_multiple_files=False)


# Sección Detalles del Evento
@st.fragment()
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
            key="event_name"
        )
    with col2:
        st.selectbox(
            "Tipo de evento",
            options=["Virtual", "En persona", "Híbrido"],
            help="""Selecciona el tipo de evento que deseas realizar. 
                \n- **Virtual**: Evento realizado completamente en línea.
                \n- **En persona**: Evento llevado a cabo físicamente en una ubicación específica.
                \n- **Híbrido**: Combina elementos de eventos virtuales y presenciales.""",
            key="event_type"
        )

def crear_fechas():
    col3, col4 = st.columns(2)
    with col3:
        st.date_input("Fecha de inicio del evento", value=st.session_state.start_date, key="start_date")
    with col4:
        st.date_input("Fecha de fin del evento", value=st.session_state.end_date, key="end_date")

    if st.session_state.start_date > st.session_state.end_date:
        st.error("La fecha de inicio debe ser menor que la fecha de fin.")

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
        key="venue"
    )
    st.text_input(
        "Ciudad (si aplica)", 
        disabled=is_virtual,
        value=city_value,
        help="Indica la ciudad en la que se encuentra la sede",
        max_chars=MEDIUM_MAX_CHARS, 
        key="city"
    )

def crear_asistentes():
    col5, col6 = st.columns(2, vertical_alignment="center")
    with col5:
        st.number_input(
            "Número de asistentes",
            min_value=0,
            step=1, 
            value=st.session_state.num_attendees,
            key="num_attendees"
        )
    with col6:
        st.text_area(
            "Perfil de los asistentes",
            max_chars=MEDIUM_MAX_CHARS,
            value=st.session_state.attendee_profile,
            key="attendee_profile"
        )

     
@st.fragment()
def validate_event_objective(objective_text):
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
    if 'prev_event_objective' not in st.session_state:
        st.session_state.prev_event_objective = ""
    
    st.text_area(
        "Objetivo del evento", 
        max_chars=LARGE_MAX_CHARS,
        value=st.session_state.get('event_objective', ''), 
        key="event_objective"
    )

    if st.session_state.event_objective != st.session_state.prev_event_objective:
        with st.spinner("Revisando objetivo..."):
            message = validate_event_objective(st.session_state.event_objective)
            st.markdown(message, unsafe_allow_html=True)
        st.session_state.prev_event_objective = st.session_state.event_objective

st.header("Detalles del Evento", divider=True)
with st.container(border=True):     
    crear_detalles_evento()
    display_objective_field()

# Sección Detalles del Patrocinio
@st.fragment()
def crear_detalles_patrocinio():
    st.header("Detalles del Patrocinio", divider=True)
    with st.container(border=True):
        col7, col8 = st.columns(2)
        with col7:
            st.number_input("Importe (en euros)", min_value=0.0, step=100.0, value=st.session_state.amount, key="amount")
        with col8:
            st.selectbox("Tipo de pago", options=["Pago directo", "Pago a través de la secretaría técnica (ST)"], key="payment_type")

        #if st.session_state.payment_type == "Pago a través de la secretaría técnica (ST)":
        col9, col10 = st.columns(2)
        with col9:
            st.text_input("Nombre de la secretaría técnica (ST)", value=st.session_state.name_st if st.session_state.payment_type != "Pago directo" else "", max_chars=MEDIUM_MAX_CHARS, disabled= st.session_state.payment_type != "Pago a través de la secretaría técnica (ST)", key="name_st")
        with col10:
            st.text_input("Email de la secretaría técnica (ST)", value=st.session_state.email_st if st.session_state.payment_type != "Pago directo" else "", max_chars=MEDIUM_MAX_CHARS, disabled= st.session_state.payment_type != "Pago a través de la secretaría técnica (ST)", key="email_st")

        st.text_input("Producto asociado", value=st.session_state.associated_product, max_chars=MEDIUM_MAX_CHARS, key="associated_product")
        col20, col21 = st.columns([5,1], vertical_alignment="center")
        with col20:
            st.text_area("Descripción del evento", placeholder="Incluye nombre, fecha, sede y organizador", value=st.session_state.short_description, max_chars=LARGE_MAX_CHARS, key="short_description")
        with col21:
            st.markdown("**Pulsa para generar:**")  # Texto encima del botón
            st.button("Generar", help="Genera una breve descripción con IA en base al resto de campos", icon="📄", use_container_width=True, type="primary", on_click=handle_invoke_chain_event_description)
        st.text_area("Beneficio para la empresa", value=st.session_state.benefits, key="benefits")

        st.selectbox("Merck único patrocinador", options=["Sí", "No"], key="exclusive_sponsorship")
        if st.session_state.exclusive_sponsorship == "Sí":
            st.warning("Debes enviar el dossier comercial o presupuesto del organizador.")

        col11, col12 = st.columns(2, vertical_alignment="center")
        with col11:
            st.selectbox("Patrocinio recurrente", options=["Sí", "No"], key="recurrent_sponsorship")
        with col12:
            #if st.session_state.recurrent_sponsorship == "Sí":
            st.text_area("Detalles del patrocinio recurrente", value=st.session_state.recurrent_text if st.session_state.recurrent_sponsorship != "No" else "", max_chars=LARGE_MAX_CHARS, disabled=st.session_state.recurrent_sponsorship != "Sí", key="recurrent_text")

crear_detalles_patrocinio()

# Sección Información del Firmante
@st.fragment()
def crear_detalles_firmante():
    st.header("Detalles del Firmante", divider=True)
    with st.container(border=True):
        col13, col14 = st.columns(2)
        with col13:
            st.text_input("Nombre de la organización", value=st.session_state.organization_name, key="organization_name")
            st.text_input("Nombre del firmante", value=st.session_state.signer_first_name, key="signer_first_name")
            st.text_input("Cargo del firmante", value=st.session_state.signer_position, key="signer_position")
        with col14:
            st.text_input("CIF", value=st.session_state.organization_cif, key="organization_cif")
            st.text_input("Apellidos del firmante", value=st.session_state.signer_last_name, key="signer_last_name")
            st.text_input("Email del firmante", value=st.session_state.signer_email, key="signer_email")

crear_detalles_firmante()

# Estado inicial para el botón de descargar
st.session_state.download_enabled = False

# Botón para enviar
def button_form():
    if st.button(label="Enviar", use_container_width=True, type="primary"):
        try:
            if check_mandatory_fields():
                df = save_form_data()
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
