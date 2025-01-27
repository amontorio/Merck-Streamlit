import json
from httpx import get
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.memory import ChatMessageHistory
from dotenv import load_dotenv
import os
from functools import lru_cache
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase

from sympy import im
import auxiliar.aux_functions as af
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import traceback
import pandas as pd
from langchain_openai import AzureChatOpenAI

load_dotenv()


def run_query(query):
    db = af.db_connection.get_db()
    return db.run(query)

def clean_query(query):
    return query.replace("```sql", "").replace("```", "").replace("[SQL:", "").replace("]", "").strip()

@lru_cache(maxsize=None)
def get_llm():
    #return ChatGroq(model_name="llama3-70b-8192")
    return AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",  # or your deployment
    api_version="2024-08-01-preview",  # or your api version
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

def invoke_chain_event_description(event_name, start_date, end_date, venue, city, organization_name):
    
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
                
                El nombre del evento debe comenzar siempre por "Sponsorship of Event/Activity" en inglés
                Si alguno de los campos está vacío. No lo incluyas en tu descripción. 
                No incluyas información adicional al texto. Debe ser escrito como si el usuario lo hubiera rellenado.
                Responde en español
                """,
            ),
            ("user", "{input}"),
        ]
    )

    chain_objetivo = prompt_objetivo | llm | StrOutputParser()
    
    res = chain_objetivo.invoke({"input": "Di algo",
                                "event_name": event_name,
                                "start_date": start_date,
                                "end_date": end_date,
                                "venue": venue,
                                "city": city,
                                "organization_name": organization_name      
                                })
    print("res", res)
    return res