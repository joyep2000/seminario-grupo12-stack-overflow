import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# Agregar el directorio scripts al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from data_loader import cargar_dataset_stack_overflow, verificar_estructura_datos
from data_cleaning import pipeline_limpieza_completa, preparar_datos_analitica_adaptada

class StackOverflowPipeline:
    def __init__(self, data_path="./data/raw"):
        self.data_path = data_path
        self.processed_path = "./data/processed"
        self.results = {}
    
    def load_data(self):
        """Carga los datasets usando data_loader.py"""
        print("📥 CARGANDO DATOS DESDE data_loader.py...")
        questions, tags = cargar_dataset_stack_overflow(self.data_path)
        
        if questions is None or tags is None:
            print("❌ Error: No se pudieron cargar los datos")
            return None, None
        
        # Verificar estructura
        verificar_estructura_datos(questions, tags)
        
        return questions, tags
    
    def clean_data(self, questions, tags):
        """Limpia los datos usando data_cleaning.py"""
        print("\n🧹 LIMPIANDO DATOS CON data_cleaning.py...")
        
        # Limpiar Questions
        questions_clean = pipeline_limpieza_completa(questions, "questions")
        if questions_clean is None:
            print("❌ Error limpiando Questions")
            return None, None
        
        # Limpiar Tags
        tags_clean = pipeline_limpieza_completa(tags, "tags")
        if tags_clean is None:
            print("❌ Error limpiando Tags")
            return None, None
        
        return questions_clean, tags_clean
    
    def merge_datasets(self, questions_clean, tags_clean):
        """Une los datasets limpios usando la función adaptada"""
        print("\n🔗 UNIENDO DATASETS...")
        
        # Usar la función adaptada directamente
        df_completo = preparar_datos_analitica_adaptada(questions_clean, tags_clean)
        
        if df_completo is None or df_completo.empty:
            print("❌ Error: No se pudo crear el dataset unido")
            return None
        
        # DEBUG: Mostrar columnas disponibles después del merge
        print(f"🔍 Columnas después del merge: {df_completo.columns.tolist()}")
        
        return df_completo
    
    def calculate_metrics(self, df_completo):
        """Calcula métricas clave para el análisis - VERSIÓN CORREGIDA"""
        print("\n📊 CALCULANDO MÉTRICAS DE ANÁLISIS...")
        
        try:
            # DEBUG: Verificar columnas disponibles
            print(f"🔍 Columnas disponibles: {df_completo.columns.tolist()}")
            
            # 1. Métricas por Tag - VERSIÓN CORREGIDA
            print("   Calculando métricas por tag...")
            
            # Verificar si tenemos tags_string para trabajar
            if 'tags_string' in df_completo.columns:
                print("   ℹ️  Procesando tags desde tags_string...")
                
                # Crear un dataset explotado donde cada tag individual sea una fila
                tags_exploded = []
                
                for idx, row in df_completo.iterrows():
                    if pd.notna(row['tags_string']) and row['tags_string'] != '':
                        tags_list = [tag.strip() for tag in row['tags_string'].split(',') if tag.strip()]
                        for tag in tags_list:
                            tags_exploded.append({
                                'tag': tag,
                                'id': row['id'],
                                'score': row.get('score', 0),
                                'creation_date': row.get('creation_date'),
                                'body_length': row.get('body_length', 0),
                                'line_count': row.get('line_count', 0),
                                'has_code': row.get('has_code', False)
                            })
                
                if tags_exploded:
                    df_tags_exploded = pd.DataFrame(tags_exploded)
                    print(f"   ✅ Dataset de tags explotado creado: {len(df_tags_exploded)} registros")
                    
                    # Calcular métricas por tag
                    aggregation_dict = {
                        'id': 'count',
                        'score': 'mean'
                    }
                    
                    # Agregar métricas adicionales si existen
                    if 'body_length' in df_tags_exploded.columns:
                        aggregation_dict['body_length'] = 'mean'
                    if 'line_count' in df_tags_exploded.columns:
                        aggregation_dict['line_count'] = 'mean'
                    if 'has_code' in df_tags_exploded.columns:
                        aggregation_dict['has_code'] = 'mean'
                    
                    tag_metrics = df_tags_exploded.groupby('tag').agg(aggregation_dict)
                    
                    # Renombrar columnas
                    new_column_names = {
                        'id': 'question_count',
                        'score': 'avg_score'
                    }
                    if 'body_length' in df_tags_exploded.columns:
                        new_column_names['body_length'] = 'avg_body_length'
                    if 'line_count' in df_tags_exploded.columns:
                        new_column_names['line_count'] = 'avg_line_count'
                    if 'has_code' in df_tags_exploded.columns:
                        new_column_names['has_code'] = 'code_ratio'
                    
                    tag_metrics = tag_metrics.rename(columns=new_column_names).round(2)
                    
                    # Filtrar tags con al menos 10 preguntas
                    tag_metrics = tag_metrics[tag_metrics['question_count'] >= 10]
                    print(f"   ✅ Métricas calculadas para {len(tag_metrics)} tags")
                else:
                    tag_metrics = pd.DataFrame()
                    print("   ⚠️  No hay tags para procesar")
            else:
                tag_metrics = pd.DataFrame()
                print("   ⚠️  No se encontró columna tags_string")
            
            # 2. Series temporales por Tag
            print("   Calculando series temporales...")
            time_series = pd.DataFrame()
            
            if 'tags_string' in df_completo.columns and 'creation_date' in df_completo.columns:
                try:
                    # Crear dataset para series temporales
                    time_series_data = []
                    
                    for idx, row in df_completo.iterrows():
                        if (pd.notna(row['tags_string']) and row['tags_string'] != '' and 
                            pd.notna(row['creation_date'])):
                            
                            tags_list = [tag.strip() for tag in row['tags_string'].split(',') if tag.strip()]
                            year = row['creation_date'].year
                            month = row['creation_date'].month
                            
                            for tag in tags_list:
                                time_series_data.append({
                                    'tag': tag,
                                    'year': year,
                                    'month': month,
                                    'date': pd.to_datetime(f"{year}-{month:02d}-01"),
                                    'count': 1
                                })
                    
                    if time_series_data:
                        time_series_df = pd.DataFrame(time_series_data)
                        # Agrupar por tag, año y mes
                        time_series = time_series_df.groupby(['tag', 'year', 'month', 'date']).agg({'count': 'sum'}).reset_index()
                        print(f"   ✅ Series temporales: {len(time_series)} registros")
                    else:
                        print("   ⚠️  No hay datos para series temporales")
                        
                except Exception as e:
                    print(f"   ⚠️  Error calculando series temporales: {e}")
                    time_series = pd.DataFrame()
            else:
                print("   ⚠️  No se pudo calcular series temporales (falta tags_string o creation_date)")
            
            # 3. Top Questions
            print("   Identificando preguntas más populares...")
            top_questions_columns = ['id', 'title', 'score', 'tags_string', 'creation_date', 'tags_count']
            available_columns = [col for col in top_questions_columns if col in df_completo.columns]
            
            if available_columns and 'score' in df_completo.columns:
                top_questions = df_completo.nlargest(100, 'score')[available_columns]
                # Remover duplicados si es necesario
                if 'id' in top_questions.columns:
                    top_questions = top_questions.drop_duplicates(subset=['id'])
                
                print(f"   ✅ Top {len(top_questions)} preguntas identificadas")
            else:
                top_questions = pd.DataFrame()
                print("   ⚠️  No se pudieron identificar preguntas top")
            
            # 4. Estadísticas generales
            general_stats = {
                'total_questions': df_completo['id'].nunique() if 'id' in df_completo.columns else 0,
                'total_unique_tags': len(tag_metrics) if not tag_metrics.empty else 0,
            }
            
            if 'score' in df_completo.columns:
                general_stats['avg_score'] = df_completo['score'].mean()
            if 'body_length' in df_completo.columns:
                general_stats['avg_body_length'] = df_completo['body_length'].mean()
            if 'tags_count' in df_completo.columns:
                general_stats['avg_tags_per_question'] = df_completo['tags_count'].mean()
            if 'creation_date' in df_completo.columns:
                general_stats['date_range'] = {
                    'min': df_completo['creation_date'].min(),
                    'max': df_completo['creation_date'].max()
                }
            
            # Calcular total de tags (suma de todos los tags_count)
            if 'tags_count' in df_completo.columns:
                general_stats['total_tags'] = df_completo['tags_count'].sum()
            else:
                general_stats['total_tags'] = 0
            
            return {
                'tag_metrics': tag_metrics,
                'time_series': time_series,
                'top_questions': top_questions,
                'general_stats': general_stats,
                'main_data': df_completo
            }
            
        except Exception as e:
            print(f"❌ Error calculando métricas: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_processed_data(self, results):
        """Guarda los datos procesados"""
        print("\n💾 GUARDANDO DATOS PROCESADOS...")
        
        try:
            # Crear directorio si no existe
            os.makedirs(self.processed_path, exist_ok=True)
            
            # Guardar datasets principales
            if not results['main_data'].empty:
                results['main_data'].to_parquet(
                    os.path.join(self.processed_path, 'stack_overflow_clean.parquet'),
                    index=False
                )
                print(f"   📁 stack_overflow_clean.parquet - {results['main_data'].shape}")
            
            if not results['tag_metrics'].empty:
                results['tag_metrics'].to_csv(
                    os.path.join(self.processed_path, 'tag_metrics.csv'),
                    index=True
                )
                print(f"   📁 tag_metrics.csv - {results['tag_metrics'].shape}")
            else:
                # Crear un archivo vacío para evitar errores
                pd.DataFrame().to_csv(os.path.join(self.processed_path, 'tag_metrics.csv'))
                print("   📁 tag_metrics.csv - (vacío)")
            
            if not results['time_series'].empty:
                results['time_series'].to_csv(
                    os.path.join(self.processed_path, 'time_series.csv'),
                    index=False
                )
                print(f"   📁 time_series.csv - {results['time_series'].shape}")
            else:
                # Crear un archivo vacío para evitar errores
                pd.DataFrame().to_csv(os.path.join(self.processed_path, 'time_series.csv'))
                print("   📁 time_series.csv - (vacío)")
            
            if not results['top_questions'].empty:
                results['top_questions'].to_csv(
                    os.path.join(self.processed_path, 'top_questions.csv'),
                    index=False
                )
                print(f"   📁 top_questions.csv - {results['top_questions'].shape}")
            else:
                # Crear un archivo vacío para evitar errores
                pd.DataFrame().to_csv(os.path.join(self.processed_path, 'top_questions.csv'))
                print("   📁 top_questions.csv - (vacío)")
            
            # Guardar estadísticas generales
            stats_df = pd.DataFrame([results['general_stats']])
            stats_df.to_csv(
                os.path.join(self.processed_path, 'general_stats.csv'),
                index=False
            )
            print(f"   📁 general_stats.csv")
            
            print("✅ DATOS GUARDADOS EXITOSAMENTE")
            
            return True
            
        except Exception as e:
            print(f"❌ Error guardando datos: {e}")
            return False
    
    def generate_report(self, results):
        """Genera un reporte del pipeline"""
        print("\n📈 REPORTE FINAL DEL PIPELINE")
        print("=" * 50)
        
        stats = results['general_stats']
        print(f"📊 ESTADÍSTICAS GENERALES:")
        print(f"   • Total preguntas procesadas: {stats.get('total_questions', 0):,}")
        print(f"   • Total tags únicos: {stats.get('total_unique_tags', 0):,}")
        print(f"   • Total tags asignados: {stats.get('total_tags', 0):,}")
        
        if 'avg_score' in stats:
            print(f"   • Score promedio: {stats['avg_score']:.2f}")
        if 'avg_tags_per_question' in stats:
            print(f"   • Tags promedio por pregunta: {stats['avg_tags_per_question']:.1f}")
        if 'avg_body_length' in stats:
            print(f"   • Longitud promedio del cuerpo: {stats['avg_body_length']:.0f} caracteres")
        
        if 'date_range' in stats and stats['date_range']['min']:
            min_date = stats['date_range']['min']
            max_date = stats['date_range']['max']
            if hasattr(min_date, 'strftime'):
                print(f"   • Rango de fechas: {min_date.strftime('%Y-%m')} a {max_date.strftime('%Y-%m')}")
        
        print(f"\n📁 DATASETS GENERADOS:")
        print(f"   • Tag Metrics: {results['tag_metrics'].shape[0]:,} tags")
        print(f"   • Time Series: {results['time_series'].shape[0]:,} registros temporales")
        print(f"   • Top Questions: {results['top_questions'].shape[0]:,} preguntas")
        
        # Top 5 tags si existen
        if not results['tag_metrics'].empty:
            top_tags = results['tag_metrics'].nlargest(5, 'question_count')
            print(f"\n🏆 TOP 5 TAGS MÁS POPULARES:")
            for i, (tag, row) in enumerate(top_tags.iterrows(), 1):
                print(f"   {i}. {tag}: {int(row['question_count']):,} preguntas")
    
    def run_pipeline(self):
        """Ejecuta todo el pipeline"""
        print("🚀 INICIANDO PIPELINE COMPLETO DE STACK OVERFLOW")
        print("=" * 60)
        
        # Paso 1: Cargar datos
        questions, tags = self.load_data()
        if questions is None or tags is None:
            return None
        
        # Paso 2: Limpiar datos
        questions_clean, tags_clean = self.clean_data(questions, tags)
        if questions_clean is None or tags_clean is None:
            return None
        
        # Paso 3: Unir datasets
        df_completo = self.merge_datasets(questions_clean, tags_clean)
        if df_completo is None:
            return None
        
        # Paso 4: Calcular métricas
        results = self.calculate_metrics(df_completo)
        if results is None:
            return None
        
        # Paso 5: Guardar datos
        success = self.save_processed_data(results)
        if not success:
            return None
        
        # Paso 6: Generar reporte
        self.generate_report(results)
        
        print("\n🎉 PIPELINE COMPLETADO EXITOSAMENTE!")
        print(f"📂 Datos disponibles en: {self.processed_path}")
        
        self.results = results
        return results

# Función para ejecución directa
if __name__ == "__main__":
    pipeline = StackOverflowPipeline()
    results = pipeline.run_pipeline()
    
    if results:
        print("\n✅ El pipeline se ejecutó correctamente!")
    else:
        print("\n❌ El pipeline encontró errores")