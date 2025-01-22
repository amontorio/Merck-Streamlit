import json
from langchain_community.utilities import SQLDatabase
import pandas as pd
import sqlite3

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)