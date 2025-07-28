import streamlit as st
import base64
from pathlib import Path
import os
import glob
import auxiliar.aux_functions as af 
from utils import (
    get_streamlit_request_headers,
    show_code,
    APP_SERVICE_FOUNDRY_ACCESS_TOKEN_HEADER,
    app_is_running_on_app_service,
)
import os

try: 
    from foundry_dev_tools import FoundryContext 
except: 
    pass

headers = None

if "headers" not in st.session_state:

    headers = get_streamlit_request_headers()

    st.session_state.first_name = headers.get("X-Appservice-Firstname", "FirstName")
    st.session_state.last_name = headers.get("X-Appservice-Lastname", "LastName")
    st.session_state.user_id = headers.get("X-Appservice-Muid", "M999999-default-user")
    st.session_state.email = headers.get(
        "X-Appservice-Email", "firstName.LastName@merckgroup.com (running-locally)"
    )

user_id = st.session_state.get("user_id", "default_user") ##### CAMBIAR PARA CLIENTE
intro_page = st.Page("./pages/intro_page.py", title="Panel principal", icon="🏠")
event_page = st.Page("./pages/event_page.py", title="Sponsorship of Event", icon="🗓️")
advisory_board = st.Page("./pages/advisory_board_page.py", title="Advisory Board", icon="👩‍💼")
consulting_services = st.Page("./pages/consulting_services_page.py", title="Consulting Services", icon="💡")
speaking_services = st.Page("./pages/speaking_services_page.py", title="Speaking Services", icon="🗣️")
templates_page = st.Page("./pages/templates_page.py", title="Templates", icon="📋")
saves_page = st.Page("./pages/saves_page.py", title=f"Gestión de Formularios", icon="⚙️")


# Setup de navegación que utiliza objetos `st.Page`
pg = st.navigation(
    {
        "Panel principal": [intro_page],
        "Plantillas": [event_page, advisory_board, speaking_services, consulting_services],
        "Templates": [templates_page],
        "Configuración": [saves_page]
    }
)

st.set_page_config(
    page_title="Merck",
    page_icon="💊",
    layout="wide"
)

def get_base64_of_bin_file(bin_file):
    """Devuelve la cadena base64 de un archivo binario."""
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

BASE_DIR = Path(__file__).resolve().parent

logo_merck = "MDG_Logo_RPurple_SP.png"
logo_path = BASE_DIR / "images" / logo_merck

logo_merck_small = "purple-mini.png"
logo_small_path = BASE_DIR / "images" / logo_merck_small

st.logo(logo_path, 
        link = "https://www.merckgroup.com/en",
        icon_image = logo_small_path, 
        size = "large")

pg.run()