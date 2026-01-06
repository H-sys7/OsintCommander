import subprocess
import shutil
import os
from src.collectors.base import BaseCollector
from src.core.logger import logger

class SubfinderCollector(BaseCollector):
    output_file = "temp_subs_gui.txt"
    def run(self, target: str) -> list:
        logger.info(f"[Subfinder] Énumération des sous-domaines pour : {target}")
        self.results = []

        # On cherche l'exécutable (souvent dans ~/go/bin sous WSL)
        executable = shutil.which("subfinder")
        # Fallback manuel si pas dans le path
        if not executable:
            home = os.path.expanduser("~")
            executable = f"{home}/go/bin/subfinder"
            if not os.path.exists(executable):
                 return [{"error": "Subfinder non trouvé. Installez Go et Subfinder."}]

        cmd = [executable, "-d", target, "-silent", "-json", "-o", self.output_file]

        try:
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            
            # Subfinder renvoie un JSON par ligne (JSON Lines)
            subdomains = []
            for line in process.stdout.splitlines():
                if line.strip():
                   # Parsing manuel simple ou json.loads si besoin
                   # Ici Subfinder -json renvoie : {"host":"sub.domaine.com", "ip":"..."}
                   import json
                   try:
                       obj = json.loads(line)
                       subdomains.append(obj.get("host"))
                   except:
                       pass

            if subdomains:
                self.results.append({
                    "source": "Subfinder",
                    "type": "subdomains_found",
                    "count": len(subdomains),
                    "data": subdomains
                })
                logger.info(f"[Subfinder] {len(subdomains)} sous-domaines trouvés.")

        except Exception as e:
            logger.error(f"[Subfinder] Erreur : {e}")
            self.results.append({"error": str(e)})

        return self.results