import streamlit as st


assistant = st.Page("./pages/assistant.py", title="Asistente", icon="🤖")

form1 = st.Page("./pages/form1.py", title="Plantilla 1", icon="🤖")

pg = st.navigation(
    {
   #    "Información": [welcome, doc],
       "Chatbot": [assistant],
       "Plantillas": [form1] 
    }
    )

st.set_page_config(
    page_title="Merck",
    page_icon="🤖",
)

pg.run()