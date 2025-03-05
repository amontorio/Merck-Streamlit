import pandas as pd
import streamlit as st
from streamlit_searchbox import st_searchbox
from datetime import date
import unicodedata
import uuid
import auxiliar.aux_functions as af
import auxiliar.create_docx as cd
import traceback
import os
import io
from streamlit.components.v1 import html
import time
import re

# Diccionario de tarifas según el tier
tarifas = {
    "0": 300,  
    "1": 250,
    "2": 200,
    "3": 150,
    "4": 150
}

# Lista de parámetros obligatorios
mandatory_fields = [
        "nombre_necesidades_cs",
        "start_date_cs",
        "end_date_cs",
        "presupuesto_estimado_cs",
        "estado_aprobacion_cs",
        "necesidad_reunion_cs",
        "owner_cs",
        "numero_consultores_cs",
        "criterios_seleccion_cs",
        "documentosubido_1_cs"

]

dependendent_fields = {
    "numero_consultores_cs": {
        "condicion": lambda x: x > 1,
        "dependientes": ["justificacion_numero_participantes_cs"]
    },
}

black_list = ["captar", "otorgar", "premio", "regalo", "ventaja", "beneficio", "precio", "Fidelizar", "excluir", "influir", "defensor", "relación", "intercambio", "pago", "retorno de la inversión", "contra ataque", "prescriptor principal", "agradecer", "generoso", "favor", "entretenimiento", "espectáculo", "reemplazar", "expulsar", "forzar", "agresivo", "ilegal", "descuento", "contratar", "Abuso", "Mal uso", "Demandar", "Investigación", "Monopolio", "Antitrust", "Anticompetitivo", "Cartel", "Manipular", "Libre mercado", "Colusión", "Ilegal", "Privilegio", "Concesión", "Agresivo"]  


def render_svg(svg_string):
    """Renders the given svg string."""
    c = st.container()
    with c:
        html(svg_string, height=100, width=50)

def save_to_session_state(key, value, key_participante=None, field_participante=None):
    if key != "participantes_cs":
        if key not in ["documentosubido_1_cs", "documentosubido_2_cs"]:
            st.session_state[key] = value
        st.session_state["form_data_consulting_services"][key] = value
    else:
        st.session_state[field_participante] = value
        st.session_state["form_data_consulting_services"][key][key_participante][field_participante] = value
        
def handle_fecha_inicio():
    save_to_session_state("start_date_cs", st.session_state["start_date_cs"])
    if st.session_state["start_date_cs"] >= st.session_state["end_date_cs"]:
        save_to_session_state("end_date_cs", st.session_state["start_date_cs"]) 


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
        f"cobra_sociedad_{id_user}": "",
        f"nombre_sociedad_{id_user}": "",
        f"honorarios_{id_user}": 0.0,
        f"preparacion_horas_{id_user}": 0,
        f"preparacion_minutos_{id_user}": 0,
        f"ponencia_horas_{id_user}": 0,
        f"ponencia_minutos_{id_user}": 0
    }
    
    st.session_state["participantes_cs"].append(new_participant)
    
    # Inicializar participantes_cs en form_data_consulting_services si no existe
    if "participantes_cs" not in st.session_state["form_data_consulting_services"]:
        st.session_state["form_data_consulting_services"]["participantes_cs"] = {}
        
    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user] = new_participant
    if f"dni_{id_user}" not in st.session_state:
        st.session_state[f"dni_{id_user}"] = ""
    if f"email_{id_user}" not in st.session_state:
        st.session_state[f"email_{id_user}"] = ""



if "errores" not in st.session_state:
    st.session_state["errores"] = False

if "errores_generales_cs" not in st.session_state:
    st.session_state.errores_generales_ss = []

if "errores_participantes_cs" not in st.session_state:
    st.session_state.errores_participantes_ss = []

########## validaciones especiales
def validacion_completa_dni(id_user):
    dni = st.session_state.get(f"dni_{id_user}", "")
    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"dni_correcto_{id_user}"] = True

    try:
        numero = int(dni[:-1])
        letra = dni[-1].upper()
        letras_validas = "TRWAGMYFPDXBNJZSQVHLCKE"
        letra_correcta = letras_validas[numero % 23]

        if letra != letra_correcta and dni != "":
            st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"dni_correcto_{id_user}"] = False
    except:
        if dni != "":
            st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"dni_correcto_{id_user}"] = False

def validacion_completa_email(id_user):    
        mail = st.session_state.get(f"email_{id_user}", "")
        st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"email_correcto_{id_user}"] = True
        try:
            tlds_validos = ['com', 'org', 'net', 'es', 'edu', 'gov', 'info', 'biz']
            tlds_pattern = '|'.join(tlds_validos)
            patron = rf'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?:{tlds_pattern})$'

            matcheo = re.match(patron, mail) 

            if matcheo == None and mail !="":
                st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"email_correcto_{id_user}"] = False
        except:
            if mail != "":
                st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"email_correcto_{id_user}"] = False
        
            
def on_change_nombre(id_user):
    if st.session_state["form_data_consulting_services"]["participantes_cs"][f"{id_user}"][f"nombre_{id_user}"] != None:
        if st.session_state.get(f"nombre_{id_user}", "") != "":
            dic = st.session_state.get(f"nombre_{id_user}", "")
            search = dic.get("search", "")
            result = dic.get("result", "")

            if search  == st.session_state["form_data_consulting_services"]["participantes_cs"][id_user].get(f"nombre_{id_user}", "") and result == None:
                st.session_state[f"nombre_{id_user}"]["search"] = " "


def asignacion_nombre(id_user):
    if f'nombre_{id_user}' in st.session_state and st.session_state["form_data_consulting_services"]["participantes_cs"][f"{id_user}"][f"nombre_{id_user}"] not in [None, ""]:
        nombre_ponente = st.session_state["form_data_consulting_services"]["participantes_cs"][f"{id_user}"][f"nombre_{id_user}"].get("result", "").rsplit('-', 1)[0] 
        st.session_state["form_data_consulting_services"]["participantes_cs"][f"{id_user}"]["name_ponente_cs"] = nombre_ponente
    else:
        st.session_state["form_data_consulting_services"]["participantes_cs"][f"{id_user}"]["name_ponente_cs"] = ""

if "clicked_cs" not in st.session_state:
    st.session_state.clicked_cs = False

def generar_toast():
    if st.session_state.clicked_cs == True:
        texto_toast = "Cambios guardados correctamente!"
        st.toast(texto_toast, icon = "✔️")
        st.session_state.clicked_cs = False

def handle_dni(id_user):
    save_to_session_state("participantes_cs", st.session_state[f"dni_{id_user}"], id_user, f"dni_copy_{id_user}")
    val = validacion_completa_dni(id_user)
    
    if st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"dni_correcto_{id_user}"] == False:
        st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"dni_{id_user}"] = ""
    else:
        st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"dni_{id_user}"] = st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"dni_copy_{id_user}"]
    
    return None

def handle_email(id_user):
    save_to_session_state("participantes_cs", st.session_state[f"email_{id_user}"], id_user, f"email_copy_{id_user}")
    val = validacion_completa_email(id_user)
    
    if st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"email_correcto_{id_user}"] == False:
        st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"email_{id_user}"] = ""
    else:
        st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"email_{id_user}"] = st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"email_copy_{id_user}"]

    return None

@st.dialog("Rellena los campos", width="large")
def single_consultant(id_user, info_user, index):
                        nombre = st_searchbox(
                                #label="Buscador de HCO / HCP *",
                                search_function= af.search_function,  # Pasamos df aquí
                                placeholder="Busca un HCO / HCP *",
                                key=f"nombre_{id_user}",
                                edit_after_submit="disabled",
                                default_searchterm= st.session_state["form_data_consulting_services"]["participantes_cs"][f"{id_user}"][f"nombre_{id_user}"].get("result", "").rsplit('-', 1)[0] if st.session_state["form_data_consulting_services"]["participantes_cs"][f"{id_user}"][f"nombre_{id_user}"] not in [None, ""] else "",
                                reset_function = on_change_nombre(id_user), 
                                submit_function= lambda x: (
                                    save_to_session_state("participantes_cs", af.handle_tier_from_name(st.session_state[f"nombre_{id_user}"]), id_user, f"tier_{id_user}"),
                                    save_to_session_state("participantes_cs", st.session_state[f"nombre_{id_user}"], id_user, f"nombre_{id_user}")
                                ),
                                rerun_on_update=True,
                                rerun_scope="fragment"
                        )     

                        col1, col2 = st.columns(2)
                        
                       
                        with col1:              
                            dni = st.text_input(
                                f"DNI del participante {index + 1}", 
                                value = info_user.get(f"dni_copy_{id_user}", ""),
                                key=f"dni_{id_user}",
                                on_change = lambda: handle_dni(id_user)
                            )

                        if st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"dni_correcto_{id_user}"] == False:
                            st.warning("El DNI introducido no es correcto.", icon="❌")

                        with col2:
                            tier = st.selectbox(
                                f"Tier del participante {index + 1} *", 
                                ["0", "1", "2", "3", "4"], 
                                index= ["0", "1", "2", "3", "4"].index(st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"tier_{id_user}"]) if f"tier_{id_user}" in st.session_state["form_data_consulting_services"]["participantes_cs"][id_user] else 0,
                                key=f"tier_{id_user}"
                            )
                            st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"tier_{id_user}"] = tier
                            
                        col1, col2 = st.columns(2)
                        with col1: 
                            centro = st.text_input(
                                f"Centro de trabajo del participante {index + 1} *", 
                                value=info_user.get(f"centro_trabajo_{id_user}", ""), 
                                key=f"centro_trabajo_{id_user}",
                                on_change = lambda: save_to_session_state("participantes_cs", st.session_state[f"centro_trabajo_{id_user}"], id_user, f"centro_trabajo_{id_user}")

                            )
                        with col2:
                            email = st.text_input(
                                f"Email del participante {index + 1} *", 
                                value = info_user.get(f"email_copy_{id_user}", ""),
                                key=f"email_{id_user}",
                                on_change= lambda: handle_email(id_user))

                        if st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"email_correcto_{id_user}"] == False:
                            st.warning("El email introducido no es correcto.", icon="❌")
                

                        col1, col2 = st.columns(2)
                        with col1: 
                            cobra = st.selectbox(
                                "¿Cobra a través de sociedad? *", 
                                ["", "No", "Sí"], 
                                key=f"cobra_sociedad_{id_user}",
                                index= ["", "No", "Sí"].index(st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"cobra_sociedad_{id_user}"]) if f"cobra_sociedad_{id_user}" in st.session_state["form_data_consulting_services"]["participantes_cs"][id_user] else 0,
                                on_change= lambda: save_to_session_state("participantes_cs", st.session_state[f"cobra_sociedad_{id_user}"], id_user, f"cobra_sociedad_{id_user}")

                            )
                            st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"cobra_sociedad_{id_user}"] = cobra
                            
                            st.markdown('<p style="font-size: 14px;">Tiempo de preparación</p>', unsafe_allow_html=True)  
                            
                        with col2:
                            nombre_sociedad = st.text_input(
                                "Nombre de la sociedad",
                                value = st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"nombre_sociedad_{id_user}"] if cobra == "Sí" else "",
                                key=f"nombre_sociedad_{id_user}",
                                on_change = lambda: save_to_session_state("participantes_cs","", id_user, f"nombre_sociedad_{id_user}")
                                    if st.session_state[f"cobra_sociedad_{id_user}"] == "No" else 
                                    save_to_session_state("participantes_cs", st.session_state[f"nombre_sociedad_{id_user}"], id_user, f"nombre_sociedad_{id_user}"),
                                disabled= cobra == "No"
                            )
                            
                            st.markdown('<p style="font-size: 14px;">Tiempo de ponencia</p>', unsafe_allow_html=True)  
                        col_prep_horas, col_prep_minutos, col_ponencia_horas, col_ponencia_minutos = st.columns(4)

                        with col_prep_horas:
                            tiempo_prep_horas = st.number_input(
                                label="Horas",
                                min_value=0,
                                step=1,
                                key=f"preparacion_horas_{id_user}",
                                value =st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"preparacion_horas_{id_user}"],
                                on_change = lambda: save_to_session_state("participantes_cs", st.session_state[f"preparacion_horas_{id_user}"], id_user, f"preparacion_horas_{id_user}")

                            )
                            
                        with col_prep_minutos:
                            
                            tiempo_prep_minutos = st.selectbox(
                                label="Minutos",
                                options=[0,15,30,45],
                                key=f"preparacion_minutos_{id_user}",
                                index= [0,15,30,45].index(st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"preparacion_minutos_{id_user}"]) if f"preparacion_minutos_{id_user}" in st.session_state["form_data_consulting_services"]["participantes_cs"][id_user] else 0,
                                on_change = lambda: save_to_session_state("participantes_cs", st.session_state[f"preparacion_minutos_{id_user}"], id_user, f"preparacion_minutos_{id_user}")

                            )
                            st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"preparacion_minutos_{id_user}"] = tiempo_prep_minutos

                            
                        with col_ponencia_horas:
                            tiempo_ponencia_horas = st.number_input(
                                label="Horas",
                                min_value=0,
                                step=1,
                                key=f"ponencia_horas_{id_user}",
                                value =st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"ponencia_horas_{id_user}"],
                                on_change = lambda: save_to_session_state("participantes_cs", st.session_state[f"ponencia_horas_{id_user}"], id_user, f"ponencia_horas_{id_user}")
                            )
                            
                        with col_ponencia_minutos:
                            tiempo_ponencia_minutos = st.selectbox(
                                label="Minutos",
                                options=[0,15,30,45],
                                key=f"ponencia_minutos_{id_user}",
                                index= [0,15,30,45].index(st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"ponencia_minutos_{id_user}"]) if f"ponencia_minutos_{id_user}" in st.session_state["form_data_consulting_services"]["participantes_cs"][id_user] else 0,
                                on_change = lambda: save_to_session_state("participantes_cs", st.session_state[f"ponencia_minutos_{id_user}"], id_user, f"ponencia_minutos_{id_user}")
                            )
                            st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"ponencia_minutos_{id_user}"] = tiempo_ponencia_minutos

                                
                        # Obtener valores de tiempo en horas decimales
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
                        st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"honorarios_{id_user}"] = honorarios     

                        if st.button("Guardar cambios", type="primary", use_container_width=True):
                            validacion_completa_email(id_user)
                            validacion_completa_dni(id_user)
                            if st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"dni_correcto_{id_user}"] == False or \
                                st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"email_correcto_{id_user}"] == False:
                                
                                st.rerun(scope="fragment")
                            else:
                                st.session_state.clicked_cs = True
                                st.rerun()



##########################################################
def participantes_section():
    st.header("3. Agregar datos de consultores", divider=True)

    if st.button("Agregar consultor", use_container_width=True, icon="➕", key="add_participant_button"):
        add_participant()

    index = 0
    # Renderizar los participantes_cs
    for info_user in st.session_state["participantes_cs"]:

        id_user = info_user["id"]

        col_participant, col_remove_participant_individual = st.columns([10,1])
        with col_participant:
            asignacion_nombre(id_user)
            nombre_expander_cs = st.session_state['form_data_consulting_services']['participantes_cs'][f'{id_user}']['name_ponente_cs']
            if nombre_expander_cs != "":
                aux = ": "
            else:
                aux = ""

            generar_toast()
            
            if st.button(label=f"Consultor {index + 1}{aux}{nombre_expander_cs}", use_container_width=True, icon="👩‍⚕️"):
                    
                single_consultant(id_user, info_user, index)
                # handle_email(id_user)
                # print("FORM", st.session_state["form_data_consulting_services"]["participantes_cs"][id_user])

                if st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"dni_correcto_{id_user}"] == False:
                    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"dni_{id_user}"] = ""
                if st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"email_correcto_{id_user}"] == False:
                    st.session_state["form_data_consulting_services"]["participantes_cs"][id_user][f"email_{id_user}"] = ""
               
    
            
        index +=1
        with col_remove_participant_individual:
            if st.button("🗑️", key=f"remove_participant_{id_user}", use_container_width=True, type="secondary"):
                if id_user in st.session_state["form_data_consulting_services"]["participantes_cs"].keys():
                    del st.session_state["form_data_consulting_services"]["participantes_cs"][id_user]
                    st.session_state["participantes_cs"] = list(filter(lambda x: x['id'] != id_user, st.session_state["participantes_cs"]))

                st.rerun()

# Inicializar estado del formulario en session_state
if "form_data_consulting_services" not in st.session_state:
    field_defaults = {
        "nombre_necesidades_cs": "",
        "owner_cs": "",
        "delegate_cs": "",
        "start_date_cs": date.today(),
        "end_date_cs": date.today(),
        "presupuesto_estimado_cs": 0.0,
        "producto_asociado_cs": "",
        "estado_aprobacion_cs": "",
        "necesidad_reunion_cs": "",
        "descripcion_servicio_cs": "",
        "numero_consultores_cs": 0,
        "justificacion_numero_participantes_cs": "",
        "criterios_seleccion_cs": [],
        }

    st.session_state["form_data_consulting_services"] = {}
    
    st.session_state["download_enabled_cs"] = False
    st.session_state["download_enabled_aux_cs"] = False
    st.session_state["path_doc_cs"] = None

    
    for key, value in field_defaults.items():
        save_to_session_state(key, value)
         
    if "participantes_cs" not in st.session_state:
        st.session_state.participantes_cs = [] 

    if "name_ponente_cs" not in st.session_state:
            st.session_state["name_ponente_cs"] = ""
    

    add_participant()


af.show_main_title(title="Consulting Services", logo_size=200)

st.header("1. Detalle de la actividad", divider=True)
col1, col2 = st.columns(2)
with col1:
    st.text_input(
        "Owner *",
        value=st.session_state["form_data_consulting_services"]["owner_cs"],
        key="owner_cs",
        on_change=lambda: save_to_session_state("owner_cs", st.session_state["owner_cs"])
    )
with col2:
    st.text_input(
        "Delegate",
        value=st.session_state["form_data_consulting_services"]["delegate_cs"],
        key="delegate_cs",
        on_change=lambda: save_to_session_state("delegate_cs", st.session_state["delegate_cs"])
    )

col1, col2 = st.columns(2)
with col1:
    st.text_input("Nombre del evento *",
                  max_chars=255,
                  key="nombre_necesidades_cs",
                  value= st.session_state["form_data_consulting_services"]["nombre_necesidades_cs"] if "nombre_necesidades_cs" in st.session_state["form_data_consulting_services"] else "",
                  on_change=lambda: save_to_session_state("nombre_necesidades_cs", st.session_state["nombre_necesidades_cs"]))
with col2:
    st.number_input("Presupuesto total estimado (€)*",
                    min_value=0.0,
                    step=100.00,
                    key="presupuesto_estimado_cs",
                    help="Ratio obligatorio (5 asistentes por ponente)",
                    value= st.session_state["form_data_consulting_services"]["presupuesto_estimado_cs"] if "presupuesto_estimado_cs" in st.session_state["form_data_consulting_services"] else 0.0,
                on_change=lambda: save_to_session_state("presupuesto_estimado_cs", st.session_state["presupuesto_estimado_cs"]))
if st.session_state["form_data_consulting_services"]["presupuesto_estimado_cs"] == 0.00:
    st.warning(f"Revisa si el presupuesto total estimado debe ser mayor a 0.")

col1, col2 = st.columns(2)
with col1:
    date_cs = st.date_input("Fecha de inicio *",
                  value=st.session_state["form_data_consulting_services"]["start_date_cs"],
                  key="start_date_cs",
                  on_change=handle_fecha_inicio,
                  format = "DD/MM/YYYY")
    if st.session_state["form_data_consulting_services"]["start_date_cs"] == date.today():
        st.warning(f"Revisa que la fecha de inicio del evento introducida sea correcta.")

    
    st.text_input("Producto asociado",
                  max_chars=255,
                  key="producto_asociado_cs",
                  value= st.session_state["form_data_consulting_services"]["producto_asociado_cs"] if "producto_asociado_cs" in st.session_state["form_data_consulting_services"] else "",
                  on_change=lambda: save_to_session_state("producto_asociado_cs", st.session_state["producto_asociado_cs"]))
        
with col2:
    st.date_input("Fecha de fin *",
                  value= date_cs if st.session_state["form_data_consulting_services"]["end_date_cs"] < date_cs else st.session_state["form_data_consulting_services"]["end_date_cs"],
                  min_value = date_cs,
                  key="end_date_cs",
                  on_change=lambda: save_to_session_state("end_date_cs", st.session_state["end_date_cs"]),
                  format = "DD/MM/YYYY")
    
    if st.session_state["form_data_consulting_services"]["end_date_cs"] == date.today():
        st.warning(f"Revisa que la fecha de fin del evento introducida sea correcta.")
    
    st.selectbox("Estado de la aprobación del producto",
                 ["", "N/A", "Aprobado", "No Aprobado"],
                 key="estado_aprobacion_cs",
                 index= ["", "N/A", "Aprobado", "No Aprobado"].index(st.session_state["form_data_consulting_services"]["estado_aprobacion_cs"]) if "estado_aprobacion_cs" in st.session_state["form_data_consulting_services"] else 0,
                 on_change=lambda: save_to_session_state("estado_aprobacion_cs", st.session_state["estado_aprobacion_cs"]))



necesidad= st.text_area("Necesidad de la reunión y resultados esperados *",
                max_chars=4000,
                key="necesidad_reunion_cs",
                help="Describa la necesidad de obtener información de los consultores y el propósito para el cual se utilizará dicha información.",
                value= st.session_state["form_data_consulting_services"]["necesidad_reunion_cs"] if "necesidad_reunion_cs" in st.session_state["form_data_consulting_services"] else "",
                on_change=lambda: save_to_session_state("necesidad_reunion_cs", st.session_state["necesidad_reunion_cs"]))
for word in black_list:  
    if word.lower() in necesidad.lower():  
        st.warning(f"La descripción contiene una palabra de la Black List: '{word}'")  
        break
    
servicio = st.text_area("Descripción del servicio *",
                max_chars=4000,
                key="descripcion_servicio_cs",
                value= f"Consulting Services - {st.session_state['form_data_consulting_services']['nombre_necesidades_cs']}", #st.session_state["form_data_consulting_services"]["descripcion_servicio_cs"] if "descripcion_servicio_cs" in st.session_state["form_data_consulting_services"] else "",
                disabled=True)
st.session_state["form_data_consulting_services"]["descripcion_servicio_cs"] = servicio

st.header("2. Detalle nº consultores", divider=True)
col3, col4 = st.columns(2)

with col3:
    st.number_input("Nº de consultores *", 
                    min_value=0, 
                    step=1, 
                    key="numero_consultores_cs",
                    value= st.session_state["form_data_consulting_services"]["numero_consultores_cs"] if "numero_consultores_cs" in st.session_state["form_data_consulting_services"] else 0,
                    on_change=lambda: (
                     save_to_session_state("numero_consultores_cs", st.session_state["numero_consultores_cs"]),
                     save_to_session_state("justificacion_numero_participantes_cs", ""),
                 ) if st.session_state["numero_consultores_cs"] <= 1 else 
                     save_to_session_state("numero_consultores_cs", st.session_state["numero_consultores_cs"])
                     )
    
with col4:
    st.multiselect(
        "Criterios de selección *",
        [
            "Experiencia como ponente", "Experiencia como consultor",
            "Experiencia como profesor", "Experiencia clínica en tema a tratar", "Especialista en tema a tratar"
        ],
        key="criterios_seleccion_cs",
        default=st.session_state["form_data_consulting_services"]["criterios_seleccion_cs"] if "criterios_seleccion_cs" in st.session_state["form_data_consulting_services"] else [],
        on_change=lambda: save_to_session_state("criterios_seleccion_cs", st.session_state["criterios_seleccion_cs"]))

st.text_area("Justificación de número de participantes *", 
             max_chars=4000, 
             key="justificacion_numero_participantes_cs", 
             help = "Asegúrese de que  se contrate la cantidad necesaria de consultores para brindar los servicios que satisfacen las necesidades comerciales legítimas.",
             value="" if st.session_state["form_data_consulting_services"]["numero_consultores_cs"] <=1 else st.session_state["form_data_consulting_services"].get("justificacion_numero_participantes_cs", ""), 
             disabled=st.session_state["form_data_consulting_services"]["numero_consultores_cs"] <= 1, 
             on_change=lambda: save_to_session_state("justificacion_numero_participantes_cs", st.session_state["justificacion_numero_participantes_cs"]))



participantes_section()



st.header("4. Documentos", divider=True)

with st.expander("Ver documentos necesarios"):
    st.file_uploader("Agenda o Guión  del evento *", type=["pdf", "docx", "xlsx", "ppt"], key="documentosubido_1_cs", on_change=lambda: save_to_session_state("documentosubido_1_cs", st.session_state["documentosubido_1_cs"]))
    st.file_uploader("Documentos adicionales", type=["pdf", "docx", "xlsx", "ppt"], key="documentosubido_2_cs", on_change=lambda: save_to_session_state("documentosubido_2_cs", st.session_state["documentosubido_2_cs"]))


st.session_state.download_enabled_cs = False

def generacion_errores():
    try:
        st.session_state.download_enabled_cs = False
        errores_general, errores_participantes = af.validar_campos(st.session_state["form_data_consulting_services"], mandatory_fields, dependendent_fields)
        if not errores_general and all(not lista for lista in errores_participantes.values()):
            doc, st.session_state.path_doc_cs = cd.crear_documento_consulting_services(st.session_state["form_data_consulting_services"])
            st.session_state.download_enabled_cs = True
    except Exception as e:
        traceback.print_exc()
        st.toast(f"Ha ocurrido un problema al generar el formulario -> {e}", icon="❌")

    return errores_general, errores_participantes

def mostrar_errores(errores_general, errores_participantes):
    try:
        errores_general, errores_participantes = af.validar_campos(st.session_state["form_data_consulting_services"], mandatory_fields, dependendent_fields)
    except Exception as e:
        traceback.print_exc()
    if not errores_general and all(not lista for lista in errores_participantes.values()):
        st.session_state.download_enabled_cs = True
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
                    participantes = st.session_state['form_data_consulting_services']['participantes_cs']

                    # Obtener la posición del ID en las claves del diccionario
                    keys_list = list(participantes.keys())  # Convertir las claves en una lista
                    posicion = keys_list.index(id_user) + 1 if id_user in keys_list else None
                    if posicion != None:
                        name_ponente = st.session_state['form_data_consulting_services']['participantes_cs'][f'{keys_list[posicion-1]}']['name_ponente_cs'].strip()
                        msg_participantes = f"\n**Errores del Consultor {posicion}:{name_ponente}**\n"
                        for msg in list_errors:
                            msg_participantes += f"\n* {msg}\n"
                        st.error(msg_participantes)
                    

# Botón para enviar
def button_form():
    if st.button(label="Generar Plantilla", use_container_width=True, type="primary"):
        #st.session_state.download_enabled_cs = False
        st.session_state.errores = True
            
        with st.status("Validando campos...", expanded=True, state = "running") as status:
            st.write("Validando información general del formulario...")
            time.sleep(1.5)
            st.write("Validando campos obligatorios y dependientes...")
            time.sleep(1.5)
            st.write("Validando información de los ponentes...")
            time.sleep(1.5)
            st.write("Validando contenido de campos con IA...")
            time.sleep(1.5)

            errores_general_cs, errores_participantes_cs = generacion_errores()

            st.session_state.errores_general_cs, st.session_state.errores_participantes_cs = errores_general_cs, errores_participantes_cs


            # Actualizo el estado
            if st.session_state.download_enabled_cs == True:
                status.update(
                    label="Validación completada!", state="complete", expanded=False
                )
                st.session_state.errores = False
            else:
                status.update(
                    label="Validación no completada. Se deben revisar los campos obligatorios faltantes.", state="error", expanded=False
                )
                st.session_state.errores = True
                st.toast("Se deben corregir los errores.", icon="❌")

            if st.session_state.download_enabled_cs == True:
                #st.session_state.download_enabled_cs = True
                st.toast("Formulario generado correctamente", icon="✔️")

    if st.session_state.errores == True:
        mostrar_errores(st.session_state.errores_general_cs, st.session_state.errores_participantes_cs)     


button_form()



def download_document(disabled):
    nombre = f"Consulting_Services - {st.session_state['form_data_consulting_services']['nombre_necesidades_cs']}.zip"
    if st.session_state.path_doc_cs:
        with open(st.session_state.path_doc_cs, "rb") as file:
            st.download_button(
                label="Descargar ZIP",
                data=file,
                file_name=nombre,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                icon="📥",
                disabled=disabled
            )
    else:
        st.download_button(
            label="Descargar ZIP",
            data=io.BytesIO(),
            file_name=nombre,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            icon="📥",
            disabled=True
        )

disabled = not st.session_state.download_enabled_cs
if disabled == False:
    download_document(disabled)


#st.write(st.session_state["form_data_consulting_services"])
#st.write(st.session_state)