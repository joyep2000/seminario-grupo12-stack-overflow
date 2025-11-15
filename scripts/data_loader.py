import pandas as pd
import numpy as np
import os

def cargar_datos(ruta_archivo, nombre_dataset="Dataset"):
    """
    Carga un archivo CSV y retorna un DataFrame con manejo robusto de errores
    """
    print(f"📥 Cargando {nombre_dataset} desde {ruta_archivo}...")
    
    try:
        # Verificar si el archivo existe
        if not os.path.exists(ruta_archivo):
            print(f"❌ Error: El archivo {ruta_archivo} no existe")
            return None
        
        # Cargar el CSV
        df = pd.read_csv(ruta_archivo, encoding='utf-8')
        
        print(f"   ✅ {nombre_dataset} cargado: {df.shape[0]:,} filas, {df.shape[1]} columnas")
        print(f"   📊 Columnas: {list(df.columns)}")
        
        return df
        
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(ruta_archivo, encoding='latin-1')
            print("   ✅ Usando encoding latin-1")
            return df
        except Exception as e:
            print(f"❌ Error de encoding: {e}")
            return None
    except Exception as e:
        print(f"❌ Error cargando {nombre_dataset}: {e}")
        return None

def cargar_dataset_stack_overflow(ruta_base="./data/raw"):
    """
    Carga tanto Questions.csv como Tags.csv y analiza su relación
    """
    print("🚀 CARGANDO DATASET COMPLETO DE STACK OVERFLOW")
    print("=" * 50)
    
    questions_path = os.path.join(ruta_base, "Questions.csv")
    tags_path = os.path.join(ruta_base, "Tags.csv")
    
    # Cargar datasets
    questions_df = cargar_datos(questions_path, "Questions")
    tags_df = cargar_datos(tags_path, "Tags")
    
    if questions_df is None or tags_df is None:
        return None, None
    
    # Análisis de la relación entre los datasets
    print("\n🔍 ANALIZANDO RELACIÓN ENTRE DATASETS:")
    print(f"   📊 Questions: {questions_df.shape[0]:,} filas, {questions_df.shape[1]} columnas")
    print(f"   📊 Tags: {tags_df.shape[0]:,} filas, {tags_df.shape[1]} columnas")
    
    # IDs únicos
    unique_questions_ids = questions_df['Id'].nunique()
    unique_tags_ids = tags_df['Id'].nunique()
    
    print(f"   🆔 IDs únicos en Questions: {unique_questions_ids:,}")
    print(f"   🆔 IDs únicos en Tags: {unique_tags_ids:,}")
    
    # Verificar superposición
    common_ids = set(questions_df['Id']).intersection(set(tags_df['Id']))
    print(f"   📈 IDs comunes: {len(common_ids):,}")
    
    if len(common_ids) == 0:
        print("   ⚠️  ADVERTENCIA: No hay IDs comunes entre Questions y Tags")
    else:
        coverage = len(common_ids) / unique_questions_ids * 100
        print(f"   📊 Cobertura: {coverage:.1f}% de preguntas tienen tags")
    
    return questions_df, tags_df

def analizar_tags_por_pregunta(tags_df):
    """
    Analiza la distribución de tags por pregunta
    """
    print("\n🏷️ ANALIZANDO DISTRIBUCIÓN DE TAGS:")
    tags_per_question = tags_df.groupby('Id').size()
    
    print(f"   📊 Estadísticas de tags por pregunta:")
    print(f"     - Mínimo: {tags_per_question.min()}")
    print(f"     - Máximo: {tags_per_question.max()}")
    print(f"     - Promedio: {tags_per_question.mean():.1f}")
    print(f"     - Mediana: {tags_per_question.median()}")
    
    # Top tags más populares
    top_tags = tags_df['Tag'].value_counts().head(10)
    print(f"\n   🏆 TOP 10 TAGS MÁS POPULARES:")
    for tag, count in top_tags.items():
        print(f"     - {tag}: {count:,} ocurrencias")

def verificar_estructura_datos(questions_df, tags_df):
    """
    Verifica la estructura y calidad de los datos
    """
    print("\n🔍 VERIFICACIÓN DE ESTRUCTURA DE DATOS")
    print("=" * 40)
    
    # Questions analysis
    print("\n📋 QUESTIONS DATASET:")
    print(f"   Forma: {questions_df.shape}")
    print(f"   Columnas: {list(questions_df.columns)}")
    print(f"   Valores nulos por columna:")
    for col in questions_df.columns:
        nulos = questions_df[col].isnull().sum()
        if nulos > 0:
            print(f"     - {col}: {nulos} nulos ({nulos/questions_df.shape[0]*100:.1f}%)")
    
    # Tags analysis  
    print("\n🏷️ TAGS DATASET:")
    print(f"   Forma: {tags_df.shape}")
    print(f"   Columnas: {list(tags_df.columns)}")
    print(f"   Valores nulos por columna:")
    for col in tags_df.columns:
        nulos = tags_df[col].isnull().sum()
        if nulos > 0:
            print(f"     - {col}: {nulos} nulos ({nulos/tags_df.shape[0]*100:.1f}%)")
    
    # Análisis de tags por pregunta
    analizar_tags_por_pregunta(tags_df)

if  __name__ == "__main__":
    # Prueba de la función
    questions, tags = cargar_dataset_stack_overflow()
    if questions is not None and tags is not None:
        verificar_estructura_datos(questions, tags)