import requests
from src.collectors.base import BaseCollector
from src.config.settings import settings
from src.core.logger import logger

class CriminalIpCollector(BaseCollector):
    def run(self, target: str) -> list:
        # Note: CriminalIP travaille souvent sur des IP, pas des domaines directement.
        # Si l'entrée est un domaine, on devrait idéalement résoudre l'IP avant.
        # Pour cet exemple, on suppose que target est une IP (ex: celle trouvée par le module DNS).
        
        logger.info(f"[CriminalIP] Analyse de l'actif : {target}")
        self.results = []

        if not settings.CRIMINALIP_API_KEY:
            logger.warning("[CriminalIP] Clé API manquante. Passage.")
            return [{"error": "Clé API CriminalIP non configurée dans .env"}]

        headers = {
            "x-api-key": settings.CRIMINALIP_API_KEY
        }

        try:
            # Endpoint "Asset Search" pour voir les ports ouverts
            url = "https://api.criminalip.io/v1/asset/ip/report/summary"
            params = {"ip": target}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extraction des données intéressantes (Normalisation simplifiée)
                open_ports = []
                if "port" in data and "data" in data["port"]:
                    for p in data["port"]["data"]:
                        open_ports.append(str(p.get("port", "Inconnu")))

                vulnerability_score = data.get("score", {}).get("total_score", "Inconnu")

                result_obj = {
                    "source": "CriminalIP",
                    "type": "infrastructure_report",
                    "ip": target,
                    "open_ports": open_ports,
                    "risk_score": vulnerability_score,
                    "raw": data  # On garde tout au cas où l'IA en veut plus
                }
                
                self.results.append(result_obj)
                logger.info(f"[CriminalIP] Succès. Score de risque : {vulnerability_score}")

            elif response.status_code == 403:
                self.results.append({"error": "Accès refusé (Clé API invalide ?)"})
            else:
                self.results.append({"error": f"Erreur API: {response.status_code}"})

        except Exception as e:
            logger.error(f"[CriminalIP] Crash : {e}")
            self.results.append({"error": str(e)})

        return self.results