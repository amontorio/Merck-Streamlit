from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import os

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
    agregar_bullet_point("Tipo de evento", datos.get("event_type", ""))
    agregar_bullet_point("Fecha de inicio", datos.get("start_date", "").strftime("%d/%m/%Y"))
    agregar_bullet_point("Fecha de fin", datos.get("end_date", "").strftime("%d/%m/%Y"))
    agregar_bullet_point("Sede", datos.get("venue", "N/A"))
    agregar_bullet_point("Ciudad", datos.get("city", "N/A"))
    agregar_bullet_point("Número de asistentes", datos.get("num_attendees", 0))
    agregar_bullet_point("Perfil de asistentes", datos.get("attendee_profile", ""))

    # Objetivo del evento
    agregar_encabezado("Objetivo del Evento:")
    agregar_bullet_point("Objetivo", datos.get("event_objective", ""))

    # Detalles del patrocinio
    agregar_encabezado("Detalles del Patrocinio:")
    agregar_bullet_point("Importe (en euros)", datos.get("amount", 0.0))
    agregar_bullet_point("Tipo de pago", datos.get("payment_type", ""))
    if datos.get("payment_type") == "Pago a través de la secretaría técnica (ST)":
        agregar_bullet_point("Nombre ST", datos.get("name_st", ""))
        agregar_bullet_point("Email ST", datos.get("email_st", ""))
    agregar_bullet_point("Producto asociado", datos.get("associated_product", ""))
    agregar_bullet_point("Descripción del evento", datos.get("short_description", ""))
    agregar_bullet_point("Beneficios", datos.get("benefits", ""))
    agregar_bullet_point("Patrocinador exclusivo", datos.get("exclusive_sponsorship", "No"))
    if datos.get("recurrent_sponsorship", "No") == "Sí":
        agregar_bullet_point("Detalles del patrocinio recurrente", datos.get("recurrent_text", ""))

    # Detalles del firmante
    agregar_encabezado("Detalles del Firmante:")
    agregar_bullet_point("Nombre de la organización", datos.get("organization_name", ""))
    agregar_bullet_point("CIF", datos.get("organization_cif", ""))
    agregar_bullet_point("Nombre del firmante", f"{datos.get('signer_first_name', '')} {datos.get('signer_last_name', '')}")
    agregar_bullet_point("Cargo del firmante", datos.get("signer_position", ""))
    agregar_bullet_point("Email del firmante", datos.get("signer_email", ""))

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
