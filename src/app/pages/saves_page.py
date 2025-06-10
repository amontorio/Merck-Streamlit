import streamlit as st
import os
import glob
import pandas as pd
import json
from datetime import datetime, date

user_id = st.session_state.get("user_id", "default_user")
directorio_formularios = "formularios_guardados"

patron_archivo = os.path.join(directorio_formularios, f"{user_id}_*.json")
archivos_guardados = glob.glob(patron_archivo)

directorio_historial = "historial"

patron_historial = os.path.join(directorio_historial, f"{user_id}_*.json")
historiales_guardados = glob.glob(patron_historial)

historiales_data=[]

formularios_data = []
tipos_validos = [
    "speaking_services_paraguas",
    "speaking_services_merck",
    "consulting_services",
    "event",
    "advisory_board"
]
mapeo_paginas = {
    "speaking services paraguas": "./pages/speaking_services_page.py",
    "speaking services merck": "./pages/speaking_services_page.py",
    "consulting services": "./pages/consulting_services_page.py",
    "event": "./pages/event_page.py",
    "advisory board": "./pages/advisory_board_page.py"
}

def deserialize_dates(obj):
    """Convierte cadenas de fecha y hora en objetos `datetime.date` o `datetime.datetime`."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str):
                    try:
                        obj[key] = date.fromisoformat(value)
                    except ValueError:
                        pass  # Si falla, no cambia la cadena ya que no es una fecha
            elif isinstance(value, dict):
                obj[key] = deserialize_dates(value)
            elif isinstance(value, list):
                obj[key] = [deserialize_dates(item) for item in value]
    elif isinstance(obj, list):
        obj = [deserialize_dates(item) for item in obj]
    return obj

for archivo_path in archivos_guardados:
    tipo_formulario = "Desconocido"
    nombre_formulario = os.path.basename(archivo_path)
    for tipo in tipos_validos:
        if tipo in nombre_formulario:
            tipo_formulario = tipo.replace('_', ' ')
            break
    fecha_guardado = datetime.fromtimestamp(os.path.getmtime(archivo_path)).strftime('%Y-%m-%d %H:%M:%S')
    
    formularios_data.append({
        "Tipo de formulario": tipo_formulario,
        "Fecha de guardado": fecha_guardado,
        "Archivo Path": archivo_path
    })

formularios_df = pd.DataFrame(formularios_data)

st.markdown(f"""
<h6 style="margin-top: 0; margin-bottom: 0px;">
<h3 style="margin-bottom: 0;">Borradores guardados ({user_id})</h3>
<hr style="margin-top: 0; margin-bottom: 50px;">
""", unsafe_allow_html=True)

st.markdown("##### 📄Lista de borradores")

# Recorriendo cada formulario para añadir botones
for index, row in formularios_df.iterrows():
    cols = st.columns([3, 1, 1])
    with cols[0]:
        st.write(f"{row['Tipo de formulario']} - {row['Fecha de guardado']}")
    with cols[1]:
        if st.button("✏️", key=f"edit_form_{index}", use_container_width=True):
            
            archivo_path = row['Archivo Path']
            
            with open(archivo_path, 'r') as f:
                form_data = json.load(f)

            form_data = deserialize_dates(form_data)
            
            tipo_formulario = row['Tipo de formulario']
            # Redirigir basado en tipo de formulario usando mapeo
            if tipo_formulario in mapeo_paginas:
                
                pagina=mapeo_paginas[tipo_formulario] 
            
                if tipo_formulario == "speaking services paraguas" or tipo_formulario == "speaking services merck":
                    st.session_state["form_data_speaking_services"]= form_data
                    
                else:
                    clave_session = f"form_data_{tipo_formulario.replace(' ', '_')}"
                    st.session_state[clave_session] = form_data

                if tipo_formulario == "speaking services paraguas":
                    lista_de_valores = list(form_data["participantes_ss"].values())   ##### hay que adaptarlo a cada form
                    st.session_state["participantes_ss"] = lista_de_valores
                if tipo_formulario == "speaking services merck":
                    lista_de_valores = list(form_data["participantes_ss"].values())   ##### hay que adaptarlo a cada form
                    st.session_state["participantes_ss"] = lista_de_valores
                if tipo_formulario == "advisory board":
                    lista_de_valores = list(form_data["participantes_ab"].values())   ##### hay que adaptarlo a cada form
                    st.session_state["participantes_ab"] = lista_de_valores
                    #print(lista_de_valores)
                if tipo_formulario == "consulting services":
                    lista_de_valores = list(form_data["participantes_cs"].values())   ##### hay que adaptarlo a cada form
                    st.session_state["participantes_cs"] = lista_de_valores
                if tipo_formulario == "event":
                    st.session_state["email_correcto"] = True

                    #print(lista_de_valores)
                #print(clave_session)
                #st.write(pagina)
                st.switch_page(pagina)
                st.rerun()
            

    with cols[2]:
        if st.button("🗑️", key=f"remove_form_{index}", use_container_width=True):
            # Elimina el archivo del formulario
            os.remove(row['Archivo Path'])
            st.rerun()

for archivo_path in historiales_guardados:
    tipo_formulario = "Desconocido"
    nombre_formulario = os.path.basename(archivo_path)
    for tipo in tipos_validos:
        if tipo in nombre_formulario:
            tipo_formulario = tipo.replace('_', ' ')
            break
    fecha_guardado = datetime.fromtimestamp(os.path.getmtime(archivo_path)).strftime('%Y-%m-%d %H:%M:%S')
    
    historiales_data.append({
        "Tipo de formulario": tipo_formulario,
        "Fecha de guardado": fecha_guardado,
        "Archivo Path": archivo_path
       })
    
historiales_df = pd.DataFrame(historiales_data)

st.markdown("##### ✔️ Historial de formularios completos") 

for index, row in historiales_df.iterrows():
    cols = st.columns([2, 1])
    with cols[0]:
        st.write(f"{row['Tipo de formulario']} - {row['Fecha de guardado']}")
    with cols[1]:
        unique_key = f"edit_form_{index}_{row['Archivo Path']}"
        if st.button("👁️", key=unique_key, use_container_width=True):
            archivo_path = row['Archivo Path']
            with open(archivo_path, 'r') as f:
                form_data = json.load(f)

            form_data = deserialize_dates(form_data)
            
            tipo_formulario = row['Tipo de formulario']
            # Redirigir basado en tipo de formulario usando mapeo
            if tipo_formulario in mapeo_paginas:
                pagina=mapeo_paginas[tipo_formulario]              
                if tipo_formulario == "speaking services paraguas" or tipo_formulario == "speaking services merck":
                    st.session_state["form_data_speaking_services"]= form_data
                else:
                    clave_session = f"form_data_{tipo_formulario.replace(' ', '_')}"
                    st.session_state[clave_session] = form_data

                if tipo_formulario == "speaking services paraguas":
                    lista_de_valores = list(form_data["participantes_ss"].values())   ##### hay que adaptarlo a cada form
                    st.session_state["participantes_ss"] = lista_de_valores
                if tipo_formulario == "speaking services merck":
                    
                    lista_de_valores = list(form_data["participantes_ss"].values())   ##### hay que adaptarlo a cada form
                    st.session_state["participantes_ss"] = lista_de_valores
                if tipo_formulario == "advisory board":
                    lista_de_valores = list(form_data["participantes_ab"].values())   ##### hay que adaptarlo a cada form
                    st.session_state["participantes_ab"] = lista_de_valores
                    #print(lista_de_valores)
                if tipo_formulario == "consulting services":
                    lista_de_valores = list(form_data["participantes_cs"].values())   ##### hay que adaptarlo a cada form
                    st.session_state["participantes_cs"] = lista_de_valores

                if tipo_formulario == "event":
                    
                    st.session_state["email_correcto"] = True
                    
                #print(clave_session)
                #st.write(pagina)
                st.switch_page(pagina)