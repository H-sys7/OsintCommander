import subprocess
import shutil
import json
import os
from src.collectors.base import BaseCollector
from src.core.logger import logger

class HttpxCollector(BaseCollector):
    def run(self, target: str) -> list:
        # Note: target peut être un domaine (ex: tesla.com) OU un chemin de fichier (ex: subs.txt)
        logger.info(f"[Httpx] Vérification des serveurs Web actifs...")
        self.results = []

        executable = shutil.which("httpx")
        if not executable:
            # Fallback path classique pour Go sur Windows/WSL
            executable = os.path.expanduser("~/go/bin/httpx")
            if not os.path.exists(executable):
                return [{"error": "Httpx non trouvé (Installez Go)"}]

        # Construction de la commande
        cmd = [executable, "-json", "-silent", "-timeout", "10", "-tech-detect", "-status-code"]
        
        # Si 'target' est un fichier existant, on l'utilise comme liste
        if os.path.isfile(target):
            cmd.extend(["-l", target])
        else:
            cmd.extend(["-u", target])

        try:
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            for line in process.stdout.splitlines():
                if not line.strip(): continue
                try:
                    data = json.loads(line)
                    # On garde l'essentiel
                    entry = {
                        "source": "Httpx",
                        "type": "live_web",
                        "url": data.get("url"),
                        "status": data.get("status_code"),
                        "title": data.get("title"),
                        "tech": data.get("tech", [])
                    }
                    self.results.append(entry)
                except:
                    pass

            logger.info(f"[Httpx] {len(self.results)} sites web actifs trouvés.")

        except Exception as e:
            logger.error(f"[Httpx] Erreur : {e}")
            self.results.append({"error": str(e)})

        return self.results