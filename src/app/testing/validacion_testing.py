import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app.auxiliar import aux_functions as af

import unittest

class TestValidacionCampos(unittest.TestCase):
    def setUp(self):
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
        
        self.obligatorios = [
            "start_date", "end_date", "estado_aprobacion",
            "otra_actividad_departamento", "otra_actividad_otro_departamento",
            "desplazamiento", "alojamiento", "tipo_evento", "participantes",
            "producto_asociado", "descripcion_servicio", "necesidad_reunion",
            "descripcion_objetivo", "num_participantes_totales", "publico_objetivo",
            "num_participantes", "criterios_seleccion", "justificacion_participantes"
        ]
        
        self.dependientes = {
            "alojamiento": {
                "condicion": lambda x: x == "Sí",
                "dependientes": ["num_noches", "hotel"]
            },
            "tipo_evento": {
                "condicion": lambda x: x != "Virtual",
                "dependientes": ["sede", "ciudad"]
            }
        }

    def test_datos_validos_sin_errores(self):
        errores = af.validar_campos(self.datos_validos, self.obligatorios, self.dependientes)
        self.assertEqual(len(errores), 0)

    def test_campos_obligatorios_faltantes(self):
        datos_incompletos = self.datos_validos.copy()
        del datos_incompletos["start_date"]
        errores = af.validar_campos(datos_incompletos, self.obligatorios, self.dependientes)
        self.assertTrue(any("start_date" in error for error in errores))

    def test_campos_dependientes_alojamiento(self):
        datos_alojamiento = self.datos_validos.copy()
        datos_alojamiento["alojamiento"] = "Sí"
        errores = af.validar_campos(datos_alojamiento, self.obligatorios, self.dependientes)
        self.assertTrue(any("num_noches" in error for error in errores))
        self.assertTrue(any("hotel" in error for error in errores))

    def test_campos_dependientes_tipo_evento(self):
        datos_presencial = self.datos_validos.copy()
        datos_presencial["tipo_evento"] = "Presencial"
        errores = af.validar_campos(datos_presencial, self.obligatorios, self.dependientes)
        self.assertTrue(any("sede" in error for error in errores))
        self.assertTrue(any("ciudad" in error for error in errores))

    def test_participantes_invalidos(self):
        datos_participante_invalido = self.datos_validos.copy()
        datos_participante_invalido["participantes"] = {
            "test-id": {
                "nombre": "",
                "apellidos": "Usuario",
                "dni": None
            }
        }
        errores = af.validar_campos(datos_participante_invalido, self.obligatorios, self.dependientes)
        self.assertTrue(any("participante" in error.lower() for error in errores))

    def test_participantes_estructura_invalida(self):
        datos_invalidos = self.datos_validos.copy()
        datos_invalidos["participantes"] = {
            "test-id": "No es un diccionario"
        }
        errores = af.validar_campos(datos_invalidos, self.obligatorios, self.dependientes)
        self.assertTrue(any("estructura válida" in error for error in errores))

    def test_sin_participantes(self):
        datos_sin_participantes = self.datos_validos.copy()
        del datos_sin_participantes["participantes"]
        errores = af.validar_campos(datos_sin_participantes, self.obligatorios, self.dependientes)
        self.assertTrue(any("participantes" in error for error in errores))

if __name__ == '__main__':
    unittest.main()