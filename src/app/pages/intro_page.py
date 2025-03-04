import streamlit as st
import auxiliar.aux_functions as af
from datetime import date


#af.setup_environment()

# def save_to_session_state_event(key, value):
#     if key not in ["documentosubido_1_event", "documentosubido_2_event", "documentosubido_3_event"]:
#         st.session_state[key] = value
#     st.session_state["form_data_event"][key] = value
    

# Título de la página
af.show_main_title(title="Events Compliance Advisor", logo_size=200)


# Botones para navegar a otras páginas
st.markdown("""
    <h3 style="margin-bottom: 0;">Accesos rápidos</h3>
    <hr style="margin-top: 0; margin-bottom: 30px;">
    """, unsafe_allow_html=True)


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
    <h6 style="margin-top: 0; margin-bottom: 0px;">
    <h3 style="margin-bottom: 0;">Instrucciones</h3>
    <hr style="margin-top: 0; margin-bottom: 50px;">
    """, unsafe_allow_html=True)
    
    st.markdown("""
 
##### 📄 Plantillas Disponibles  
- **Sponsorship of event:** Colaboración en la que Merck apoya un evento/actividad organizado por una Organización Sanitaria o de Pacientes por la cual se recibe una contraprestación. 

- **Speaking Services:** Contratación de uno o más proveedores de servicios de oratoria (HCPs) para hablar (o moderar) en nombre de Merck en una reunión. 

- **Advisory Board:** Contratación de uno o varios proveedores de servicios (HCPs) para obtener información y orientación en relación a temas o actividades específicos.
            
- **Consulting Services:** Contratación de uno o más Proveedores de Servicios (HCPs) para proporcionar conocimiento experto sobre un tema específico, desarrollo de contenido, servicios de traducción, servicios de autoría, brindar asesoramiento científico/médico, etc, con el fin de obtener aportes y orientación de expertos relacionados con temas  o actividades específicos.

                
##### 🚀 ¿Cómo Funciona?  
1. Completa el formulario de la plantilla que necesites.  
2. Adjunta los documentos requeridos.  
3. Genera la carpeta ZIP automáticamente.  
4. ¡Tu carpeta zip se ha descargago! Envíala por correo electrónico a quien corresponda.

                
##### 📌 Notas  
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