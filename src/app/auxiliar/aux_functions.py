import unicodedata
import pandas as pd
import streamlit as st
import os
import base64
from pathlib import Path
import json 
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from pydantic import BaseModel, Field
import certifi
import traceback


FIELD_MAPPINGS = {
    
    # Consulting Services
    "nombre_necesidades_cs": "Nombre Necesidades",
    "start_date_cs": "Start Date",
    "end_date_cs": "End Date",
    "presupuesto_estimado_cs": "Presupuesto Estimado",
    "producto_asociado_cs": "Producto Asociado",
    "estado_aprobacion_cs": "Estado Aprobación",
    "necesidad_reunion_cs": "Necesidad Reunión",
    "descripcion_servicio_cs": "Descripción Servicio",
    "numero_consultores_cs": "Número Consultores",
    "justificacion_numero_participantes_cs": "Justificación Número Participantes",
    "criterios_seleccion_cs": "Criterios Selección",
    "documentosubido_1_cs": "Agenda/Guión del Evento",
    "documentosubido_2_cs": "Documentación Adicional",


    # Speaking Services
    "documentosubido_1_ss": "Agenda del Evento",
    "documentosubido_2_ss": "Contratos inferiores a 1000€",
    "documentosubido_3_ss": "Documentación Adicional",
    "start_date_ss": "Start Date",
    "end_date_ss": "End Date",
    "presupuesto_estimado_ss": "Presupuesto Estimado",
    "necesidad_reunion_ss": "Necesidad Reunión",
    "descripcion_objetivo_ss": "Descripción y objetivo",
    "desplazamiento_ponentes_ss": "Desplazamiento de los ponentes",
    "alojamiento_ponentes": "Alojamiento de los ponentes",
    "nombre_evento_ss": "Nombre Evento",
    "descripcion_objetivo_ss": "Descripción y objetivo",
    "tipo_evento_ss": "Tipo Evento",
    "num_asistentes_totales_ss": "Número Asistentes Totales",
    "publico_objetivo_ss": "Público Objetivo",
    "num_ponentes_ss": "Número Ponentes",
    "criterios_seleccion_ss": "Criterios Selección",
    "servicio_ss": "Servicio",
    "desplazamiento_ponentes_ss": "Desplazamiento Ponentes",
    "alojamiento_ponentes_ss": "Alojamiento Ponentes",
    "num_noches_ss": "Número Noches",
    "hotel_ss":"Hotel",
    "tipo_evento_ss": "Tipo Evento",
    "sede_ss": "Sede",
    "ciudad_ss": "Ciudad",
    
    # Detalle Consultores
    "nombre_": "Nombre",
    "dni_": "DNI",
    "tier_": "Tier",
    "centro_trabajo_": "Centro de Trabajo",
    "email_": "Email",
    "cobra_sociedad_": "Cobra Sociedad",
    "nombre_sociedad_": "Nombre Sociedad",
    "honorarios_": "Honorarios",
    "preparacion_horas_": "Preparación Horas",
    "preparacion_minutos_": "Preparación Minutos",
    "ponencia_horas_": "Ponencia Horas",
    "ponencia_minutos_": "Ponencia Minutos",
    "name_ponente_ss": "Nombre del Ponente",
    "name_ponente_ab": "Nombre del Participante",
    "name_ponente_cs": "Nombre del Consultor",

    # Advisory Board
    "documentosubido_1": "Programa del Evento",
    "documentosubido_2": "Documentación Adicional",
    "start_date_ab": "Start Date",
    "end_date_ab": "End Date",
    "estado_aprobacion_ab": "Estado Aprobación",
    "otra_actividad_departamento_ab": "Otra Actividad Departamento",
    "otra_actividad_otro_departamento_ab": "Otra Actividad de Otro Departamento",
    "desplazamiento_ab": "Desplazamiento",
    "alojamiento_ab": "Alojamiento",
    "tipo_evento_ab": "Tipo Evento",
    "participantes_ab": "Participantes",
    "producto_asociado_ab": "Producto Asociado",
    "descripcion_servicio_ab": "Descripción Servicio",
    "necesidad_reunion_ab": "Necesidad Reunión",
    "descripcion_objetivo_ab": "Descripción Objetivo",
    "num_participantes_totales_ab": "Número Participantes Totales",
    "publico_objetivo_ab": "Público Objetivo",
    "num_participantes_ab": "Número Participantes",
    "criterios_seleccion_ab": "Criterios Selección",
    "justificacion_participantes_ab": "Justificación Participantes",
    "sede_ab": "Sede",
    "ciudad_ab": "Ciudad",
    "num_noches_ab": "Número Noches",
    "hotel_ab": "Hotel",

    "documentosubido_1_event": "Agenda del Evento",
    "documentosubido_2_event": "Solicitud de Patrocinio",
    "documentosubido_4_event": "Documentación Adicional",
    "documentosubido_3_event": "Presupuesto Desglosado/Dossier Comercial",
    "event_name": "Nombre del Evento",
    "event_type": "Tipo de Evento",
    "start_date": "Fecha de Inicio",
    "end_date": "Fecha de Fin",
    "num_attendees": "Número de Asistentes",
    "attendee_profile": "Perfil de Asistentes",
    "event_objetive": "Objetivo del Evento",
    "amount": "Importe",
    "payment_type": "Tipo de Pago",
    "short_description": "Descripción Corta",
    "benefits": "Beneficios",
    "exclusive_sponsorship": "Patrocinio Exclusivo",
    "recurrent_sponsorship": "Patrocinio Recurrente",
    "organization_name": "Nombre de la Organización",
    "organization_cif": "CIF de la Organización",
    "signer_first_name": "Nombre del Firmante",
    "signer_position": "Cargo del Firmante",
    "signer_email": "Email del Firmante",
    "event_objetive": "Objetivo del Evento",
    "name_st": "Nombre ST",
    "recurrent_text": "Texto Recurrente",
    "city": "Ciudad",
    "venue": "Sede",

    "owner": "Owner",
    "owner_ss": "Owner",
    "owner_cs": "Owner",
    "owner_ab": "Owner",
    "delegate": "Delegate",
    "delegate_ss": "Delegate",
    "delegate_cs": "Delegate",
    "delegate_ab": "Delegate"
}

BASE_DIR = Path(__file__).resolve().parent.parent


@st.cache_data
def load_data():
    path = BASE_DIR / "database" / "Accounts with HCP tiering_ES_2025_01_29.xlsx"
    return pd.read_excel(path)
dataset = load_data()

def show_main_title(title, logo_size):
    if title == "Events Compliance Advisor":
        logo_merck = "MDG_Logo_RGreen_SP.png"
    else:
        logo_merck = "MDG_Logo_RPurple_SP.png"

    logo_path = BASE_DIR / "images" / logo_merck

    # Función para convertir la imagen a base64
    def get_base64_image(image_path):
        with open(image_path, "rb") as img_file:
            data = img_file.read()
        # Codificar a base64 y luego convertir los bytes resultantes a cadena UTF-8
        return base64.b64encode(data).decode("utf-8")

    base64_image = get_base64_image(logo_path)

    # Mostrar el logo centrado con HTML y CSS en Streamlit
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png+xml;base64,{base64_image}" alt="Logo Merck" width="{logo_size}">
            <h1>{title}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
def remove_after_last_underscore(s: str) -> str:
    return "_".join(s.rsplit("_", 1)[:-1]) if "_" in s else s

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)



def validar_campos(input_data, parametros_obligatorios, parametros_dependientes):
    """
    Valida que los parámetros obligatorios y los parámetros dependientes (según su condición)
    tengan un valor en el input_data. Además, valida que los participantes (si existen) tengan
    todos sus campos rellenos.

    Args:
        input_data (dict): Diccionario con los datos a validar. -> diccionario del formulario
        parametros_obligatorios (list): Lista de nombres de parámetros obligatorios.
        parametros_dependientes (dict): Diccionario con la estructura:
            {
                "parametro_principal": {
                    "condicion": función que recibe el valor del parametro_principal y retorna True/False,
                    "dependientes": [listado de parámetros dependientes]
                },
                ...
            }

    Returns:
        list: Lista de mensajes de error. Si está vacía, no se encontraron errores.
    """
    errores_general = []
    errores_participantes= {}

    # Validar los parámetros obligatorios
    for param in parametros_obligatorios:
        # Se considera "sin valor" si no está presente, es None o es cadena vacía.
        if param not in input_data or input_data[param] is None or input_data[param] == "" or (isinstance(input_data[param], list) and len(input_data[param]) == 0):
            # Get friendly name from MAPPINGS or use original param name if not found
            if param.strip().startswith("documentosubido"):
                errores_general.append(f"El documento *{FIELD_MAPPINGS.get(param, param)}* es obligatorio y no tiene valor.")
            else:
                errores_general.append(f"El parámetro *{FIELD_MAPPINGS.get(param, param)}* es obligatorio y no tiene valor.")


    # Validar los parámetros dependientes
    for parametro_principal, reglas in parametros_dependientes.items():
        # Obtener la función de condición y la lista de dependientes.
        condicion = reglas.get("condicion", lambda valor: False)
        dependientes = reglas.get("dependientes", [])

        # Solo se evalúa si el parámetro principal existe en input_data.
        if parametro_principal in input_data:
            valor_principal = input_data[parametro_principal]
            # Si la condición se cumple, se exigen los parámetros dependientes.
            if condicion(valor_principal):
                for dep in dependientes:
                    if dep not in input_data or input_data[dep] is None or input_data[dep] == "":
                        if dep.strip().startswith("documentosubido"):
                            errores_general.append(
                            f"El documento *{FIELD_MAPPINGS.get(dep, dep)}* es obligatorio cuando *{FIELD_MAPPINGS.get(parametro_principal, parametro_principal)}* cumple la condición."
                        )
                        else:
                            errores_general.append(
                                f"El parámetro dependiente *{FIELD_MAPPINGS.get(dep, dep)}* es obligatorio cuando *{FIELD_MAPPINGS.get(parametro_principal, parametro_principal)}* cumple la condición."
                            )
        else:
            # Opcional: Se puede reportar si el parámetro principal no está presente.
            errores_general.append(f"El parámetro principal '{parametro_principal}' no se encontró en los datos.")
    

    # Validar los participantes de forma modular
    participanes_name = ""
    if "participantes_ab" in input_data:
        participanes_name = "participantes_ab"
    elif "participantes_cs" in input_data:
        participanes_name = "participantes_cs"
    elif "participantes_ss" in input_data:
        participanes_name = "participantes_ss"

    if participanes_name in input_data:
        errores_participantes = validar_participantes(input_data[participanes_name])
    else:
        #errores_general.append("No se encontró la clave 'participantes' en los datos.")
        errores_participantes = {}
        
    return errores_general, errores_participantes

def validar_participantes(participantes):
    """
    Valida que cada participante tenga todos sus campos rellenados.
    
    Args:
        participantes (dict): Diccionario donde cada clave es un identificador de participante y
                              el valor es otro diccionario con los campos del participante.

    Returns:
        list: Lista de mensajes de error para los participantes que tengan campos sin valor.
    """
    errores_participantes = {}
    cnt = 1
    # Iterar sobre cada participante en el diccionario
    for id_participante, datos_participante in participantes.items():
        # Si el participante no es un diccionario, se notifica el error.
        errores_participantes[id_participante] = []
        if not isinstance(datos_participante, dict):
            errores_participantes[id_participante].append(f"El participante con id '{id_participante}' no tiene una estructura válida.\n")
            continue
        

        # Revisar cada campo del participante
        for campo, valor in datos_participante.items():
            
            # Si el campo es cobra_sociedad_id y es "Sí", verificar campo_nombre_sociedad
            if campo == f"cobra_sociedad_{id_participante}" and valor == "Sí":
                if f"nombre_sociedad_{id_participante}" not in datos_participante or \
                   datos_participante[f"nombre_sociedad_{id_participante}"] is None or \
                   datos_participante[f"nombre_sociedad_{id_participante}"].strip() == "":
                    #errores_participantes[id_participante].append(f"El campo 'nombre_sociedad_{id_participante}' del participante con id '{id_participante}' es obligatorio cuando cobra_sociedad_{id_participante} es 'Sí'.\n")
                    errores_participantes[id_participante].append(f"El campo Nombre de la Sociedad del participante *{cnt}* es obligatorio cuando cobra a través de sociedad.\n")
            # Para los demás campos (excepto nombre_sociedad cuando cobra_sociedad no es "Sí" y dni_), verificar que no estén vacíos
            elif not campo.startswith("nombre_sociedad_") and not campo.startswith("dni_") and (valor is None or (isinstance(valor, str) and valor.strip() == "")) and not campo.startswith("email_copy_"):
                if remove_after_last_underscore(campo).startswith("name_ponente"):
                    errores_participantes[id_participante].append(
                    f"El campo *{FIELD_MAPPINGS.get(campo)}* es obligatorio y no tiene valor.\n"
                )
                else:
                    errores_participantes[id_participante].append(
                        f"El campo *{FIELD_MAPPINGS.get(remove_after_last_underscore(campo) + '_', campo)}* es obligatorio y no tiene valor.\n"
                    )

        cnt+=1
    return errores_participantes


def get_model():
    azure_endpoint = "https://merck-test.openai.azure.com/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-08-01-preview"
    api_key = ""

    llm = AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        azure_deployment="gpt-4o-mini", 
        api_version="2024-10-01-preview",
        temperature=0
    )

    return llm


class BooleanValueDescription(BaseModel):
    valor: bool = Field(description="Un valor booleano (true o false)")
    descripcion: str = Field(description="Una descripción detallada explicando el valor booleano")


def validar_hotel(llm, fecha_inicio, fecha_fin, hotel):
    prompt = ChatPromptTemplate([
        ("system",  '''
            Tu tarea es indicar si el campo 'hotel' cumple con la normativa que te voy a definir. Vas a recibir una serie de campos necesarios para evaluar el cumplimiento de la normativa.
            #campos#
            fecha inicio: {fecha_inicio}
            fecha fin: {fecha_fin}
            hotel: {hotel}
            #campos#

            #normativa#
            - No se pueden reservar hoteles de gran lujo. Por tanto, todos los hoteles en cuya semántica aparezca 'Gran lujo', 'Luxury' o términos del estilo.
            - El nombre del hotel **no puede incluir** palabras (o derivados de la familia de palabras) relacionadas con los siguentes alojamientos prohibidos: 
                1. Complejos deportivos: golf, etc.
                2. Parques temáticos (y nombres propios de parques temáticos)
                3. Bodegas
                4. Hoteles de Gran Lujo: gran lujo, luxury, spa, resort...
            #normativa#
         
            #importante#
            No debes ser excesivamente riguroso con la aplicación de la normativa. **Solo debes poner False (no cumplimiento), en caso de que claramente no se cumpla con la norma**. 
            Sin embargo, si no es tan evidente, la normativa SÍ se cumple. No debes ser muy restrictivo, **solo se tienen que descartar casos muy concretos que claramente no cumplan la normativa**.
            Si no se tiene información suficiente para aplicar la normativa (algún input está en blanco), debes asumir que SÍ se aplica bien (True). No hay que ser excesivamente restrictivo.
            #importante#

            Debes responder con un json que siga el siguiente los siguientes valores:
            'valor': es un booleano que debe ser True en caso de que se cumpla la normativa, y False en caso contrario
            'descripcion': explicación breve de las razones por las que no se cumple la normativa. Quiero que la explicación sea breve y concisa, directamente relacionada con los inputs que recibes. 
            Debes responder con unica y exclusivamente un json con estos campos. No incluyas informacion adicional.
         '''
        ),
        ("user", "{input}")
    ])

    parser = JsonOutputParser(pydantic_object=BooleanValueDescription)

    chain = prompt | llm | json_correccion | parser 

    result = chain.invoke({
        "input": "Realiza tu tarea de forma precisa.",
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "hotel": hotel    
    })

    return result

def validar_sede_location(llm, fecha_inicio, fecha_fin, sede):
    prompt = ChatPromptTemplate([
    ("system", '''
        Tu tarea es indicar si el campo 'sede' cumple con la normativa que te voy a definir. La sede suelen ser hoteles, recintos, restaurantes... en los que tienen lugar los eventos.
        Vas a recibir una serie de campos necesarios para evaluar el cumplimiento de la normativa.
            #campos#
            fecha inicio: {fecha_inicio}
            fecha fin: {fecha_fin}
            sede: {sede}
            #campos#

            #normativa#
            Fecha inicio y fecha fin se van a utilizar para detectar el periodo / estación en la que se realiza la reserva. Acorde a estos valores, 
            - Entre diciembre y marzo no es posible seleccionar una sede en cuya semántica aparezca 'Esquí', 'Snow' o deportes de invierno. Tiene que aparecer en el nombre de la sede claramente algo relacionado con esto.
            - Desde el 15 de junio al 15 de septiembre no es posible seleccionar una sede cuyo nombre incluya los términos 'Playa', 'Mar' (o derivadas, de la misma familia de palabras). **Los términos de 'Spa' o 'Resort' no indican incumplimiento de la normativa.**
            #normativa#
     
            #IMPORTANTE#
            No debes ser excesivamente riguroso con la aplicación de la normativa. **Solo debes poner False (no cumplimiento), en caso de que claramente no se cumpla con la norma**. 
            Sin embargo, si no es tan evidente, la normativa SÍ se cumple. No debes ser muy restrictivo, **solo se tienen que descartar casos muy concretos que claramente no cumplan la normativa**.
            Ten claro el status final de si la normativa se cumple o no se cumple.
            #IMPORTANTE#
     
            #instrucciones#
            Debes responder con un json que siga el siguiente los siguientes valores:
            'valor': es un booleano que debe ser True en caso de que se SÍ cumpla la normativa, y False en caso de que NO se cumpla. 
            'descripcion': explicación breve de las razones por las que NO se cumple la normativa. No mencionar concretamente la palabra que no cumple la normativa, sino el contexto de por qué relacionandolo con la época (verano o invierno).
            Debes responder con unica y exclusivamente un json con estos campos. No incluyas informacion adicional.
            #instrucciones#
    '''
    ),
    ("user", "{input}")
    ])

    parser = JsonOutputParser(pydantic_object=BooleanValueDescription)

    chain = prompt | llm |json_correccion | parser 

    result = chain.invoke({
        "input": "Realiza tu tarea de forma precisa.",
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "sede": sede
    })

    return result

def validar_sede_venue(llm, sede):
    prompt = ChatPromptTemplate([
    ("system", '''
        Tu tarea es indicar si el campo 'sede' cumple con la normativa que te voy a definir. La sede suelen ser hoteles, recintos, restaurantes... en los que tienen lugar los eventos.
        Vas a recibir una serie de campos necesarios para evaluar el cumplimiento de la normativa.            
            #campos#
            sede: {sede}
            #campos#

            #normativa#
            - El nombre de la sede **no puede incluir** palabras (o derivados de la familia de palabras) relacionadas con los siguentes sedes prohibidas: 
                1. Complejos deportivos: golf, etc.
                2. Parques temáticos (y nombres propios de parques temáticos)
                3. Bodegas
                4. Lugares de Gran Lujo: gran lujo, luxury, spa, resort... 
            #normativa#
     
            #IMPORTANTE#
            No debes ser excesivamente riguroso con la aplicación de la normativa. **Solo debes poner False (no cumplimiento), en caso de que claramente no se cumpla con la norma**. 
            Sin embargo, si no es tan evidente, la normativa SÍ se cumple. No debes ser muy restrictivo, **solo se tienen que descartar casos muy concretos que claramente no cumplan la normativa**.
            Ten claro el status final de si la normativa se cumple o no se cumple.
            #IMPORTANTE#
     
            #instrucciones#
            Debes responder con un json que siga el siguiente los siguientes valores:
            'valor': es un booleano que debe ser True en caso de que se SÍ cumpla la normativa, y False en caso de que NO se cumpla. 
            'descripcion': explicación breve de las razones por las que NO se cumple la normativa. 
            Debes responder con unica y exclusivamente un json con estos campos. No incluyas informacion adicional.
            #instrucciones#
        '''
        ),
            ("user", "{input}")
        ])

    parser = JsonOutputParser(pydantic_object=BooleanValueDescription)

    chain = prompt | llm | json_correccion | parser 

    result = chain.invoke({
        "input": "Realiza tu tarea de forma precisa.",
        "sede": sede
    })

    return result



def validar_campos_ia(input_data, campos_ia):
    errores_ia = []
    result = {}

    llm = get_model()

    # Validación de hoteles
    campos_ia_hoteles = campos_ia.get("validar_hotel", {})
    if campos_ia_hoteles:
        fecha_inicio = input_data.get(campos_ia_hoteles.get("start_date"))
        fecha_fin = input_data.get(campos_ia_hoteles.get("end_date"))
        hotel = input_data.get(campos_ia_hoteles.get("hotel"))
        if hotel != "":
            try:
                result_hoteles = validar_hotel(llm, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, hotel=hotel) 
                if result_hoteles:  
                    result['hoteles'] = result_hoteles
            except:
                print("")

    # Validación de sede y ubicación
    campos_ia_sede_location = campos_ia.get("validar_sede_location", {})
    if campos_ia_sede_location:
        fecha_inicio = input_data.get(campos_ia_sede_location.get("start_date"))
        fecha_fin = input_data.get(campos_ia_sede_location.get("end_date"))
        sede = input_data.get(campos_ia_sede_location.get("sede"))

        if sede != "":
            try:
                result_location = validar_sede_location(llm, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, sede=sede) 
                if result_location:
                    result['location'] = result_location
            except:
                print("")

    # Validación de sede y venue
    campos_ia_sede_venue = campos_ia.get("validar_sede_venue", {})
    if campos_ia_sede_venue:
        sede = input_data.get(campos_ia_sede_venue.get("sede"))
        if sede != "":
            try:
                result_venue = validar_sede_venue(llm, sede=sede) 
                if result_venue:
                    result['venue'] = result_venue
            except:
                print("")
    for key, res in result.items():
        if not res["valor"]:
            errores_ia.append(res["descripcion"])

    return errores_ia

def json_correccion(ai_message):
    json_str = ai_message.content.replace("```json", "").replace("```", "")#.replace('"', "'")

    return json_str


def aviso_correspondencias(llm, contraprestaciones):
    prompt = ChatPromptTemplate.from_messages([
        ("system", '''
            Tu tarea es indicar si el campo 'contraprestacion' cumple con la normativa.
            #campos#
            contraprestacion: {contraprestaciones}
            #campos#
            
            #normativa#
            Indica si el campo 'contraprestacion' se trata de una contraprestación válida o no. Una contraprestacion es valida si incluye alguno de la siguiente información o conceptos similares.
            - Inclusión del Logo de Merck: en el programa, presentaciones, sala, web, cartel, pantalla de la sala plenaria, email de agradecimiento, photocall y demás medios de difusión
            - Espacio expositivo, enaras, roll up de Merck
            - Inscripciones para profesionales sanitarios o staff
            - Espacio de tiempo para una ponencia en nombre de Merck.
            - Banner
            - Distribución tarjetones en la cartera de los congresistas
            #normativa#
            
            #IMPORTANTE#
            Tienes que determinar si la contraprestacion indicada es válida o no. 
            Si la contraprestación no es válida, el mensaje de aviso mencionará que el contenido introducido no se parece a las contraprestaciones habituales. 
            #IMPORTANTE#
            
            #instrucciones#
            Devuelve un JSON con los siguientes valores:
            {{
                'valor': True si la contraprestación es valida, False si NO es válida.
                'descripcion': 'Aviso breve de que la contraprestación no se parece al estilo habitual. Y mencionar qué campos se suelen introducir.'
            }}
            No devuelvas nada más que el JSON.
            #instrucciones#
        '''),
        ("user", """
            Realiza tu tarea de forma precisa. A continuación te paso los datos:
            - Contraprestacion: {contraprestaciones}
        """),
    ])


    parser = JsonOutputParser(pydantic_object=BooleanValueDescription)  

    chain = prompt | llm | json_correccion | parser
    result = chain.invoke({"contraprestaciones": contraprestaciones})
    
    return result

def avisos_campos_ia(input_data, campos_avisos_ia):
    avisos = []
    result = {}
    llm = get_model()

    # Contraprestaciones
    avisos_contraprestaciones = campos_avisos_ia.get("validar_contraprestaciones", {})
    if avisos_contraprestaciones:
        contra = input_data.get(avisos_contraprestaciones.get("contraprestaciones"))
        if contra != "":
            try:
                result_correspondencias = aviso_correspondencias(llm, contraprestaciones = contra) 
                if result_correspondencias:
                    result['correspondencias'] = result_correspondencias
            except:
                traceback.print_exc()
                print("")

    for key, res in result.items():
        if not res["valor"]:
            avisos.append(res["descripcion"])

    return avisos

     

def normalize_text(text):
    # Convertir a string y minúsculas
    text = str(text).lower()
    # Eliminar tildes y caracteres especiales
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')
    # Eliminar espacios adicionales
    text = text.strip()
    return text

def search_function(search_text, datos = dataset):
    # Eliminar filas donde 'Nombre de la cuenta' sea NaN
    df = datos.copy()

    df = df.dropna(subset=['Nombre de la cuenta'])
    #print(df.head(5))

    # Reemplazar NaN en 'Especialidad' con 'Ninguna'
    df['Especialidad'] = df['Especialidad'].fillna('Ninguna')

    # Reemplazar NaN en 'Tier' con 0
    df['Tier'] = df['Tier'].fillna(0)

    # Asegurarse de que la columna 'Tier' sea numérica
    df['Tier'] = pd.to_numeric(df['Tier'], errors='coerce').fillna(0)

    # Extraer las columnas necesarias y convertirlas a una lista de tuplas
    lista = list(df[['Nombre de la cuenta', 'Especialidad', 'Tier']].itertuples(index=False, name=None))
    
    # Normalizar el texto de búsqueda
    texto_normalizado = normalize_text(search_text)
    # Buscar coincidencias normalizando los elementos de la lista
    lista = [
        f"{elemento[0]} - {elemento[1]}" for elemento in lista
        if texto_normalizado in normalize_text(elemento[0])
    ]
    if search_text not in lista and len(lista) == 0: lista.append(search_text)
              # noqa: E701
    return lista

def handle_tier_from_name(name, datos = dataset):
    df = datos.copy()
    # Eliminar filas donde 'Nombre de la cuenta' sea NaN
    df = df.dropna(subset=['Nombre de la cuenta'])

    # Reemplazar NaN en 'Especialidad' con 'Ninguna'
    df['Especialidad'] = df['Especialidad'].fillna('Ninguna')

    # Reemplazar NaN en 'Tier' con 0
    df['Tier'] = df['Tier'].fillna(0)

    # Asegurarse de que la columna 'Tier' sea numérica
    df['Tier'] = pd.to_numeric(df['Tier'], errors='coerce').fillna(0)
    
    raw_name = name["result"].split("-")[0].strip()

    tier = df.loc[df["Nombre de la cuenta"] == raw_name, "Tier"]
        
    if not tier.empty:
        return str(int(tier.values[0]))  # Devuelve el Tier encontrado
    return "0"  # Devuelve 0 si el nombre no está en los datos


MERCK_ROOT_CA = """-----BEGIN CERTIFICATE-----
MIIGOzCCBCOgAwIBAgIQHt22MoeoebZLg1n5IiALWTANBgkqhkiG9w0BAQsFADBT
MQswCQYDVQQGEwJERTEUMBIGA1UECgwLTWVyY2sgR3JvdXAxEzARBgNVBAsMCk1l
cmNrIEtHYUExGTAXBgNVBAMMEE1FUkNLIFJPT1QgQ0EgMDEwHhcNMTYxMDI4MDg1
MjU2WhcNMzYxMDI4MDkwMjUyWjBTMQswCQYDVQQGEwJERTEUMBIGA1UECgwLTWVy
Y2sgR3JvdXAxEzARBgNVBAsMCk1lcmNrIEtHYUExGTAXBgNVBAMMEE1FUkNLIFJP
T1QgQ0EgMDEwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQDQGa8XIrc9
Ri5hhJfXHCfzbJY9sueLJXtOuwYdGD/riltHGCOitOxFGCTTwelCDwpvT+9VB0rM
tbtU5pZMNhWhPm+6xVG0pBOsZW65sL+rgh9o4kvSfAmLE7n8qZmek1jfK/i8tRHI
D51YM+1+ObBcrCi5KrqROEpJEvGIQjbaKM6kCuhJGGcxr40gQ1hc4mVysRELOv4y
8YU3bSHiqDpMvwzCD+57xuYSfuZx6YXSfPXM1JU6vjZ1fp3NjbArp9+Ml9b4UC7Q
FInGmwRhEmd1UMdDm2IshhOlQ8Q4NXoOdecrQCkyHKHKpvvolDmnpucdUa8hVrDq
Xk94r/AEbIk87OBjl9r/V2ei7lD45pjanam24Xm5uwJDX2RrL+LxD4tNQTDig/f5
F75hSPHWsFatQrxT2mNtOihfAFWZySTzVTNE+Ez3nei0GZ92QcdX3jn0oTvezGEn
cnSp9mhGnWlXUXQ5GXEIUsF3Krvkw30xSM1tJt7tpnAR8ZIqBFcfhdVuNnhSZvzS
qoxBEEf2N76k28rCq/PuxcAd0EwE5x7eDcD7ZNjLev/wgqthUv+zddkKlfhRWop7
Z7hmvQRYWp9mOqX0t6B6y0/ulAqgn67U7qb/XzpnvVp5Aydv1tQ+qq6Od1JlMScj
nv0F7KSTrnc5K8KPsSFxOkcNkoCMdVgGzQIDAQABo4IBCTCCAQUwDgYDVR0PAQH/
BAQDAgEGMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFNDmVlzqHY/5Kj0GGKWU
kZwA1VUzMIHCBgNVHSAEgbowgbcwgbQGBFUdIAAwgaswgagGCCsGAQUFBwICMIGb
HoGYAEMAZQByAHQAaQBmAGkAYwBhAHQAaQBvAG4AIABQAHIAYQBjAHQAaQBjAGUA
IABTAHQAYQB0AGUAbQBlAG4AdAAgACgAQwBQAFMAKQAgAGEAdgBhAGkAbABhAGIA
bABlACAAbwBuACAAcgBlAHEAdQBlAHMAdAAgAGYAcgBvAG0AIABJAFQAIABTAGUA
YwB1AHIAaQB0AHkwDQYJKoZIhvcNAQELBQADggIBADaPFSRRqFU9Uu8xEgk7rxJt
XHoVnMoDiHhHcTBeG+9U3q1tSA/MohIPZN98isEP6BLlN2tv5xVZRG8VjmIj3bE5
KUcwSNKRPUYZHIelTkXZnyfjnWLG1aFloLmnysZOQcK/ce/uRTIeivGPIneJgifs
NTeYZF7b5WYAGtkTC5t+TFdAxVw4ptmwX1NDgAwclUE72JxtDk8xPxYfy/26vA6+
Rfl3YaRiwB++WxUaG68wYHWV4+uo6enz0NIJwvlg+4sZGCeoQ/zRl1yQM4sBu3DT
uYVoN15MAnrxbXJ81LSrCYJGLNM1pbA75a3UwTercGoCh0gchLuuCWk8vz3TmkU2
xZRGVpqFveoO4Y2Gd08QMJBSRmCaCmaDFUqbqPump/euTbjPICTZ0gEn9SfhAVWK
dotKAz7yqhrjOx08x3fBtbggnLvQrK1NBgsXUz6+c2WcqVh1yR9DCYqLSW656psv
J42zE5cplnkhc+0XS7itIaBwEEHR6XDq006YZpQeYapSAZ5F+Vc782UGQa+4fFg2
0rkON71IUxOG6rsVG85Fnt4xPAIHxJxMT4FKKlN0yFxc4aBn8Mj/GRP9up0caUoF
lmIhWZaOkQFhYXt7TGNzYxf2FUM1OVZetlF8cIX29LoqzSVYIT6kJVoO/+JnKjqv
1U8Ol3yI5k05mg+n+Tac
-----END CERTIFICATE-----
"""

def _create_cacert_bundle_with_merck_additions() -> str:
    """
    Takes certifi's cacert bundle, adds Merck Root CA and Merck ssl decryption
    certificate and returns the path to the combined cacert.pem file.

    Returns: the path to the combined cacert.pem file.
    """
    ca_certs = Path(certifi.where()).read_text(encoding="UTF-8")
    cacert_path = BASE_DIR / "cacert.pem"
    with cacert_path.open("w") as f:
        f.write(ca_certs)
        f.write('\n# Label: "MERCK ROOT CA 01"\n')
        f.write(MERCK_ROOT_CA)
    return str(cacert_path.absolute())


def app_is_running_on_app_service() -> bool:
    return True if "APP_SERVICE_TS" in os.environ else False

def setup_environment() -> None:
    """Sets up the necessary environment variables for the application.

    This function should be called before the application initializes. It configures
     environment variables for running the application.
    For local development it ensures that:
    - The application configuration is loaded from 'config.json'
    - The requests and httpx libraries are configured to use the Merck SSL certificates
    When running in the app service in ensures that:
    - If the user provides a runtime configuration through the app service console, then
      each configured json entry is exposed as environment variables.
    """
    if not app_is_running_on_app_service():
        path_config = BASE_DIR / "config.json"
        try:
            os.environ["APP_SERVICE_CONFIG"] = Path(path_config).read_text()
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "Missing config.json. Please duplicate the config-template.json file and fill with your own credentials."
            ) from e

        # local development requires certificate / ssl setup
        cacert_path = _create_cacert_bundle_with_merck_additions()
        # The httpx library used by openai uses SSL_CERT_FILE environment variable:
        # https://www.python-httpx.org/compatibility/#ssl-configuration
        os.environ["SSL_CERT_FILE"] = cacert_path
        # The requests library uses the REQUESTS_CA_BUNDLE environment variable:
        # https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification
        os.environ["REQUESTS_CA_BUNDLE"] = cacert_path

    # In appservice, APP_SERVICE_CONFIG is present when the user provides a runtime
    # configuration through the app service console
    if "APP_SERVICE_CONFIG" in os.environ:
        config = json.loads(os.environ["APP_SERVICE_CONFIG"])
        os.environ.update(config)
