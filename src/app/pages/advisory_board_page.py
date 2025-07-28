import pandas as pd
import streamlit as st
from streamlit_searchbox import st_searchbox
from datetime import date, timedelta
import uuid
import auxiliar.aux_functions as af
import auxiliar.create_docx as cd
import traceback
import io
import time
import re
import json
from datetime import datetime
import os
import copy
import importlib
import glob

# Recargar el módulo aux_functions para asegurar que se carguen las funciones más recientes
importlib.reload(af)

st.markdown("""
    <style>
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #28a745 !important;  /* Verde */
        color: white !important;
        border-radius: 10px !important;
    }

    .stMultiSelect [data-baseweb="tag"] span {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)



# Diccionario de tarifas según el tier
tarifas = {
    "0": 0, 
    "1": 250,
    "2": 200,
    "3": 150,
    "4": 150,
    "KOL Global": 300
}

# Lista de parámetros obligatorios
mandatory_fields = [
"start_date_ab",
"end_date_ab",
"nombre_evento_ab",
"owner_ab",
"otra_actividad_departamento_ab",
"otra_actividad_otro_departamento_ab",
"desplazamiento_ab",
"alojamiento_ab",
"tipo_evento_ab",
"participantes_ab",
#"descripcion_servicio_ab",
"necesidad_reunion_ab",
"num_participantes_ab",
"criterios_seleccion_ab",
"justificacion_participantes_ab",
"documentosubido_1"
]

# Parámetros dependientes: por ejemplo, si 'alojamiento_ab' es "Sí", se requiere que 'num_noches_ab' y 'hotel_ab' tengan valor.
dependendent_fields = {
    "alojamiento_ab": {
        "condicion": lambda x: x == "Sí",
        "dependientes": ["num_noches_ab", "hotel_ab"]
    },
    "tipo_evento_ab": {
        "condicion": lambda x: x != "Virtual",
        "dependientes": ["sede_ab", "ciudad_ab"]
    }
}

validar_ia ={
        "validar_hotel": {"start_date": "start_date_ab",
                          "end_date": "end_date_ab",
                          "hotel": "hotel_ab"
                          },
        "validar_sede_location": {"start_date":"start_date_ab", 
                                  "end_date": "end_date_ab", 
                                  "sede": "sede_ab"},
        "validar_sede_venue": {"sede": "sede_ab"}
    }

if "errores_ab" not in st.session_state:
    st.session_state.errores_ab = False

if "num_noches_copy_ab" not in st.session_state:
    st.session_state.num_noches_copy_ab = ""


black_list = ["captar", "otorgar", "premio", "regalo", "ventaja", "beneficio", "precio", "Fidelizar", "excluir", "influir", "defensor", "relación", "intercambio", "pago", "retorno de la inversión", "contra ataque", "prescriptor principal", "agradecer", "generoso", "favor", "entretenimiento", "espectáculo", "reemplazar", "expulsar", "forzar", "agresivo", "ilegal", "descuento", "contratar", "Abuso", "Mal uso", "Demandar", "Investigación", "Monopolio", "Antitrust", "Anticompetitivo", "Cartel", "Manipular", "Libre mercado", "Colusión", "Ilegal", "Privilegio", "Concesión", "Agresivo"]  


def save_to_session_state(key, value, key_participante=None, field_participante=None):
    if key != "participantes_ab":
        if key not in ["documentosubido_1", "documentosubido_2"]:
            st.session_state[key] = value
        st.session_state["form_data_advisory_board"][key] = value
    else:
        st.session_state[field_participante] = value
        st.session_state["form_data_advisory_board"][key][key_participante][field_participante] = value
        st.session_state[f"session_ab_{key_participante}"] = True
#dario: nueva funcion para serializar para guardar en json
def serialize_dates(obj):
    """Convierte objetos datetime.date a cadenas para la serialización JSON."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (datetime, date)):  # Verificar si es `datetime` o `date`
                obj[key] = value.isoformat()
            elif isinstance(value, dict):
                obj[key] = serialize_dates(value)
            elif isinstance(value, list):
                obj[key] = [serialize_dates(item) for item in value]
    elif isinstance(obj, list):
        obj = [serialize_dates(item) for item in obj]
    return obj

def add_participant():
    # Añadir un nuevo participante con campos inicializados
    id_user = str(uuid.uuid4())
    new_participant = {
        "id": id_user,
        f"nombre_{id_user}": "",
        f"dni_{id_user}": "",
        f"dni_copy_{id_user}": "",
        f"dni_correcto_{id_user}": True,
        f"tier_{id_user}": "0",
        f"centro_trabajo_{id_user}": "",
        f"email_{id_user}": "",
        f"email_copy_{id_user}": "",
        f"email_correcto_{id_user}": True,
        f"cobra_sociedad_{id_user}": "No",
        f"nombre_sociedad_{id_user}": "",
        f"honorarios_{id_user}": 0.0,
        f"preparacion_horas_{id_user}": 0,
        f"preparacion_minutos_{id_user}": 0,
        f"ponencia_horas_{id_user}": 0,
        f"ponencia_minutos_{id_user}": 0,
    }
    
    st.session_state["participantes_ab"].append(new_participant)
    st.session_state["id_participantes"].append(id_user)
    
    # Inicializar participantes_ab en form_data_advisory_board si no existe
    if "participantes_ab" not in st.session_state["form_data_advisory_board"]:
        st.session_state["form_data_advisory_board"]["participantes_ab"] = {}
        
    st.session_state["form_data_advisory_board"]["participantes_ab"][id_user] = new_participant
    if f"dni_{id_user}" not in st.session_state:
        st.session_state[f"dni_{id_user}"] = ""
    if f"email_{id_user}" not in st.session_state:
        st.session_state[f"email_{id_user}"] = ""

########## validaciones especiales
def validacion_completa_dni(id_user):
    dni = st.session_state.get(f"dni_{id_user}", "")
    st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_correcto_{id_user}"] = True
    if dni == "":
        st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_correcto_{id_user}"] = True
        return  # Salimos de la función porque no hay más que validar
    try:
        numero = int(dni[:-1])
        letra = dni[-1].upper()
        letras_validas = "TRWAGMYFPDXBNJZSQVHLCKE"
        letra_correcta = letras_validas[numero % 23]

        if letra != letra_correcta:
            st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_correcto_{id_user}"] = False

    except:
        if dni != "":
            st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_correcto_{id_user}"] = False
        

def validacion_completa_email(id_user):    
        mail = st.session_state.get(f"email_{id_user}", "")
        st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] = True
        if mail == "":
            st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] = True
            return  # Salimos de la función porque no hay más que validar
        try:
            tlds_validos = ['com', 'org', 'net', 'es', 'edu', 'gov', 'info', 'biz']
            tlds_pattern = '|'.join(tlds_validos)
            patron = rf'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?:{tlds_pattern})$'

            matcheo = re.match(patron, mail) 

            if matcheo == None and mail !="":
                st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] = False
        except:
            if mail != "":
                st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] = False
            else:
                st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] = True

def on_change_nombre(id_user):
    if st.session_state["form_data_advisory_board"]["participantes_ab"][f"{id_user}"][f"nombre_{id_user}"] != None:
        if st.session_state.get(f"nombre_{id_user}", "") != "":
            dic = st.session_state.get(f"nombre_{id_user}", "")
            search = dic.get("search", "")
            result = dic.get("result", "")

            if search  == st.session_state["form_data_advisory_board"]["participantes_ab"][id_user].get(f"nombre_{id_user}", "") and result == None:
                st.session_state[f"nombre_{id_user}"]["search"] = " "



def asignacion_nombre(id_user):
    if f'nombre_{id_user}' in st.session_state and st.session_state["form_data_advisory_board"]["participantes_ab"][f"{id_user}"][f"nombre_{id_user}"] not in [None, ""]:
        nombre_ponente = st.session_state["form_data_advisory_board"]["participantes_ab"][f"{id_user}"][f"nombre_{id_user}"]
        st.session_state["form_data_advisory_board"]["participantes_ab"][f"{id_user}"]["name_ponente_ab"] = nombre_ponente
    else:
        st.session_state["form_data_advisory_board"]["participantes_ab"][f"{id_user}"]["name_ponente_ab"] = ""

def handle_fecha_inicio():
    save_to_session_state("start_date_ab", st.session_state["start_date_ab"])
    if st.session_state["start_date_ab"] >= st.session_state["end_date_ab"]:
        save_to_session_state("end_date_ab", st.session_state["start_date_ab"]) 

def handle_dni(id_user):
    save_to_session_state("participantes_ab", st.session_state[f"dni_{id_user}"], id_user, f"dni_copy_{id_user}")
    val = validacion_completa_dni(id_user)
    
    if st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_correcto_{id_user}"] == False:
        st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_{id_user}"] =""
    else:
        st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_{id_user}"] = st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_copy_{id_user}"]
    
    return None

def handle_email(id_user):
    save_to_session_state("participantes_ab", st.session_state[f"email_{id_user}"], id_user, f"email_copy_{id_user}")
    val = validacion_completa_email(id_user)
    
    if st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] == False:
        st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_{id_user}"] =""
    else:
        st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_{id_user}"] = st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_copy_{id_user}"]

    return None

def validacion_num_noches():
    save_to_session_state("num_noches_copy_ab", st.session_state["num_noches_ab"])
    st.session_state.num_noches_correcto_ab = True

    if st.session_state.num_noches_ab.isdigit():
        duracion = (st.session_state["end_date_ab"] - st.session_state["start_date_ab"]).days
        if int(st.session_state.num_noches_ab) > duracion + 1: 
            st.session_state.num_noches_correcto_ab = False
        save_to_session_state("num_noches_ab", st.session_state["num_noches_ab"]) 
            
    else:
        st.session_state["form_data_advisory_board"]["num_noches_ab"] = ""
        st.session_state.num_noches_correcto_ab = False
    
    

if "clicked_ab" not in st.session_state:
    st.session_state.clicked_ab = False

if "errores_generales_ab" not in st.session_state:
    st.session_state.errores_generales_ab = []

if "errores_participantes_ab" not in st.session_state:
    st.session_state.errores_participantes_ab = {}

if "errores_ia_ab" not in st.session_state:
    st.session_state.errores_ia_ab = []

if "errores_ia_ab" not in st.session_state:
    st.session_state.errores_ia_ab = []

if "num_noches_correcto_ab" not in st.session_state:
    st.session_state.num_noches_correcto_ab = True

def generar_toast():
    if st.session_state.clicked_ab == True:
        texto_toast = "Cambios guardados correctamente!"
        st.toast(texto_toast, icon = "✔️")
        st.session_state.clicked_ab = False

@st.dialog("Rellena los campos", width="large")
def single_participante(id_user, info_user, index):
                        nombre = st_searchbox(
                                #label="Buscador de HCO / HCP *",
                                search_function= af.search_function,  # Pasamos df aquí
                                placeholder="Busca un HCO / HCP *",
                                key=f"nombre_{id_user}",
                                edit_after_submit="disabled",
                                default_searchterm= st.session_state["form_data_advisory_board"]["participantes_ab"][f"{id_user}"][f"nombre_{id_user}"] if st.session_state["form_data_advisory_board"]["participantes_ab"][f"{id_user}"][f"nombre_{id_user}"] not in [None, ""] else "",
                                default= st.session_state["form_data_advisory_board"]["participantes_ab"][f"{id_user}"][f"nombre_{id_user}"],

                                reset_function = on_change_nombre(id_user), 
                                submit_function= lambda x: (
                                    save_to_session_state("participantes_ab", af.handle_tier_from_name(st.session_state[f"nombre_{id_user}"]), id_user, f"tier_{id_user}"),
                                    save_to_session_state("participantes_ab", af.handle_dni_from_name(st.session_state[f"nombre_{id_user}"]), id_user, f"dni_{id_user}"),
                                    save_to_session_state("participantes_ab", af.handle_dni_from_name(st.session_state[f"nombre_{id_user}"]), id_user, f"dni_copy_{id_user}"),
                                    save_to_session_state("participantes_ab", af.handle_centro_from_name(st.session_state[f"nombre_{id_user}"]), id_user, f"centro_trabajo_{id_user}"),
                                    save_to_session_state("participantes_ab", st.session_state[f"nombre_{id_user}"], id_user, f"nombre_{id_user}"),
                                ),
                                rerun_on_update=True,
                                rerun_scope="fragment"
                        )     

                        st.session_state["form_data_advisory_board"]["participantes_ab"][f"{id_user}"][f"nombre_{id_user}"] = nombre
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            
                            dni = st.text_input(
                                f"DNI del participante {index + 1}", 
                                value = info_user.get(f"dni_copy_{id_user}", ""),
                                key=f"dni_{id_user}",
                                on_change = lambda: handle_dni(id_user)
                            )
                        
                        if st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_correcto_{id_user}"] == False:
                            st.warning("El DNI introducido no es correcto.", icon="❌")

                        with col2:
                            tier = st.selectbox(
                                f"Tier del participante {index + 1} *", 
                                ["0", "1", "2", "3", "4","KOL Global"],  
                                index= ["0", "1", "2", "3", "4","KOL Global"].index(st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"tier_{id_user}"]) if f"tier_{id_user}" in st.session_state["form_data_advisory_board"]["participantes_ab"][id_user] else 0,
                                key=f"tier_{id_user}"
                            )
                            st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"tier_{id_user}"] = tier

                        col1, col2 = st.columns(2)
                        with col1:
                            centro = st.text_input(
                                f"Centro de trabajo del participante {index + 1} *", 
                                value=info_user.get(f"centro_trabajo_{id_user}", ""), 
                                key=f"centro_trabajo_{id_user}",
                                on_change = lambda: save_to_session_state("participantes_ab", st.session_state[f"centro_trabajo_{id_user}"], id_user, f"centro_trabajo_{id_user}")

                            )
                        with col2:                        
                            email = st.text_input(
                                f"Email del participante {index + 1}", 
                                value = info_user.get(f"email_copy_{id_user}", ""),
                                key=f"email_{id_user}",
                                on_change= lambda: handle_email(id_user)
                            )
                            
                        if st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] == False:
                            st.warning("El email introducido no es correcto.", icon="❌")

                        col1, col2 = st.columns(2)
                        with col1:
                            cobra = st.selectbox(
                                "¿Cobra a través de sociedad? *", 
                                ["", "No", "Sí"], 
                                key=f"cobra_sociedad_{id_user}",
                                index= ["No", "Sí", ""].index(st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"cobra_sociedad_{id_user}"]) if f"cobra_sociedad_{id_user}" in st.session_state["form_data_advisory_board"]["participantes_ab"][id_user] else 0,
                                on_change= lambda: save_to_session_state("participantes_ab", st.session_state[f"cobra_sociedad_{id_user}"], id_user, f"cobra_sociedad_{id_user}")
                            )
                            st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"cobra_sociedad_{id_user}"] = cobra
                            
                            st.markdown('<p style="font-size: 14px;">Tiempo de preparación *</p>', unsafe_allow_html=True)  
                            
                        with col2:                        
                            nombre_sociedad = st.text_input(
                                "Nombre de la sociedad *",
                                value = st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"nombre_sociedad_{id_user}"] if cobra == "Sí" else "",
                                key=f"nombre_sociedad_{id_user}",
                                on_change = lambda: save_to_session_state("participantes_ab","", id_user, f"nombre_sociedad_{id_user}")
                                    if st.session_state[f"cobra_sociedad_{id_user}"] == "No" else 
                                    save_to_session_state("participantes_ab", st.session_state[f"nombre_sociedad_{id_user}"], id_user, f"nombre_sociedad_{id_user}"),
                                disabled= cobra == "No"
                            )
                            
                            st.markdown('<p style="font-size: 14px;">Tiempo de ponencia *</p>', unsafe_allow_html=True)  
                        col_prep_horas, col_prep_minutos, col_ponencia_horas, col_ponencia_minutos = st.columns(4)

                        with col_prep_horas:
                            tiempo_prep_horas = st.number_input(
                                label="Horas",
                                min_value=0,
                                step=1,
                                key=f"preparacion_horas_{id_user}",
                                value =st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"preparacion_horas_{id_user}"],
                                on_change = lambda: save_to_session_state("participantes_ab", st.session_state[f"preparacion_horas_{id_user}"], id_user, f"preparacion_horas_{id_user}")

                            )                            
                        with col_prep_minutos:
                            
                            tiempo_prep_minutos = st.selectbox(
                                label="Minutos",
                                options=[0,15,30,45],
                                key=f"preparacion_minutos_{id_user}",
                                index= [0,15,30,45].index(st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"preparacion_minutos_{id_user}"]) if f"preparacion_minutos_{id_user}" in st.session_state["form_data_advisory_board"]["participantes_ab"][id_user] else 0,
                                on_change = lambda: save_to_session_state("participantes_ab", st.session_state[f"preparacion_minutos_{id_user}"], id_user, f"preparacion_minutos_{id_user}")
                            )
                            st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"preparacion_minutos_{id_user}"] = tiempo_prep_minutos
                            
                        with col_ponencia_horas:
                            tiempo_ponencia_horas = st.number_input(
                                label="Horas",
                                min_value=0,
                                step=1,
                                key=f"ponencia_horas_{id_user}",
                                value =st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"ponencia_horas_{id_user}"],
                                on_change = lambda: save_to_session_state("participantes_ab", st.session_state[f"ponencia_horas_{id_user}"], id_user, f"ponencia_horas_{id_user}")
                            )
                            
                        with col_ponencia_minutos:
                            tiempo_ponencia_minutos = st.selectbox(
                                label="Minutos",
                                options=[0,15,30,45],
                                key=f"ponencia_minutos_{id_user}",
                                index= [0,15,30,45].index(st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"ponencia_minutos_{id_user}"]) if f"ponencia_minutos_{id_user}" in st.session_state["form_data_advisory_board"]["participantes_ab"][id_user] else 0,
                                on_change = lambda: save_to_session_state("participantes_ab", st.session_state[f"ponencia_minutos_{id_user}"], id_user, f"ponencia_minutos_{id_user}")
                            )
                            st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"ponencia_minutos_{id_user}"] = tiempo_ponencia_minutos

                            
                                
                        tiempo_ponencia_horas = tiempo_ponencia_horas + tiempo_ponencia_minutos / 60
                        tiempo_prep_horas = tiempo_prep_horas + tiempo_prep_minutos / 60

                        # Obtener tarifa en función del tier
                        tarifa = tarifas.get(tier, 0)  # Si no encuentra el tier, usa 0

                        # Calcular honorarios
                        honorarios = (tiempo_ponencia_horas + tiempo_prep_horas) * tarifa
                        
                        honorarios = st.number_input(
                            "Honorarios (€)", 
                            value= float(honorarios), 
                            min_value=0.0, 
                            step=0.01, 
                            key=f"honorarios_{id_user}",
                            disabled=True
                        )
                        st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"honorarios_{id_user}"] = honorarios     

                        if st.button("Guardar cambios", type="primary", use_container_width=True):
                            validacion_completa_email(id_user)
                            validacion_completa_dni(id_user)
                            if st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_correcto_{id_user}"] == False or \
                                st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] == False :
                                st.rerun(scope="fragment")
                            else:
                                st.session_state.clicked_ab = True
                                st.rerun()

def participantes_section():
    st.header("5. Agregar datos de participantes", divider=True)

    if st.button("Agregar participante", use_container_width=True, icon="➕", key="add_participant_button"):
        add_participant()

    index = 0
    # Renderizar los participantes_ab
    for info_user in st.session_state["participantes_ab"]:
        id_user = info_user["id"]

        col_participant, col_remove_participant_individual = st.columns([10,1])
        with col_participant:
            #asignacion_nombre(id_user)
            nombre_expander_ab = st.session_state['form_data_advisory_board']['participantes_ab'][f'{id_user}'][f"nombre_{id_user}"]
            if nombre_expander_ab != "":
                aux = ": "
            else:
                aux = ""

            generar_toast()

            if st.button(label=f"Participante {index + 1}{aux}{nombre_expander_ab}", use_container_width=True, icon="👩‍⚕️"):
                single_participante(id_user, info_user, index)
                if st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_correcto_{id_user}"] == False:
                    st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_{id_user}"] = ""
                if st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] == False:
                    st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_{id_user}"] = ""

        index +=1
        with col_remove_participant_individual:
            if st.button("🗑️", key=f"remove_participant_{id_user}", use_container_width=True, type="secondary"):
                if id_user in st.session_state["form_data_advisory_board"]["participantes_ab"].keys():
                    del st.session_state["form_data_advisory_board"]["participantes_ab"][id_user]
                    st.session_state["participantes_ab"] = list(filter(lambda x: x['id'] != id_user, st.session_state["participantes_ab"]))

                st.rerun()


if "form_data_advisory_board" not in st.session_state:
    field_defaults = {
        "nombre_evento_ab": "",
        "owner_ab": "",
        "delegate_ab": "",
        "start_date_ab": date.today(),
        "end_date_ab": date.today(),
        "estado_aprobacion_ab": "",
        "otra_actividad_departamento_ab": "", #
        "otra_actividad_otro_departamento_ab": "", #
        "desplazamiento_ab": "", #
        "alojamiento_ab": "",  #
        "num_noches_ab": "",
        "hotel_ab": "",
        "tipo_evento_ab": "", #
        "num_participantes_ab": 0
    }

    st.session_state["form_data_advisory_board"] = {}   
    st.session_state["id_participantes"] = [] 
    st.session_state["download_enabled_ab"] = False
    st.session_state["path_doc_ab"] = None
    st.session_state["tipo_evento_ab"] = "Virtual"

    for key, value in field_defaults.items():
        save_to_session_state(key, value)

    if "participantes_ab" not in st.session_state:
        st.session_state.participantes_ab = []
    add_participant()
        

af.show_main_title(title="Advisory Board", logo_size=200)


st.header("1. Detalles del Evento", divider=True)
col1, col2 = st.columns(2)
with col1:
    st.text_input(
        "Owner *",
        value=st.session_state["form_data_advisory_board"]["owner_ab"],
        key="owner_ab",
        on_change=lambda: save_to_session_state("owner_ab", st.session_state["owner_ab"])
    )
with col2:
    st.text_input(
        "Delegate",
        value=st.session_state["form_data_advisory_board"]["delegate_ab"],
        key="delegate_ab",
        on_change=lambda: save_to_session_state("delegate_ab", st.session_state["delegate_ab"])
    )
st.text_input("Nombre del evento*", 
              max_chars=255, 
              key="nombre_evento_ab",
              value= st.session_state["form_data_advisory_board"]["nombre_evento_ab"] if "nombre_evento_ab" in st.session_state["form_data_advisory_board"] else "",
              on_change=lambda: save_to_session_state("nombre_evento_ab", st.session_state["nombre_evento_ab"]))


col1, col2 = st.columns(2)

def dias_habiles_entre(fecha_inicio, fecha_fin):
    dias_habiles = 0
    fecha_actual = fecha_inicio
    while fecha_actual < fecha_fin:
        if fecha_actual.weekday() < 5:  # 0-4 son lunes a viernes
            dias_habiles += 1
        fecha_actual += timedelta(days=1)
    return dias_habiles

def valor_fecha(start_ab):
    if start_ab != None:
        if st.session_state["form_data_advisory_board"]["end_date_ab"] == None:
            st.session_state["form_data_advisory_board"]["end_date_ab"] = start_ab
        if st.session_state["form_data_advisory_board"]["end_date_ab"] < start_ab:
            value = start_ab
        else:
            value = st.session_state["form_data_advisory_board"]["end_date_ab"]
    else:
        value = None
    return value

with col1:
    start_ab = st.date_input("Fecha de inicio del evento *",
                  value=st.session_state["form_data_advisory_board"]["start_date_ab"],
                  key="start_date_ab",
                  on_change= handle_fecha_inicio,
                  format = "DD/MM/YYYY")
    if st.session_state["form_data_advisory_board"]["start_date_ab"] == date.today():
        st.warning(f"Revisa que la fecha de inicio del evento introducida sea correcta.")

with col2:
    #end_date_value = valor_fecha(start_ab)
    st.date_input("Fecha de fin del evento *",
                  #value = end_date_value,
                  value= start_ab if st.session_state["form_data_advisory_board"]["end_date_ab"] < start_ab else st.session_state["form_data_advisory_board"]["end_date_ab"],
                  min_value = start_ab,
                  key="end_date_ab",
                  on_change=lambda: save_to_session_state("end_date_ab", st.session_state["end_date_ab"]),
                  format = "DD/MM/YYYY")

    if st.session_state["form_data_advisory_board"]["end_date_ab"] == date.today():
        st.warning(f"Revisa que la fecha de fin del evento introducida sea correcta.")

start_date = st.session_state["form_data_advisory_board"]["start_date_ab"]
hoy = date.today()
dias_habiles = dias_habiles_entre(hoy, start_date)

#if (st.session_state["form_data_advisory_board"]["start_date_ab"] - date.today()).days < 10:
if dias_habiles < 10:
    st.warning(f"Recuerda que esta actividad deberá ser aprobada en IHUB por el director de la Unidad al no cumplir el plazo de registro de al menos 10 días hábiles de antelación al evento.")

# col1, col2 = st.columns(2)
# with col1:
st.selectbox("Tipo de evento *",
                ["", "Virtual", "Presencial", "Híbrido"],
                key="tipo_evento_ab",
                index= ["Virtual", "Presencial", "Híbrido", ""].index(st.session_state["form_data_advisory_board"]["tipo_evento_ab"]) if "tipo_evento_ab" in st.session_state["form_data_advisory_board"] else 0,
                on_change=lambda: (
                    save_to_session_state("tipo_evento_ab", st.session_state["tipo_evento_ab"]),
                    save_to_session_state("sede_ab", ""),
                    save_to_session_state("ciudad_ab", "")
                ) if st.session_state["tipo_evento_ab"] == "Virtual" else 
                    save_to_session_state("tipo_evento_ab", st.session_state["tipo_evento_ab"]))

col1, col2 = st.columns(2)
with col1:
    st.text_input(
        "Sede *",
        max_chars=255,
        key="sede_ab",
        disabled=st.session_state["form_data_advisory_board"]["tipo_evento_ab"] == "Virtual",
        value="" if st.session_state["form_data_advisory_board"]["tipo_evento_ab"] == "Virtual" else st.session_state["form_data_advisory_board"].get("sede_ab", ""),
        on_change=lambda: save_to_session_state("sede_ab", st.session_state["sede_ab"])
    )
with col2:
    st.text_input(
        "Ciudad *",
        max_chars=255,
        key="ciudad_ab",
        disabled=st.session_state["form_data_advisory_board"]["tipo_evento_ab"] == "Virtual",
        value="" if st.session_state["form_data_advisory_board"]["tipo_evento_ab"] == "Virtual" else st.session_state["form_data_advisory_board"].get("ciudad_ab", ""),
        on_change=lambda: save_to_session_state("ciudad_ab", st.session_state["ciudad_ab"])
    )




st.header("2. Detalles de la Actividad", divider=True)
col1, col2 = st.columns(2)

with col1:
    st.text_input("Producto asociado",
                  max_chars=255,
                  key="producto_asociado_ab",
                  value= st.session_state["form_data_advisory_board"]["producto_asociado_ab"] if "producto_asociado_ab" in st.session_state["form_data_advisory_board"] else "",
                  on_change=lambda: save_to_session_state("producto_asociado_ab", st.session_state["producto_asociado_ab"]))

with col2:
    st.selectbox("Estado de la aprobación", 
                 ["", "Aprobado", "No Aprobado"], 
                 key="estado_aprobacion_ab", 
                 index= ["", "Aprobado", "No Aprobado"].index(st.session_state["form_data_advisory_board"]["estado_aprobacion_ab"]) if "estado_aprobacion_ab" in st.session_state["form_data_advisory_board"] else 0,
                 on_change=lambda: save_to_session_state("estado_aprobacion_ab", st.session_state["estado_aprobacion_ab"]))


servicio = st.text_area("Descripción del servicio *", 
                 max_chars=4000, 
                 key="descripcion_servicio_ab", 
                 value= f"Advisory Board Participation - {st.session_state['form_data_advisory_board']['nombre_evento_ab']}")
st.session_state["form_data_advisory_board"]["descripcion_servicio_ab"] = servicio

necesidad = st.text_area("Necesidad de la reunión y resultados esperados *",
                 max_chars=4000,
                 key="necesidad_reunion_ab",
                 help = "Describa la necesidad de obtener imput de los participantes y el propósito para el cual se utilizará.",
                 value= st.session_state["form_data_advisory_board"]["necesidad_reunion_ab"] if "necesidad_reunion_ab" in st.session_state["form_data_advisory_board"] else "",
                 on_change=lambda: save_to_session_state("necesidad_reunion_ab", st.session_state["necesidad_reunion_ab"]))

for word in black_list:  
    if word.lower() in necesidad.lower():  
        st.warning(f"La descripción contiene una palabra de la Black List: '{word}'")  
        break

col1, col2 = st.columns(2)

with col1:
    st.selectbox("¿Ha habido alguna actividad en su departamento que haya abordado el mismo tema durante los últimos 12 meses? *", 
                 ["", "No lo sé", "Sí", "No"], 
                 key="otra_actividad_departamento_ab", 
                 index= ["", "No lo sé", "Sí", "No"].index(st.session_state["form_data_advisory_board"]["otra_actividad_departamento_ab"]) if "otra_actividad_departamento_ab" in st.session_state["form_data_advisory_board"] else 0,
                 on_change=lambda: save_to_session_state("otra_actividad_departamento_ab", st.session_state["otra_actividad_departamento_ab"]))
with col2:
    st.selectbox("¿Y en otro departamento? *",
                 ["", "No lo sé", "Sí", "No"],
                 key="otra_actividad_otro_departamento_ab",
                 index= ["", "No lo sé", "Sí", "No"].index(st.session_state["form_data_advisory_board"]["otra_actividad_otro_departamento_ab"]) if "otra_actividad_otro_departamento_ab" in st.session_state["form_data_advisory_board"] else 0,
                 on_change=lambda: save_to_session_state("otra_actividad_otro_departamento_ab", st.session_state["otra_actividad_otro_departamento_ab"]))

st.header("3. Detalle nº participantes", divider=True)
col1, col2 = st.columns(2)
with col1:
    st.number_input("Nº de participantes *",
                    min_value=0,
                    step=1,
                    key="num_participantes_ab",
                    help="Asegúrese de que se contrate la cantidad necesaria de ponentes para brindar los servicios que satisfacen las necesidades  legítimas.",
                    value= st.session_state["form_data_advisory_board"]["num_participantes_ab"] if "num_participantes_ab" in st.session_state["form_data_advisory_board"] else "",
                    on_change=lambda: save_to_session_state("num_participantes_ab", st.session_state["num_participantes_ab"]))
with col2:

    st.multiselect(
        "Criterios de selección *",
        [
            "Experiencia como ponente", "Experiencia como Participante de Advisory",
            "Experiencia como profesor", "Experiencia clínica en tema a tratar", "Especialista en tema a tratar", "Especialidad Médica relacionada con el área terapéutica en la que se basa la actividad"
        ],
        key="criterios_seleccion_ab",
        default=st.session_state["form_data_advisory_board"]["criterios_seleccion_ab"] if "criterios_seleccion_ab" in st.session_state["form_data_advisory_board"] else [],
        on_change=lambda: save_to_session_state("criterios_seleccion_ab", st.session_state["criterios_seleccion_ab"])
    )

if int(st.session_state.num_participantes_ab) > 9:
    st.warning("Recueda comunicar a Farmaindustria antes de 10 días hábiles del evento los proyectos que compartan objetivo, método y enfoque, con la participación remunerada de al menos 10 profesionales sanitarios en el marco temporal de un año.")

st.text_area("Justificación de número de participantes *",
             max_chars=4000,
             key="justificacion_participantes_ab",
             help="Asegúrese de que se contrate la cantidad necesaria de ponentes para brindar los servicios que satisfacen las necesidades  legítimas.",
             value= st.session_state["form_data_advisory_board"]["justificacion_participantes_ab"] if "justificacion_participantes_ab" in st.session_state["form_data_advisory_board"] else "",
             on_change=lambda: save_to_session_state("justificacion_participantes_ab", st.session_state["justificacion_participantes_ab"]))
    

st.header("4. Logística de los participantes", divider=True)
col1, col2 = st.columns(2)
with col1:
    st.selectbox("¿Desplazamiento de participantes? *", 
                 ["", "No", "Sí"], 
                 key="desplazamiento_ab",
                 index= ["", "No", "Sí"].index(st.session_state["form_data_advisory_board"]["desplazamiento_ab"]) if "desplazamiento_ab" in st.session_state["form_data_advisory_board"] else 0,
                 on_change=lambda: save_to_session_state("desplazamiento_ab", st.session_state["desplazamiento_ab"]))
with col2:
    st.selectbox("¿Alojamiento de participantes? *",
                 ["", "No", "Sí"],
                 key="alojamiento_ab",
                 index= ["", "No", "Sí"].index(st.session_state["form_data_advisory_board"]["alojamiento_ab"]) if "alojamiento_ab" in st.session_state["form_data_advisory_board"] else 0,
                 on_change=lambda: (
                     save_to_session_state("alojamiento_ab", st.session_state["alojamiento_ab"]),
                     save_to_session_state("hotel_ab", ""),
                     save_to_session_state("num_noches_ab", "")
                 ) if st.session_state["alojamiento_ab"] == "No" else 
                     save_to_session_state("alojamiento_ab", st.session_state["alojamiento_ab"]))


with col1:
    alojam = st.text_input("Nº de noches *", 
        key="num_noches_ab", 
        disabled=st.session_state["form_data_advisory_board"]["alojamiento_ab"] == "No",
        value= "" if st.session_state["form_data_advisory_board"]["alojamiento_ab"] == "No" else st.session_state["form_data_advisory_board"].get("num_noches_copy_ab"),
        help = "Se debe introducir un número.",
        on_change = lambda: validacion_num_noches()
    )

noches = (st.session_state["end_date_ab"] - st.session_state["start_date_ab"]).days + 1
if st.session_state.num_noches_correcto_ab == False:
    st.warning(f"El número de noches no puede exceder la duración del evento ({noches} días).")
    
with col2:
    st.text_input(
        "Hotel *",
        max_chars=255,
        key="hotel_ab",
        disabled=st.session_state["form_data_advisory_board"]["alojamiento_ab"] == "No",
        value="" if st.session_state["form_data_advisory_board"]["alojamiento_ab"] == "No" else st.session_state["form_data_advisory_board"].get("hotel_ab", ""),
        on_change=lambda: save_to_session_state("hotel_ab", st.session_state["hotel_ab"])
    )                      


participantes_section()

st.header("6. Documentos", divider=True)
with st.expander("Ver documentos necesarios"):
    st.file_uploader("Programa del evento *", type=["pdf", "docx", "xlsx", "ppt"], key="documentosubido_1", on_change=lambda: save_to_session_state("documentosubido_1", st.session_state["documentosubido_1"]))
    st.file_uploader("Documentos adicionales", type=["pdf", "docx", "xlsx", "ppt"], key="documentosubido_2", on_change=lambda: save_to_session_state("documentosubido_2", st.session_state["documentosubido_2"]), accept_multiple_files = True)


# Estado inicial para el botón de descargar
st.session_state.download_enabled_ab = False

def generacion_errores():
    try:
        st.session_state.download_enabled_ab = False
        errores_general, errores_participantes = af.validar_campos(st.session_state["form_data_advisory_board"], mandatory_fields, dependendent_fields)
        errores_ia = af.validar_campos_ia(st.session_state["form_data_advisory_board"], validar_ia)
        if not errores_general and all(not lista for lista in errores_participantes.values()) and not errores_ia:
            doc, st.session_state.path_doc_ab = cd.crear_documento_advisory(st.session_state["form_data_advisory_board"])
            st.session_state.download_enabled_ab = True
    except Exception as e:
        traceback.print_exc()
        st.toast(f"Ha ocurrido un problema al generar el formulario -> {e}", icon="❌")

    return errores_general, errores_participantes, errores_ia

def mostrar_errores(errores_general, errores_participantes, errores_ia):
    try:
        errores_general, errores_participantes = af.validar_campos(st.session_state["form_data_advisory_board"], mandatory_fields, dependendent_fields)
    except Exception as e:
        traceback.print_exc()
    if not errores_general and all(not lista for lista in errores_participantes.values()) and not errores_ia:
        st.session_state.download_enabled_ab = True
    else:
        if len(errores_general) != 0:
            msg_general = "\n**Errores Generales del Formulario**\n"
            for msg in errores_general:
                msg_general += f"\n* {msg}\n"
            st.error(msg_general)

        if len(errores_participantes)>0:
            for id_user, list_errors in errores_participantes.items():
                if len(list_errors) > 0:
                    # Obtener el diccionario de participantes
                    participantes = st.session_state['form_data_advisory_board']['participantes_ab']

                    # Obtener la posición del ID en las claves del diccionario
                    keys_list = list(participantes.keys())  # Convertir las claves en una lista
                    posicion = keys_list.index(id_user) + 1 if id_user in keys_list else None
                    if posicion != None:
                        name_ponente = st.session_state['form_data_advisory_board']['participantes_ab'][f'{keys_list[posicion-1]}'][f'nombre_{id_user}'].strip()
                        msg_participantes = f"\n**Errores del Participante {posicion}:{name_ponente}**\n"
                        for msg in list_errors:
                            msg_participantes += f"\n* {msg}\n"
                        st.error(msg_participantes)

        if len(errores_ia) > 0:
            msg_aviso = "\n**Errores detectados con IA**\n"
            for msg in errores_ia:
                msg_aviso += f"\n* {msg}\n"
            st.error(msg_aviso)
                    

# Botón para enviar
def button_form():
    if st.button(label="Generar Plantilla", use_container_width=True, type="primary"):
        st.session_state.errores_ab = True
        with st.status("Validando campos...", expanded=True, state = "running") as status:
            st.write("Validando información general del formulario...")
            time.sleep(1.5)
            st.write("Validando campos obligatorios y dependientes...")
            time.sleep(1.5)
            st.write("Validando información de los ponentes...")
            time.sleep(1.5)
            st.write("Validando contenido de campos con IA...")
            time.sleep(1.5)
        
            errores_general_ab, errores_participantes_ab, errores_ia_ab = generacion_errores()
            st.session_state.errores_general_ab, st.session_state.errores_participantes_ab, st.session_state.errores_ia_ab = errores_general_ab, errores_participantes_ab, errores_ia_ab

            st.write("Guardando formulario en el historial...")
            time.sleep(1.5)

            # Actualizo el estado
            if st.session_state.download_enabled_ab == True:
                status.update(
                    label="Validación completada!", state="complete", expanded=False
                )
                #dario: guardar el formulario si se ha verificado (en el historial)
                formulario_tipo = "advisory_board"  # Cambia según el tipo de formulario
                user_id = st.session_state.get("user_id", "default_user") #### CAMBIAR CUANDO SE INTEGRE EN CLIENTE
                fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
                

                datos = copy.deepcopy(st.session_state["form_data_advisory_board"]) # Cambia según el tipo de formulario
                datos_ser = serialize_dates(datos)
                datos_ser["user_id"] = user_id
                datos_ser["formulario_tipo"] = formulario_tipo
                datos_ser["documentosubido_1"] = ""
                datos_ser["documentosubido_2"] = ""
                ruta= os.path.join("historial",f"{user_id}_{formulario_tipo}_{fecha_actual}.json" )
                with open(ruta, "w") as f:
                    json.dump(datos_ser, f)
                st.session_state.errores_event = False
                st.session_state.errores_ab = False
            else:
                status.update(
                    label="Validación no completada. Se deben revisar los campos obligatorios faltantes.", state="error", expanded=False
                )
                st.session_state.errores_ab = True
                st.toast("Se deben corregir los errores.", icon="❌")

            if st.session_state.download_enabled_ab == True:
                st.toast("Formulario generado correctamente", icon="✔️")

    if st.session_state.errores_ab == True:
        mostrar_errores(st.session_state.errores_general_ab, st.session_state.errores_participantes_ab, st.session_state.errores_ia_ab)     

        
def download_document():
    if st.session_state.path_doc_ab:
        with open(st.session_state.path_doc_ab, "rb") as file:
            st.download_button(
                label="Descargar ZIP",
                data=file,
                file_name= f"Advisory_Board - {st.session_state['form_data_advisory_board']['nombre_evento_ab']}.zip",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                icon="📥",
                disabled=disabled
            )
    else:
        st.download_button(
            label="Descargar ZIP",
            data=io.BytesIO(),
            file_name="documento_advisory_board.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            icon="📥",
            disabled=True
        )
        
button_form()
# Botón de descarga
disabled = not st.session_state.download_enabled_ab
if disabled == False:
    download_document()

#st.header("Datos guardados")
#st.write(st.session_state["form_data_advisory_board"])

#dario: función para encontrar formulario existente por nombre y fechas
def encontrar_formulario_existente(user_id, formulario_tipo, nombre_evento, start_date, end_date):
    """
    Busca un formulario existente basado en nombre del evento y fechas de inicio/fin
    """
    directorio = "formularios_guardados"
    if not os.path.exists(directorio):
        return None
        
    # Convertir fechas a string para comparación
    start_date_str = start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date)
    end_date_str = end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date)
    
    # Buscar archivos del usuario y tipo de formulario
    patron = f"{user_id}_{formulario_tipo}_*.json"
    archivos = glob.glob(os.path.join(directorio, patron))
    
    for archivo in archivos:
        try:
            with open(archivo, "r") as f:
                datos = json.load(f)
                
            # Comparar nombre del evento y fechas
            if (datos.get("nombre_evento_ab", "") == nombre_evento and
                datos.get("start_date_ab", "") == start_date_str and
                datos.get("end_date_ab", "") == end_date_str):
                return archivo
        except:
            continue
    
    return None

#dario: Botón y funcionalidades para guardar el formulario   
if st.sidebar.button("Guardar borrador", use_container_width=True, icon="💾"):
    formulario_tipo = "advisory_board"  # Cambia según el tipo de formulario
    user_id = st.session_state.get("user_id", "default_user") #### CAMBIAR CUANDO SE INTEGRE EN CLIENTE
    
    datos = copy.deepcopy(st.session_state["form_data_advisory_board"]) # Cambia según el tipo de formulario
    datos_ser = serialize_dates(datos)
    datos_ser["user_id"] = user_id
    datos_ser["formulario_tipo"] = formulario_tipo
    datos_ser["documentosubido_1"] = "" #esto se hace para que no se guarden los documentos
    datos_ser["documentosubido_2"] = ""
    
    # Buscar si ya existe un formulario con el mismo nombre y fechas
    archivo_existente = encontrar_formulario_existente(
        user_id, 
        formulario_tipo, 
        datos_ser.get("nombre_evento_ab", ""),
        datos_ser.get("start_date_ab", ""),
        datos_ser.get("end_date_ab", "")
    )
    
    if archivo_existente:
        # Actualizar el archivo existente
        ruta = archivo_existente
        mensaje = "Borrador actualizado exitosamente!"
        icono = "🔄"
    else:
        # Crear nuevo archivo
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta = os.path.join("formularios_guardados", f"{user_id}_{formulario_tipo}_{fecha_actual}.json")
        mensaje = "Borrador guardado exitosamente!"
        icono = "✔️"
    
    with open(ruta, "w") as f:
        json.dump(datos_ser, f)
    st.toast(mensaje, icon=icono)

