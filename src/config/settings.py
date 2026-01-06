import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Charge le fichier .env s'il existe
load_dotenv()

class Settings(BaseSettings):
    # Définition des variables attendues
    APP_NAME: str = "OsintAI Tool"
    VERSION: str = "1.0.0"
    
    # Clés API (Optionnelles au début, mais nécessaires pour les modules spécifiques)
    # Elles seront lues depuis le fichier .env ou les variables système
    CRIMINALIP_API_KEY: str = os.getenv("CRIMINALIP_API_KEY", "")
    OPENAI_API_KEY: str = ""
    METAGOOFIL_PATH: str = os.getenv("METAGOOFIL_PATH", "metagoofil")
    THEHARVESTER_PATH: str = os.getenv("THEHARVESTER_PATH", "theHarvester")
    
    # Groq
    # Si il ne trouve rien, ALORS il met "" par défaut.
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "groq")

    # HaveIBeenPawned
    HIBP_API_KEY: str = os.getenv("HIBP_API_KEY", "") # Clé HaveIBeenPwned (Optionnelle mais recommandée)

    #Censys
    CENSYS_API_ID: str = os.getenv("CENSYS_API_ID", "")
    CENSYS_API_SECRET: str = os.getenv("CENSYS_API_SECRET", "")

    class Config:
        # Permet de lire le fichier .env automatiquement aussi
        env_file = ".env"
        env_file_encoding = "utf-8"

    

# Création d'une instance unique (Singleton)
settings = Settings()

# Petit test rapide si exécuté directement
if __name__ == "__main__":
    print(f"Chargement de la configuration pour {settings.APP_NAME}")
    if settings.CRIMINALIP_API_KEY:
        print("✅ Clé CriminalIP détectée")
    else:
        print("⚠️ Aucune clé CriminalIP trouvée dans le .env")