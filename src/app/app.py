import streamlit as st


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

pg.run()