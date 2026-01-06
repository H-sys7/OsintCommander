import whois
from src.collectors.base import BaseCollector
from src.core.logger import logger

class WhoisCollector(BaseCollector):
    def run(self, target: str) -> list:
        logger.info(f"[Whois] Récupération des infos pour {target}...")
        self.results = []
        
        try:
            w = whois.whois(target)
            
            # Conversion des dates en string pour éviter les erreurs JSON
            def format_date(d):
                if isinstance(d, list): return [str(x) for x in d]
                return str(d) if d else None

            data = {
                "domain_name": w.get("domain_name"),
                "registrar": w.get("registrar"),
                "creation_date": format_date(w.get("creation_date")),
                "expiration_date": format_date(w.get("expiration_date")),
                "emails": w.get("emails"),
                "country": w.get("country"),
                "org": w.get("org")
            }
            
            self.results.append(data)
            logger.info(f"[Whois] Succès : {w.get('registrar')}")
        except Exception as e:
            logger.error(f"[Whois] Erreur : {e}")
            self.results.append({"error": str(e)})

        return self.results