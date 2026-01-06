from censys.search import CensysHosts
from src.config.settings import settings
from src.collectors.base import BaseCollector
from src.core.logger import logger

class CensysCollector(BaseCollector):
    def run(self, target: str) -> list:
        logger.info(f"[Censys] Recherche d'infos pour l'IP : {target}...")
        self.results = []

        # 1. Vérification des Clés (Indispensable pour Censys)
        if not settings.CENSYS_API_ID or not settings.CENSYS_API_SECRET:
            logger.warning("[Censys] Clés API manquantes. Le scan est ignoré.")
            return [{"error": "Clés API Censys non configurées dans le .env"}]

        try:
            # 2. Connexion Officielle à Censys
            c = CensysHosts(api_id=settings.CENSYS_API_ID, api_secret=settings.CENSYS_API_SECRET)
            
            # 3. Récupération des données (On utilise 'target' ici)
            host = c.view(target)
            
            if not host:
                logger.info("[Censys] Aucune donnée trouvée pour cette IP.")
                return []

            # 4. Extraction des Ports et Services
            extracted_data = {
                "ip": target, # La clé reste 'ip' pour la clarté, la valeur est 'target'
                "services": [],
                "location": host.get("location", {}).get("country", "Unknown"),
                "asn": host.get("autonomous_system", {}).get("name", "Unknown")
            }

            for service in host.get("services", []):
                port = service.get("port")
                protocol = service.get("service_name") or service.get("transport_protocol")
                extracted_data["services"].append(f"{port}/{protocol}")

            self.results.append({
                "source": "Censys",
                "type": "related_ips",
                "value": target, # Ici aussi
                "data": [target],
                "details": extracted_data
            })
            
            logger.info(f"[Censys] Succès : {len(extracted_data['services'])} services identifiés.")

        except Exception as e:
            # Gestion précise des erreurs
            error_msg = str(e)
            if "403" in error_msg: error_msg = "Accès refusé (Vérifie tes clés API Censys dans le .env)"
            if "404" in error_msg: error_msg = "IP inconnue de Censys ou format invalide"
            
            logger.error(f"[Censys] Erreur : {error_msg}")
            self.results.append({"error": f"Censys échec: {error_msg}"})

        return self.results