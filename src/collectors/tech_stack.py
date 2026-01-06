import builtwith
from src.collectors.base import BaseCollector
from src.core.logger import logger

class TechStackCollector(BaseCollector):
    def run(self, target: str) -> list:
        # Assurer qu'il y a le protocole
        if not target.startswith("http"):
            url = f"https://{target}"
        else:
            url = target
            
        logger.info(f"[TechStack] Identification des technologies sur {url}")
        self.results = []

        try:
            # builtwith retourne un dictionnaire { 'web-servers': ['Nginx'], ... }
            info = builtwith.parse(url)
            
            flat_techs = []
            for category, techs in info.items():
                for t in techs:
                    flat_techs.append(f"{t} ({category})")
                    
            if flat_techs:
                self.results.append({
                    "source": "BuiltWith",
                    "type": "technology",
                    "count": len(flat_techs),
                    "data": flat_techs
                })
                logger.info(f"[TechStack] {len(flat_techs)} technos identifiées.")
            else:
                self.results.append({"error": "Aucune techno identifiée."})

        except Exception as e:
            logger.error(f"[TechStack] Erreur : {e}")
            self.results.append({"error": str(e)})

        return self.results