import subprocess
import sys
import time
import webbrowser

def main():
    """Script específico para ejecutar solo la API"""
    print("🚀 EJECUTANDO API STACK OVERFLOW...")
    print("=" * 40)
    
    try:
        # Comando corregido
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "src.api.main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ])
        
        print("⏳ Iniciando API...")
        time.sleep(5)
        
        print("✅ API ejecutándose en:")
        print("   🌐 http://localhost:8000")
        print("   📚 http://localhost:8000/docs")
        print("   🔧 http://localhost:8000/health")
        
        # Abrir automáticamente
        webbrowser.open("http://localhost:8000/docs")
        
        print("\n🛑 Presiona Ctrl+C para detener la API")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo API...")
            process.terminate()
            print("✅ API detenida")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()