from googlesearch import search
from src.collectors.base import BaseCollector
from src.core.logger import logger
import time

class GoogleDocsCollector(BaseCollector):
    def run(self, target: str) -> list:
        logger.info(f"[GoogleDocs] Recherche de fichiers sensibles sur : {target}")
        self.results = []
        
        # Types de fichiers à chasser
        extensions = ["pdf", "xlsx", "docx", "pptx"]
        
        found_count = 0

        try:
            for ext in extensions:
                # La requête magique : site:tesla.com filetype:pdf
                query = f"site:{target} filetype:{ext}"
                
                # On récupère max 5 résultats par extension pour aller vite
                # pause=2 est important pour ne pas se faire bannir par Google
                for url in search(query, num_results=5, sleep_interval=2):
                    self.results.append({
                        "source": "GoogleDorks",
                        "type": "public_file",
                        "value": url,
                        "details": {"extension": ext, "desc": "Fichier public indexé"}
                    })
                    found_count += 1
                    logger.debug(f"[GoogleDocs] Trouvé : {url}")

            logger.info(f"[GoogleDocs] Terminé. {found_count} fichiers trouvés.")

        except Exception as e:
            logger.error(f"[GoogleDocs] Erreur (Probable blocage Google 429) : {e}")
            self.results.append({"error": "Google a bloqué les requêtes (Trop rapide)."})

        return self.results