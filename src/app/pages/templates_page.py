import streamlit as st
import os
import json
from pathlib import Path
from datetime import date

def deserialize_dates(obj):
    """Convierte strings ISO de fecha a objetos date para compatibilidad con formularios"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                try:
                    obj[k] = date.fromisoformat(v)
                except ValueError:
                    pass
            elif isinstance(v, (dict, list)):
                obj[k] = deserialize_dates(v)
    elif isinstance(obj, list):
        obj = [deserialize_dates(i) for i in obj]
    return obj

def extraer_informacion_template(contenido, tipo_form):
    """Extrae información relevante del template para mostrar en la interfaz"""
    if tipo_form == "event":
        return {
            "nombre": contenido.get("event_name", "Sin nombre"),
            "fecha_inicio": contenido.get("start_date", ""),
            "fecha_fin": contenido.get("end_date", ""),
            "lugar": contenido.get("venue", ""),
            "ciudad": contenido.get("city", "")
        }
    elif tipo_form == "advisory_board":
        return {
            "nombre": contenido.get("nombre_evento_ab", "Sin nombre"),
            "fecha_inicio": contenido.get("start_date_ab", ""),
            "fecha_fin": contenido.get("end_date_ab", ""),
            "lugar": contenido.get("venue_ab", ""),
            "ciudad": contenido.get("city_ab", "")
        }
    elif tipo_form == "consulting_services":
        return {
            "nombre": contenido.get("nombre_necesidades_cs", "Sin nombre"),
            "fecha_inicio": contenido.get("start_date_cs", ""),
            "fecha_fin": contenido.get("end_date_cs", ""),
            "lugar": "Servicio de consultoría",
            "ciudad": ""
        }
    elif tipo_form == "speaking_services":
        return {
            "nombre": contenido.get("nombre_evento_ss", "Sin nombre"),
            "fecha_inicio": contenido.get("start_date_ss", ""),
            "fecha_fin": contenido.get("end_date_ss", ""),
            "lugar": contenido.get("venue_ss", ""),
            "ciudad": contenido.get("city_ss", "")
        }
    else:
        return {
            "nombre": "Template sin nombre",
            "fecha_inicio": "",
            "fecha_fin": "",
            "lugar": "",
            "ciudad": ""
        }

def cargar_template(template_path, tipo_formulario):
    """Carga un template y lo coloca en el session_state para su uso en el formulario correspondiente"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            form_data = json.load(f)
        
        # Deserializar fechas si es necesario
        form_data = deserialize_dates(form_data)
        
        # Mapear el nombre del template al nombre del formulario
        tipo_mapping = {
            "advisory_board_ejemplo": "advisory_board",
            "consulting_services_ejemplo": "consulting_services", 
            "speaking_services_ejemplo": "speaking_services",
            "sponsorship_event_ejemplo": "event"
        }
        
        tipo_form_real = tipo_mapping.get(tipo_formulario, tipo_formulario)
        clave = f"form_data_{tipo_form_real}"
        
        # Configurar session state según el tipo de formulario
        if "speaking_services" in tipo_formulario:
            st.session_state[clave] = form_data
            # Inicializar participantes si existen
            if 'participantes_ss' in form_data:
                st.session_state['participantes_ss'] = list(form_data.get('participantes_ss', {}).values())
                
        elif "advisory_board" in tipo_formulario:
            st.session_state[clave] = form_data
            # Inicializar participantes si existen
            if 'participantes_ab' in form_data:
                st.session_state['participantes_ab'] = list(form_data.get('participantes_ab', {}).values())
                
        elif "consulting_services" in tipo_formulario:
            st.session_state[clave] = form_data
            # Inicializar participantes si existen
            if 'participantes_cs' in form_data:
                st.session_state['participantes_cs'] = list(form_data.get('participantes_cs', {}).values())
                
        elif "sponsorship_event" in tipo_formulario or tipo_formulario == "event":
            st.session_state[clave] = form_data
            st.session_state['email_correcto'] = True
            
        # Mapeo de páginas para redireccionar
        MAPEO_PAGINAS = {
            "advisory_board": "./pages/advisory_board_page.py",
            "consulting_services": "./pages/consulting_services_page.py",
            "speaking_services": "./pages/speaking_services_page.py",
            "event": "./pages/event_page.py"
        }
        
        # Redireccionar a la página correspondiente
        if tipo_form_real in MAPEO_PAGINAS:
            st.switch_page(MAPEO_PAGINAS[tipo_form_real])
        else:
            st.error(f"No se encontró la página para el tipo de formulario: {tipo_form_real}")
            
    except Exception as e:
        st.error(f"Error al cargar el template: {str(e)}")

def main():
    st.title("📋 Templates de Formularios")
    st.markdown("Selecciona un template para comenzar a completar tu formulario con datos predefinidos.")
    
    # Obtener la ruta de templates
    current_dir = Path(__file__).resolve().parent.parent.parent.parent  # Subir 4 niveles desde pages/
    templates_dir = current_dir / "file_templates"
    
    # Verificar que el directorio existe
    if not templates_dir.exists():
        st.error(f"No se encontró el directorio de templates: {templates_dir}")
        return
    
    # Mapeo de archivos de template
    templates_info = {
        "advisory_board_ejemplo.json": {
            "nombre": "Advisory Board",
            "descripcion": "Template para eventos de Advisory Board con expertos médicos",
            "icono": "👩‍💼"
        },
        "consulting_services_ejemplo.json": {
            "nombre": "Consulting Services", 
            "descripcion": "Template para servicios de consultoría médica",
            "icono": "💡"
        },
        "speaking_services_ejemplo.json": {
            "nombre": "Speaking Services",
            "descripcion": "Template para servicios de ponencias y presentaciones",
            "icono": "🗣️"
        },
        "sponsorship_event_ejemplo.json": {
            "nombre": "Sponsorship of Event",
            "descripcion": "Template para patrocinio de eventos y actividades",
            "icono": "🗓️"
        }
    }
    
    # Crear cards para cada template
    cols = st.columns(2)
    col_index = 0
    
    for filename, info in templates_info.items():
        template_path = templates_dir / filename
        
        if not template_path.exists():
            continue
            
        with cols[col_index % 2]:
            with st.container():
                # Card del template
                st.markdown(f"""
                <div style="
                    border: 1px solid #ddd; 
                    border-radius: 10px; 
                    padding: 20px; 
                    margin: 10px 0;
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <h3 style="color: #495057; margin-bottom: 10px;">
                        {info['icono']} {info['nombre']}
                    </h3>
                    <p style="color: #6c757d; margin-bottom: 15px; font-size: 14px;">
                        {info['descripcion']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Leer y mostrar información del template
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                    
                    # Extraer información del template
                    tipo_template = filename.replace("_ejemplo.json", "").replace("sponsorship_", "")
                    info_template = extraer_informacion_template(template_data, tipo_template)
                    
                    # Mostrar información básica del template
                    st.markdown(f"**Nombre del evento:** {info_template['nombre']}")
                    if info_template['fecha_inicio'] and info_template['fecha_fin']:
                        if info_template['fecha_inicio'] == info_template['fecha_fin']:
                            st.markdown(f"**Fecha:** {info_template['fecha_inicio']}")
                        else:
                            st.markdown(f"**Fechas:** {info_template['fecha_inicio']} - {info_template['fecha_fin']}")
                    
                    if info_template['lugar']:
                        ubicacion = info_template['lugar']
                        if info_template['ciudad']:
                            ubicacion += f", {info_template['ciudad']}"
                        st.markdown(f"**Ubicación:** {ubicacion}")
                    
                    # Botón para cargar template
                    tipo_form = filename.replace(".json", "")
                    if st.button(
                        f"🚀 Cargar Template", 
                        key=f"load_{tipo_form}",
                        use_container_width=True,
                        type="primary"
                    ):
                        cargar_template(str(template_path), tipo_form)
                        
                except Exception as e:
                    st.error(f"Error al leer el template {filename}: {str(e)}")
                
                st.markdown("---")
        
        col_index += 1
    
    # Información adicional
    st.markdown("""
    ### ℹ️ Información sobre Templates
    
    Los templates contienen datos de ejemplo que te ayudarán a:
    - **Completar formularios más rápido** con información predefinida
    - **Ver ejemplos** de cómo llenar cada campo
    - **Mantener consistencia** en el formato de datos
    
    Una vez que cargues un template, podrás modificar cualquier campo según tus necesidades específicas.
    """)

if __name__ == '__main__':
    main()
