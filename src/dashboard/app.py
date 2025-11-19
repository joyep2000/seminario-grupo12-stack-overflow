import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
import sys
from datetime import datetime, timedelta
import numpy as np
import re

# Configurar path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '../..')
sys.path.append(project_root)

# Configuración de la página
st.set_page_config(
    page_title="Stack Overflow Analytics",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# URL base de la API en Google Cloud
API_BASE_URL = "https://api-stack-overflow-grupo12-964545988140.us-central1.run.app"

# Función para parsear fechas del date_range
def parse_date_range(date_range_str):
    """Parsear el string date_range de manera segura"""
    if not date_range_str:
        return {'min': None, 'max': None}
    
    try:
        # Extraer fechas usando expresiones regulares
        if isinstance(date_range_str, str):
            # Buscar patrones de fecha en el string
            date_pattern = r"(\d{4}-\d{2}-\d{2})"
            dates = re.findall(date_pattern, date_range_str)
            
            if len(dates) >= 2:
                min_date = pd.to_datetime(dates[0])
                max_date = pd.to_datetime(dates[1])
                return {'min': min_date, 'max': max_date}
        
        # Si no se puede parsear, retornar None
        return {'min': None, 'max': None}
    except:
        return {'min': None, 'max': None}

# Título principal
st.markdown('<h1 class="main-header">🔍 Stack Overflow Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown("**Análisis de tendencias y patrones en el ecosistema de desarrollo - Grupo 12**")
st.markdown("---")

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración del Sistema")

# Verificar estado de la API
@st.cache_data(ttl=300)
def check_api_health():
    """Verificar estado de la API"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, {}
    except requests.exceptions.RequestException as e:
        return False, {}

# Cargar TODOS los datos de la API
@st.cache_data(ttl=600)
def load_all_data_from_api():
    """Cargar todos los datos desde la API"""
    try:
        # 1. Cargar stats generales
        stats_response = requests.get(f"{API_BASE_URL}/stats", timeout=15)
        stats_data = stats_response.json() if stats_response.status_code == 200 else {}
        
        # 2. Cargar top tags (más tags para mejor análisis)
        tags_response = requests.get(f"{API_BASE_URL}/tags/top?limit=100", timeout=15)
        tags_data = tags_response.json() if tags_response.status_code == 200 else {}
        
        # 3. Cargar top questions
        questions_response = requests.get(f"{API_BASE_URL}/questions/top?limit=50", timeout=15)
        questions_data = questions_response.json() if questions_response.status_code == 200 else {}
        
        return {
            'stats': stats_data,
            'tags': tags_data.get('data', []),
            'questions': questions_data.get('data', [])
        }
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return {'stats': {}, 'tags': [], 'questions': []}

# Estado del sistema
api_healthy, health_info = check_api_health()

st.sidebar.subheader("🔍 Estado del Sistema")
if api_healthy:
    st.sidebar.success("✅ API Conectada")
    if health_info.get('data_stats'):
        stats = health_info['data_stats']
        st.sidebar.info(f"📊 Tags cargados: {stats.get('tags_count', 0):,}")
        st.sidebar.info(f"📈 Series temporales: {stats.get('time_series_records', 0):,}")
        st.sidebar.info(f"🔥 Top preguntas: {stats.get('top_questions', 0):,}")
else:
    st.sidebar.error("❌ API No disponible")
    st.sidebar.markdown(f"""
    **API desplegada en:** 
    `{API_BASE_URL}`
    """)

# Cargar datos
data = load_all_data_from_api() if api_healthy else {'stats': {}, 'tags': [], 'questions': []}

# Mostrar advertencia si no hay datos
if not api_healthy:
    st.markdown(f"""
    <div class="warning-box">
        <h3>⚠️ API No Disponible</h3>
        <p>No se puede conectar a la API en:</p>
        <code>{API_BASE_URL}</code>
        <p>Verifica que la API esté ejecutándose correctamente en Google Cloud.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Sección 1: Métricas Generales
st.header("📈 Métricas Generales del Dataset")

if data['stats'] and data['stats'].get('general_statistics'):
    stats = data['stats']['general_statistics']
    
    # Primera fila de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_questions = stats.get('total_questions', 0)
        st.metric(
            "Total Preguntas",
            f"{total_questions:,}",
            help="Número total de preguntas procesadas"
        )
    
    with col2:
        total_tags = stats.get('total_unique_tags', 0)
        st.metric(
            "Total Tags Únicos", 
            f"{total_tags:,}",
            help="Tags diferentes identificados"
        )
    
    with col3:
        avg_score = stats.get('avg_score', 0)
        st.metric(
            "Score Promedio",
            f"{avg_score:.2f}",
            help="Puntuación promedio de las preguntas"
        )
    
    with col4:
        avg_tags = stats.get('avg_tags_per_question', 0)
        st.metric(
            "Tags/Pregunta",
            f"{avg_tags:.1f}",
            help="Tags promedio por pregunta"
        )
    
    # Segunda fila de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        body_length = stats.get('avg_body_length', 0)
        st.metric(
            "Long. Cuerpo Prom.",
            f"{body_length:.0f}",
            help="Longitud promedio del cuerpo de las preguntas"
        )
    
    with col2:
        total_tags_assigned = stats.get('total_tags', 0)
        st.metric(
            "Total Tags Asignados",
            f"{total_tags_assigned:,}",
            help="Total de tags asignados a todas las preguntas"
        )
    
    with col3:
        # Manejo seguro del date_range
        date_range_str = stats.get('date_range', '')
        date_range = parse_date_range(date_range_str)
        min_date = date_range.get('min')
        if min_date:
            st.metric("Fecha Inicio", min_date.strftime('%Y-%m'))
        else:
            st.metric("Fecha Inicio", "N/A")
    
    with col4:
        # Manejo seguro del date_range
        date_range_str = stats.get('date_range', '')
        date_range = parse_date_range(date_range_str)
        max_date = date_range.get('max')
        if max_date:
            st.metric("Fecha Fin", max_date.strftime('%Y-%m'))
        else:
            st.metric("Fecha Fin", "N/A")
            
    # Debug opcional
    with st.expander("🔍 Ver datos crudos de estadísticas"):
        st.json(stats)
else:
    st.warning("No se pudieron cargar las estadísticas generales")

# Sección 2: Top Tecnologías
st.header("🏆 Top Tecnologías Más Populares")

if data['tags']:
    # Convertir a DataFrame
    tags_df = pd.DataFrame(data['tags'])
    
    # Controles en sidebar
    st.sidebar.header("🎛️ Controles de Visualización")
    
    # Selector de métrica
    available_metrics = ['question_count', 'avg_score', 'avg_body_length', 'avg_line_count', 'code_ratio']
    metric_option = st.sidebar.selectbox(
        "Métrica para ranking:",
        available_metrics,
        format_func=lambda x: {
            'question_count': 'Número de Preguntas',
            'avg_score': 'Puntuación Promedio', 
            'avg_body_length': 'Longitud Cuerpo Promedio',
            'avg_line_count': 'Líneas Promedio',
            'code_ratio': 'Ratio de Código'
        }[x]
    )
    
    n_techs = st.sidebar.slider("Número de tecnologías a mostrar:", 5, 50, 15)
    
    # Ordenar datos
    if metric_option in tags_df.columns:
        sorted_tags = tags_df.nlargest(n_techs, metric_option)
        
        # Gráfico de barras
        fig_bar = px.bar(
            sorted_tags,
            x='tag',
            y=metric_option,
            title=f'Top {n_techs} Tecnologías por {metric_option.replace("_", " ").title()}',
            labels={
                'tag': 'Tecnología',
                'question_count': 'Número de Preguntas',
                'avg_score': 'Puntuación Promedio',
                'avg_body_length': 'Longitud Cuerpo Promedio',
                'avg_line_count': 'Líneas Promedio',
                'code_ratio': 'Ratio de Código'
            },
            color=metric_option,
            color_continuous_scale='viridis'
        )
        
        fig_bar.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
            height=500
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Mostrar tabla detallada
        with st.expander("📋 Ver tabla detallada de tecnologías"):
            display_cols = ['tag', 'question_count', 'avg_score', 'avg_body_length', 'avg_line_count', 'code_ratio']
            available_cols = [col for col in display_cols if col in sorted_tags.columns]
            
            display_df = sorted_tags[available_cols].copy()
            
            # Formatear números
            formatting = {
                'question_count': lambda x: f"{int(x):,}",
                'avg_score': lambda x: f"{x:.2f}",
                'avg_body_length': lambda x: f"{x:.0f}",
                'avg_line_count': lambda x: f"{x:.1f}",
                'code_ratio': lambda x: f"{x:.2f}"
            }
            
            for col in available_cols:
                if col in formatting:
                    display_df[col] = display_df[col].apply(formatting[col])
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
    else:
        st.error(f"La métrica '{metric_option}' no está disponible en los datos")
else:
    st.warning("No hay datos de tags disponibles")

# Sección 3: Análisis Temporal Interactivo
st.header("📈 Evolución Temporal de Tecnologías")

# Función para cargar datos temporales
@st.cache_data(ttl=1800)
def load_temporal_data(tag_name):
    """Cargar datos temporales para un tag específico"""
    try:
        response = requests.get(f"{API_BASE_URL}/tags/{tag_name}/timeseries", timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

if data['tags']:
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("🔧 Configuración")
        
        # Selector de tecnologías
        available_tags = [tag['tag'] for tag in data['tags'][:30]]  # Top 30 tags
        selected_tags = st.multiselect(
            "Selecciona tecnologías para comparar:",
            options=available_tags,
            default=available_tags[:3] if len(available_tags) >= 3 else available_tags,
            max_selections=5
        )
        
        # Selector de rango de años
        year_range = st.slider(
            "Rango de años:",
            min_value=2008,
            max_value=2016,  # Según tus datos, max 2016
            value=(2009, 2015)
        )
    
    with col1:
        if selected_tags:
            st.subheader("📊 Comparativa Temporal")
            
            # Container para el gráfico
            chart_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            # Cargar y combinar datos
            all_data = []
            total_tags = len(selected_tags)
            
            for i, tag in enumerate(selected_tags):
                temporal_data = load_temporal_data(tag)
                if temporal_data and 'data' in temporal_data:
                    tag_df = pd.DataFrame(temporal_data['data'])
                    tag_df['tag'] = tag
                    all_data.append(tag_df)
                
                # Actualizar progress bar
                progress_bar.progress((i + 1) / total_tags)
            
            progress_bar.empty()
            
            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                
                # Convertir fecha
                if 'date' in combined_df.columns:
                    combined_df['date'] = pd.to_datetime(combined_df['date'])
                    
                    # Filtrar por rango de años
                    combined_df = combined_df[
                        (combined_df['date'].dt.year >= year_range[0]) & 
                        (combined_df['date'].dt.year <= year_range[1])
                    ]
                    
                    if not combined_df.empty:
                        # Crear gráfico de líneas
                        fig_line = px.line(
                            combined_df,
                            x='date',
                            y='count',
                            color='tag',
                            title=f'Evolución de Preguntas por Tecnología ({year_range[0]}-{year_range[1]})',
                            labels={'count': 'Número de Preguntas', 'date': 'Fecha'},
                            line_shape='spline'
                        )
                        
                        fig_line.update_layout(
                            height=500,
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )
                        
                        chart_placeholder.plotly_chart(fig_line, use_container_width=True)
                        
                        # Mostrar métricas por tecnología
                        st.subheader("📈 Métricas por Tecnología")
                        metrics_cols = st.columns(min(len(selected_tags), 4))
                        
                        for idx, tag in enumerate(selected_tags):
                            tag_data = combined_df[combined_df['tag'] == tag]
                            if not tag_data.empty:
                                with metrics_cols[idx % len(metrics_cols)]:
                                    total_questions = tag_data['count'].sum()
                                    max_questions = tag_data['count'].max()
                                    avg_questions = tag_data['count'].mean()
                                    
                                    st.metric(
                                        label=f"**{tag}**",
                                        value=f"{int(total_questions):,}",
                                        delta=f"Peak: {int(max_questions):,}"
                                    )
                                    st.caption(f"Promedio: {avg_questions:.1f} preguntas/mes")
                    else:
                        st.info("No hay datos disponibles para el rango de años seleccionado")
                else:
                    st.warning("Los datos temporales no contienen información de fechas")
            else:
                st.info("No se pudieron cargar datos temporales para las tecnologías seleccionadas")
        else:
            st.info("Selecciona al menos una tecnología para ver la comparativa temporal")
else:
    st.warning("No hay datos disponibles para el análisis temporal")

# Sección 4: Preguntas Más Populares
st.header("🔥 Preguntas Más Destacadas")

if data['questions']:
    # Controles para preguntas
    col1, col2 = st.columns([1, 1])
    with col1:
        questions_limit = st.slider("Número de preguntas a mostrar:", 5, 50, 10, key="questions_limit")
    with col2:
        min_score = st.slider("Score mínimo:", 0, 100, 0, key="min_score")
    
    # Filtrar preguntas
    filtered_questions = [q for q in data['questions'] if q.get('score', 0) >= min_score]
    displayed_questions = filtered_questions[:questions_limit]
    
    if displayed_questions:
        # Mostrar preguntas en tarjetas
        for i, question in enumerate(displayed_questions, 1):
            with st.expander(f"{i}. {question.get('title', 'Sin título')[:120]}... (Score: {question.get('score', 0)})", expanded=i <= 2):
                col_left, col_right = st.columns([3, 1])
                
                with col_left:
                    st.write(f"**ID:** {question.get('id', 'N/A')}")
                    
                    # Mostrar tags
                    if question.get('tags_string'):
                        st.write(f"**Tags:** {question['tags_string']}")
                    
                    if question.get('tags_count'):
                        st.write(f"**Número de tags:** {question['tags_count']}")
                    
                    # Mostrar fecha
                    if question.get('creation_date'):
                        st.write(f"**Fecha:** {question['creation_date']}")
                    
                    # Mostrar título completo si es diferente del truncado
                    title = question.get('title', '')
                    if len(title) > 120:
                        st.write(f"**Título completo:** {title}")
                
                with col_right:
                    st.metric("Score", question.get('score', 0))
                    
                    if question.get('tags_count'):
                        st.metric("N° Tags", question['tags_count'])
    else:
        st.info("No se encontraron preguntas que cumplan los criterios")
else:
    st.warning("No hay datos de preguntas disponibles")

# Sección 5: Búsqueda de Tags
st.header("🔍 Búsqueda de Tecnologías")

@st.cache_data(ttl=1800)
def search_tags_api(query):
    """Buscar tags mediante API"""
    try:
        response = requests.get(f"{API_BASE_URL}/tags/search?query={query}&limit=15", timeout=10)
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    except:
        return []

# Búsqueda de tags
search_query = st.text_input("Buscar tecnología:", placeholder="Ej: python, javascript, machine learning...", key="search_input")

if search_query and search_query.strip():
    with st.spinner(f"Buscando '{search_query}'..."):
        search_results = search_tags_api(search_query)
    
    if search_results:
        st.success(f"Se encontraron {len(search_results)} resultados para '{search_query}'")
        
        # Mostrar resultados en columnas
        cols = st.columns(2)
        for idx, result in enumerate(search_results):
            with cols[idx % 2]:
                with st.container():
                    st.markdown(f"**{result.get('tag', 'N/A')}**")
                    st.write(f"**Preguntas:** {result.get('question_count', 0):,}")
                    
                    if result.get('avg_score'):
                        st.write(f"**Score promedio:** {result['avg_score']:.2f}")
                    
                    if result.get('match_type'):
                        st.write(f"**Tipo de coincidencia:** {result['match_type']}")
                    
                    st.markdown("---")
    elif search_query.strip():
        st.warning(f"No se encontraron resultados para '{search_query}'")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center'>
    <p><strong>Stack Overflow Analytics Dashboard</strong> · Grupo 12</p>
    <p>Datos de <a href="https://www.kaggle.com/datasets/stackoverflow/stacksample" target="_blank">Stack Overflow Dataset</a> · 
    Desarrollado con Python, FastAPI y Streamlit</p>
    <p><small>API: {API_BASE_URL}</small></p>
</div>
""", unsafe_allow_html=True)

# Información adicional en sidebar
st.sidebar.markdown("---")
st.sidebar.header("ℹ️ Información")
st.sidebar.info("""
Este dashboard analiza datos de Stack Overflow para identificar tendencias tecnológicas.

**Características:**
- Top tecnologías por preguntas
- Evolución temporal comparativa  
- Preguntas más populares
- Búsqueda de tecnologías
- Métricas agregadas
""")

# Botón para recargar datos
if st.sidebar.button("🔄 Recargar Datos"):
    st.cache_data.clear()
    st.rerun()

if __name__ == "__main__":
    pass