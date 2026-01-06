from googlesearch import search
from src.collectors.base import BaseCollector
from src.core.logger import logger
import time
import random

class CareerCollector(BaseCollector):
    def run(self, target: str) -> list:
        # identity peut être "Prénom Nom" ou un pseudo
        logger.info(f"[Career] Recherche de traces professionnelles pour : {target}")
        self.results = []
        
        # Liste des requêtes ciblées (Dorks)
        queries = [
            f'site:linkedin.com/in/ "{target}"',           # Profils LinkedIn précis
            f'site:viadeo.com "{target}"',                # Viadeo
            f'site:xing.com "{target}"',                  # Xing (Europe)
            f'site:github.com "{target}"',                # Codeurs
            f'site:stackoverflow.com/users/ "{target}"',  # Développeurs
            f'filetype:pdf "{target}" CV OR "Curriculum Vitae"', # CVs publics
            f'inurl:resume "{target}"'                    # Resumes en ligne
        ]

        found_links = []

        try:
            for q in queries:
                # Pause aléatoire pour ne pas énerver Google
                time.sleep(random.uniform(2, 4))
                
                # On récupère max 3 résultats par dork
                for url in search(q, num_results=3, sleep_interval=2):
                    
                    # On nettoie un peu les résultats
                    url_str = str(url)
                    if "google.com" in url_str: continue
                    
                    # Identification de la source
                    source_site = "Web"
                    if "linkedin" in url_str: source_site = "LinkedIn"
                    elif "github" in url_str: source_site = "GitHub"
                    elif "pdf" in url_str: source_site = "Document PDF (CV ?)"

                    found_links.append({
                        "url": url,
                        "site": source_site
                    })
                    logger.debug(f"[Career] Trouvé : {url}")

            if found_links:
                self.results.append({
                    "source": "CareerHunter",
                    "type": "professional_trace",
                    "count": len(found_links),
                    "data": found_links
                })
                logger.info(f"[Career] {len(found_links)} profils/documents professionnels trouvés.")
            else:
                logger.info("[Career] Rien de probant trouvé (Profil discret).")

        except Exception as e:
            logger.error(f"[Career] Erreur (Google Block ?) : {e}")
            self.results.append({"error": "Google Dorks limités/bloqués."})

        return self.results