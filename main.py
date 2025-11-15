import os
import subprocess
import sys
import webbrowser
import time
import threading
from src.data_pipeline import StackOverflowPipeline

def print_banner():
    """Imprime el banner del sistema"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║         🎮 SISTEMA DE ANÁLISIS STACK OVERFLOW               ║
    ║                     GRUPO 12 - SEMINARIO                     ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def ensure_directories():
    """Asegura que los directorios necesarios existan"""
    directories = [
        'data/raw',
        'data/processed', 
        'src/api',
        'src/dashboard',
        'src/utils'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ Directorios verificados")

def run_pipeline():
    """Ejecuta el pipeline de datos"""
    print("\n🚀 EJECUTANDO PIPELINE DE DATOS...")
    print("=" * 50)
    
    try:
        pipeline = StackOverflowPipeline()
        results = pipeline.run_pipeline()
        
        if results:
            print("\n✅ PIPELINE COMPLETADO EXITOSAMENTE!")
            return True
        else:
            print("\n❌ EL PIPELINE ENCONTRÓ ERRORES")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando pipeline: {e}")
        return False

def run_api_server():
    """Ejecuta el servidor de la API correctamente"""
    print("\n🌐 INICIANDO API FASTAPI...")
    try:
        # Comando corregido para la API
        api_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "src.api.main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ])
        
        print("⏳ Esperando a que la API inicie...")
        time.sleep(5)
        
        print("✅ API ejecutándose correctamente en:")
        print("   📚 Documentación: http://localhost:8000/docs")
        print("   🏠 Página principal: http://localhost:8000")
        print("   🔧 Health check: http://localhost:8000/health")
        
        # Abrir navegador automáticamente
        webbrowser.open("http://localhost:8000/docs")
        
        return api_process
        
    except Exception as e:
        print(f"❌ Error iniciando API: {e}")
        return None

def run_dashboard_server():
    """Ejecuta el dashboard de Streamlit"""
    print("\n📊 INICIANDO DASHBOARD STREAMLIT...")
    try:
        dashboard_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "src/dashboard/app.py",
            "--server.port", "8501", "--server.address", "localhost"
        ])
        
        time.sleep(8)
        
        print("✅ Dashboard ejecutándose en: http://localhost:8501")
        webbrowser.open("http://localhost:8501")
        
        return dashboard_process
        
    except Exception as e:
        print(f"❌ Error iniciando Dashboard: {e}")
        return None

def check_system_health():
    """Verifica la salud del sistema"""
    print("\n🔍 VERIFICANDO SALUD DEL SISTEMA...")
    
    required_files = [
        'data/raw/Questions.csv',
        'data/raw/Tags.csv',
        'src/api/main.py',
        'src/dashboard/app.py',
        'src/data_pipeline.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Archivos faltantes:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ Todos los archivos necesarios están presentes")
        return True

def monitor_services(api_process, dashboard_process):
    """Monitorea los servicios en ejecución"""
    print("\n📡 SERVICIOS EN EJECUCIÓN:")
    print("   🌐 API: http://localhost:8000/docs")
    print("   📊 Dashboard: http://localhost:8501")
    print("\n🛑 Presiona Ctrl+C para detener todos los servicios")
    
    try:
        while True:
            # Verificar si los procesos están activos
            api_alive = api_process.poll() is None if api_process else False
            dashboard_alive = dashboard_process.poll() is None if dashboard_process else False
            
            if not api_alive and not dashboard_alive:
                print("❌ Todos los servicios se detuvieron")
                break
            elif not api_alive:
                print("❌ API se detuvo inesperadamente")
            elif not dashboard_alive:
                print("❌ Dashboard se detuvo inesperadamente")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n🛑 DETENIENDO SERVICIOS...")
        
        # Terminar procesos
        if api_process:
            api_process.terminate()
        if dashboard_process:
            dashboard_process.terminate()
        
        time.sleep(2)
        print("✅ Servicios detenidos correctamente")

def run_api_only():
    """Ejecuta solo la API"""
    api_process = run_api_server()
    if api_process:
        input("\n🌐 API ejecutándose. Presiona Enter para detenerla...")
        api_process.terminate()
        print("✅ API detenida")

def run_dashboard_only():
    """Ejecuta solo el Dashboard"""
    dashboard_process = run_dashboard_server()
    if dashboard_process:
        input("\n📊 Dashboard ejecutándose. Presiona Enter para detenerlo...")
        dashboard_process.terminate()
        print("✅ Dashboard detenido")

def run_complete_system():
    """Ejecuta el sistema completo"""
    print("\n🔄 INICIANDO SISTEMA COMPLETO...")
    
    # Paso 1: Pipeline (opcional, preguntar al usuario)
    run_pipeline_option = input("\n¿Ejecutar pipeline de datos? (s/n): ").strip().lower()
    if run_pipeline_option == 's':
        if not run_pipeline():
            print("❌ No se puede continuar sin datos procesados")
            return
    
    # Paso 2: Iniciar servicios
    api_process = run_api_server()
    dashboard_process = run_dashboard_server()
    
    if api_process and dashboard_process:
        print("\n🎉 SISTEMA COMPLETO EN EJECUCIÓN!")
        monitor_services(api_process, dashboard_process)
    else:
        print("❌ Error iniciando algunos servicios")
        # Limpiar procesos si alguno falló
        if api_process:
            api_process.terminate()
        if dashboard_process:
            dashboard_process.terminate()

def main():
    """Función principal del sistema CORREGIDA"""
    print_banner()
    
    # Verificar salud del sistema
    if not check_system_health():
        print("\n❌ El sistema no está listo. Por favor verifica los archivos faltantes.")
        return
    
    # Asegurar directorios
    ensure_directories()
    
    while True:
        print("\n📋 MENU PRINCIPAL CORREGIDO:")
        print("1. Ejecutar Pipeline de Datos (ETL)")
        print("2. Iniciar API FastAPI")
        print("3. Iniciar Dashboard Streamlit")
        print("4. Ejecutar Sistema Completo")
        print("5. Verificar Estado del Sistema")
        print("6. Salir")
        
        choice = input("\nSelecciona una opción (1-6): ").strip()
        
        if choice == "1":
            success = run_pipeline()
            if success:
                input("\n✅ Pipeline completado. Presiona Enter para continuar...")
            else:
                input("\n❌ Pipeline falló. Presiona Enter para continuar...")
                
        elif choice == "2":
            run_api_only()
                
        elif choice == "3":
            run_dashboard_only()
                
        elif choice == "4":
            run_complete_system()
                
        elif choice == "5":
            check_system_health()
            input("\nPresiona Enter para continuar...")
            
        elif choice == "6":
            print("\n👋 ¡Hasta luego! Gracias por usar el sistema.")
            break
            
        else:
            print("❌ Opción inválida. Por favor selecciona 1-6.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario. ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")