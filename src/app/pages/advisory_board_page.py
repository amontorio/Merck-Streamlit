import pandas as pd
import streamlit as st
from streamlit_searchbox import st_searchbox
from datetime import date
import uuid
import auxiliar.aux_functions as af
import auxiliar.create_docx as cd
import traceback
import io
import time
# Diccionario de tarifas según el tier

tarifas = {
    "0": 300, 
    "1": 250,
    "2": 200,
    "3": 150,
    "4": 200 #NO APARECE
}

# Lista de parámetros obligatorios
mandatory_fields = [
"start_date_ab",
"end_date_ab",
#"estado_aprobacion_ab",
"otra_actividad_departamento_ab",
"otra_actividad_otro_departamento_ab",
"desplazamiento_ab",
"alojamiento_ab",
"tipo_evento_ab",
"participantes_ab",
"producto_asociado_ab",
#"descripcion_servicio_ab",
"necesidad_reunion_ab",
"descripcion_objetivo_ab",
"num_participantes_totales_ab",
"publico_objetivo_ab",
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

def save_to_session_state(key, value, key_participante=None, field_participante=None):
    if key != "participantes_ab":
        if key not in ["documentosubido_1"]:
            st.session_state[key] = value
        st.session_state["form_data_advisory_board"][key] = value
    else:
        st.session_state[field_participante] = value
        st.session_state["form_data_advisory_board"][key][key_participante][field_participante] = value
        st.session_state[f"session_ab_{key_participante}"] = True

def add_participant():
    # Añadir un nuevo participante con campos inicializados
    id_user = str(uuid.uuid4())
    new_participant = {
        "id": id_user,
        f"nombre_{id_user}": "",
        f"dni_{id_user}": "",
        f"dni_correcto_{id_user}": True,
        f"tier_{id_user}": "0",
        f"centro_trabajo_{id_user}": "",
        f"email_{id_user}": "",
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


def asignacion_nombre(id_user):
        if not f"session_ab_{id_user}" in st.session_state:
            st.session_state[f"session_ab_{id_user}"] = False
        if f'nombre_{id_user}' in st.session_state and st.session_state["form_data_advisory_board"]["participantes_ab"][f"{id_user}"].get(f"nombre_{id_user}", "") != None:
            nombre_ponente = st.session_state["form_data_advisory_board"]["participantes_ab"][f"{id_user}"].get(f"nombre_{id_user}", "").rsplit('-', 1)[0] 
            st.session_state["form_data_advisory_board"]["participantes_ab"][f"{id_user}"]["name_ponente_ab"] = nombre_ponente
        else:
            st.session_state["form_data_advisory_board"]["participantes_ab"][f"{id_user}"]["name_ponente_ab"] = ""
            #st.session_state[f"session_ab_{id_user}"] = False

########## validaciones especiales
def validacion_dni(id_user):
        if not f'dni_{id_user}' in st.session_state:
            st.session_state[f'dni_{id_user}'] = ""
            st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_correcto_{id_user}"] = True
        else:
            dni = st.session_state.get(f"dni_{id_user}", "")
            st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_correcto_{id_user}"] = True
            if dni =="":
                st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_correcto_{id_user}"] = True
            else:
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


def validacion_completa_dni(id_user):
        validacion_dni(id_user)
        if st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"dni_correcto_{id_user}"] == True:
            save_to_session_state("participantes_ab", st.session_state[f"dni_{id_user}"], id_user, f"dni_{id_user}")
        else:
            st.toast("El DNI introducido no es correcto.", icon="❌")
            time.sleep(1)
            save_to_session_state("participantes_ab", "", id_user, f"dni_{id_user}")

def validacion_email(id_user):
        if not f'email_{id_user}' in st.session_state:
            st.session_state[f'email_{id_user}'] = ""
            st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] = True
        else:
            mail = st.session_state.get(f"email_{id_user}", "")
            st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] = True
            if mail =="":
                st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] = True
            else:
                try:
                    #patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    tlds_validos = ['com', 'org', 'net', 'es', 'edu', 'gov', 'info', 'biz']
                    tlds_pattern = '|'.join(tlds_validos)
                    patron = rf'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?:{tlds_pattern})$'

                    matcheo = re.match(patron, mail) 

                    if matcheo == None:
                        st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] = False

                except:
                    if mail != "":
                        st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] = False


def validacion_completa_email(id_user):
        validacion_email(id_user)
        if st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"email_correcto_{id_user}"] == True:
            save_to_session_state("participantes_ab", st.session_state[f"email_{id_user}"], id_user, f"email_{id_user}")
        else:
            st.toast("El email introducido no es correcto.", icon="❌")
            time.sleep(1)
            save_to_session_state("participantes_ab", "", id_user, f"email_{id_user}")
            

def participantes_section():
    st.header("5. Detalles de los Participantes", divider=True)

    if st.button("Agregar participante", use_container_width=True, icon="➕", key="add_participant_button"):
        add_participant()

    index = 0
    # Renderizar los participantes_ab
    for info_user in st.session_state["participantes_ab"]:

        id_user = info_user["id"]

        col_participant, col_remove_participant_individual = st.columns([10,1])
        with col_participant:
            asignacion_nombre(id_user)
            nombre_expander_ab = st.session_state['form_data_advisory_board']['participantes_ab'][f'{id_user}']['name_ponente_ab']
            if nombre_expander_ab != "":
                aux = ": "
            else:
                aux = ""
            with st.expander(f"Participante {index + 1}{aux}{nombre_expander_ab}", expanded=st.session_state[f"session_ab_{id_user}"], icon="👩‍⚕️"):
                nombre = st_searchbox(
                        #label="Buscador de HCO / HCP *",
                        search_function=af.search_function,
                        placeholder="Busca un HCO / HCP *",
                        key=f"nombre_{id_user}",
                        edit_after_submit="option",
                        default_searchterm=info_user.get(f"nombre_{id_user}", ""),
                        #submit_function=print(st.session_state[f"nombre_{id_user}"])
                        submit_function= lambda x: save_to_session_state("participantes_ab", af.handle_tier_from_name(st.session_state[f"nombre_{id_user}"]), id_user, f"tier_{id_user}")
                    )

                st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"nombre_{id_user}"] = nombre
                if st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"nombre_{id_user}"] != None:
                        if st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"nombre_{id_user}"].rsplit('-', 1)[0] != st.session_state['form_data_advisory_board']['participantes_ab'][f'{id_user}']["name_ponente_ab"]:
                            st.rerun()

                col1, col2 = st.columns(2)
                with col1:
                    
                    dni = st.text_input(
                        f"DNI del participante {index + 1}", 
                        value=info_user.get(f"dni_{id_user}", ""), 
                        key=f"dni_{id_user}",
                        on_change= validacion_completa_dni(id_user)
                    )

                    centro = st.text_input(
                        f"Centro de trabajo del participante {index + 1} *", 
                        value=info_user.get(f"centro_trabajo_{id_user}", ""), 
                        key=f"centro_trabajo_{id_user}",
                        on_change=lambda: save_to_session_state("participantes_ab", st.session_state[f"centro_trabajo_{id_user}"], id_user, f"centro_trabajo_{id_user}")
                    )

                    cobra = st.selectbox(
                        "¿Cobra a través de sociedad? *", 
                        ["No", "Sí"], 
                        key=f"cobra_sociedad_{id_user}",
                        index= ["No", "Sí"].index(st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"cobra_sociedad_{id_user}"]) if f"cobra_sociedad_{id_user}" in st.session_state["form_data_advisory_board"]["participantes_ab"][id_user] else 0

                    )
                    st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"cobra_sociedad_{id_user}"] = cobra
                    
                    st.markdown('<p style="font-size: 14px;">Tiempo de preparación</p>', unsafe_allow_html=True)  
 
                    
                with col2:
                    tier = st.selectbox(
                        f"Tier del participante {index + 1} *", 
                        ["0", "1", "2", "3", "4"],
                        key=f"tier_{id_user}",
                        index= ["0", "1", "2", "3", "4"].index(st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"tier_{id_user}"]) if f"tier_{id_user}" in st.session_state["form_data_advisory_board"]["participantes_ab"][id_user] else 0,

                    )
                    st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"tier_{id_user}"] = tier
                    
                    email = st.text_input(
                        f"Email del participante {index + 1} *", 
                        value=info_user.get(f"email_{id_user}", ""), 
                        key=f"email_{id_user}",
                        on_change= validacion_completa_email(id_user)
                    )
                    
                    nombre_sociedad = st.text_input(
                        "Nombre de la sociedad",
                        value = st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"nombre_sociedad_{id_user}"] if cobra == "Sí" else "",
                        key=f"nombre_sociedad_{id_user}",
                        on_change = lambda: save_to_session_state("participantes_ab","", id_user, f"nombre_sociedad_{id_user}")
                              if st.session_state[f"cobra_sociedad_{id_user}"] == "No" else 
                              save_to_session_state("participantes_ab", st.session_state[f"nombre_sociedad_{id_user}"], id_user, f"nombre_sociedad_{id_user}"),
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
                        value= st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"preparacion_horas_{id_user}"] if f"preparacion_horas_{id_user}" in st.session_state["form_data_advisory_board"]["participantes_ab"][id_user] else 0,  
                    )
                    st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"preparacion_horas_{id_user}"] = tiempo_prep_horas
                    
                with col_prep_minutos:
                    
                    tiempo_prep_minutos = st.selectbox(
                        label="Minutos",
                        options=[0,15,30,45],
                        key=f"preparacion_minutos_{id_user}",
                        index= [0,15,30,45].index(st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"preparacion_minutos_{id_user}"]) if f"preparacion_minutos_{id_user}" in st.session_state["form_data_advisory_board"]["participantes_ab"][id_user] else 0,
                    )
                    st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"preparacion_minutos_{id_user}"] = tiempo_prep_minutos
                    
                with col_ponencia_horas:
                    tiempo_ponencia_horas = st.number_input(
                        label="Horas",
                        min_value=0,
                        step=1,
                        key=f"ponencia_horas_{id_user}",
                        value= st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"ponencia_horas_{id_user}"] if f"ponencia_horas_{id_user}" in st.session_state["form_data_advisory_board"]["participantes_ab"][id_user] else 0,

                    )
                    st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"ponencia_horas_{id_user}"] = tiempo_ponencia_horas
                    
                with col_ponencia_minutos:
                    tiempo_ponencia_minutos = st.selectbox(
                        label="Minutos",
                        options=[0,15,30,45],
                        key=f"ponencia_minutos_{id_user}",
                        index= [0,15,30,45].index(st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"ponencia_minutos_{id_user}"]) if f"ponencia_minutos_{id_user}" in st.session_state["form_data_advisory_board"]["participantes_ab"][id_user] else 0,
                    )
                    
                    st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"ponencia_minutos_{id_user}"] = tiempo_ponencia_minutos
                        
                # Obtener valores de tiempo en horas decimales
                tiempo_ponencia_horas = tiempo_ponencia_horas + tiempo_ponencia_minutos / 60
                tiempo_prep_horas = tiempo_prep_horas + tiempo_prep_minutos / 60

                # Obtener tarifa en función del tier
                tarifa = tarifas.get(tier, 0)  # Si no encuentra el tier, usa 0

                # Calcular honorarios
                honorarios = (tiempo_ponencia_horas + tiempo_prep_horas) * tarifa
                
                honorarios = st.number_input(
                    "Honorarios", 
                    value= float(honorarios), 
                    min_value=0.0, 
                    step=0.01, 
                    key=f"honorarios_{id_user}",
                    disabled=True
                )
                st.session_state["form_data_advisory_board"]["participantes_ab"][id_user][f"honorarios_{id_user}"] = honorarios
        index +=1
        with col_remove_participant_individual:
            if st.button("🗑️", key=f"remove_participant_{id_user}", use_container_width=True, type="secondary"):
                if id_user in st.session_state["form_data_advisory_board"]["participantes_ab"].keys():
                    del st.session_state["form_data_advisory_board"]["participantes_ab"][id_user]
                    st.session_state["participantes_ab"] = list(filter(lambda x: x['id'] != id_user, st.session_state["participantes_ab"]))

                st.rerun()



















# Inicializar estado del formulario en session_state
if "form_data_advisory_board" not in st.session_state:

    field_defaults = {
        "nombre_evento_ab": "",
        "start_date_ab": date.today(),
        "end_date_ab": date.today(),
        "estado_aprobacion_ab": "N/A",
        "otra_actividad_departamento_ab": "No lo sé", 
        "otra_actividad_otro_departamento_ab": "No lo sé",
        "desplazamiento_ab": "No",
        "alojamiento_ab": "No", 
        "num_noches_ab": 0,
        "hotel_ab": "",
        "tipo_evento_ab": "Virtual",
        "num_participantes_totales_ab": 0,
        "num_participantes_ab": 0
    }

    st.session_state["form_data_advisory_board"] = {}
    st.session_state["id_participantes"] = []
    
    st.session_state["download_enabled_ab"] = False
    st.session_state["path_doc_ab"] = None
    
    
    for key, value in field_defaults.items():
        save_to_session_state(key, value)

    if "participantes_ab" not in st.session_state:
        st.session_state.participantes_ab = []
    add_participant()
        

af.show_main_title(title="Advisory Board", logo_size=200)


st.header("1. Detalles del Evento", divider=True)
st.text_input("Nombre *", 
              max_chars=255, 
              key="nombre_evento_ab",
              value= st.session_state["form_data_advisory_board"]["nombre_evento_ab"] if "nombre_evento_ab" in st.session_state["form_data_advisory_board"] else "",
              on_change=lambda: save_to_session_state("nombre_evento_ab", st.session_state["nombre_evento_ab"]))

st.text_area("Descripción y objetivo *",
             max_chars=4000,
             key="descripcion_objetivo_ab",
             value= st.session_state["form_data_advisory_board"]["descripcion_objetivo_ab"] if "descripcion_objetivo_ab" in st.session_state["form_data_advisory_board"] else "",
             on_change=lambda: save_to_session_state("descripcion_objetivo_ab", st.session_state["descripcion_objetivo_ab"]))

col1, col2 = st.columns(2)
with col1:
    start_ab = st.date_input("Fecha de inicio del evento *",
                  value=st.session_state["form_data_advisory_board"]["start_date_ab"],
                  key="start_date_ab",
                  on_change=lambda: save_to_session_state("start_date_ab", st.session_state["start_date_ab"]),
                  format = "DD/MM/YYYY")

with col2:
    st.date_input("Fecha de fin del evento *",
                  value= start_ab if st.session_state["form_data_advisory_board"]["end_date_ab"] < start_ab else st.session_state["form_data_advisory_board"]["end_date_ab"],
                  min_value = start_ab,
                  key="end_date_ab",
                  on_change=lambda: save_to_session_state("end_date_ab", st.session_state["end_date_ab"]),
                  format = "DD/MM/YYYY")


col1, col2 = st.columns(2)
with col1:
    st.selectbox("Tipo de evento *",
                 ["Virtual", "Presencial", "Híbrido"],
                 key="tipo_evento_ab",
                 index= ["Virtual", "Presencial", "Híbrido"].index(st.session_state["form_data_advisory_board"]["tipo_evento_ab"]) if "tipo_evento_ab" in st.session_state["form_data_advisory_board"] else 0,

                 on_change=lambda: (
                     save_to_session_state("tipo_evento_ab", st.session_state["tipo_evento_ab"]),
                     save_to_session_state("sede_ab", ""),
                     save_to_session_state("ciudad_ab", "")
                 ) if st.session_state["tipo_evento_ab"] == "Virtual" else 
                     save_to_session_state("tipo_evento_ab", st.session_state["tipo_evento_ab"]))
with col2:
    st.number_input("Nº de participantes totales *",
                    min_value=0,
                    step=1,
                    key="num_participantes_totales_ab",
                    help="Ratio obligatorio (5 asistentes por ponente)",
                    value= st.session_state["form_data_advisory_board"]["num_participantes_totales_ab"] if "num_participantes_totales_ab" in st.session_state["form_data_advisory_board"] else "",
                    on_change=lambda: save_to_session_state("num_participantes_totales_ab", st.session_state["num_participantes_totales_ab"]))

col1, col2 = st.columns(2)
with col1:
    st.text_input(
        "Sede",
        max_chars=255,
        key="sede_ab",
        disabled=st.session_state["form_data_advisory_board"]["tipo_evento_ab"] == "Virtual",
        value="" if st.session_state["form_data_advisory_board"]["tipo_evento_ab"] == "Virtual" else st.session_state["form_data_advisory_board"].get("sede_ab", ""),
        on_change=lambda: save_to_session_state("sede_ab", st.session_state["sede_ab"])
    )
with col2:
    st.text_input(
        "Ciudad",
        max_chars=255,
        key="ciudad_ab",
        disabled=st.session_state["form_data_advisory_board"]["tipo_evento_ab"] == "Virtual",
        value="" if st.session_state["form_data_advisory_board"]["tipo_evento_ab"] == "Virtual" else st.session_state["form_data_advisory_board"].get("ciudad_ab", ""),
        on_change=lambda: save_to_session_state("ciudad_ab", st.session_state["ciudad_ab"])
    )

st.text_input(
        "Público objetivo del programa *",
        max_chars=255,
        key="publico_objetivo_ab",
        value= st.session_state["form_data_advisory_board"]["publico_objetivo_ab"] if "publico_objetivo_ab" in st.session_state["form_data_advisory_board"] else "",
        on_change=lambda: save_to_session_state("publico_objetivo_ab", st.session_state["publico_objetivo_ab"])
    )



st.header("2. Detalles de la Actividad", divider=True)
col1, col2 = st.columns(2)

with col1:
    st.text_input("Producto asociado *",
                  max_chars=255,
                  key="producto_asociado_ab",
                  value= st.session_state["form_data_advisory_board"]["producto_asociado_ab"] if "producto_asociado_ab" in st.session_state["form_data_advisory_board"] else "",
                  on_change=lambda: save_to_session_state("producto_asociado_ab", st.session_state["producto_asociado_ab"]))

with col2:
    st.selectbox("Estado de la aprobación", 
                 ["N/A", "Aprobado", "No Aprobado"], 
                 key="estado_aprobacion_ab", 
                 index= ["N/A", "Aprobado", "No Aprobado"].index(st.session_state["form_data_advisory_board"]["estado_aprobacion_ab"]) if "estado_aprobacion_ab" in st.session_state["form_data_advisory_board"] else 0,
                 on_change=lambda: save_to_session_state("estado_aprobacion_ab", st.session_state["estado_aprobacion_ab"]))


servicio = st.text_area("Descripción del servicio *", 
                 max_chars=4000, 
                 key="descripcion_servicio_ab", 
                 help="Describa la necesidad de obtener información de los paticipantes y el propósito para el cual se utilizará dicha información.", 
                 value= f"Advisory Board Participation - {st.session_state['form_data_advisory_board']['nombre_evento_ab']}", #st.session_state["form_data_advisory_board"]["descripcion_servicio_ab"] if "descripcion_servicio_ab" in st.session_state["form_data_advisory_board"] else "",
                 disabled = True)
st.session_state["form_data_advisory_board"]["descripcion_servicio_ab"] = servicio

st.text_area("Necesidad de la reunión y resultados esperados *",
                 max_chars=4000,
                 key="necesidad_reunion_ab",
                 value= st.session_state["form_data_advisory_board"]["necesidad_reunion_ab"] if "necesidad_reunion_ab" in st.session_state["form_data_advisory_board"] else "",
                 on_change=lambda: save_to_session_state("necesidad_reunion_ab", st.session_state["necesidad_reunion_ab"]))


col1, col2 = st.columns(2)

with col1:
    st.selectbox("¿Otra actividad en el departamento en últimos 12 meses? *", 
                 ["No lo sé", "Sí", "No"], 
                 key="otra_actividad_departamento_ab", 
                 index= ["No lo sé", "Sí", "No"].index(st.session_state["form_data_advisory_board"]["otra_actividad_departamento_ab"]) if "otra_actividad_departamento_ab" in st.session_state["form_data_advisory_board"] else 0,
                 on_change=lambda: save_to_session_state("otra_actividad_departamento_ab", st.session_state["otra_actividad_departamento_ab"]))
with col2:
    st.selectbox("¿Y en otro departamento? *",
                 ["No lo sé", "Sí", "No"],
                 key="otra_actividad_otro_departamento_ab",
                 index= ["No lo sé", "Sí", "No"].index(st.session_state["form_data_advisory_board"]["otra_actividad_otro_departamento_ab"]) if "otra_actividad_otro_departamento_ab" in st.session_state["form_data_advisory_board"] else 0,
                 on_change=lambda: save_to_session_state("otra_actividad_otro_departamento_ab", st.session_state["otra_actividad_otro_departamento_ab"]))

st.header("3. Logística de la Actividad", divider=True)
col1, col2 = st.columns(2)
with col1:
    st.selectbox("¿Desplazamiento de participantes? *", 
                 ["No", "Sí"], 
                 key="desplazamiento_ab",
                 index= ["No", "Sí"].index(st.session_state["form_data_advisory_board"]["desplazamiento_ab"]) if "desplazamiento_ab" in st.session_state["form_data_advisory_board"] else 0,
                 on_change=lambda: save_to_session_state("desplazamiento_ab", st.session_state["desplazamiento_ab"]))
with col2:
    st.selectbox("¿Alojamiento de participantes? *",
                 ["No", "Sí"],
                 key="alojamiento_ab",
                 index= ["No", "Sí"].index(st.session_state["form_data_advisory_board"]["alojamiento_ab"]) if "alojamiento_ab" in st.session_state["form_data_advisory_board"] else 0,
                 on_change=lambda: (
                     save_to_session_state("alojamiento_ab", st.session_state["alojamiento_ab"]),
                     save_to_session_state("hotel_ab", ""),
                     save_to_session_state("num_noches_ab", 0)
                 ) if st.session_state["alojamiento_ab"] == "No" else 
                     save_to_session_state("alojamiento_ab", st.session_state["alojamiento_ab"]))

with col1:
    st.text_input(
        "Hotel",
        max_chars=255,
        key="hotel_ab",
        disabled=st.session_state["form_data_advisory_board"]["alojamiento_ab"] == "No",
        value="" if st.session_state["form_data_advisory_board"]["alojamiento_ab"] == "No" else st.session_state["form_data_advisory_board"].get("hotel_ab", ""),
        on_change=lambda: save_to_session_state("hotel_ab", st.session_state["hotel_ab"])
    )
with col2:
    st.number_input(
        "Nº de noches", 
        min_value=0, 
        step=1, 
        key="num_noches_ab", 
        disabled=st.session_state["form_data_advisory_board"]["alojamiento_ab"] == "No",
        value=0 if st.session_state["form_data_advisory_board"]["alojamiento_ab"] == "No" else st.session_state["form_data_advisory_board"].get("num_noches_ab", 0),
        on_change=lambda: save_to_session_state("num_noches_ab", st.session_state["num_noches_ab"])
    )
    

st.header("4. Participantes del Advisory", divider=True)
col1, col2 = st.columns(2)
with col1:
    st.number_input("Nº de participantes *",
                    min_value=0,
                    step=1,
                    key="num_participantes_ab",
                    help="Asegúrese de que se contrate la cantidad necesaria de participantes_ab para brindar los servicios que satisfacen las necesidades legítimas.",
                    value= st.session_state["form_data_advisory_board"]["num_participantes_ab"] if "num_participantes_ab" in st.session_state["form_data_advisory_board"] else "",
                    on_change=lambda: save_to_session_state("num_participantes_ab", st.session_state["num_participantes_ab"]))
with col2:
    st.multiselect(
        "Criterios de selección *",
        [
            "Kol Global", "Experiencia como ponente", "Experiencia como Participante de Advisory",
            "Experiencia como profesor", "Experiencia clínica en tema a tratar", "Especialista en tema a tratar"
        ],
        key="criterios_seleccion_ab",
        default=st.session_state["form_data_advisory_board"]["criterios_seleccion_ab"] if "criterios_seleccion_ab" in st.session_state["form_data_advisory_board"] else [],
        on_change=lambda: save_to_session_state("criterios_seleccion_ab", st.session_state["criterios_seleccion_ab"])
    )
st.text_area("Justificación de número de participantes *",
             max_chars=4000,
             key="justificacion_participantes_ab",
             value= st.session_state["form_data_advisory_board"]["justificacion_participantes_ab"] if "justificacion_participantes_ab" in st.session_state["form_data_advisory_board"] else "",
             on_change=lambda: save_to_session_state("justificacion_participantes_ab", st.session_state["justificacion_participantes_ab"]))


participantes_section()

st.header("6. Documentos", divider=True)
st.file_uploader("Programa del evento *", type=["pdf", "docx", "xlsx", "ppt"], key="documentosubido_1", on_change=lambda: save_to_session_state("documentosubido_1", st.session_state["documentosubido_1"]))


# Estado inicial para el botón de descargar
st.session_state.download_enabled_ab = False
# Botón para enviar
def button_form():
    if st.button(label="Generar Plantilla", use_container_width=True, type="primary"):
        with st.status("Validando campos...", expanded=True, state = "running") as status:
            st.write("Validando información general del formulario...")
            time.sleep(4)
            st.write("Validando información de los consultores...")
            time.sleep(4)
        
        try:
            errores_general, errores_participantes = af.validar_campos(st.session_state["form_data_advisory_board"], mandatory_fields, dependendent_fields)
            if not errores_general and all(not lista for lista in errores_participantes.values()):
                doc, st.session_state.path_doc_ab = cd.crear_documento_advisory(st.session_state["form_data_advisory_board"])
                st.session_state.download_enabled_ab = True
                st.toast("Formulario generado correctamente", icon="✔️")
            else:
                msg_general = ""
                for msg in errores_general:
                    msg_general += f"\n* {msg}\n"
                st.error(msg_general)

                print(st.session_state['form_data_advisory_board']['participantes_ab'])
                for id_user, list_errors in errores_participantes.items():
                    if len(list_errors) > 0:
                        # Obtener el diccionario de participantes
                        participantes = st.session_state['form_data_advisory_board']['participantes_ab']

                        # Obtener la posición del ID en las claves del diccionario
                        keys_list = list(participantes.keys())  # Convertir las claves en una lista
                        posicion = keys_list.index(id_user) + 1 if id_user in keys_list else None
                        msg_participantes = f"\n**Errores del Participante {posicion}**\n"
                        for msg in list_errors:
                            msg_participantes += f"\n* {msg}\n"
                        st.error(msg_participantes)
                        
                st.toast("Debes rellenar todos los campos obligatorios.", icon="❌")
            # Leer el archivo Word y prepararlo para descarga
        except Exception as e:
            traceback.print_exc()
            st.toast(f"Ha ocurrido un problema al generar el formulario -> {e}", icon="❌")
        
        # Actualizo el estado
        if st.session_state.download_enabled_ab == True:
            status.update(
                label="Validación completada!", state="complete", expanded=False
            )
        else:
            status.update(
                label="Validación no completada. Se deben revisar los campos obligatorios faltantes.", state="error", expanded=False
            )
        
def download_document():
    if st.session_state.path_doc_ab:
        with open(st.session_state.path_doc_ab, "rb") as file:
            st.download_button(
                label="Descargar ZIP",
                data=file,
                file_name="Advisory_Board.zip",
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
download_document()

#st.header("Datos guardados")
#st.write(st.session_state["form_data_advisory_board"])


