import subprocess
import shutil
import json
import os
from src.collectors.base import BaseCollector
from src.core.logger import logger

class NucleiCollector(BaseCollector):
    def run(self, target: str) -> list:
        logger.info(f"[Nuclei] Scan de vulnérabilités sur : {target}")
        self.results = []

        executable = shutil.which("nuclei")
        if not executable:
            executable = os.path.expanduser("~/go/bin/nuclei")
            if not os.path.exists(executable):
                return [{"error": "Nuclei non trouvé (Installez Go)"}]

        # On limite le scan pour la vitesse : tags cve, critical, high
        # Target peut être un fichier ou une URL
        cmd = [
            executable, 
            "-u" if not os.path.isfile(target) else "-l", target,
            "-json", "-silent",
            "-severity", "critical,high,medium", # On ignore les 'info' pour ne pas spammer
            "-timeout", "5"
        ]

        try:
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            for line in process.stdout.splitlines():
                try:
                    data = json.loads(line)
                    vuln_name = data.get("info", {}).get("name")
                    severity = data.get("info", {}).get("severity")
                    url = data.get("matched-at")
                    
                    self.results.append({
                        "source": "Nuclei",
                        "type": "vulnerability",
                        "value": vuln_name,
                        "metadata": {"severity": severity, "url": url}
                    })
                except:
                    pass

            if self.results:
                logger.info(f"[Nuclei] ⚠️ {len(self.results)} vulnérabilités potentielles !")
            else:
                logger.info("[Nuclei] Aucune vulnérabilité critique détectée.")

        except Exception as e:
            logger.error(f"[Nuclei] Erreur : {e}")
            self.results.append({"error": str(e)})

        return self.results