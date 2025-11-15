from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import os
import sys
from datetime import datetime

# Configurar path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '../..')
sys.path.append(project_root)

app = FastAPI(
    title="Stack Overflow Analytics API",
    description="API para análisis de tendencias en Stack Overflow - Grupo 12",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def debug_file_info(filepath):
    """Debug información de un archivo"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            first_lines = [f.readline() for _ in range(3)]
        return {
            "exists": True,
            "size_bytes": size,
            "first_lines": first_lines
        }
    else:
        return {"exists": False}

def load_tag_metrics_correctly(filepath):
    """Carga tag_metrics de manera robusta"""
    try:
        print(f"🔍 Intentando cargar: {filepath}")
        
        # Verificar si el archivo existe y tiene contenido
        if not os.path.exists(filepath):
            print("❌ Archivo no existe")
            return pd.DataFrame()
        
        file_size = os.path.getsize(filepath)
        if file_size < 10:  # Menos de 10 bytes = básicamente vacío
            print("❌ Archivo demasiado pequeño")
            return pd.DataFrame()
        
        # Leer el archivo
        df = pd.read_csv(filepath)
        print(f"✅ Archivo leído: {df.shape}")
        
        # Debug: mostrar información del DataFrame
        print(f"   Columnas: {df.columns.tolist()}")
        print(f"   Primeras filas:")
        print(df.head(2))
        
        # Diferentes estructuras posibles del archivo
        if df.empty:
            print("❌ DataFrame vacío")
            return pd.DataFrame()
        
        # Caso 1: Tiene columna 'Unnamed: 0' (índice guardado)
        if 'Unnamed: 0' in df.columns:
            print("📊 Estructura: Con índice 'Unnamed: 0'")
            df = df.set_index('Unnamed: 0')
            df.index.name = 'tag'
            return df
        
        # Caso 2: Tiene columna 'tag' explícita
        elif 'tag' in df.columns:
            print("📊 Estructura: Con columna 'tag'")
            df = df.set_index('tag')
            return df
        
        # Caso 3: El índice ya es los tags (primera columna)
        else:
            print("📊 Estructura: Usando primera columna como tag")
            df = df.set_index(df.columns[0])
            df.index.name = 'tag'
            return df
            
    except Exception as e:
        print(f"❌ Error cargando tag_metrics: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

# Cargar datos procesados
def load_processed_data():
    """Carga los datos procesados desde los archivos"""
    try:
        base_path = os.path.join(project_root, "data", "processed")
        
        print("📥 CARGANDO DATOS PROCESADOS...")
        print(f"📁 Ruta base: {base_path}")
        
        # 1. Cargar tag_metrics - CON DEBUG COMPLETO
        tag_metrics_path = os.path.join(base_path, 'tag_metrics.csv')
        print(f"🔍 Información de tag_metrics.csv:")
        file_info = debug_file_info(tag_metrics_path)
        print(f"   - Existe: {file_info['exists']}")
        if file_info['exists']:
            print(f"   - Tamaño: {file_info['size_bytes']} bytes")
            print(f"   - Primeras líneas: {file_info['first_lines']}")
        
        tag_metrics = load_tag_metrics_correctly(tag_metrics_path)
        
        # 2. Cargar time_series
        time_series_path = os.path.join(base_path, 'time_series.csv')
        time_series = pd.DataFrame()
        if os.path.exists(time_series_path) and os.path.getsize(time_series_path) > 10:
            time_series = pd.read_csv(time_series_path)
            if 'date' in time_series.columns:
                time_series['date'] = pd.to_datetime(time_series['date'])
            print(f"✅ Time Series cargado: {time_series.shape}")
        else:
            print("⚠️  Time Series no disponible")
        
        # 3. Cargar top_questions
        top_questions_path = os.path.join(base_path, 'top_questions.csv')
        top_questions = pd.DataFrame()
        if os.path.exists(top_questions_path) and os.path.getsize(top_questions_path) > 10:
            top_questions = pd.read_csv(top_questions_path)
            if 'creation_date' in top_questions.columns:
                top_questions['creation_date'] = pd.to_datetime(top_questions['creation_date'])
            print(f"✅ Top Questions cargado: {top_questions.shape}")
        else:
            print("❌ Top Questions no disponible")
        
        # 4. Cargar general_stats
        general_stats_path = os.path.join(base_path, 'general_stats.csv')
        stats_dict = {}
        if os.path.exists(general_stats_path) and os.path.getsize(general_stats_path) > 10:
            general_stats = pd.read_csv(general_stats_path)
            stats_dict = general_stats.iloc[0].to_dict() if not general_stats.empty else {}
            print(f"✅ General Stats cargado: {len(stats_dict)} métricas")
        else:
            print("⚠️  General Stats no disponible")
        
        print("\n🎯 RESUMEN DE CARGA:")
        print(f"   • Tag Metrics: {tag_metrics.shape}")
        print(f"   • Time Series: {time_series.shape}")
        print(f"   • Top Questions: {top_questions.shape}")
        print(f"   • General Stats: {len(stats_dict)} métricas")
        
        return {
            'tag_metrics': tag_metrics,
            'time_series': time_series,
            'top_questions': top_questions,
            'general_stats': stats_dict
        }
        
    except Exception as e:
        print(f"❌ Error crítico cargando datos: {e}")
        import traceback
        traceback.print_exc()
        return None

# Cargar datos al iniciar
print("🚀 INICIANDO CARGA DE DATOS DE LA API...")
data = load_processed_data()
print("✅ CARGA DE DATOS COMPLETADA\n")

@app.get("/")
async def root():
    return {
        "message": "Stack Overflow Analytics API - Grupo 12", 
        "status": "active" if data else "no_data",
        "endpoints": {
            "/docs": "Documentación interactiva",
            "/health": "Estado del sistema",
            "/debug/data-structure": "Estructura de datos (debug)",
            "/tags/top": "Top tags más populares",
            "/tags/search": "Buscar tags",
            "/tags/{tag}/timeseries": "Series temporales por tag",
            "/questions/top": "Preguntas más populares",
            "/stats": "Estadísticas generales"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de salud del sistema"""
    if not data:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "message": "Datos no disponibles. Ejecute el pipeline de datos primero.",
                "details": "Ejecute: python src/data_pipeline.py"
            }
        )
    
    # Verificar qué datos tenemos
    tags_loaded = not data['tag_metrics'].empty
    questions_loaded = not data['top_questions'].empty
    stats_loaded = len(data['general_stats']) > 0
    
    status = "healthy" if (tags_loaded or questions_loaded) else "partial"
    
    return {
        "status": status,
        "data_loaded": True,
        "timestamp": datetime.now().isoformat(),
        "components": {
            "tag_metrics": tags_loaded,
            "top_questions": questions_loaded,
            "general_stats": stats_loaded
        },
        "data_stats": {
            "tags_count": len(data['tag_metrics']),
            "time_series_records": len(data['time_series']),
            "top_questions": len(data['top_questions'])
        }
    }

@app.get("/tags/top")
async def get_top_tags(
    limit: int = Query(20, description="Número de tags a retornar", ge=1, le=100),
    min_questions: int = Query(1, description="Mínimo número de preguntas", ge=1),
    sort_by: str = Query("question_count", description="Campo para ordenar")
):
    """Obtiene los tags más populares"""
    if not data or data['tag_metrics'].empty:
        raise HTTPException(
            status_code=404, 
            detail="Datos de tags no disponibles. Ejecute el pipeline de datos primero."
        )
    
    tag_metrics = data['tag_metrics']
    
    print(f"🔍 Procesando tags: {tag_metrics.shape}")
    print(f"   Columnas disponibles: {tag_metrics.columns.tolist()}")
    
    # Verificar que tenemos las columnas necesarias
    if 'question_count' not in tag_metrics.columns:
        raise HTTPException(
            status_code=500, 
            detail=f"Estructura de tags incorrecta. Columnas: {tag_metrics.columns.tolist()}"
        )
    
    # Filtrar por mínimo de preguntas
    filtered_tags = tag_metrics[tag_metrics['question_count'] >= min_questions]
    
    if filtered_tags.empty:
        return {
            "metadata": {
                "total_tags": 0,
                "sort_by": sort_by,
                "min_questions": min_questions,
                "message": "No hay tags que cumplan el criterio mínimo de preguntas"
            },
            "data": []
        }
    
    # Ordenar
    if sort_by in filtered_tags.columns:
        top_tags = filtered_tags.nlargest(limit, sort_by)
    else:
        # Si la columna no existe, ordenar por question_count
        top_tags = filtered_tags.nlargest(limit, 'question_count')
        sort_by = 'question_count'
    
    # Formatear respuesta
    result = []
    for tag_name, row in top_tags.iterrows():
        tag_data = {
            "tag": str(tag_name),  # Asegurar que sea string
            "question_count": int(row['question_count']),
        }
        
        # Agregar métricas adicionales si existen
        if 'avg_score' in row and pd.notna(row['avg_score']):
            tag_data["avg_score"] = float(row['avg_score'])
        if 'avg_body_length' in row and pd.notna(row['avg_body_length']):
            tag_data["avg_body_length"] = float(row['avg_body_length'])
        if 'avg_line_count' in row and pd.notna(row['avg_line_count']):
            tag_data["avg_line_count"] = float(row['avg_line_count'])
        if 'code_ratio' in row and pd.notna(row['code_ratio']):
            tag_data["code_ratio"] = float(row['code_ratio'])
        
        result.append(tag_data)
    
    return {
        "metadata": {
            "total_tags": len(result),
            "sort_by": sort_by,
            "min_questions": min_questions,
            "available_columns": tag_metrics.columns.tolist()
        },
        "data": result
    }

# Los otros endpoints se mantienen igual...
@app.get("/tags/search")
async def search_tags(
    query: str = Query(..., description="Texto a buscar en tags"),
    limit: int = Query(10, description="Límite de resultados", ge=1, le=50)
):
    """Busca tags por nombre"""
    if not data or data['tag_metrics'].empty:
        raise HTTPException(
            status_code=404, 
            detail="Datos de tags no disponibles"
        )
    
    tag_metrics = data['tag_metrics']
    
    # Búsqueda case-insensitive en el índice (nombres de tags)
    matching_tags = tag_metrics[
        tag_metrics.index.astype(str).str.contains(query, case=False, na=False)
    ]
    
    results = []
    for tag_name, row in matching_tags.head(limit).iterrows():
        result_item = {
            "tag": str(tag_name),
            "question_count": int(row['question_count']),
            "match_type": "exact" if query.lower() == str(tag_name).lower() else "partial"
        }
        
        if 'avg_score' in row and pd.notna(row['avg_score']):
            result_item["avg_score"] = float(row['avg_score'])
        
        results.append(result_item)
    
    return {
        "query": query,
        "results_found": len(results),
        "data": results
    }

@app.get("/questions/top")
async def get_top_questions(
    limit: int = Query(10, description="Número de preguntas", ge=1, le=50),
    min_score: int = Query(0, description="Score mínimo", ge=0)
):
    """Obtiene las preguntas más populares"""
    if not data or data['top_questions'].empty:
        raise HTTPException(
            status_code=404, 
            detail="Datos de preguntas no disponibles"
        )
    
    top_questions = data['top_questions']
    
    # Verificar columnas disponibles
    required_columns = ['id', 'title', 'score']
    missing_columns = [col for col in required_columns if col not in top_questions.columns]
    
    if missing_columns:
        raise HTTPException(
            status_code=500, 
            detail=f"Estructura de datos incorrecta. Columnas: {top_questions.columns.tolist()}"
        )
    
    # Filtrar por score mínimo
    filtered_questions = top_questions[top_questions['score'] >= min_score]
    
    # Ordenar y limitar
    result_questions = filtered_questions.nlargest(limit, 'score')
    
    # Formatear respuesta
    result = []
    for _, row in result_questions.iterrows():
        question_data = {
            "id": int(row['id']),
            "title": row['title'],
            "score": int(row['score'])
        }
        
        # Agregar campos opcionales si existen
        if 'tags_string' in row and pd.notna(row['tags_string']):
            question_data["tags"] = row['tags_string']
        if 'creation_date' in row and pd.notna(row['creation_date']):
            question_data["creation_date"] = row['creation_date'].strftime('%Y-%m-%d')
        if 'tags_count' in row and pd.notna(row['tags_count']):
            question_data["tags_count"] = int(row['tags_count'])
        if 'body_length' in row and pd.notna(row['body_length']):
            question_data["body_length"] = int(row['body_length'])
        
        result.append(question_data)
    
    return {
        "metadata": {
            "total_questions": len(result),
            "min_score": min_score
        },
        "data": result
    }

@app.get("/stats")
async def get_general_stats():
    """Obtiene estadísticas generales del dataset"""
    if not data:
        raise HTTPException(status_code=503, detail="Datos no disponibles")
    
    stats = data['general_stats']
    tag_metrics = data['tag_metrics']
    
    # Calcular estadísticas adicionales
    additional_stats = {}
    
    if not tag_metrics.empty and len(tag_metrics) > 0:
        additional_stats["total_unique_tags"] = len(tag_metrics)
        if len(tag_metrics) > 0:
            most_popular = tag_metrics.nlargest(1, 'question_count')
            if not most_popular.empty:
                additional_stats["most_popular_tag"] = most_popular.index[0]
                additional_stats["most_popular_count"] = int(most_popular.iloc[0]['question_count'])
    
    return {
        "general_statistics": stats,
        "additional_metrics": additional_stats
    }

@app.get("/debug/data-structure")
async def debug_data_structure():
    """Endpoint para debug de la estructura de datos"""
    if not data:
        return {"error": "No hay datos cargados"}
    
    debug_info = {
        "tag_metrics": {
            "loaded": not data['tag_metrics'].empty,
            "row_count": len(data['tag_metrics']),
            "columns": data['tag_metrics'].columns.tolist() if not data['tag_metrics'].empty else [],
            "sample": data['tag_metrics'].head(3).to_dict() if not data['tag_metrics'].empty else {}
        },
        "time_series": {
            "loaded": not data['time_series'].empty,
            "row_count": len(data['time_series']),
            "columns": data['time_series'].columns.tolist() if not data['time_series'].empty else []
        },
        "top_questions": {
            "loaded": not data['top_questions'].empty,
            "row_count": len(data['top_questions']),
            "columns": data['top_questions'].columns.tolist() if not data['top_questions'].empty else []
        },
        "general_stats": data['general_stats']
    }
    
    return debug_info

# Manejo de errores
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint no encontrado"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)