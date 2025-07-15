# utils/db_utils.py

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

class ConnectionManager:
    def __init__(self):
        self.engine = None
        self.instance = None
        self.user = None
        self.password = None
        self.databases = []
        self.db_selected = None

    def listar_bases(self, instancia, usuario, password):
        """
        Conecta a la instancia y lista las bases de datos disponibles.
        """
        try:
            conn_str = f"mssql+pyodbc://{usuario}:{quote_plus(password)}@{instancia}/master?driver=SQL+Server"
            engine = create_engine(conn_str)

            with engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM sys.databases WHERE state_desc = 'ONLINE'"))
                self.databases = [row[0] for row in result]

            # Guardamos los datos para conectar después a la base específica
            self.engine = engine
            self.instance = instancia
            self.user = usuario
            self.password = password

            return True, self.databases

        except Exception as e:
            print(f"Error al listar bases: {e}")
            return False, []

    def conectar_base(self, base):
        """
        Conecta a una base específica.
        """
        try:
            conn_str = f"mssql+pyodbc://{self.user}:{quote_plus(self.password)}@{self.instance}/{base}?driver=SQL+Server"
            self.engine = create_engine(conn_str)
            self.db_selected = base
            return True
        except Exception as e:
            print(f"Error al conectar base: {e}")
            return False
