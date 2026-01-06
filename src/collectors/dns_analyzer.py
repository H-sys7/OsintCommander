import socket
from src.collectors.base import BaseCollector
from src.core.logger import logger

class DnsCollector(BaseCollector):
    def run(self, target: str) -> list:
        logger.info(f"[DNS] Démarrage de la résolution pour : {target}")
        self.results = []
        
        try:
            # Nettoyage basique (enlever http:// si l'utilisateur l'a mis)
            clean_target = target.replace("https://", "").replace("http://", "").split("/")[0]
            
            # Récupération de l'IP
            ip_address = socket.gethostbyname(clean_target)
            
            # On structure la donnée (simulation de normalisation)
            data = {
                "type": "ip_address",
                "value": ip_address,
                "source": "DnsModule",
                "details": f"IP principale pour {clean_target}"
            }
            self.results.append(data)
            logger.info(f"[DNS] Trouvé : {ip_address}")
            
        except socket.gaierror:
            logger.error(f"[DNS] Impossible de résoudre le domaine {target}")
            self.results.append({"error": "Domaine introuvable"})
            
        except Exception as e:
            logger.error(f"[DNS] Erreur inattendue : {e}")

        return self.results