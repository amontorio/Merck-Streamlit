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
    errores = []

    # Validar los parámetros obligatorios
    for param in parametros_obligatorios:
        # Se considera "sin valor" si no está presente, es None o es cadena vacía.
        if param not in input_data or input_data[param] is None or input_data[param] == "":
            errores.append(f"El parámetro '{param}' es obligatorio y no tiene valor.")

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
                        errores.append(
                            f"El parámetro dependiente '{dep}' es obligatorio cuando '{parametro_principal}' cumple la condición."
                        )
        else:
            # Opcional: Se puede reportar si el parámetro principal no está presente.
            errores.append(f"El parámetro principal '{parametro_principal}' no se encontró en los datos.")

    # Validar los participantes de forma modular
    if "participantes" in input_data:
        errores.extend(validar_participantes(input_data["participantes"]))
    else:
        errores.append("No se encontró la clave 'participantes' en los datos.")

    return errores

def validar_participantes(participantes):
    """
    Valida que cada participante tenga todos sus campos rellenados.
    
    Args:
        participantes (dict): Diccionario donde cada clave es un identificador de participante y
                              el valor es otro diccionario con los campos del participante.

    Returns:
        list: Lista de mensajes de error para los participantes que tengan campos sin valor.
    """
    errores = []
    # Iterar sobre cada participante en el diccionario
    for id_participante, datos_participante in participantes.items():
        # Si el participante no es un diccionario, se notifica el error.
        if not isinstance(datos_participante, dict):
            errores.append(f"El participante con id '{id_participante}' no tiene una estructura válida.")
            continue

        # Revisar cada campo del participante
        for campo, valor in datos_participante.items():
            if valor is None or (isinstance(valor, str) and valor.strip() == ""):
                errores.append(f"El campo '{campo}' del participante con id '{id_participante}' está vacío.")
    return errores


import unittest

class TestValidacionCampos(unittest.TestCase):
    def setUp(self):
        # Datos de prueba básicos
        self.datos_validos = {
            "start_date": "2025-02-03",
            "end_date": "2025-02-03",
            "estado_aprobacion": "Aprobado",
            "otra_actividad_departamento": "Sí",
            "otra_actividad_otro_departamento": "Sí", 
            "desplazamiento": "Sí",
            "alojamiento": "No",
            "tipo_evento": "Virtual",
            "participantes": {
                "test-id": {
                    "nombre": "Test",
                    "apellidos": "Usuario",
                    "dni": "12345678A"
                }
            },
            "producto_asociado": "Producto Test",
            "descripcion_servicio": "Descripción",
            "necesidad_reunion": "Necesidad",
            "descripcion_objetivo": "Objetivo",
            "num_participantes_totales": 1,
            "publico_objetivo": "Público",
            "num_participantes": 1,
            "criterios_seleccion": ["Test"],
            "justificacion_participantes": "Justificación"
        }

    def test_campos_obligatorios(self):
        # Test con todos los campos obligatorios
        errores = validar_campos(self.datos_validos, obligatorios, dependientes)
        self.assertEqual(len(errores), 0, "No deberían existir errores con datos válidos")

        # Test con campo obligatorio faltante
        datos_incompletos = self.datos_validos.copy()
        del datos_incompletos["start_date"]
        errores = validar_campos(datos_incompletos, obligatorios, dependientes)
        self.assertTrue(any("start_date" in error for error in errores))

    def test_campos_dependientes(self):
        # Test alojamiento con dependientes
        datos_alojamiento = self.datos_validos.copy()
        datos_alojamiento["alojamiento"] = "Sí"
        errores = validar_campos(datos_alojamiento, obligatorios, dependientes)
        self.assertTrue(any("num_noches" in error for error in errores))
        self.assertTrue(any("hotel" in error for error in errores))

        # Test tipo_evento presencial
        datos_presencial = self.datos_validos.copy()
        datos_presencial["tipo_evento"] = "Presencial"
        errores = validar_campos(datos_presencial, obligatorios, dependientes)
        self.assertTrue(any("sede" in error for error in errores))
        self.assertTrue(any("ciudad" in error for error in errores))

    def test_participantes_validacion(self):
        # Test participante con campos vacíos
        datos_participante_invalido = self.datos_validos.copy()
        datos_participante_invalido["participantes"] = {
            "test-id": {
                "nombre": "",
                "apellidos": "Usuario",
                "dni": None
            }
        }
        errores = validar_campos(datos_participante_invalido, obligatorios, dependientes)
        self.assertTrue(any("participante" in error.lower() for error in errores))

if __name__ == '__main__':
    # Ejemplo de input_data (puede ser el resultado de json.loads(...))
    datos = {
        "start_date": "datetime.date(2025, 2, 3)",
        "end_date": "datetime.date(2025, 2, 3)",
        "estado_aprobacion": "Aprobado",
        "otra_actividad_departamento": "Sí",
        "otra_actividad_otro_departamento": "Sí",
        "desplazamiento": "Sí",
        "alojamiento": "Sí",
        "num_noches": "8",
        "hotel": "dewd2e2q",
        "tipo_evento": "Presencial",
        "participantes": {
            "a2388ebb-7a0e-4879-a07b-c7f53f480e7d": {
                "id": "a2388ebb-7a0e-4879-a07b-c7f53f480e7d",
                "nombre_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": "Juan",
                "apellidos_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": "Moreno",
                "dni_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": "de234df234",
                "tier_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": "0",
                "centro_trabajo_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": "de342fd34",
                "email_contrato_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": "email@gmail.com",
                "cobra_sociedad_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": "Sí",
                "nombre_sociedad_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": "d4e3df34",
                "honorarios_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": 300,
                "preparacion_horas_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": 1,
                "preparacion_minutos_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": 15,
                "ponencia_horas_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": 4,
                "ponencia_minutos_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": 45,
                "email_a2388ebb-7a0e-4879-a07b-c7f53f480e7d": "d342fd34"
            },
        },
        "producto_asociado": "dwed",
        "descripcion_servicio": "dew",
        "necesidad_reunion": "deqw",
        "descripcion_objetivo": "fdwe3fd3w",
        "num_participantes_totales": 2,
        "ciudad": "de2d",
        "sede": "d2e2",
        "publico_objetivo": "d2ed23",
        "num_participantes": 2,
        "criterios_seleccion": [
            "Tier 3"
        ],
        "justificacion_participantes": "d2e3d"
    }

    # Lista de parámetros obligatorios
    obligatorios = [
    "start_date",
    "end_date",
    "estado_aprobacion",
    "otra_actividad_departamento",
    "otra_actividad_otro_departamento",
    "desplazamiento",
    "alojamiento",
    "tipo_evento",
    "participantes",
    "producto_asociado",
    "descripcion_servicio",
    "necesidad_reunion",
    "descripcion_objetivo",
    "num_participantes_totales",
    "publico_objetivo",
    "num_participantes",
    "criterios_seleccion",
    "justificacion_participantes"
]

    # Parámetros dependientes: por ejemplo, si 'alojamiento' es "Sí", se requiere que 'num_noches' y 'hotel' tengan valor.
    dependientes = {
        "alojamiento": {
            "condicion": lambda x: x == "Sí",
            "dependientes": ["num_noches", "hotel"]
        },
        "tipo_evento": {
            "condicion": lambda x: x != "Virtual",
            "dependientes": ["sede", "ciudad"]
        }
    }

    errores = validar_campos(datos, obligatorios, dependientes)
    if errores:
        print("Se encontraron los siguientes errores de validación:")
        for err in errores:
            print(f"- {err}")
    else:
        print("Todos los parámetros requeridos están presentes y los participantes están completos.")
        
    unittest.main()