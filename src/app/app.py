import streamlit as st
import os

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

pg.run()