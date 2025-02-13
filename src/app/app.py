import streamlit as st
import base64
from pathlib import Path



#assistant = st.Page("./pages/assistant.py", title="Asistente", icon="🤖")

event_page = st.Page("./pages/event_page.py", title="Sponsorship of Event", icon="🗓️")
advisory_board = st.Page("./pages/advisory_board_page.py", title="Advisory Board", icon="👩‍💼")
consulting_services = st.Page("./pages/consulting_services_page.py", title="Consulting Services", icon="💡")
speaking_services = st.Page("./pages/speaking_services_page.py", title="Speaking Services", icon="🗣️")

# path = os.path.join(os.getcwd(), 'src', 'app', 'database', "Accounts with HCP tiering_ES_2025_01_29.xlsx")
# df = pd.read_excel(path)

pg = st.navigation(
    {
    #    "Información": [welcome, doc],
       #"Chatbot": [assistant],
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

# logo_merck = 'logo-merck-kgaa-2015-1.svg'
# logo_path = os.path.join(os.getcwd(), f'src/app/images/{logo_merck}')
# logo_merck_small = "logo-merck-small.png"
# logo_small_path = os.path.join(os.getcwd(), f'src/app/images/{logo_merck_small}')

BASE_DIR = Path(__file__).resolve().parent

logo_merck = 'logo-merck-kgaa-2015-1.svg'

logo_path = BASE_DIR / "images" / logo_merck
logo_merck_small = "logo-merck-small.png"
logo_small_path = BASE_DIR / "images" / logo_merck_small

st.logo(logo_path, 
        link = "https://www.merckgroup.com/en",
        icon_image = logo_small_path, 
        size = "large")

pg.run()