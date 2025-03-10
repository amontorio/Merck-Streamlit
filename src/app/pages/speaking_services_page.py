import streamlit as st
from streamlit_searchbox import st_searchbox
from datetime import date
import unicodedata
import uuid
from datetime import time
import auxiliar.create_docx as cd
import traceback
import auxiliar.aux_functions as af
import io
import time
import re


tarifas = {
    "0": 300, 
    "1": 250,
    "2": 200,
    "3": 150,
    "4": 150
}


black_list = ["captar", "otorgar", "premio", "regalo", "ventaja", "beneficio", "precio", "Fidelizar", "excluir", "influir", "defensor", "relación", "intercambio", "pago", "retorno de la inversión", "contra ataque", "prescriptor principal", "agradecer", "generoso", "favor", "entretenimiento", "espectáculo", "reemplazar", "expulsar", "forzar", "agresivo", "ilegal", "descuento", "contratar", "Abuso", "Mal uso", "Demandar", "Investigación", "Monopolio", "Antitrust", "Anticompetitivo", "Cartel", "Manipular", "Libre mercado", "Colusión", "Ilegal", "Privilegio", "Concesión", "Agresivo"]  

def save_to_session_state(key, value, key_participante=None, field_participante=None):
    """
    Saves a value to the Streamlit session state.

    Parameters:
        key (str): The key under which the value will be saved in the session state.
        value (any): The value to be saved in the session state.
        key_participante (str, optional): The key for the participant, used only if key is "participantes_ss".
        field_participante (str, optional): The field for the participant, used only if key is "participantes_ss".

    Returns:
        None
    """
    if key != "participantes_ss":
        if key not in ["documentosubido_1_ss", "documentosubido_2_ss", "documentosubido_3_ss"]:
            st.session_state[key] = value
        st.session_state["form_data_speaking_services"][key] = value
    else:
        st.session_state[field_participante] = value
        st.session_state["form_data_speaking_services"][key][key_participante][field_participante] = value


def handle_fecha_inicio():
    save_to_session_state("start_date_ss", st.session_state["start_date_ss"])
    if st.session_state["start_date_ss"] >= st.session_state["end_date_ss"]:
        save_to_session_state("end_date_ss", st.session_state["start_date_ss"]) 

def handle_dni(id_user):
    save_to_session_state("participantes_ss", st.session_state[f"dni_{id_user}"], id_user, f"dni_copy_{id_user}")
    val = validacion_completa_dni(id_user)
    
    if st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"dni_correcto_{id_user}"] == False:
        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"dni_{id_user}"] = ""
    else:
        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"dni_{id_user}"] = st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"dni_copy_{id_user}"]
    
    return None

def handle_email(id_user):
    save_to_session_state("participantes_ss", st.session_state[f"email_{id_user}"], id_user, f"email_copy_{id_user}")
    val = validacion_completa_email(id_user)
    
    if st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"email_correcto_{id_user}"] == False:
        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"email_{id_user}"] = ""
    else:
        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"email_{id_user}"] = st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"email_copy_{id_user}"]

    return None
def normalize_text(text):
    # Convertir a string y minúsculas
    text = str(text).lower()
    # Eliminar tildes y caracteres especiales
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')
    # Eliminar espacios adicionales
    text = text.strip()
    return text

def add_ponente():
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
    
    st.session_state["participantes_ss"].append(new_participant)
    #st.session_state["id_participantes_ss"].append(id_user)

    # Inicializar participantes_ss en form_data_speaking_services si no existe
    if "participantes_ss" not in st.session_state["form_data_speaking_services"]:
        st.session_state["form_data_speaking_services"]["participantes_ss"] = {}        

    st.session_state["form_data_speaking_services"]["participantes_ss"][id_user] = new_participant
    if f"dni_{id_user}" not in st.session_state:
        st.session_state[f"dni_{id_user}"] = ""
    if f"email_{id_user}" not in st.session_state:
        st.session_state[f"email_{id_user}"] = ""

def remove_last_participant():
    # Eliminar el último participante
    if st.session_state["participantes_ss"]:
        pos = len(st.session_state["participantes_ss"])
        print(st.session_state["form_data_speaking_services"]["participantes_ss"].pop(pos))

        st.session_state["participantes_ss"].pop()


########## validaciones especiales
def validacion_completa_dni(id_user):
    dni = st.session_state.get(f"dni_{id_user}", "")
    st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"dni_correcto_{id_user}"] = True

    try:
        numero = int(dni[:-1])
        letra = dni[-1].upper()
        letras_validas = "TRWAGMYFPDXBNJZSQVHLCKE"
        letra_correcta = letras_validas[numero % 23]

        if letra != letra_correcta:
            st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"dni_correcto_{id_user}"] = False

    except:
        if dni != "":
            st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"dni_correcto_{id_user}"] = False
        

def validacion_completa_email(id_user):    
        mail = st.session_state.get(f"email_{id_user}", "")
        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"email_correcto_{id_user}"] = True
        try:
            tlds_validos = ['com', 'org', 'net', 'es', 'edu', 'gov', 'info', 'biz']
            tlds_pattern = '|'.join(tlds_validos)
            patron = rf'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?:{tlds_pattern})$'

            matcheo = re.match(patron, mail) 

            if matcheo == None and mail !="":
                st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"email_correcto_{id_user}"] = False
        except:
            if mail != "":
                st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"email_correcto_{id_user}"] = False


def validacion_num_noches():
    save_to_session_state("num_noches_copy_ss", st.session_state["num_noches_ss"])
    st.session_state.num_noches_correcto_ss = True
    if st.session_state.num_noches_ss.isdigit():
        duracion = (st.session_state["end_date_ss"] - st.session_state["start_date_ss"]).days
        if int(st.session_state.num_noches_ss) > duracion + 1: 
            st.session_state.num_noches_correcto_ss = False
        save_to_session_state("num_noches_ss", st.session_state["num_noches_ss"]) 
                    
    else:
        st.session_state["form_data_speaking_services"]["num_noches_ss"] = ""
        st.session_state.num_noches_correcto_ss = False
    

def on_change_nombre(id_user):
    if st.session_state["form_data_speaking_services"]["participantes_ss"][f"{id_user}"][f"nombre_{id_user}"] != None:
        if st.session_state.get(f"nombre_{id_user}", "") != "":
            dic = st.session_state.get(f"nombre_{id_user}", "")
            search = dic.get("search", "")
            result = dic.get("result", "")

            if search  == st.session_state["form_data_speaking_services"]["participantes_ss"][id_user].get(f"nombre_{id_user}", "") and result == None:
                st.session_state[f"nombre_{id_user}"]["search"] = " "



def asignacion_nombre(id_user):
    if f'nombre_{id_user}' in st.session_state and st.session_state["form_data_speaking_services"]["participantes_ss"][f"{id_user}"][f"nombre_{id_user}"] not in [None, ""]:
        nombre_ponente = st.session_state["form_data_speaking_services"]["participantes_ss"][f"{id_user}"][f"nombre_{id_user}"].get("result", "").rsplit('-', 1)[0] 
        st.session_state["form_data_speaking_services"]["participantes_ss"][f"{id_user}"]["name_ponente_ss"] = nombre_ponente
    else:
        st.session_state["form_data_speaking_services"]["participantes_ss"][f"{id_user}"]["name_ponente_ss"] = ""


if "clicked_ss" not in st.session_state:
    st.session_state.clicked_ss = False

if "errores_ss" not in st.session_state:
    st.session_state.errores_ss = False

if "errores_ss_reducido" not in st.session_state:
    st.session_state.errores_ss_reducido = False

if "errores_generales_ss" not in st.session_state:
    st.session_state.errores_generales_ss = []

if "errores_participantes_ss" not in st.session_state:
    st.session_state.errores_participantes_ss = {}

if "errores_ia_ss" not in st.session_state:
    st.session_state.errores_ia_ss = []

if "errores_generales_ss_red" not in st.session_state:
    st.session_state.errores_generales_ss_red = []

if "errores_participantes_ss_red" not in st.session_state:
    st.session_state.errores_participantes_ss_red = {}

if "errores_ia_ss_red" not in st.session_state:
    st.session_state.errores_ia_ss_red = []

if "num_noches_copy_ss" not in st.session_state:
    st.session_state.num_noches_copy_ss = ""

if "num_noches_correcto_ss" not in st.session_state:
    st.session_state.num_noches_correcto_ss = True

if "num_ponentes_copy_ss" not in st.session_state:
    st.session_state.num_ponentes_copy_ss = ""

if "num_ponentes_correcto_ss" not in st.session_state:
    st.session_state.num_ponentes_correcto_ss = True

def generar_toast():
    if st.session_state.clicked_ss == True:
        texto_toast = "Cambios guardados correctamente!"
        st.toast(texto_toast, icon = "✔️")
        st.session_state.clicked_ss = False


@st.dialog("Rellena los campos", width="large")
def single_ponente(id_user, info_user, index):
                        nombre = st_searchbox(
                                #label="Buscador de HCO / HCP *",
                                search_function= af.search_function,  # Pasamos df aquí
                                placeholder="Busca un HCO / HCP *",
                                key=f"nombre_{id_user}",
                                edit_after_submit="disabled",
                                default_searchterm= st.session_state["form_data_speaking_services"]["participantes_ss"][f"{id_user}"][f"nombre_{id_user}"].get("result", "").rsplit('-', 1)[0] if st.session_state["form_data_speaking_services"]["participantes_ss"][f"{id_user}"][f"nombre_{id_user}"] not in [None, ""] else "",
                                reset_function = on_change_nombre(id_user), 
                                submit_function= lambda x: (
                                    save_to_session_state("participantes_ss", af.handle_tier_from_name(st.session_state[f"nombre_{id_user}"]), id_user, f"tier_{id_user}"),
                                    save_to_session_state("participantes_ss", st.session_state[f"nombre_{id_user}"], id_user, f"nombre_{id_user}")
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

                        if not st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"dni_correcto_{id_user}"]:
                            st.warning("El DNI introducido no es correcto.", icon="❌")
                        
                        with col2:
                            tier = st.selectbox(
                                f"Tier del participante {index + 1} *", 
                                ["0", "1", "2", "3", "4"], 
                                index= ["0", "1", "2", "3", "4"].index(st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"tier_{id_user}"]) if f"tier_{id_user}" in st.session_state["form_data_speaking_services"]["participantes_ss"][id_user] else 0,
                                key=f"tier_{id_user}"
                            )
                            st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"tier_{id_user}"] = tier
                            
                        col1, col2 = st.columns(2)
                        with col1:
                            centro = st.text_input(
                                f"Centro de trabajo del participante {index + 1} *", 
                                value=info_user.get(f"centro_trabajo_{id_user}", ""), 
                                key=f"centro_trabajo_{id_user}",
                                on_change = lambda: save_to_session_state("participantes_ss", st.session_state[f"centro_trabajo_{id_user}"], id_user, f"centro_trabajo_{id_user}")

                            )
                        
                        with col2:       
                            email = st.text_input(
                                f"Email del participante {index + 1} *", 
                                value = info_user.get(f"email_copy_{id_user}", ""),
                                key=f"email_{id_user}",
                                on_change= lambda: handle_email(id_user)
                            )
                            
                        if not st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"email_correcto_{id_user}"]:
                            st.warning("El email introducido no es correcto.", icon="❌")

                        col1, col2 = st.columns(2)
                        with col1:
                            cobra = st.selectbox(
                                "¿Cobra a través de sociedad? *", 
                                ["", "No", "Sí"], 
                                key=f"cobra_sociedad_{id_user}",
                                index= ["", "No", "Sí"].index(st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"cobra_sociedad_{id_user}"]) if f"cobra_sociedad_{id_user}" in st.session_state["form_data_speaking_services"]["participantes_ss"][id_user] else 0,
                                on_change= lambda: save_to_session_state("participantes_ss", st.session_state[f"cobra_sociedad_{id_user}"], id_user, f"cobra_sociedad_{id_user}")
                            )
                            st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"cobra_sociedad_{id_user}"] = cobra
                            
                            st.markdown('<p style="font-size: 14px;">Tiempo de preparación</p>', unsafe_allow_html=True)  

                           
                        with col2:                   
                            nombre_sociedad = st.text_input(
                                "Nombre de la sociedad *",
                                value = st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"nombre_sociedad_{id_user}"] if cobra == "Sí" else "",
                                key=f"nombre_sociedad_{id_user}",
                                on_change = lambda: save_to_session_state("participantes_ss","", id_user, f"nombre_sociedad_{id_user}")
                                    if st.session_state[f"cobra_sociedad_{id_user}"] == "No" else 
                                    save_to_session_state("participantes_ss", st.session_state[f"nombre_sociedad_{id_user}"], id_user, f"nombre_sociedad_{id_user}"),
                                disabled= cobra == "No"
                            )
                            st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"nombre_sociedad_{id_user}"] = nombre_sociedad

                            
                            st.markdown('<p style="font-size: 14px;">Tiempo de ponencia</p>', unsafe_allow_html=True)  
                        col_prep_horas, col_prep_minutos, col_ponencia_horas, col_ponencia_minutos = st.columns(4)

                        with col_prep_horas:
                            tiempo_prep_horas = st.number_input(
                                label="Horas",
                                min_value=0,
                                step=1,
                                key=f"preparacion_horas_{id_user}",
                                value =st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"preparacion_horas_{id_user}"],
                                on_change = lambda: save_to_session_state("participantes_ss", st.session_state[f"preparacion_horas_{id_user}"], id_user, f"preparacion_horas_{id_user}")
                            )
                            
                        with col_prep_minutos:
                            
                            tiempo_prep_minutos = st.selectbox(
                                label="Minutos",
                                options=[0,15,30,45],
                                key=f"preparacion_minutos_{id_user}",
                                index= [0,15,30,45].index(st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"preparacion_minutos_{id_user}"]) if f"preparacion_minutos_{id_user}" in st.session_state["form_data_speaking_services"]["participantes_ss"][id_user] else 0,
                                on_change = lambda: save_to_session_state("participantes_ss", st.session_state[f"preparacion_minutos_{id_user}"], id_user, f"preparacion_minutos_{id_user}")
                            )
                            st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"preparacion_minutos_{id_user}"] = tiempo_prep_minutos


                        with col_ponencia_horas:
                            tiempo_ponencia_horas = st.number_input(
                                label="Horas",
                                min_value=0,
                                step=1,
                                key=f"ponencia_horas_{id_user}",
                                value =st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"ponencia_horas_{id_user}"],
                                on_change = lambda: save_to_session_state("participantes_ss", st.session_state[f"ponencia_horas_{id_user}"], id_user, f"ponencia_horas_{id_user}")
                            )
                            
                            
                        with col_ponencia_minutos:
                            tiempo_ponencia_minutos = st.selectbox(
                                label="Minutos",
                                options=[0,15,30,45],
                                key=f"ponencia_minutos_{id_user}",
                                index= [0,15,30,45].index(st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"ponencia_minutos_{id_user}"]) if f"ponencia_minutos_{id_user}" in st.session_state["form_data_speaking_services"]["participantes_ss"][id_user] else 0,
                                on_change = lambda: save_to_session_state("participantes_ss", st.session_state[f"ponencia_minutos_{id_user}"], id_user, f"ponencia_minutos_{id_user}")
                            )
                            st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"ponencia_minutos_{id_user}"] = tiempo_ponencia_minutos

                            
                                
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
                        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"honorarios_{id_user}"] = honorarios     

                        if st.button("Guardar cambios", type="primary", use_container_width=True):
                            validacion_completa_email(id_user)
                            validacion_completa_dni(id_user)
                            if st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"dni_correcto_{id_user}"] == False or \
                                st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"email_correcto_{id_user}"] == False :
                                st.rerun(scope="fragment")
                            else:
                                st.session_state.clicked_ss = True
                                st.rerun()
                        

        
def ponentes_section():
        if st.button("Agregar ponente", use_container_width=True, icon="➕", key="add_ponente_button"):
            add_ponente()

        index = 0
        # Renderizar los participantes
        for info_user in st.session_state["participantes_ss"]:
            id_user = info_user["id"]
            col_participant, col_remove_participant_individual = st.columns([10,1])
            with col_participant:

                asignacion_nombre(id_user)
                nombre_expander_ss = st.session_state['form_data_speaking_services']['participantes_ss'][f'{id_user}']['name_ponente_ss']
                if nombre_expander_ss != "":
                    aux = ": "
                else:
                    aux = ""
                
                generar_toast()

                if st.button(label=f"Ponente {index + 1}{aux}{nombre_expander_ss}", use_container_width=True, icon="👩‍⚕️"):
                    single_ponente(id_user, info_user, index)
                    if st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"dni_correcto_{id_user}"] == False:
                        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"dni_{id_user}"] = ""
                    if st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"email_correcto_{id_user}"] == False:
                        st.session_state["form_data_speaking_services"]["participantes_ss"][id_user][f"email_{id_user}"] = ""
            index +=1
            with col_remove_participant_individual:
                if st.button("🗑️", key=f"remove_participant_ss_{id_user}", use_container_width=True, type="secondary"):
                    if id_user in st.session_state["form_data_speaking_services"]["participantes_ss"].keys():
                        del st.session_state["form_data_speaking_services"]["participantes_ss"][id_user]
                        st.session_state["participantes_ss"] = list(filter(lambda x: x['id'] != id_user, st.session_state["participantes_ss"]))
                    st.rerun()



def generacion_errores(tipo):
    try:
        st.session_state.download_enabled_ss = False
        errores_general, errores_participantes = af.validar_campos(st.session_state["form_data_speaking_services"], mandatory_fields, dependendent_fields)
        errores_ia = af.validar_campos_ia(st.session_state["form_data_speaking_services"], validar_ia)

        if not errores_general and all(not lista for lista in errores_participantes.values()) and not errores_ia:
            if tipo == "Reunión Merck Program":
                doc, st.session_state.path_doc_ss = cd.crear_documento_speaking(st.session_state["form_data_speaking_services"])
            else:
                doc, st.session_state.path_doc_ss = cd.crear_documento_speaking_reducido(st.session_state["form_data_speaking_services"])
            st.session_state.download_enabled_ss = True
    except Exception as e:
        traceback.print_exc()
        st.toast(f"Ha ocurrido un problema al generar el formulario -> {e}", icon="❌")

    return errores_general, errores_participantes, errores_ia


def mostrar_errores(errores_general, errores_participantes, errores_ia):
    try:
        errores_general, errores_participantes = af.validar_campos(st.session_state["form_data_speaking_services"], mandatory_fields, dependendent_fields)
    except Exception as e:
        traceback.print_exc()
    if not errores_general and all(not lista for lista in errores_participantes.values()) and not errores_ia:
        st.session_state.download_enabled_ss = True
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
                    participantes = st.session_state['form_data_speaking_services']['participantes_ss']

                    # Obtener la posición del ID en las claves del diccionario
                    keys_list = list(participantes.keys())  # Convertir las claves en una lista
                    posicion = keys_list.index(id_user) + 1 if id_user in keys_list else None
                    if posicion != None:
                        name_ponente = st.session_state['form_data_speaking_services']['participantes_ss'][f'{keys_list[posicion-1]}']['name_ponente_ss'].strip()
                        msg_participantes = f"\n**Errores del Ponente {posicion}:{name_ponente}**\n"
                        for msg in list_errors:
                            msg_participantes += f"\n* {msg}\n"
                        st.error(msg_participantes)

        if len(errores_ia) > 0:
            msg_aviso = "\n**Errores detectados con IA**\n"
            for msg in errores_ia:
                msg_aviso += f"\n* {msg}\n"
            st.error(msg_aviso)
                    
def button_form(tipo):
    if st.button(label="Generar Plantilla", use_container_width=True, type="primary"):
        st.session_state.errores_ss = True
        with st.status("Validando campos...", expanded=True, state = "running") as status:
            st.write("Validando información general del formulario...")
            time.sleep(1.5)
            st.write("Validando campos obligatorios y dependientes...")
            time.sleep(1.5)
            st.write("Validando información de los ponentes...")
            time.sleep(1.5)
            st.write("Validando contenido de campos con IA...")
            time.sleep(1.5)

            errores_general_ss, errores_participantes_ss, errores_ia_ss = generacion_errores(tipo)

            st.session_state.errores_general_ss, st.session_state.errores_participantes_ss, st.session_state.errores_ia_ss = errores_general_ss, errores_participantes_ss, errores_ia_ss

            # Actualizo el estado
            if st.session_state.download_enabled_ss == True:
                status.update(
                    label="Validación completada!", state="complete", expanded=False
                )
                st.session_state.errores_ss = False
            else:
                status.update(
                    label="Validación no completada. Se deben revisar los campos obligatorios faltantes.", state="error", expanded=False
                )
                st.session_state.errores_ss = True
                st.toast("Se deben corregir los errores.", icon="❌")

            if st.session_state.download_enabled_ss == True:
                st.toast("Formulario generado correctamente", icon="✔️")

    if st.session_state.errores_ss == True:
        mostrar_errores(st.session_state.errores_general_ss, st.session_state.errores_participantes_ss, st.session_state.errores_ia_ss)     

def button_form_reducido(tipo):
    if st.button(label="Generar Plantilla", use_container_width=True, type="primary"):
        st.session_state.errores_ss_reducido = True
        with st.status("Validando campos...", expanded=True, state = "running") as status:
            st.write("Validando información general del formulario...")
            time.sleep(1.5)
            st.write("Validando campos obligatorios y dependientes...")
            time.sleep(1.5)
            st.write("Validando información de los ponentes...")
            time.sleep(1.5)
            st.write("Validando contenido de campos con IA...")
            time.sleep(1.5)

            errores_general_ss, errores_participantes_ss, errores_ia_ss = generacion_errores(tipo)

            st.session_state.errores_general_ss_red, st.session_state.errores_participantes_ss_red, st.session_state.errores_ia_ss_red = errores_general_ss, errores_participantes_ss, errores_ia_ss

            # Actualizo el estado
            if st.session_state.download_enabled_ss == True:
                status.update(
                    label="Validación completada!", state="complete", expanded=False
                )
                st.session_state.errores_ss = False
            else:
                status.update(
                    label="Validación no completada. Se deben revisar los campos obligatorios faltantes.", state="error", expanded=False
                )
                st.session_state.errores_ss = True
                st.toast("Se deben corregir los errores.", icon="❌")

            if st.session_state.download_enabled_ss == True:
                st.toast("Formulario generado correctamente", icon="✔️")

    if st.session_state.errores_ss_reducido == True:
        mostrar_errores(st.session_state.errores_general_ss_red, st.session_state.errores_participantes_ss_red, st.session_state.errores_ia_ss_red)     
            

def download_document(disabled, tipo):
    if tipo == "Reunión Merck Program":
        nombre = f"Speaking_Service_Merck_Program - {st.session_state['form_data_speaking_services']['nombre_evento_ss']}.zip"
    else:
        nombre = f"Speaking_Service_Paragüas - {st.session_state['form_data_speaking_services']['nombre_evento_ss']}.zip"
    if st.session_state.path_doc_ss:
        with open(st.session_state.path_doc_ss, "rb") as file:
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

def numero_ponentes_completo():
        save_to_session_state("num_ponentes_copy_ss", st.session_state["num_ponentes_ss"])
        st.session_state.num_ponentes_correcto_ss = True
        try:    
            if st.session_state.num_ponentes_ss.isdigit():
                save_to_session_state("num_ponentes_ss", st.session_state["num_ponentes_ss"]) 
            else:
                st.session_state["form_data_speaking_services"]["num_ponentes_ss"] = ""
                st.session_state.num_ponentes_correcto_ss = False
        except:
            st.session_state["form_data_speaking_services"]["num_ponentes_ss"] = ""
            st.session_state.num_ponentes_correcto_ss = False

def reset_session_participant():
    for key in list(st.session_state.keys()):
        if key.startswith("session"):
            st.session_state[key] = False
            
        # quiero reiniciar el search
        if key.startswith("nombre_") and isinstance(st.session_state[key], dict) and "search" in st.session_state[key]:
            st.session_state[key]["search"] = ""  

if "form_data_speaking_services" not in st.session_state:
    field_defaults = {
        "start_date_ss": date.today(),
        "end_date_ss": date.today(),
        "tipo_evento_ss": "",
        "num_noches_ss": "",
        "hotel_ss": "",
        "documentosubido_1_ss": None,
        "documentosubido_2_ss": None,
        "documentosubido_3_ss": None,
        "desplazamiento_ponentes_ss": "",
        "alojamiento_ponentes_ss": "",
        "presupuesto_estimado_ss": 0.00,
        "publico_objetivo_ss": "",
        "nombre_evento_ss": "",
        "descripcion_objetivo_ss": "",
        "producto_asociado_ss": "",
        "necesidad_reunion_ss": "",
        "servicio_ss": "",
        "num_ponentes_ss": "",
        "num_asistentes_totales_ss":0,
        "owner_ss": "",
        "delegate_ss": ""
    }

    st.session_state["form_data_speaking_services"] = {}
    st.session_state["id_participantes_ss"] = []
    st.session_state["download_enabled_ss"] = False
    st.session_state["path_doc_ss"] = None

    for key, value in field_defaults.items():
        save_to_session_state(key, value)


    if "name_ponente_ss" not in st.session_state:
            st.session_state["name_ponente_ss"] = ""

    if "participantes_ss" not in st.session_state:
        st.session_state.participantes_ss = [] 
    
    add_ponente()


    # Inicializar participantes en form_data_speaking_services si no existe
    # if "participantes_ss" not in st.session_state["form_data_speaking_services"]:
    #     st.session_state["form_data_speaking_services"]["participantes_ss"] = {}

    # if "participant_index_ss" not in st.session_state:
    #     st.session_state["participant_index_ss"] = 0


af.show_main_title(title="Speaking Services", logo_size=200)

meeting_type = st.sidebar.selectbox("**Tipo de reunión**",["Reunión Merck Program", "Paragüas iniciado"])

if meeting_type == "Reunión Merck Program":

    # Lista de parámetros obligatorios
    mandatory_fields = [
    "nombre_evento_ss",
    "owner_ss",
    "start_date_ss",
    "end_date_ss",
    "presupuesto_estimado_ss",
    "necesidad_reunion_ss",
    "tipo_evento_ss",
    "desplazamiento_ponentes_ss",
    "alojamiento_ponentes_ss",
    "descripcion_objetivo_ss",
    "num_asistentes_totales_ss",
    "publico_objetivo_ss",
    "num_ponentes_ss",
    "criterios_seleccion_ss",
    "documentosubido_1_ss",
    "documentosubido_2_ss"
    ]

    # Parámetros dependientes: por ejemplo, si 'alojamiento_ab' es "Sí", se requiere que 'num_noches_ss' y 'hotel_ab' tengan valor.
    dependendent_fields = {
        "alojamiento_ponentes_ss": {
            "condicion": lambda x: x == "Sí",
            "dependientes": ["num_noches_ss", "hotel_ss"]
        },
        "tipo_evento_ss": {
            "condicion": lambda x: x != "Virtual",
            "dependientes": ["sede_ss", "ciudad_ss"]
        }
    }

    validar_ia ={
        "validar_hotel": {"start_date": "start_date_ss",
                          "end_date": "end_date_ss",
                          "hotel": "hotel_ss"
                          },
        "validar_sede_location": {"start_date":"start_date_ss", 
                                  "end_date": "end_date_ss", 
                                  "sede": "sede_ss"},
        "validar_sede_venue": {"sede": "sede_ss"}
    }

    st.header("1. Detalles del Evento", divider=True)
    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            "Owner *",
            value=st.session_state["form_data_speaking_services"]["owner_ss"],
            key="owner_ss",
            on_change=lambda: save_to_session_state("owner_ss", st.session_state["owner_ss"])
        )
    with col2:
        st.text_input(
            "Delegate",
            value=st.session_state["form_data_speaking_services"]["delegate_ss"],
            key="delegate_ss",
            on_change=lambda: save_to_session_state("delegate_ss", st.session_state["delegate_ss"])
        )
    col1, col2 = st.columns(2)
    st.text_input("Nombre del evento *", value=st.session_state["form_data_speaking_services"]["nombre_evento_ss"], max_chars=255, key="nombre_evento_ss", on_change=lambda: save_to_session_state("nombre_evento_ss", st.session_state["nombre_evento_ss"]))
    descr = st.text_area("Descripción y objetivo *", value=st.session_state["form_data_speaking_services"]["descripcion_objetivo_ss"], max_chars=4000, key="descripcion_objetivo_ss", on_change=lambda: save_to_session_state("descripcion_objetivo_ss", st.session_state["descripcion_objetivo_ss"]))
    
    for word in black_list:  
        if word.lower() in descr.lower():  
            st.warning(f"La descripción contiene una palabra de la Black List: '{word}'")  
            break 

    col1, col2 = st.columns(2)
    with col1:
        start_date_ss = st.date_input("Fecha de inicio del evento *", 
                    value=st.session_state["form_data_speaking_services"]["start_date_ss"],
                    key="start_date_ss", 
                    on_change=handle_fecha_inicio,
                    format = "DD/MM/YYYY")
        if st.session_state["form_data_speaking_services"]["start_date_ss"] == date.today():
            st.warning(f"Revisa que la fecha de inicio del evento introducida sea correcta.")
    with col2:
        end_date_ss = st.date_input("Fecha de fin del evento *", 
                    value= start_date_ss if st.session_state["form_data_speaking_services"]["end_date_ss"] < start_date_ss else  st.session_state["form_data_speaking_services"]["end_date_ss"],
                    key="end_date_ss", 
                    min_value = start_date_ss,
                    on_change=lambda: save_to_session_state("end_date_ss", st.session_state["end_date_ss"]),
                    format = "DD/MM/YYYY")
        if st.session_state["form_data_speaking_services"]["end_date_ss"] == date.today():
            st.warning(f"Revisa que la fecha de fin del evento introducida sea correcta.")


    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("Tipo de evento *", ["", "Virtual", "Presencial", "Híbrido"], key="tipo_evento_ss", 
                    index= ["", "Virtual", "Presencial", "Híbrido"].index(st.session_state["form_data_speaking_services"]["tipo_evento_ss"]) if "tipo_evento_ss" in st.session_state["form_data_speaking_services"] else 0,
                    on_change=lambda: (
                        save_to_session_state("tipo_evento_ss", st.session_state["tipo_evento_ss"]),
                        save_to_session_state("sede_ss", ""),
                        save_to_session_state("ciudad_ss", "")
                    ) if st.session_state["tipo_evento_ss"] == "Virtual" else 
                        save_to_session_state("tipo_evento_ss", st.session_state["tipo_evento_ss"]))
    with col2:
        st.number_input("Nº de asistentes totales *",
                        min_value=0,
                        step=1,
                        key="num_asistentes_totales_ss",
                        value = st.session_state["form_data_speaking_services"]["num_asistentes_totales_ss"],
                        help="Ratio obligatorio (5 asistentes por ponente)",
                        on_change=lambda: save_to_session_state("num_asistentes_totales_ss", st.session_state["num_asistentes_totales_ss"]))
        
    if st.session_state["num_asistentes_totales_ss"] >= 20:
        st.warning("Cuando el número de asistentes es mayor o igual a 20, y si alguno pernocta, se debería haber comunicado y rellenado el **Formulario Farma Industria** con antelación.")

        
    col1, col2 = st.columns(2)
    with col1:

            st.text_input(
            "Sede *",
            max_chars=255,
            key="sede_ss",
            disabled=st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual",
            value="" if st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual" else st.session_state["form_data_speaking_services"].get("sede_ss", ""),
            on_change=lambda: save_to_session_state("sede_ss", st.session_state["sede_ss"])
        )
    with col2:
        st.text_input(
            "Ciudad *",
            max_chars=255,
            key="ciudad_ss",
            disabled=st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual",
            value="" if st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual" else st.session_state["form_data_speaking_services"].get("ciudad_ss", ""),
            on_change=lambda: save_to_session_state("ciudad_ss", st.session_state["ciudad_ss"])
        )

    st.text_input(
            "Público objetivo del programa *",
            max_chars=4000,
            key="publico_objetivo_ss",
            value =st.session_state["form_data_speaking_services"]["publico_objetivo_ss"],
            on_change=lambda: save_to_session_state("publico_objetivo_ss", st.session_state["publico_objetivo_ss"])
        )
    
    st.header("2. Detalles de la Actividad", divider=True)
    col1, col2 = st.columns(2)

    with col1:
        st.number_input("Presupuesto total estimado (€)*", min_value=0.0, 
                        value= st.session_state["form_data_speaking_services"]["presupuesto_estimado_ss"] if "presupuesto_estimado_ss" in st.session_state["form_data_speaking_services"] else 0.0,
                        step=100.00, key="presupuesto_estimado_ss", on_change=lambda: save_to_session_state("presupuesto_estimado_ss", st.session_state["presupuesto_estimado_ss"]))
    with col2:
        st.text_input("Producto asociado", max_chars=255, 
                      value =st.session_state["form_data_speaking_services"]["producto_asociado_ss"],
                      key="producto_asociado_ss", on_change=lambda: save_to_session_state("producto_asociado_ss", st.session_state["producto_asociado_ss"]))



    necesidad = st.text_area("Necesidad de la reunión y resultados esperados *", max_chars=4000, 
                      value =st.session_state["form_data_speaking_services"]["necesidad_reunion_ss"],
                      key="necesidad_reunion_ss", help = "Describa la necesidad detectada para organizar esta reunión de la mano de los profesionales seleccionados y cuál el resultado que se espera obtener esperado.", on_change=lambda: save_to_session_state("necesidad_reunion_ss", st.session_state["necesidad_reunion_ss"]))
    
    for word in black_list:  
        if word.lower() in necesidad.lower():  
            st.warning(f"La descripción contiene una palabra de la Black List: '{word}'")  
            break
    
    servicio = st.text_area("Descripción del servicio *", max_chars=4000, 
                    key="servicio_ss", 
                    help = "Ponencia [nombre del evento]",
                    value = f"Ponencia - {st.session_state['form_data_speaking_services']['nombre_evento_ss']}", #st.session_state["form_data_speaking_services"]["servicio_ss"]
                    disabled=True)
    st.session_state["form_data_speaking_services"]["servicio_ss"] = servicio

    st.header("3. Detalle nº ponentes", divider=True)

    col1, col2 = st.columns(2)
    col1, col2 = st.columns(2)

    
    with col1:
        num_ponentes = st.text_input(
            "Nº de ponentes *", 
            value=st.session_state["form_data_speaking_services"].get("num_ponentes_copy_ss"), 
            key="num_ponentes_ss", 
            help="Asegúrese de que se contrate la cantidad necesaria de ponentes para brindar los servicios que satisfacen las necesidades comerciales legítimas. El valor del campo debe de ser un número entero.",
            on_change = lambda: numero_ponentes_completo()
        )

    if st.session_state.num_ponentes_correcto_ss == False:
        st.warning("Se debe introducir un valor numérico.", icon="❌")
    
        
        
    with col2:
        st.multiselect(
            "Criterios de selección *",
            [
                "Experiencia como ponente", "Experiencia como profesor",
                "Experiencia clínica en tema a tratar", "Especialista en tema a tratar"
            ],
            key="criterios_seleccion_ss",
            default=st.session_state["form_data_speaking_services"]["criterios_seleccion_ss"] if "criterios_seleccion_ss" in st.session_state["form_data_speaking_services"] else [],
            on_change=lambda: save_to_session_state("criterios_seleccion_ss", st.session_state["criterios_seleccion_ss"])
        )


    st.header("4. Logística de los ponentes", divider=True)

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox("¿Desplazamiento de ponentes? *",
                     ["", "No", "Sí"],
                     index=["", "No", "Sí"].index(st.session_state["form_data_speaking_services"]["desplazamiento_ponentes_ss"]),
                     key="desplazamiento_ponentes_ss",
                     on_change=lambda: save_to_session_state("desplazamiento_ponentes_ss", st.session_state["desplazamiento_ponentes_ss"]))
    with col2:
        st.selectbox("¿Alojamiento de ponentes? *", ["","No", "Sí"], 
                    index=["","No", "Sí"].index(st.session_state["form_data_speaking_services"]["alojamiento_ponentes_ss"]),
                    key="alojamiento_ponentes_ss", 
                    on_change=lambda: (
                                        save_to_session_state("alojamiento_ponentes_ss", st.session_state["alojamiento_ponentes_ss"]),
                                        save_to_session_state("num_noches_ss", ""),
                                        save_to_session_state("hotel_ss", "")
                                    ) if st.session_state["alojamiento_ponentes_ss"] == "No" else 
                                        save_to_session_state("alojamiento_ponentes_ss", st.session_state["alojamiento_ponentes_ss"]))

    col1, col2 = st.columns(2)


    with col1:
        st.text_input("Nº de noches *", 
                        key="num_noches_ss", 
                        disabled=st.session_state["form_data_speaking_services"]["alojamiento_ponentes_ss"] == "No",
                        value= "" if st.session_state["form_data_speaking_services"]["alojamiento_ponentes_ss"] == "No" else st.session_state["form_data_speaking_services"].get("num_noches_copy_ss"),
                        help = "Se debe introducir un número.",
                        on_change=lambda: validacion_num_noches()
        )

    noches = (st.session_state["end_date_ss"] - st.session_state["start_date_ss"]).days + 1
    if st.session_state.num_noches_correcto_ss == False:
        st.warning(f"El número de noches no puede exceder la duración del evento ({noches} días).")

                        
    with col2:
        st.text_input("Hotel *", 
                    max_chars=255, 
                    key="hotel_ss",
                    disabled=st.session_state["form_data_speaking_services"]["alojamiento_ponentes_ss"] == "No", 
                    value="" if st.session_state["form_data_speaking_services"]["alojamiento_ponentes_ss"] == "No" else st.session_state["form_data_speaking_services"].get("hotel_ss", ""),
                    on_change=lambda: save_to_session_state("hotel_ss", st.session_state["hotel_ss"]))



    st.header("5. Agregar datos de ponentes", divider=True)
    ponentes_section()

    st.header("6. Documentos", divider=True)
    with st.expander("Ver documentos necesarios"):
        st.file_uploader("Agenda del evento *",
                  type=["pdf", "docx", "xlsx", "ppt"],
                  key="documentosubido_1_ss", 
                  on_change=lambda: save_to_session_state("documentosubido_1_ss", st.session_state["documentosubido_1_ss"] if st.session_state["documentosubido_1_ss"] else "")) 
        st.file_uploader("Contratos inferiores a 1000€: MINUTA reunión previa con Compliance *", 
                 type=["pdf", "docx", "xlsx", "ppt"],
                 key="documentosubido_2_ss", 
                 on_change=lambda: save_to_session_state("documentosubido_2_ss", st.session_state["documentosubido_2_ss"] if st.session_state["documentosubido_2_ss"] else "")) 
        st.file_uploader("Documentos adicionales", 
                 type=["pdf", "docx", "xlsx", "ppt"],
                 key="documentosubido_3_ss", 
                 on_change=lambda: save_to_session_state("documentosubido_3_ss", st.session_state["documentosubido_3_ss"] if st.session_state["documentosubido_3_ss"] else "")) 


    # Estado inicial para el botón de descargar
    st.session_state.download_enabled_ss = False
    button_form(meeting_type)
    disabled = not st.session_state.download_enabled_ss
    if disabled == False:
        download_document(disabled, meeting_type)



else:
    mandatory_fields = [
        "start_date_ss",
        "end_date_ss",
        "nombre_evento_ss",
        "tipo_evento_ss",
        "owner_ss"
    ]

    # Parámetros dependientes: por ejemplo, si 'alojamiento_ab' es "Sí", se requiere que 'num_noches_ss' y 'hotel_ab' tengan valor.
    dependendent_fields = {
        "tipo_evento_ss": {
            "condicion": lambda x: x != "Virtual",
            "dependientes": ["sede_ss", "ciudad_ss"]
        }
    }

    validar_ia ={
        "validar_sede_location": {"start_date":"start_date_ss", 
                                  "end_date": "end_date_ss", 
                                  "sede": "sede_ss"},
        "validar_sede_venue": {"sede": "sede_ss"}
    }
    #st.header("Caso Paragüas", divider=True)
    st.header("1. Detalles del Evento", divider=True)
    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            "Owner *",
            value=st.session_state["form_data_speaking_services"]["owner_ss"],
            key="owner_ss",
            on_change=lambda: save_to_session_state("owner_ss", st.session_state["owner_ss"])
        )
    with col2:
        st.text_input(
            "Delegate",
            value=st.session_state["form_data_speaking_services"]["delegate_ss"],
            key="delegate_ss",
            on_change=lambda: save_to_session_state("delegate_ss", st.session_state["delegate_ss"])
        )
    col1, col2 = st.columns(2)
    st.text_input("Nombre del evento *", 
                  value=st.session_state["form_data_speaking_services"]["nombre_evento_ss"],
                  max_chars=255, key="nombre_evento_ss", on_change=lambda: save_to_session_state("nombre_evento_ss", st.session_state["nombre_evento_ss"]))
    #st.text_area("Descripción y objetivo *", max_chars=4000, key="descripcion_objetivo_ss", on_change=lambda: save_to_session_state("descripcion_objetivo_ss", st.session_state["descripcion_objetivo_ss"]))

    col1, col2 = st.columns(2)
    with col1:
        start_date_ss = st.date_input("Fecha de inicio del evento *", 
                    value=st.session_state["form_data_speaking_services"]["start_date_ss"],
                    key="start_date_ss", 
                    on_change=handle_fecha_inicio,
                    format = "DD/MM/YYYY")
        if st.session_state["form_data_speaking_services"]["start_date_ss"] == date.today():
            st.warning(f"Revisa que la fecha de inicio del evento introducida sea correcta.")
    with col2:
        st.date_input("Fecha de fin del evento *", 
                    value= start_date_ss if st.session_state["form_data_speaking_services"]["end_date_ss"] < start_date_ss else  st.session_state["form_data_speaking_services"]["end_date_ss"],
                    key="end_date_ss", 
                    min_value = start_date_ss,
                    on_change=lambda: save_to_session_state("end_date_ss", st.session_state["end_date_ss"]),
                    format = "DD/MM/YYYY")
    
        if st.session_state["form_data_speaking_services"]["end_date_ss"] == date.today():
            st.warning(f"Revisa que la fecha de fin del evento introducida sea correcta.")
        
    st.selectbox("Tipo de evento *", ["", "Virtual", "Presencial", "Híbrido"], key="tipo_evento_ss", 
                    index= ["", "Virtual", "Presencial", "Híbrido"].index(st.session_state["form_data_speaking_services"]["tipo_evento_ss"]) if "tipo_evento_ss" in st.session_state["form_data_speaking_services"] else 0,
                    on_change=lambda: (
                        save_to_session_state("tipo_evento_ss", st.session_state["tipo_evento_ss"]),
                        save_to_session_state("sede_ss", ""),
                        save_to_session_state("ciudad_ss", "")
                    ) if st.session_state["tipo_evento_ss"] == "Virtual" else 
                        save_to_session_state("tipo_evento_ss", st.session_state["tipo_evento_ss"]))

        
    col1, col2 = st.columns(2)
    with col1:

            st.text_input(
            "Sede",
            max_chars=255,
            key="sede_ss",
            disabled=st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual",
            value="" if st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual" else st.session_state["form_data_speaking_services"].get("sede_ss", ""),
            on_change=lambda: save_to_session_state("sede_ss", st.session_state["sede_ss"])
        )
    with col2:
        st.text_input(
            "Ciudad",
            max_chars=255,
            key="ciudad_ss",
            disabled=st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual",
            value="" if st.session_state["form_data_speaking_services"]["tipo_evento_ss"] == "Virtual" else st.session_state["form_data_speaking_services"].get("ciudad_ss", ""),
            on_change=lambda: save_to_session_state("ciudad_ss", st.session_state["ciudad_ss"])
        )

    st.header("2. Agregar datos de ponentes", divider=True)
    ponentes_section()
    st.session_state.download_enabled_ss = False
    button_form_reducido(meeting_type)
    disabled = not st.session_state.download_enabled_ss
    if disabled == False:
        download_document(disabled, meeting_type)


#st.write(st.session_state["form_data_speaking_services"])
#st.write(st.session_state)