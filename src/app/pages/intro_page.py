import streamlit as st
import auxiliar.aux_functions as af
from datetime import date



#af.setup_environment()




def save_to_session_state_event(key, value):
    if key not in ["documentosubido_1_event", "documentosubido_2_event", "documentosubido_3_event"]:
        st.session_state[key] = value
    st.session_state["form_data_event"][key] = value
    
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
        "documentosubido_1_event": None,
        "documentosubido_2_event": None,
        "documentosubido_3_event": None
    }
    
    st.session_state["form_data_event"] = {}
    
    for key, value in field_defaults.items():
        save_to_session_state_event(key, value)
        
    st.session_state["res_generate_event_description"] = ""
    st.session_state["download_enabled"] = False
    st.session_state["path_doc"] = None
    st.session_state["email_correcto"] = True
    st.session_state["signer_email"] = ""







































# Título de la página
af.show_main_title(title="Events Compliance Advisor", logo_size=300)


# Botones para navegar a otras páginas
st.markdown("## Accesos rápidos")
col1, col2 = st.columns(2)

with col1:
    if st.button("Sponsorship of Event", use_container_width=True, icon="🗓️"):
        st.switch_page("pages/event_page.py")

with col2:
    if st.button("Advisory Board", use_container_width=True, icon="👩‍💼"):
        st.switch_page("pages/advisory_board_page.py")

col3, col4 = st.columns(2)
with col3:
    if st.button("Speaking Services", use_container_width=True, icon="🗣️"):
        st.switch_page("pages/speaking_services_page.py")

with col4:
    if st.button("Consulting Services", use_container_width=True, icon="💡"):
        st.switch_page("pages/consulting_services_page.py")



# Contenedor con información sobre la app
with st.container():
    st.markdown("""

## 📄 Plantillas Disponibles  
**Patrocinio de Eventos:** Para gestionar patrocinios y detalles del evento.  
**Speaking Services:** Contratación de ponentes y logística del evento.  
**Consulting Services:** Servicios de consultoría y selección de consultores.  
**Advisory Board:** Reuniones de consejo asesor y selección de ponentes.  

## 🚀 ¿Cómo Funciona?  
1. Completa el formulario de la plantilla que necesites.  
2. Adjunta los documentos requeridos.  
3. Genera el documento Word automáticamente.  

## 📌 Notas  
Algunos campos se incluirán automáticamente en el contrato.  
Adjunta todos los documentos necesarios para evitar retrasos.  

¡Empieza a generar tus plantillas ahora!

    """)


#rain(
#        emoji="💊",
#        font_size=54,
#        falling_speed=5,
#        animation_length="infinite",
#    )