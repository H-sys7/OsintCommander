import subprocess
import shutil
import json
import os
import sys
from src.collectors.base import BaseCollector
from src.config.settings import settings # On importe les settings
from src.core.logger import logger

class HarvesterCollector(BaseCollector):
    def run(self, target: str) -> list:
        logger.info(f"[TheHarvester] Lancement de la recherche sur : {target}")
        self.results = []
        
        # Définition des variables de commande
        executable = ""
        args = []

        # CAS 1 : L'utilisateur a défini un chemin spécifique dans .env
        if settings.THEHARVESTER_PATH:
            script_path = os.path.join(settings.THEHARVESTER_PATH, "theHarvester.py")
            if os.path.exists(script_path):
                # On utilise le python du système actuel pour lancer le script
                executable = sys.executable 
                args = [script_path]
                logger.info(f"[TheHarvester] Utilisation du script local : {script_path}")
            else:
                logger.error(f"[TheHarvester] Script introuvable au chemin : {script_path}")

        # CAS 2 : Pas de chemin config, on cherche la commande globale
        if not executable:
            executable = shutil.which("theHarvester")
            if executable:
                logger.info("[TheHarvester] Outil trouvé dans le PATH global.")
            else:
                # Échec total
                return [{"error": "TheHarvester introuvable. Configurez THEHARVESTER_PATH dans .env"}]

        # Préparation fichier sortie
        output_file = f"harvester_{target.replace('.', '_')}"

        # Construction de la commande complète
        # python3 /path/to/theHarvester.py -d target -b google -f output
        cmd = [executable] + args + [
            "-d", target,
            "-b", "google",
            "-l", "20",
            "-f", output_file
        ]

        try:
            logger.debug(f"Commande exécutée : {' '.join(cmd)}")
            
            # Exécution
            subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Lecture du JSON
            json_output_path = output_file + ".json"
            
            if os.path.exists(json_output_path):
                with open(json_output_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Parsing
                emails = data.get("emails", [])
                hosts = data.get("hosts", [])

                self.results.append({
                    "source": "TheHarvester",
                    "type": "emails_found",
                    "count": len(emails),
                    "data": emails
                })
                
                self.results.append({
                    "source": "TheHarvester",
                    "type": "subdomains_found",
                    "count": len(hosts),
                    "data": hosts
                })

                # Nettoyage
                os.remove(json_output_path)
                xml_file = output_file + ".xml"
                if os.path.exists(xml_file):
                    os.remove(xml_file)
            else:
                logger.warning("[TheHarvester] Aucun fichier JSON généré (Google a peut-être bloqué).")
                self.results.append({"error": "Pas de résultats bruts."})

        except Exception as e:
            logger.error(f"[TheHarvester] Erreur : {e}")
            self.results.append({"error": str(e)})

        return self.results