import subprocess
import json
import os
import sys
import glob
from src.collectors.base import BaseCollector
from src.core.logger import logger

class MaigretCollector(BaseCollector):
    def run(self, target: str) -> list:
        clean_username = target.replace(" ", "")
        logger.info(f"[Maigret] Recherche précise du pseudo : {clean_username}...")
        self.results = []

        try:
            import maigret
        except ImportError:
            return [{"error": "Maigret non installé"}]

        # Nettoyage vieux fichiers
        for f in glob.glob(f"report_{clean_username}*.json"):
            try: os.remove(f)
            except: pass

        cmd = [
            sys.executable, "-m", "maigret",
            clean_username,
            "--json", "simple",
            "--folderoutput", ".",
            "--timeout", "20",
            "--retries", "0",
            "--no-progressbar"
        ]

        try:
            logger.info(f"[Maigret] Exécution en cours...")
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=200)

            # Recherche du fichier
            json_files = glob.glob(f"report_{clean_username}*.json")
            
            if json_files:
                latest_file = json_files[0]
                
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                found_accounts = []
                
                # Parsing Intelligent (Récupère Site + Tags)
                # Structure attendue : {"Twitter": {"url": "...", "tags": [...]}, ...}
                
                # Si c'est un dictionnaire, les clés sont les noms des sites
                if isinstance(data, dict):
                    # On ignore les clés "metadata" ou autre, on veut les sites
                    if "sites" in data: # Format ancien
                        sites_dict = data["sites"]
                    else: # Format récent (Racine)
                        sites_dict = data

                    for site_name, site_info in sites_dict.items():
                        if not isinstance(site_info, dict): continue
                        
                        url = site_info.get("url_user") or site_info.get("url_main") or site_info.get("url")
                        tags = site_info.get("tags", [])
                        
                        # On filtre les faux positifs courants
                        if url and "{" not in url:
                            found_accounts.append({
                                "site": site_name,
                                "url": url,
                                "tags": ", ".join(tags) if tags else "General"
                            })

                # Si c'est une liste (rare maintenant), on fait au mieux
                elif isinstance(data, list):
                    for item in data:
                        url = item.get("url_user") or item.get("url")
                        if url:
                            found_accounts.append({
                                "site": "Unknown",
                                "url": url,
                                "tags": "Unknown"
                            })

                if found_accounts:
                    self.results.append({
                        "source": "Maigret",
                        "type": "social_account",
                        "count": len(found_accounts),
                        "data": found_accounts # On passe la liste d'objets riches
                    })
                    logger.info(f"[Maigret] Succès : {len(found_accounts)} comptes identifiés.")
                else:
                    logger.info(f"[Maigret] Aucun compte valide trouvé.")
                
                try: os.remove(latest_file)
                except: pass

            else:
                logger.warning("[Maigret] Fichier JSON introuvable.")
        
        except Exception as e:
            logger.error(f"[Maigret] Erreur : {e}")
            self.results.append({"error": str(e)})

        return self.results