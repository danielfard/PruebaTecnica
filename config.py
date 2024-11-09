from dotenv import load_dotenv
import os

class ConfigLoader:
    def __init__(self, env_file_path=".env"):
        # Cargar las variables del archivo .env
        load_dotenv(env_file_path)
        
        # Inicializar variables
        self.COLLECTOR_ID = os.getenv("COLLECTOR_ID")
        self.LUMU_CLIENT_KEY = os.getenv("LUMU_CLIENT_KEY")

    def get_collector_id(self):
        return self.COLLECTOR_ID

    def get_lumu_client_key(self):
        return self.LUMU_CLIENT_KEY
