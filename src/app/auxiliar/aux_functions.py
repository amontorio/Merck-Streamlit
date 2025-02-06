import unicodedata
import pandas as pd

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
}

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
        input_data (dict): Diccionario con los datos a validar.
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
                        errores_general.append(
                            f"El parámetro dependiente '{dep}' es obligatorio cuando '{parametro_principal}' cumple la condición."
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
        errores_general.append("No se encontró la clave 'participantes' en los datos.")

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
                    errores_participantes[id_participante].append(f"El campo 'nombre_sociedad_{id_participante}' del participante con id '{id_participante}' es obligatorio cuando cobra_sociedad_{id_participante} es 'Sí'.\n")
            # Para los demás campos (excepto nombre_sociedad cuando cobra_sociedad no es "Sí"), verificar que no estén vacíos
            elif not campo.startswith("nombre_sociedad_") and (valor is None or (isinstance(valor, str) and valor.strip() == "")):
                print(remove_after_last_underscore(campo))
                errores_participantes[id_participante].append(
                    f"El campo *{FIELD_MAPPINGS.get(remove_after_last_underscore(campo) + '_', campo)}* "
                    f"del participante *{cnt}* está vacío.\n"
                )

        cnt+=1
    return errores_participantes

def normalize_text(text):
    # Convertir a string y minúsculas
    text = str(text).lower()
    # Eliminar tildes y caracteres especiales
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')
    # Eliminar espacios adicionales
    text = text.strip()
    return text

def search_function(search_text):

    df = pd.read_excel(r"C:\Users\AMONTORIOP002\Documents\Merck-Streamlit\src\app\database\Accounts with HCP tiering_ES_2025_01_29.xlsx")
    # Eliminar filas donde 'Nombre de la cuenta' sea NaN
    df = df.dropna(subset=['Nombre de la cuenta'])

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
    if search_text not in lista and len(lista) == 0: lista.append(search_text)  # noqa: E701
    return lista

def handle_tier_from_name(name):

    df = pd.read_excel(r"C:\Users\AMONTORIOP002\Documents\Merck-Streamlit\src\app\database\Accounts with HCP tiering_ES_2025_01_29.xlsx")
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