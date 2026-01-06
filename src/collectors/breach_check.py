import requests
import time
from src.collectors.base import BaseCollector
from src.config.settings import settings
from src.core.logger import logger

class BreachCollector(BaseCollector):
    def run(self, target: str) -> list:
        logger.info(f"[HIBP] Recherche de fuites de données pour : {target}")
        self.results = []

        if not settings.HIBP_API_KEY:
            logger.warning("[HIBP] Pas de clé API configurée. Le scan de fuites est désactivé.")
            self.results.append({"warning": "Clé API HIBP manquante. Impossible de vérifier les mots de passe fuités."})
            return self.results

        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{target}?truncateResponse=false"
        headers = {
            "hibp-api-key": settings.HIBP_API_KEY,
            "user-agent": "OsintTool-Python"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                breaches = response.json()
                breach_list = []
                for b in breaches:
                    breach_list.append(f"{b['Name']} ({b['BreachDate']})")
                
                self.results.append({
                    "source": "HaveIBeenPwned",
                    "type": "data_breach",
                    "count": len(breach_list),
                    "data": breach_list,
                    "metadata": {"risk": "HIGH" if len(breach_list) > 5 else "MEDIUM"}
                })
                logger.info(f"[HIBP] ⚠️ {len(breach_list)} fuites détectées !")

            elif response.status_code == 404:
                logger.info("[HIBP] Bonne nouvelle : Aucune fuite connue pour cet email.")
                self.results.append({
                    "source": "HaveIBeenPwned",
                    "type": "data_breach",
                    "count": 0,
                    "data": [],
                    "metadata": {"status": "Clean"}
                })

            elif response.status_code == 401:
                logger.error("[HIBP] Clé API invalide ou non autorisée.")
                self.results.append({"error": "Clé API HIBP invalide."})
            
            elif response.status_code == 429:
                logger.error("[HIBP] Trop de requêtes (Rate Limit).")
                self.results.append({"error": "Rate Limit HIBP atteint."})

        except Exception as e:
            logger.error(f"[HIBP] Erreur : {e}")
            self.results.append({"error": str(e)})

        return self.results