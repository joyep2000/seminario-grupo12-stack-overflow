# seminario-grupo12-stack-overflow
Repositorio del seminario complexivo grupo 12

**Nombre Caso de Estudio**

Análisis del Ecosistema de Stack Overflow: Tendencias y Patrones.

---

**Integrantes**

Henry Alexander Chulde Malquin
Johanna Lizeth Haro Murillo
Fabian Josue Yepez Gomez de la Torre

---

**Tema**

Análisis de popularidad de las diferentes tecnologías en Stack Overflow

---

**Objetivos**

Construir un dashboard de "Tendencias de Desarrollo" que permita a un analista explorar la popularidad y las dinámicas de las diferentes tecnologías en Stack Overflow. El objetivo es consolidar y visualizar datos de preguntas y etiquetas para extraer insights sobre el estado actual del mundo de la programación.

🎯 Descripción del Proyecto

Sistema completo de análisis de datos de Stack Overflow que permite explorar tendencias tecnológicas, popularidad de lenguajes de programación y frameworks a través de un pipeline de datos ETL, API RESTful y dashboard interactivo.
🏗️ Arquitectura del Sistema
text

seminario-grupo12-stack-overflow/
├── 📁 data/                          # Gestión de datos
│   ├── raw/                          # Datos crudos originales
│   └── processed/                    # Datos procesados y enriquecidos
├── 📁 scripts/                       # Pipeline de procesamiento
│   ├── data_loader.py               # Carga y validación de datos
│   ├── data_cleaning.py             # Limpieza y transformación
│   └── data_pipeline.py             # Orquestación del ETL
├── 📁 src/                          # Código de aplicación
│   ├── api/
│   │   └── main.py                  # API FastAPI
│   └── dashboard/
│       └── app.py                   # Dashboard Streamlit
├── 📁 docs/                         # Documentación
├── 🐳 Dockerfile                    # Contenedor API
├── 📋 requirements-*.txt           # Dependencias
└── 🔧 scripts de despliegue

🚀 Características Implementadas
🔄 Pipeline de Datos (ETL)

    Carga inteligente: Detección automática de encoding y validación de estructura

    Limpieza avanzada:

        Normalización de nombres de columnas

        Conversión de tipos de datos

        Manejo de valores nulos

        Procesamiento de texto (cuerpo de preguntas)

    Enriquecimiento de datos:

        Cálculo de longitud de texto

        Detección de código en preguntas

        Conteo de líneas

        Agrupación de tags por pregunta

    Métricas calculadas:

        Popularidad de tags por tiempo

        Score promedio por tecnología

        Estadísticas de engagement

🌐 API RESTful (FastAPI)

    Documentación automática en /docs y /redoc

    Endpoints implementados:

Endpoint	            Método	        Descripción
/	                    GET	            Información general de la API
/health	                GET	            Estado del sistema y salud de datos
/tags/top	            GET	            Top tags más populares con filtros
/tags/search	        GET	            Búsqueda de tags por nombre
/tags/{tag}/timeseries	GET	            Series temporales por tag
/questions/top	        GET	            Preguntas más populares
/stats	                GET	            Estadísticas generales del dataset
/debug/data-structure	GET	            Debug de estructura de datos

    Características de la API:

        ✅ Validación de parámetros

        ✅ Manejo robusto de errores

        ✅ Paginación y filtros

        ✅ CORS habilitado

        ✅ Tipado estático con Pydantic

📊 Dashboard Interactivo (Streamlit)

    Módulos implementados:

1. Métricas Generales

    Total de preguntas procesadas

    Tags únicos identificados

    Score promedio del dataset

    Distribución temporal

2. Top Tecnologías

    Ranking de tecnologías por popularidad

    Múltiples métricas de ordenamiento

    Visualizaciones interactivas con Plotly

    Tablas detalladas con estadísticas

3. Evolución Temporal

    NUEVO: Comparativa de tendencias temporales

    Selector de tecnologías para comparar

    Filtros por rango de años

    Agregación mensual, trimestral y anual

    Métricas de crecimiento y periodo pico

4. Preguntas Destacadas

    Listado de preguntas con mayor score

    Filtros por puntuación mínima

    Información detallada de cada pregunta

    Tags asociados y fechas

5. Búsqueda de Tecnologías

    Búsqueda en tiempo real

    Resultados con métricas de popularidad

    Tipos de coincidencia (exacta/parcial)

🛠️ Tecnologías      Utilizadas
Categoría	        Tecnologías
Backend	            Python 3.9, FastAPI, Uvicorn
Procesamiento	    Pandas, NumPy, Scikit-learn
Visualización	    Streamlit, Plotly, Matplotlib
Contenedores	    Docker, Docker Compose
Cloud	            Google Cloud Run, Streamlit Cloud
Datasets	        Stack Overflow Data (500k+ registros)

📈 Funcionalidades de Análisis

Análisis de Popularidad

    Identificación de tecnologías más preguntadas

    Tendencias temporales de adopción

    Correlación entre tecnologías

    Estacionalidad en preguntas

Métricas de Calidad

    Score promedio por tag

    Longitud promedio de preguntas

    Frecuencia de código en preguntas

    Distribución de votos

Series Temporales

    Evolución mensual de preguntas

    Identificación de picos de popularidad

    Comparativa entre tecnologías

    Tendencias de crecimiento

🚀 Despliegue Multi-Entorno
🌐 API - Google Cloud Run
bash

# URL de producción
https://api-stack-overflow-grupo12-964545988140.us-central1.run.app

# Características
- Auto-scaling automático
- SSL/TLS integrado
- Logging centralizado
- Monitoreo con Cloud Monitoring

📊 Dashboard - Streamlit Cloud
bash

# URL de producción  
https://seminario-grupo12-stack-overflow-grado-uniandes.streamlit.app/

# Características
- Despliegue continuo desde GitHub
- Recursos escalables
- Dominio personalizado

🐳 Contenedores Docker
dockerfile

# API Container
FROM python:3.9-slim
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0"]

🔧 Instalación y Desarrollo
Requisitos Previos
bash

Python 3.9+
Docker (opcional)
Git

Instalación Local
bash

# 1. Clonar repositorio
git clone https://github.com/joyep2000/seminario-grupo12-stack-overflow.git
cd seminario-grupo12-stack-overflow

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar pipeline de datos
python src/data_pipeline.py

# 5. Iniciar servicios
python src/api/main.py          # API en http://localhost:8000
streamlit run src/dashboard/app.py  # Dashboard en http://localhost:8501

Despliegue con Docker
bash

# Construir y ejecutar
docker build -t stack-overflow-api -f Dockerfile.api .
docker run -p 8000:8000 stack-overflow-api

📊 Estructura de Datos
Datasets Procesados

    tag_metrics.csv: Métricas agregadas por tag

    time_series.csv: Series temporales mensuales

    top_questions.csv: Preguntas más populares

    general_stats.csv: Estadísticas globales

Métricas Calculadas
python

{
  "question_count": "Número total de preguntas",
  "avg_score": "Puntuación promedio",
  "avg_body_length": "Longitud promedio del cuerpo",
  "avg_line_count": "Líneas promedio por pregunta", 
  "code_ratio": "Porcentaje de preguntas con código",
  "tags_count": "Número de tags por pregunta"
}

🎯 Endpoints de la API
Ejemplos de Uso
bash

# Top 10 tecnologías más populares
GET /tags/top?limit=10&min_questions=50

# Búsqueda de tecnologías
GET /tags/search?query=python&limit=15

# Series temporales para Python
GET /tags/python/timeseries?start_date=2010-01-01&aggregation=yearly

# Preguntas más votadas
GET /questions/top?limit=20&min_score=100

# Estadísticas generales
GET /stats

🔍 Ejemplos de Análisis
Identificación de Tendencias
python

# Ejemplo: Tecnologías con crecimiento más rápido
1. ReactJS - Crecimiento del 300% (2015-2016)
2. Docker - Adopción empresarial (2014-2015)  
3. TypeScript - Maduración ecosistema (2016-2017)

Correlaciones Tecnológicas
python

# Stack típico frontend moderno
javascript + reactjs + nodejs + express

# Stack data science
python + pandas + numpy + matplotlib + scikit-learn

📈 Resultados y Hallazgos
Tecnologías Más Populares

    JavaScript - Dominio en desarrollo web

    Java - Fuerte presencia empresarial

    Python - Crecimiento en data science

    C# - Desarrollo de aplicaciones Windows

    PHP - Continúa en desarrollo web

Tendencias Temporales

    2012-2014: Crecimiento de móviles (Android, iOS)

    2015-2016: Explosión de frameworks frontend (React, Angular)

    2017-2018: Adopción masiva de contenedores (Docker, Kubernetes)

    2019-2020: Consolidación de cloud (AWS, Azure)

🚀 Roadmap y Mejoras Futuras
Próximas Características

    Análisis de sentimiento en preguntas

    Sistema de recomendación de tags

    Alertas de tendencias emergentes

    Integración con GitHub trends

    Análisis de dificultad de preguntas

Optimizaciones Planeadas

    Caché Redis para consultas frecuentes

    Indexación Elasticsearch para búsquedas

    Streaming de datos en tiempo real

    Machine learning para predicciones

👥 Contribución
Integrantes del Grupo 12

    Henry Alexander Chulde Malquin

    Johanna Lizeth Haro Murillo

    Fabian Josue Yepez Gomez de la Torre

Flujo de Desarrollo
bash

# 1. Fork del proyecto
# 2. Crear feature branch
git checkout -b feature/nueva-funcionalidad

# 3. Commit de cambios
git commit -m "feat: añadir nueva funcionalidad"

# 4. Push al branch
git push origin feature/nueva-funcionalidad

# 5. Crear Pull Request

📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.
🔗 Enlaces Importantes

    📚 Documentación API: https://api-stack-overflow-grupo12-964545988140.us-central1.run.app/docs

    📊 Dashboard: https://seminario-grupo12-stack-overflow-grado-uniandes.streamlit.app/

    🐙 Repositorio: https://github.com/joyep2000/seminario-grupo12-stack-overflow.git

📞 Soporte

Para reportar bugs o solicitar características, por favor crear un issue en el repositorio de GitHub.