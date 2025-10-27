
import pandas as pd
import os

# ruta absoluta de la carpeta donde esta el script(.../scripts/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# construir la ruta del archivo csv de data
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "data", "tags.csv")

# crear funcion
def cargar_datos(path):
    print(f"Cargando datos desde {path}...")
    
    try:
        df = pd.read_csv(path, encoding = "latin1")
        print("Datos han sido cargados!!!")
        return df
    except FileNotFoundError:
        print(f"Error: El archivo {path} no existe.")
        print("Asegurate de tener el archivo en la carpeta 'data'.")
        return None
    except Exception as e:
        print(f"Ocurrio un error inesperado {e}")
        return None
    
# este archivo se esta ejecutando directamente por el usuario o esta siendo importado por otro script?
if __name__ == "__main__":
    # indica donde esta el script actual
    print(f"Ejecutando script desde: {os.path.abspath(__file__)}")
    
    # llama a la funcion de arriba para cargar el csv
    dataframe_quiestions = cargar_datos(DATA_PATH)
    
    if dataframe_quiestions is not None:
        print("\n---Primeras 5 filas ---")
        print(dataframe_quiestions.head())
        
        print("\n---Informacino del Dataframe---")
        dataframe_quiestions.info(show_counts=True)