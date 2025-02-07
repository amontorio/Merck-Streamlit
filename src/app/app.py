import streamlit as st
import os
import base64

assistant = st.Page("./pages/assistant.py", title="Asistente", icon="🤖")

event_page = st.Page("./pages/event_page.py", title="Sponsorship of Event", icon="🗓️")
advisory_board = st.Page("./pages/advisory_board_page.py", title="Advisory Board", icon="👩‍💼")
consulting_services = st.Page("./pages/consulting_services_page.py", title="Consulting Services", icon="💡")
speaking_services = st.Page("./pages/speaking_services_page.py", title="Speaking Services", icon="🗣️")


pg = st.navigation(
    {
    #    "Información": [welcome, doc],
       "Chatbot": [assistant],
       "Plantillas": [event_page, advisory_board, speaking_services, consulting_services] 
    }
    )


st.set_page_config(
    page_title="Merck",
    page_icon="💊",
    layout="wide"
)

#logo_merck = 'logo-merck-kgaa-2015-1.svg'
#st.sidebar.image(os.path.join(os.getcwd(), fr'src/app/images/{logo_merck}'), width=200, use_container_width=True)

def get_base64_of_bin_file(bin_file):
    """Devuelve la cadena base64 de un archivo binario."""
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def add_logo():
    logo_merck = 'logo-merck-kgaa-2015-1.svg'
    logo_path = os.path.join(os.getcwd(), f'src/app/images/{logo_merck}')
    
    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url('src/app/images/{logo_merck}');
                background-repeat: no-repeat;
                background-size: 100px auto;  /* Ajusta el tamaño del logo aquí */
                padding-top: 120px;
                background-position: 20px 20px;
            }}
            [data-testid="stSidebarNav"]::before {{
                content: "Form Assistant";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 5px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Si aún deseas mostrar la imagen de forma adicional, asegúrate de ajustar su tamaño
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=100)  # O puedes omitir esto si el fondo es suficiente
    else:
        st.sidebar.warning("No se encontró el logo.")

#add_logo()

pg.run()