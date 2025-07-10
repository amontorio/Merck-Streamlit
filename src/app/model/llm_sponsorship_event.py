from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from functools import lru_cache
import auxiliar.aux_functions as af
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureChatOpenAI
import os
import streamlit as st

load_dotenv()


def run_query(query):
    db = af.db_connection.get_db()
    return db.run(query)

def clean_query(query):
    return query.replace("```sql", "").replace("```", "").replace("[SQL:", "").replace("]", "").strip()

@st.cache_resource
def get_llm():
    azure_endpoint = str(os.getenv("APP_SERVICE_NLP_API_URL", "")).rstrip("/")
    api_key = os.getenv("APP_SERVICE_NLP_API_KEY", "")

    return AzureChatOpenAI(
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    azure_deployment="gpt-4o-mini",  # or your deployment
    api_version="2024-08-01-preview",  # or your api version
    temperature=0
)


def invoke_chain_event_description(event_name, start_date, end_date, venue, city, organization_name, event_objetive):
    
    llm = get_llm()
    
    prompt_objetivo = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Tu trabajo es escribir en un campo de un formulario un breve texto. Para ello debes sintetizar la información utilizando la información que te voy a pasar a continuación.
                - Nombre del evento: {event_name}
                - Fecha de inicio: {start_date}
                - Fecha de fin: {end_date}
                - Sede: {venue}
                - Ciudad:{city}
                - Organización: {organization_name}
                - Descripción y objetivos: {event_objetive}
                
                El nombre del evento debe comenzar siempre por "Sponsorship of Event/Activity" en inglés
                Si alguno de los campos está vacío. No lo incluyas en tu descripción. 
                No incluyas información adicional al texto. Debe ser escrito como si el usuario lo hubiera rellenado.
                Debes responder en uno o dos párrafos en lenguaje natural. No realices bullet points
                Responde en español
                """,
            ),
            ("user", "{input}"),
        ]
    )

    chain_objetivo = prompt_objetivo | llm | StrOutputParser()
    
    res = chain_objetivo.invoke({"input": "Responde de forma clara",
                                "event_name": event_name,
                                "start_date": start_date,
                                "end_date": end_date,
                                "venue": venue,
                                "city": city,
                                "organization_name": organization_name,
                                "event_objetive": event_objetive    
                                })
    print("res", res)
    return res