prompt_hoteles = '''
        Tu tarea es indicar si los siguientes campos cumplen con la normativa que te paso a continuación:
            #campos#
            fecha inicio: {fecha_inicio}
            fecha fin: {fecha_fin}
            hotel: {hotel}
            ciudad: {ciudad}
            #campos#

            #normativa#
            - en invierno no es posible seleccionar un hotel en el que se puedan ahacer deportes de nieve
            - en verano no es posible seleccionar un hotel que haga referencia a sditios vacacionales de playa
            #normativa#

            Debes responder con un json que siga el siguiente los siguientes valores:
            "valor": es un booleano que debe ser True en caso de que se cumpla la normativa, y False en caso contrario
            "descripcion": explicación breve de las razones por las que no se cumple la normativa
     '''

