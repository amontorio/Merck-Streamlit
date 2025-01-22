import streamlit as st
import pandas as pd
from datetime import datetime
import time

LARGE_MAX_CHARS = 4000
MEDIUM_MAX_CHARS = 255

# Initialize session state variables
if "event_name" not in st.session_state:
    st.session_state.event_name = "Sponsorship of Event/Activity "
    st.session_state.event_type = "Virtual"
    st.session_state.start_date = datetime.now()
    st.session_state.end_date = datetime.now()
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
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Nombre del evento", placeholder="Escribe el nombre del evento", help="Introduce el nombre del evento", key="event_name")
    with col2:
        event_type = st.selectbox("Tipo de evento", options=["Virtual", "En persona", "Híbrido"],help="""Selecciona el tipo de evento que deseas realizar. 
            \n- **Virtual**: Evento realizado completamente en línea.
            \n- **En persona**: Evento llevado a cabo físicamente en una ubicación específica.
            \n- **Híbrido**: Combina elementos de eventos virtuales y presenciales.""", key="event_type")

    col3, col4 = st.columns(2)
    with col3:
        st.date_input("Fecha de inicio del evento", value=st.session_state.start_date, key="start_date")
    with col4:
        st.date_input("Fecha de fin del evento", value=st.session_state.end_date, key="end_date")

    st.text_input("Sede (si aplica)", disabled=st.session_state.event_type == "Virtual", value=st.session_state.venue, help="Indica la dirección de la sede", key="venue")
    st.text_input("Ciudad (si aplica)", disabled=st.session_state.event_type == "Virtual", value=st.session_state.city, help="Indica la ciudad en la que se encuentra la sede", key="city")

    col5, col6 = st.columns(2, vertical_alignment="center")
    with col5:
        st.number_input("Número de asistentes", min_value=0, step=1, value=st.session_state.num_attendees, key="num_attendees")
    with col6:
        st.text_area("Perfil de los asistentes", max_chars=MEDIUM_MAX_CHARS, value=st.session_state.attendee_profile, key="attendee_profile")

        
        
@st.fragment()
def crear_detalles_evento_objetivo():
    # Inicializar variable para comparar el cambio del texto
    if 'prev_event_objective' not in st.session_state:
        st.session_state.prev_event_objective = ""
    
    st.text_area("Objetivo del evento", max_chars=LARGE_MAX_CHARS, 
                value=st.session_state.get('event_objective', ''), key="event_objective")

    # Mensaje inicial
    mensaje = ""

    # Verificar solo si el texto ha cambiado
    if st.session_state.event_objective != st.session_state.prev_event_objective:
        st.session_state.prev_event_objective = st.session_state.event_objective  # Actualizar valor anterior
        if st.session_state.event_objective:
            with st.spinner("Revisando objetivo..."):
                time.sleep(3)  # Simula una operación de validación
                if "nombre del evento" in st.session_state.event_objective.lower():
                    mensaje = '<p style="color:green;">El texto es correcto.</p>'
                else:
                    mensaje = '<p style="color:red;">El objetivo debe incluir el nombre del evento.</p>'

    # Mostrar el mensaje encima del campo de texto
    st.markdown(mensaje, unsafe_allow_html=True)

st.header("Detalles del Evento", divider=True)
with st.container(border=True):     
    crear_detalles_evento()
    crear_detalles_evento_objetivo()

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

        if st.session_state.payment_type == "Pago a través de la secretaría técnica (ST)":
            col9, col10 = st.columns(2)
            with col9:
                st.text_input("Nombre de la secretaría técnica (ST)", value=st.session_state.name_st, key="name_st")
            with col10:
                st.text_input("Email de la secretaría técnica (ST)", value=st.session_state.email_st, key="email_st")

        st.text_input("Producto asociado", value=st.session_state.associated_product, key="associated_product")
        st.text_area("Descripción del evento", placeholder="Incluye nombre, fecha, sede y organizador", value=st.session_state.short_description, key="short_description")
        st.text_area("Beneficio para la empresa", value=st.session_state.benefits, key="benefits")

        st.selectbox("Merck único patrocinador", options=["Sí", "No"], key="exclusive_sponsorship")
        if st.session_state.exclusive_sponsorship == "Sí":
            st.warning("Debes enviar el dossier comercial o presupuesto del organizador.")

        col11, col12 = st.columns(2)
        with col11:
            st.selectbox("Patrocinio recurrente", options=["Sí", "No"], key="recurrent_sponsorship")
        with col12:
            if st.session_state.recurrent_sponsorship == "Sí":
                st.text_area("Detalles del patrocinio recurrente", value=st.session_state.recurrent_text, key="recurrent_text")

crear_detalles_patrocinio()
# Sección Información del Firmante
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

# Botón para enviar
if st.button(label="Enviar", use_container_width=True, type="primary"):
    df = save_form_data()
    st.dataframe(df)
    # Create a markdown string with bullet points for each column
    markdown_text = "### Resumen de la solicitud:\n"
    for column in df.columns:
        value = df[column].iloc[0]
        markdown_text += f"* **{column}**: {value}\n"
        
    st.markdown(markdown_text)
    st.success("Formulario enviado correctamente.")
