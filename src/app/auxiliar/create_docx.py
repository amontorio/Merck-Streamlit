from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import os
from datetime import datetime

def crear_documento_sponsorship_of_event(dataframe):
    # Crear un nuevo documento
    documento = Document()

    # Agregar el título con estilo y color personalizado
    titulo = documento.add_paragraph()
    run_titulo = titulo.add_run('Formulario de Patrocinio de Evento')
    run_titulo.font.size = Pt(16)
    run_titulo.font.bold = True
    run_titulo.font.color.rgb = RGBColor(128, 0, 128)  # Color morado
    titulo.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # Agregar secciones con encabezados estilizados
    def agregar_encabezado(texto):
        parrafo = documento.add_paragraph()
        run = parrafo.add_run(texto)
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 102, 204)  # Color azul
        parrafo.space_after = Pt(6)

    def agregar_bullet_point(campo, valor):
        parrafo = documento.add_paragraph(style='List Bullet')
        run_campo = parrafo.add_run(f"{campo}: ")
        run_campo.font.size = Pt(11)
        run_campo.font.bold = True
        run_valor = parrafo.add_run(f"{valor}")
        run_valor.font.size = Pt(11)

    # Leer los datos del DataFrame
    datos = dataframe.iloc[0].to_dict()

    # Documentos a adjuntar
    agregar_encabezado("Documentos a Adjuntar:")
    agregar_bullet_point("Agenda del evento", "Adjunto")
    agregar_bullet_point("Solicitud de patrocinio", "Adjunto")
    if datos.get("exclusive_sponsorship", "No") == "Sí":
        agregar_bullet_point("Dossier comercial", "Adjunto")

    # Detalles del evento
    agregar_encabezado("Detalles del Evento:")
    agregar_bullet_point("Nombre del evento", datos.get("event_name", ""))
    agregar_bullet_point("Fecha de inicio", datos.get("start_date", "").strftime("%d/%m/%Y"))
    agregar_bullet_point("Fecha de fin", datos.get("end_date", "").strftime("%d/%m/%Y"))
    agregar_bullet_point("Tipo de evento", datos.get("event_type", ""))
    agregar_bullet_point("Sede", datos.get("venue", "N/A"))
    agregar_bullet_point("Ciudad", datos.get("city", "N/A"))
    agregar_bullet_point("Número de asistentes", datos.get("num_attendees", 0))
    agregar_bullet_point("Perfil de asistentes", datos.get("attendee_profile", ""))
    agregar_bullet_point("Descripción y objetivo del evento", datos.get("event_objetive", ""))

    # Detalles del patrocinio
    agregar_encabezado("Detalles del Patrocinio:")
    agregar_bullet_point("Nombre del evento", datos.get("event_name", ""))
    agregar_bullet_point("Importe (€)", datos.get("amount", 0.0))
    agregar_bullet_point("Tipo de pago", datos.get("payment_type", ""))
    if datos.get("payment_type") == "Pago a través de la secretaría técnica (ST)":
        agregar_bullet_point("Nombre ST", datos.get("name_st", ""))
    agregar_bullet_point("Producto asociado", datos.get("associated_product", ""))
    agregar_bullet_point("Descripción del evento", datos.get("short_description", ""))
    agregar_bullet_point("Contraprestaciones", datos.get("benefits", ""))
    agregar_bullet_point("Patrocinador único o mayoritario", datos.get("exclusive_sponsorship", "No"))
    agregar_bullet_point("Patrocinio recurrente", datos.get("recurrent_sponsorship", ""))
    if datos.get("recurrent_sponsorship", "No") == "Sí":
        agregar_bullet_point("Detalles del patrocinio recurrente", datos.get("recurrent_text", ""))

    # Detalles del firmante
    agregar_encabezado("Detalles del Organizador:")
    agregar_bullet_point("Nombre de la organización", datos.get("organization_name", ""))
    agregar_bullet_point("CIF", datos.get("organization_cif", ""))
    agregar_bullet_point("Nombre", f"{datos.get('signer_first_name', '')} {datos.get('signer_last_name', '')}")
    agregar_bullet_point("Cargo", datos.get("signer_position", ""))
    agregar_bullet_point("Email", datos.get("signer_email", ""))

    # Guardar el documento
    nombre_archivo = 'Formulario_Sponsorship_of_event.docx'
    # Establecer la ruta a la carpeta 'app/docs'
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    output_dir = os.path.abspath(output_dir)  # Convertir en una ruta absoluta
    os.makedirs(output_dir, exist_ok=True)  # Crear la carpeta si no existe

    # Guardar el archivo en la carpeta 'app/docs'
    documento.save(os.path.join(output_dir, nombre_archivo))
    print(f'Documento guardado como {nombre_archivo}')
    
    return documento, os.path.join(output_dir, nombre_archivo)

def crear_documento_advisory(data):
    documento = Document()

    # Agregar el título
    titulo = documento.add_paragraph()
    run_titulo = titulo.add_run('Advisory Board Participation')
    run_titulo.font.size = Pt(16)
    run_titulo.font.bold = True
    run_titulo.font.color.rgb = RGBColor(0, 0, 128)  # Azul oscuro
    titulo.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    def agregar_encabezado(texto):
        parrafo = documento.add_paragraph()
        run = parrafo.add_run(texto)
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 102, 204)  # Azul
        parrafo.space_after = Pt(6)

    def agregar_bullet_point(campo, valor):
        parrafo = documento.add_paragraph(style='List Bullet')
        run_campo = parrafo.add_run(f"{campo}: ")
        run_campo.font.size = Pt(11)
        run_campo.font.bold = True
        run_valor = parrafo.add_run(f"{valor}")
        run_valor.font.size = Pt(11)

    # Agregar secciones
    agregar_encabezado("Detalles de la Actividad")
    agregar_bullet_point("Nombre", f"Advisory Board Participation {data.get('nombre', '')}")
    agregar_bullet_point("Fecha de inicio", data.get("start_date", "").strftime("%d/%m/%Y"))
    agregar_bullet_point("Fecha de fin", data.get("end_date", "").strftime("%d/%m/%Y"))
    agregar_bullet_point("Producto asociado", data.get("producto_asociado", ""))
    agregar_bullet_point("Estado de la aprobación", data.get("estado_aprobacion", ""))
    agregar_bullet_point("Necesidad de la reunión y resultados esperados", data.get("necesidad_reunion", ""))
    agregar_bullet_point("Descripción del servicio", data.get("descripcion_servicio", ""))

    agregar_encabezado("Logística de la Actividad")
    agregar_bullet_point("Desplazamiento de participantes", data.get("desplazamiento", ""))
    agregar_bullet_point("Alojamiento de participantes", data.get("alojamiento", ""))
    if data.get("alojamiento") == "Sí":
        agregar_bullet_point("Nº de noches", data.get("num_noches", ""))
        agregar_bullet_point("Hotel", data.get("hotel", ""))

    agregar_encabezado("Información del Evento")
    agregar_bullet_point("Tipo de evento", data.get("tipo_evento", ""))
    agregar_bullet_point("Sede", data.get("sede", ""))
    agregar_bullet_point("Ciudad", data.get("ciudad", ""))
    agregar_bullet_point("Número de participantes totales", data.get("num_participantes_totales", ""))
    
    agregar_encabezado("Criterios de Selección")
    agregar_bullet_point("Nº de participantes", data.get("num_participantes", ""))
    agregar_bullet_point("Justificación de número de participantes", data.get("justificacion_participantes", ""))
    criterios = ", ".join(data.get("criterios_seleccion", []))
    agregar_bullet_point("Criterios de selección", criterios)
    
    agregar_encabezado("Detalles de los Participantes del Advisory")
    def agregar_tabla_participantes(participantes):
        tabla = documento.add_table(rows=1, cols=8)
        tabla.style = 'Table Grid'  # Aplicar bordes a la tabla
        encabezados = ["Nombre", "DNI", "Tier", "Centro de trabajo", "Email", "Cobra a través de sociedad", "Honorarios", "Tiempos"]
        hdr_cells = tabla.rows[0].cells
        for i, encabezado in enumerate(encabezados):
            hdr_cells[i].text = encabezado
            hdr_cells[i].paragraphs[0].runs[0].bold = True
            hdr_cells[i]._element.get_or_add_tcPr().append(parse_xml(r'<w:tcBorders %s><w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tcBorders>' % nsdecls('w')))
        
        for participante in participantes.values():
            id_participante = participante["id"]
            row_cells = tabla.add_row().cells
            row_cells[0].text = participante.get(f"nombre_{id_participante}", "")
            row_cells[1].text = participante.get(f"dni_{id_participante}", "")
            row_cells[2].text = participante.get(f"tier_{id_participante}", "")
            row_cells[3].text = participante.get(f"centro_trabajo_{id_participante}", "")
            row_cells[4].text = participante.get(f"email_{id_participante}", "")
            row_cells[5].text = participante.get(f"cobra_sociedad_{id_participante}", "")
            row_cells[6].text = str(participante.get(f"honorarios_{id_participante}", ""))
            row_cells[7].text = f"Preparación: {participante.get(f'tiempo_preparacion_{id_participante}', '')}, Reunión: {participante.get(f'tiempo_reunion_{id_participante}', '')}"
            
            for cell in row_cells:
                cell._element.get_or_add_tcPr().append(parse_xml(r'<w:tcBorders %s><w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/><w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/></w:tcBorders>' % nsdecls('w')))
    
    agregar_tabla_participantes(data.get("participantes", {}))
    # Guardar el documento
    nombre_archivo = 'Advisory_Board_Participation.docx'
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    os.makedirs(output_dir, exist_ok=True)
    documento.save(os.path.join(output_dir, nombre_archivo))
    print(f'Documento guardado como {nombre_archivo}')
    
    return documento, os.path.join(output_dir, nombre_archivo)
