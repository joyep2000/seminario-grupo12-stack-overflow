import pandas as pd
import numpy as np
from datetime import datetime

def limpieza_nombres_columnas(df, dataset_type="generic"):
    
    print(f"🧹 Iniciando limpieza de nombres de columnas para {dataset_type}...")
    
    # Mapeo específico de la estructura de Stack Overflow
    mapeo_personalizado = {
        # Questions.csv 
        "Id": "id",
        "OwnerUserId": "owner_user_id", 
        "CreationDate": "creation_date",
        "ClosedDate": "closed_date",
        "Score": "score",
        "Title": "title",
        "Body": "body",
        
        # Tags.csv
        "Tag": "tag"
    }
    
    # Renombrar solo las columnas que existen
    columnas_existentes = df.columns.tolist()
    columnas_a_renombrar = {}
    
    for col_original, col_nuevo in mapeo_personalizado.items():
        if col_original in columnas_existentes:
            columnas_a_renombrar[col_original] = col_nuevo
    
    df_renombrado = df.rename(columns=columnas_a_renombrar)
    
    # Convertir todas a minúsculas (para columnas no mapeadas)
    df_renombrado.columns = df_renombrado.columns.str.lower()
    
    print(f"   Columnas originales: {df.columns.tolist()}")
    print(f"   Columnas después de limpieza: {df_renombrado.columns.tolist()}")
    print("✅ Nombres de columnas limpias.")
    
    return df_renombrado

def convertir_fechas(df):
    """
    Convierte columnas de fecha de string a datetime
    """
    print("📅 Convirtiendo columnas de fecha a datetime...")
    
    posibles_columnas_fecha = ['creation_date', 'closed_date']
    columnas_existentes = df.columns.tolist()
    columnas_convertidas = 0
    
    for col_fecha in posibles_columnas_fecha:
        if col_fecha in columnas_existentes:
            # Verificar si ya es datetime
            if not pd.api.types.is_datetime64_any_dtype(df[col_fecha]):
                print(f"   Convirtiendo {col_fecha}...")
                df[col_fecha] = pd.to_datetime(df[col_fecha], errors='coerce')
                nulos = df[col_fecha].isnull().sum()
                if nulos > 0:
                    print(f"     ⚠️  {nulos} valores no convertidos en {col_fecha}")
                columnas_convertidas += 1
    
    if columnas_convertidas > 0:
        print(f"✅ {columnas_convertidas} columnas de fecha convertidas")
    else:
        print("ℹ️  No se encontraron columnas de fecha para convertir")
    
    return df

def limpiar_valores_numericos(df):
    """
    Limpia y convierte columnas numéricas
    """
    print("🔢 Limpiando valores numéricos...")
    
    columnas_numericas = ['score', 'owner_user_id']
    columnas_existentes = df.columns.tolist()
    
    for col_num in columnas_numericas:
        if col_num in columnas_existentes:
            # Verificar si necesita conversión
            if not pd.api.types.is_numeric_dtype(df[col_num]):
                print(f"   Convirtiendo {col_num} a numérico...")
                df[col_num] = pd.to_numeric(df[col_num], errors='coerce')
            
            # Reemplazar NaN con 0 para columnas de conteo
            nulos_antes = df[col_num].isnull().sum()
            if nulos_antes > 0:
                # Para owner_user_id, usar -1 para indicar usuario anónimo
                if col_num == 'owner_user_id':
                    df[col_num] = df[col_num].fillna(-1)
                    print(f"   {col_num}: {nulos_antes} NaN reemplazados con -1 (anónimo)")
                else:
                    df[col_num] = df[col_num].fillna(0)
                    print(f"   {col_num}: {nulos_antes} NaN reemplazados con 0")
    
    return df

def limpiar_valores_texto(df):
    """
    Limpia columnas de texto
    """
    print("📝 Limpiando columnas de texto...")
    
    columnas_texto = ['title', 'body', 'tag']
    columnas_existentes = df.columns.tolist()
    
    for col_texto in columnas_texto:
        if col_texto in columnas_existentes:
            # Rellenar NaN con string vacío
            nulos = df[col_texto].isnull().sum()
            if nulos > 0:
                df[col_texto] = df[col_texto].fillna('')
                print(f"   {col_texto}: {nulos} NaN reemplazados con string vacío")
            
            # Eliminar espacios en blanco extra
            df[col_texto] = df[col_texto].str.strip()
    
    return df

def procesar_body_texto(df):
    """
    Procesa la columna Body para extraer información útil
    """
    if 'body' in df.columns:
        print("📄 Procesando contenido de Body...")
        
        # Calcular longitud del body
        df['body_length'] = df['body'].str.len()
        
        # Extraer si tiene código
        df['has_code'] = df['body'].str.contains('<code>|```', case=False, na=False)
        
        # Calcular número de líneas aproximado
        df['line_count'] = df['body'].str.count('\n') + 1
        
        print(f"   Estadísticas de Body:")
        print(f"     - Longitud promedio: {df['body_length'].mean():.0f} caracteres")
        print(f"     - Preguntas con código: {df['has_code'].sum():,}")
        print(f"     - Líneas promedio: {df['line_count'].mean():.1f}")
    
    return df

def eliminar_filas_inconsistentes(df, dataset_type="questions"):
    """
    Elimina filas que no contienen información esencial
    """
    print("🗑️ Eliminando filas inconsistentes...")
    
    filas_antes = len(df)
    criterios_eliminacion = []
    
    if dataset_type == "questions":
        # Para questions, debe tener al menos título
        if 'title' in df.columns:
            sin_titulo = (df['title'].isnull()) | (df['title'] == '')
            criterios_eliminacion.append(sin_titulo)
            print(f"   Preguntas sin título: {sin_titulo.sum()}")
        
        # Debe tener fecha de creación
        if 'creation_date' in df.columns:
            sin_fecha = df['creation_date'].isnull()
            criterios_eliminacion.append(sin_fecha)
            print(f"   Preguntas sin fecha: {sin_fecha.sum()}")
        
        # Debe tener ID
        if 'id' in df.columns:
            sin_id = df['id'].isnull()
            criterios_eliminacion.append(sin_id)
            print(f"   Preguntas sin ID: {sin_id.sum()}")
    
    elif dataset_type == "tags":
        # Para tags, debe tener tag y id
        if 'tag' in df.columns:
            sin_tag = (df['tag'].isnull()) | (df['tag'] == '')
            criterios_eliminacion.append(sin_tag)
            print(f"   Tags vacíos: {sin_tag.sum()}")
        
        if 'id' in df.columns:
            sin_id = df['id'].isnull()
            criterios_eliminacion.append(sin_id)
            print(f"   Tags sin ID: {sin_id.sum()}")
    
    # Combinar criterios
    if criterios_eliminacion:
        criterio_final = criterios_eliminacion[0]
        for criterio in criterios_eliminacion[1:]:
            criterio_final = criterio_final | criterio
        
        df_limpio = df[~criterio_final].copy()
    else:
        df_limpio = df.copy()
    
    filas_despues = len(df_limpio)
    filas_eliminadas = filas_antes - filas_despues
    
    print(f"   📊 Resumen eliminación:")
    print(f"     - Filas antes: {filas_antes:,}")
    print(f"     - Filas después: {filas_despues:,}")
    print(f"     - Filas eliminadas: {filas_eliminadas:,} ({filas_eliminadas/filas_antes*100:.1f}%)")
    
    return df_limpio.reset_index(drop=True)

def pipeline_limpieza_completa(df, dataset_type="questions"):
    """
    Ejecuta todo el pipeline de limpieza para un dataset
    """
    print(f"\n🚀 INICIANDO PIPELINE DE LIMPIEZA PARA {dataset_type.upper()}")
    print("=" * 50)
    
    df_limpio = limpieza_nombres_columnas(df, dataset_type)
    df_limpio = convertir_fechas(df_limpio)
    df_limpio = limpiar_valores_numericos(df_limpio)
    df_limpio = limpiar_valores_texto(df_limpio)
    
    if dataset_type == "questions":
        df_limpio = procesar_body_texto(df_limpio)
    
    df_limpio = eliminar_filas_inconsistentes(df_limpio, dataset_type)
    
    print(f"✅ PIPELINE DE {dataset_type.upper()} COMPLETADO")
    print(f"🎯 Dataset final: {df_limpio.shape[0]:,} filas, {df_limpio.shape[1]} columnas")
    
    return df_limpio

def unir_datasets_adaptada(questions_clean, tags_clean):
    """
    Une los datasets de Questions y Tags
    """
    print("\n🔗 UNIENDO DATASETS QUESTIONS Y TAGS")
    print("=" * 50)
    
    # Verificar columnas disponibles
    print("🔍 Columnas en Questions:", questions_clean.columns.tolist())
    print("🔍 Columnas en Tags:", tags_clean.columns.tolist())
    
    # Encontrar IDs comunes
    common_ids = set(questions_clean['id']).intersection(set(tags_clean['id']))
    print(f"   📈 IDs comunes para unión: {len(common_ids):,}")
    
    if len(common_ids) == 0:
        print("⚠️  ADVERTENCIA: No hay IDs comunes - unión vacía")
        return pd.DataFrame()
    
    # Filtrar solo IDs comunes para optimizar memoria
    questions_filtered = questions_clean[questions_clean['id'].isin(common_ids)].copy()
    tags_filtered = tags_clean[tags_clean['id'].isin(common_ids)].copy()
    
    print(f"   Questions filtrados: {questions_filtered.shape[0]:,}")
    print(f"   Tags filtrados: {tags_filtered.shape[0]:,}")
    
    # Agrupar tags por pregunta (crear lista de tags para cada pregunta)
    print("   Agrupando tags por pregunta...")
    tags_agrupados = tags_filtered.groupby('id')['tag'].apply(list).reset_index()
    
    # Asegurar que tags_string sea una string, no una lista
    tags_agrupados['tags_string'] = tags_agrupados['tag'].apply(
        lambda x: ', '.join(x) if isinstance(x, list) and x else ''
    )
    tags_agrupados['tags_count'] = tags_agrupados['tag'].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    
    print(f"   Tags agrupados: {tags_agrupados.shape[0]:,} preguntas con tags")
    
    # Realizar la unión
    print("   Realizando unión...")
    try:
        df_completo = questions_filtered.merge(
            tags_agrupados, 
            on='id', 
            how='left',
            suffixes=('_question', '_tags')
        )
        
        # Rellenar valores nulos en tags_string y tags_count
        df_completo['tags_string'] = df_completo['tags_string'].fillna('')
        df_completo['tags_count'] = df_completo['tags_count'].fillna(0)
        
        print(f"✅ UNIÓN COMPLETADA: {df_completo.shape[0]:,} filas, {df_completo.shape[1]} columnas")
        print(f"🔍 Columnas resultantes: {df_completo.columns.tolist()}")
        
        return df_completo
        
    except Exception as e:
        print(f"❌ Error en la unión: {e}")
        return pd.DataFrame()

def preparar_datos_analitica_adaptada(questions_df, tags_df):
    """
    Prepara los datos para el análisis uniendo Questions y Tags
    """
    print("\n🔗 PREPARANDO DATOS PARA ANÁLISIS")
    print("=" * 50)
    
    # Limpiar ambos datasets
    questions_clean = pipeline_limpieza_completa(questions_df, "questions")
    tags_clean = pipeline_limpieza_completa(tags_df, "tags")
    
    # Unir los datasets usando la versión adaptada
    df_completo = unir_datasets_adaptada(questions_clean, tags_clean)
    
    if df_completo is None or df_completo.empty:
        print("❌ No se pudo crear el dataset unido")
        return None
    
    # Análisis final
    print("\n📊 ANÁLISIS FINAL DEL DATASET UNIDO:")
    print(f"   • Preguntas procesadas: {df_completo.shape[0]:,}")
    print(f"   • Columnas disponibles: {df_completo.shape[1]}")
    print(f"   • Tags promedio por pregunta: {df_completo['tags_count'].mean():.1f}")
    print(f"   • Score promedio: {df_completo['score'].mean():.1f}")
    
    if 'creation_date' in df_completo.columns:
        fecha_min = df_completo['creation_date'].min()
        fecha_max = df_completo['creation_date'].max()
        print(f"   • Rango temporal: {fecha_min.strftime('%Y-%m')} a {fecha_max.strftime('%Y-%m')}")
    
    print(f"✅ DATASET COMPLETO CREADO EXITOSAMENTE!")
    
    return df_completo

# Función principal de prueba
if __name__ == "__main__":
    from data_loader import cargar_dataset_stack_overflow
    
    print("🧪 EJECUTANDO PRUEBA DEL SISTEMA DE LIMPIEZA")
    print("=" * 60)
    
    # Cargar datos
    questions, tags = cargar_dataset_stack_overflow()
    
    if questions is not None and tags is not None:
        # Probar el pipeline
        df_completo = preparar_datos_analitica_adaptada(questions, tags)
        
        if df_completo is not None and not df_completo.empty:
            print("\n🎉 PRUEBA EXITOSA!")
            print(f"📁 Dataset final: {df_completo.shape}")
            
            # Mostrar muestra
            print("\n📋 MUESTRA DEL DATASET FINAL:")
            print(df_completo[['id', 'title', 'score', 'tags_count', 'tags_string']].head(3))
        else:
            print("\n❌ PRUEBA FALLÓ - No se pudo crear el dataset unido")
    else:
        print("\n❌ PRUEBA FALLÓ - No se pudieron cargar los datos originales")