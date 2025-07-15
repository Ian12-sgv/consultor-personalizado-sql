from utils.db_utils import set_instance_by_selection, get_db_connection
from sqlalchemy import text

def probar_conexion():
    """
    Prueba de conexión a la base de datos y lista las bases disponibles.
    """
    try:
        if not set_instance_by_selection():
            print("No se seleccionó ninguna instancia.")
            return
        
        engine = get_db_connection()
        
        if engine is None:
            print("No se pudo obtener el engine.")
            return
        
        with engine.connect() as conn:
            # Mostrar a qué base se conectó realmente
            current_db = conn.execute(text("SELECT DB_NAME()")).fetchone()[0]
            print(f"\n✅ Conexión exitosa a la base de datos '{current_db}'.")

            # Listar bases de datos activas (solo como referencia)
            query = text("SELECT name FROM sys.databases WHERE state_desc = 'ONLINE'")
            result = conn.execute(query)

            print("\n📂 Bases de datos disponibles en la instancia:")
            for row in result:
                print(f"- {row[0]}")   # Mostrar los nombres de las bases

    except Exception as e:
        print(f"\n❌ Error al conectar: {e}")

if __name__ == "__main__":
    print("Prueba de conexión seleccionando instancia y base de datos:\n")
    probar_conexion()
