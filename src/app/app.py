import streamlit as st
from datetime import date, datetime


assistant = st.Page("./pages/assistant.py", title="Asistente", icon="🤖")

event_page = st.Page("./pages/event_page.py", title="Sponsorship of Event", icon="🗓️")
advisory_board = st.Page("./pages/advisory_board_page.py", title="Advisory Board", icon="👩‍💼")

pg = st.navigation(
    {
   #    "Información": [welcome, doc],
       "Chatbot": [assistant],
       "Plantillas": [event_page, advisory_board] 
    }
    )

st.set_page_config(
    page_title="Merck",
    page_icon="💊",
    layout="wide"
)

pg.run()