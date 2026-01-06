import subprocess
import shutil
import sys
import json
from src.collectors.base import BaseCollector
from src.core.logger import logger

class HoleheCollector(BaseCollector):
    def run(self, target: str) -> list:
        logger.info(f"[Holehe] Analyse de l'email : {target}")
        self.results = []

        # Holehe n'a pas de sortie JSON native facile via CLI, 
        # on va l'utiliser comme module python ou parser sa sortie.
        # Le plus simple et stable est d'appeler la commande holehe.
        
        cmd = [sys.executable, "-m", "holehe", target, "--only-used", "--no-color"]
        
        try:
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Holehe affiche : "[+] Twitter" ou "[-] Instagram"
            # On cherche les lignes avec "[+]"
            found_sites = []
            
            for line in process.stdout.splitlines():
                if "[+]" in line:
                    # Exemple: "[+] Twitter" -> "Twitter"
                    site = line.split("]")[1].strip()
                    found_sites.append(site)
            
            if found_sites:
                self.results.append({
                    "source": "Holehe",
                    "type": "registered_account",
                    "count": len(found_sites),
                    "data": found_sites
                })
                logger.info(f"[Holehe] Email utilisé sur : {', '.join(found_sites)}")
            else:
                logger.info("[Holehe] Email non trouvé sur les sites testés.")

        except Exception as e:
            logger.error(f"[Holehe] Erreur : {e}")
            self.results.append({"error": str(e)})

        return self.results