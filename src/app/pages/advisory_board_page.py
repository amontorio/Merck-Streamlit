import streamlit as st

def show_participant(index):
    if f"nombre_participante_{index}" not in st.session_state:
        st.session_state[f"nombre_participante_{index}"] = ""

    with st.expander(f"Participante {index + 1}"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(f"Nombre del participante {index + 1}", max_chars=255, key=f"nombre_participante_{index}")
            st.text_input(f"DNI del participante {index + 1}", max_chars=255, key=f"dni_participante_{index}")
            st.selectbox(f"Tier del participante {index + 1}", ["", "1", "2", "3"], key=f"tier_participante_{index}")
            st.text_input(f"Centro de trabajo del participante {index + 1}", max_chars=255, key=f"centro_trabajo_{index}")
            st.selectbox(f"Cobra a través de sociedad?", ["", "Sí", "No"], key=f"cobra_sociedad_{index}")
        with col2:
            st.text_input(f"Apellidos del participante {index + 1}", max_chars=255, key=f"apellidos_participante_{index}")
            st.text_input(f"Email del participante {index + 1}", max_chars=255, key=f"email_contrato_{index}")
            st.number_input(f"Honorarios", min_value=0.0, step=0.01, key=f"honorarios_{index}")
            st.number_input(f"Tiempo de preparación (min: 0, 15, 30, 45)", min_value=0, step=15, key=f"tiempo_preparacion_{index}")
            st.number_input(f"Tiempo de reunión (min: 0, 15, 30, 45)", min_value=0, step=15, key=f"tiempo_reunion_{index}")

def save_to_session_state(key, value, key_participante=None, field_participante=None):
    if key != "participantes":
        st.session_state["form_data"][key] = value
    else:
        st.session_state["form_data"][key][key_participante][field_participante] = value

def add_participant():
    # Añadir un nuevo participante con campos inicializados
    new_participant = {
        "nombre": "",
        "apellidos": "",
        "dni": "",
        "tier": "",
        "centro_trabajo": "",
        "email_contrato": "",
        "cobra_sociedad": "",
        "honorarios": 0.0,
        "tiempo_preparacion": 0,
        "tiempo_reunion": 0,
    }
    st.session_state["participants"].append(new_participant)

def remove_last_participant():
    # Eliminar el último participante
    if st.session_state["participants"]:
        st.session_state["participants"].pop()


if "form_data" not in st.session_state:
    st.session_state["form_data"] = {}
if "participants" not in st.session_state:
    st.session_state["participants"] = []
if "participant_index" not in st.session_state:
    st.session_state["participant_index"] = 0
    add_participant()

st.header("Documentos a adjuntar")
st.file_uploader("Programa del evento (Obligatorio)", type=["pdf"], key="doc1", on_change=lambda: save_to_session_state("doc1", st.session_state["doc1"]))

st.header("Declaración de necesidades")
col1, col2 = st.columns(2)
with col1:
    st.text_input("Nombre (Advisory Board Participation [nombre del evento])", max_chars=255, key="nombre", on_change=lambda: save_to_session_state("nombre", st.session_state["nombre"]))
    st.date_input("Fecha de inicio", key="fecha_inicio", on_change=lambda: save_to_session_state("fecha_inicio", st.session_state["fecha_inicio"]))
    st.text_input("Producto asociado", max_chars=255, key="producto_asociado", on_change=lambda: save_to_session_state("producto_asociado", st.session_state["producto_asociado"]))
    st.text_area("Necesidad de la reunión y resultados esperados", max_chars=4000, key="necesidad_reunion", on_change=lambda: save_to_session_state("necesidad_reunion", st.session_state["necesidad_reunion"]))
with col2:
    st.date_input("Fecha de fin", key="fecha_fin", on_change=lambda: save_to_session_state("fecha_fin", st.session_state["fecha_fin"]))
    st.selectbox("Estado de la aprobación", ["", "Aprobado", "No Aprobado"], key="estado_aprobacion", on_change=lambda: save_to_session_state("estado_aprobacion", st.session_state["estado_aprobacion"]))
    st.text_area("Descripción del servicio (Advisory Board Participation [nombre del evento])", max_chars=4000, key="descripcion_servicio", on_change=lambda: save_to_session_state("descripcion_servicio", st.session_state["descripcion_servicio"]))
    st.selectbox("Otra actividad en el departamento en últimos 12 meses?", ["", "Sí", "No"], key="otra_actividad_departamento", on_change=lambda: save_to_session_state("otra_actividad_departamento", st.session_state["otra_actividad_departamento"]))

st.header("Logística de la actividad")
col1, col2 = st.columns(2)
with col1:
    st.selectbox("Desplazamiento de participantes?", ["", "Sí", "No"], key="desplazamiento", on_change=lambda: save_to_session_state("desplazamiento", st.session_state["desplazamiento"]))
    if st.session_state.get("alojamiento") == "Sí":
        st.number_input("Nº de noches", min_value=0, step=1, key="num_noches", on_change=lambda: save_to_session_state("num_noches", st.session_state["num_noches"]))

with col2:
    st.selectbox("Alojamiento de participantes?", ["", "Sí", "No"], key="alojamiento", on_change=lambda: save_to_session_state("alojamiento", st.session_state["alojamiento"]))
    if st.session_state.get("alojamiento") == "Sí":
        st.text_input("Hotel", max_chars=255, key="hotel", on_change=lambda: save_to_session_state("hotel", st.session_state["hotel"]))

st.header("Información del evento")
st.text_area("Descripción y objetivo", max_chars=4000, key="descripcion_objetivo", on_change=lambda: save_to_session_state("descripcion_objetivo", st.session_state["descripcion_objetivo"]))
col1, col2 = st.columns(2)
with col1:
    st.selectbox("Tipo de evento", ["", "virtual", "en persona", "híbrido"], key="tipo_evento", on_change=lambda: save_to_session_state("tipo_evento", st.session_state["tipo_evento"]))
    st.number_input("Número de participantes totales", min_value=0, step=1, key="num_participantes_totales", on_change=lambda: save_to_session_state("num_participantes_totales", st.session_state["num_participantes_totales"]))
with col2:
    if st.session_state.get("tipo_evento") in ["en persona", "híbrido"]:
        st.text_input("Sede", max_chars=255, key="sede", on_change=lambda: save_to_session_state("sede", st.session_state["sede"]))
        st.text_input("Ciudad", max_chars=255, key="ciudad", on_change=lambda: save_to_session_state("ciudad", st.session_state["ciudad"]))

st.header("Criterios del destinatario (consultores)")
col1, col2 = st.columns(2)
with col1:
    st.number_input("Nº de participantes", min_value=0, step=1, key="num_participantes", on_change=lambda: save_to_session_state("num_participantes", st.session_state["num_participantes"]))
with col2:
    st.multiselect(
        "Criterios de selección",
        [
            "Tier 1", "Tier 2", "Tier 3", "Experiencia como ponente", "Experiencia como Participante de Advisory",
            "Experiencia como profesor", "Experiencia clínica en tema a tratar", "Especialista en tema a tratar",
            "Criterios adicionales: campo abierto"
        ],
        key="criterios_seleccion",
        on_change=lambda: save_to_session_state("criterios_seleccion", st.session_state["criterios_seleccion"])
    )
st.text_area("Justificación de número de participantes", max_chars=4000, key="justificacion_participantes", on_change=lambda: save_to_session_state("justificacion_participantes", st.session_state["justificacion_participantes"]))

#@st.fragment
def participants_section():
    st.header("Participantes")

    # Botones para añadir y quitar participantes
    col_add_participant, col_remove_participant = st.columns(2)
    with col_add_participant:
        if st.button("Agregar participante", use_container_width=True, icon="➕", key="add_participant_button"):
            add_participant()
    with col_remove_participant:
        if st.button("Quitar último participante", use_container_width=True, icon="➖", key="remove_participant_button"):
            remove_last_participant()

    # Inicializar almacenamiento en `form_data` si no existe
    if "participantes" not in st.session_state["form_data"]:
        st.session_state["form_data"]["participantes"] = {}

    # Renderizar los participantes
    for index, participant in enumerate(st.session_state["participants"]):
        participant_key = f"Participante {index + 1}"

        # Inicializar el participante en `form_data` si no existe
        if participant_key not in st.session_state["form_data"]["participantes"]:
            st.session_state["form_data"]["participantes"][participant_key] = {}

        with st.expander(f"{participant_key}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                participant["nombre"] = st.text_input(
                    f"Nombre del {participant_key}", 
                    value=participant["nombre"], 
                    key=f"nombre_{index}",
                    on_change=lambda: save_to_session_state(
                        f"participantes", 
                        st.session_state[f"nombre_{index}"],
                        participant_key,
                        f'nombre'
                    )
                )
                participant["dni"] = st.text_input(
                    f"DNI del {participant_key}", 
                    value=participant["dni"], 
                    key=f"dni_{index}",
                    on_change=lambda: save_to_session_state(
                        f"participantes", 
                        st.session_state[f"dni_{index}"],
                        participant_key,
                        f'dni'
                    )
                )
                participant["tier"] = st.selectbox(
                    f"Tier del {participant_key}", 
                    ["", "1", "2", "3"], 
                    index=["", "1", "2", "3"].index(participant["tier"]), 
                    key=f"tier_{index}",
                    on_change=lambda: save_to_session_state(
                        f"participantes", 
                        st.session_state[f"tier_{index}"],
                        participant_key,
                        f'tier'
                    )
                )
                participant["centro_trabajo"] = st.text_input(
                    f"Centro de trabajo del {participant_key}", 
                    value=participant["centro_trabajo"], 
                    key=f"centro_trabajo_{index}",
                    on_change=lambda: save_to_session_state(
                        f"participantes", 
                        st.session_state[f"centro_trabajo_{index}"],
                        participant_key,
                        f'centro_trabajo'
                    )
                )
                participant["cobra_sociedad"] = st.selectbox(
                    f"Cobra a través de sociedad?", 
                    ["", "Sí", "No"], 
                    index=["", "Sí", "No"].index(participant["cobra_sociedad"]), 
                    key=f"cobra_sociedad_{index}",
                    on_change=lambda: save_to_session_state(
                        f"participantes", 
                        st.session_state[f"cobra_sociedad_{index}"],
                        participant_key,
                        f'cobra_sociedad'
                    )
                )

            with col2:
                participant["apellidos"] = st.text_input(
                    f"Apellidos del {participant_key}", 
                    value=participant["apellidos"], 
                    key=f"apellidos_{index}",
                    on_change=lambda: save_to_session_state(
                        f"participantes", 
                        st.session_state[f"apellidos_{index}"],
                        participant_key,
                        f'apellidos'
                    )
                )
                participant["email_contrato"] = st.text_input(
                    f"Email del {participant_key}", 
                    value=participant["email_contrato"], 
                    key=f"email_{index}",
                    on_change=lambda: save_to_session_state(
                        f"participantes", 
                        st.session_state[f"email_{index}"],
                        participant_key,
                        f'email_contrato'
                    )
                )
                participant["honorarios"] = st.number_input(
                    f"Honorarios del {participant_key}", 
                    value=participant["honorarios"], 
                    min_value=0.0, 
                    step=0.01, 
                    key=f"honorarios_{index}",
                    on_change=lambda: save_to_session_state(
                        f"participantes", 
                        st.session_state[f"honorarios_{index}"],
                        participant_key,
                        f'honorarios'
                    )
                )
                participant["tiempo_preparacion"] = st.number_input(
                    f"Tiempo de preparación (min: 0, 15, 30, 45)", 
                    value=participant["tiempo_preparacion"], 
                    min_value=0, 
                    step=15, 
                    key=f"preparacion_{index}",
                    on_change=lambda: save_to_session_state(
                        f"participantes", 
                        st.session_state[f"preparacion_{index}"],
                        participant_key,
                        f'tiempo_preparacion'
                    )
                )
                participant["tiempo_reunion"] = st.number_input(
                    f"Tiempo de reunión (min: 0, 15, 30, 45)", 
                    value=participant["tiempo_reunion"], 
                    min_value=0, 
                    step=15, 
                    key=f"reunion_{index}",
                    on_change=lambda: save_to_session_state(
                        f"participantes", 
                        st.session_state[f"reunion_{index}"],
                        participant_key,
                        f'tiempo_reunion'
                    )
                )

participants_section()


st.header("Datos guardados")
st.write(st.session_state["form_data"])
