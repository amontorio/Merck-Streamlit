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
    # CSS personalizado con diseño moderno
    st.markdown("""
    <style>
    .template-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .template-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border-color: #e0e0e0;
    }
    .template-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    .template-header {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
    }
    .template-icon {
        font-size: 28px;
        margin-right: 12px;
        min-width: 40px;
    }
    .template-title {
        font-size: 18px;
        font-weight: 700;
        color: #2d3748;
        margin: 0;
        line-height: 1.2;
    }
    .template-description {
        color: #718096;
        font-size: 13px;
        line-height: 1.4;
        margin: 0;
        flex-grow: 1;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .page-header {
        text-align: center;
        margin-bottom: 40px;
    }
    .page-title {
        font-size: 32px;
        font-weight: 800;
        color: #2d3748;
        margin-bottom: 8px;
    }
    .page-subtitle {
        font-size: 18px;
        color: #718096;
        font-weight: 400;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header de la página
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">📋 Plantillas de Formularios</h1>
        <p class="page-subtitle">Acelera tu trabajo con plantillas prediseñadas</p>
    </div>
    """, unsafe_allow_html=True)
    
    templates_dir = Path(__file__).resolve().parent.parent / "file_templates"

    if not templates_dir.exists():
        st.error(f"No se encontró el directorio de templates: {templates_dir}")
        return
    
    # Información de templates con colores
    templates_info = {
        "advisory_board_ejemplo.json": {
            "nombre": "Advisory Board",
            "descripcion": "Organiza reuniones con expertos médicos para obtener asesoramiento estratégico",
            "icono": "👥",
            "color": "#667eea"
        },
        "consulting_services_ejemplo.json": {
            "nombre": "Consulting Services", 
            "descripcion": "Servicios de consultoría especializada para proyectos médicos",
            "icono": "💡",
            "color": "#f093fb"
        },
        "speaking_services_ejemplo.json": {
            "nombre": "Speaking Services",
            "descripcion": "Gestiona ponencias y presentaciones de expertos médicos",
            "icono": "🎤",
            "color": "#4facfe"
        },
        "sponsorship_event_ejemplo.json": {
            "nombre": "Sponsorship of Event",
            "descripcion": "Patrocinio de eventos médicos y actividades educativas",
            "icono": "🎯",
            "color": "#43e97b"
        }
    }
    
    # Crear las tarjetas
    cols = st.columns(2, gap="large")
    
    for i, (filename, info) in enumerate(templates_info.items()):
        template_path = templates_dir / filename
        
        if not template_path.exists():
            continue
            
        with cols[i % 2]:
            # Card moderna
            st.markdown(f"""
            <div class="template-card">
                <div class="template-header">
                    <div class="template-icon">{info['icono']}</div>
                    <h3 class="template-title">{info['nombre']}</h3>
                </div>
                <p class="template-description">{info['descripcion']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botón debajo de la card
            tipo_form = filename.replace(".json", "")
            if st.button(
                f"Usar plantilla de {info['nombre']}", 
                key=f"load_{tipo_form}",
                use_container_width=True,
                type="primary"
            ):
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                    cargar_template(str(template_path), tipo_form)
                except Exception as e:
                    st.error(f"Error al cargar el template: {str(e)}")
            
            st.markdown("<br>", unsafe_allow_html=True)

if __name__ == '__main__':
    main()
