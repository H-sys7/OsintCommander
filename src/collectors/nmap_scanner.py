import subprocess
import shutil
import xml.etree.ElementTree as ET
from src.collectors.base import BaseCollector
from src.core.logger import logger

class NmapCollector(BaseCollector):
    def run(self, target: str) -> list:
        logger.info(f"[Nmap] Scan AVANCÉ (OS & Versions) sur : {target}")
        self.results = []

        executable = shutil.which("nmap")
        if not executable:
             return [{"error": "Nmap non trouvé."}]

        # -sV : Versions des services
        # -O : Détection d'OS (Nécessite Admin/Sudo)
        # --osscan-guess : Essaie de deviner si incertain
        # -T4 : Vitesse rapide
        cmd = [executable, "-sV", "-O", "--osscan-guess", "-T4", target, "-oX", "-"]

        try:
            # Timeout augmenté car ce scan est long
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if process.stdout.strip().startswith("<?xml"):
                root = ET.fromstring(process.stdout)
                
                # 1. Récupération des Ports & Services
                for host in root.findall("host"):
                    # Récupération de l'OS
                    os_name = "Inconnu"
                    os_match = host.find(".//osmatch")
                    if os_match is not None:
                        os_name = os_match.attrib.get("name")
                        accuracy = os_match.attrib.get("accuracy")
                        self.results.append({
                            "source": "Nmap",
                            "type": "os_detected",
                            "value": os_name,
                            "metadata": {"accuracy": f"{accuracy}%"}
                        })
                        logger.info(f"[Nmap] OS Détecté : {os_name}")

                    # Récupération des Services
                    for port in host.findall(".//port"):
                        state_elem = port.find("state")
                        state = state_elem.attrib.get("state") if state_elem is not None else None
                        if state == "open":
                            port_id = port.attrib.get("portid")
                            
                            service_elem = port.find("service")
                            service_name = service_elem.attrib.get("name", "unknown") if service_elem is not None else "unknown"
                            product = service_elem.attrib.get("product", "") if service_elem is not None else ""
                            version = service_elem.attrib.get("version", "") if service_elem is not None else ""
                            
                            full_desc = f"{service_name} {product} {version}".strip()
                            
                            self.results.append({
                                "source": "Nmap",
                                "type": "open_port",
                                "value": f"{port_id}/tcp",
                                "metadata": {"service": full_desc}
                            })
            else:
                 # Si pas de XML, peut-être une erreur de privilèges
                 if "root" in process.stderr or "administrator" in process.stderr:
                     self.results.append({"error": "Nmap a besoin des droits Admin/Root pour la détection d'OS (-O)."})
                 else:
                     self.results.append({"error": "Erreur Nmap générique."})

        except Exception as e:
            logger.error(f"[Nmap] Erreur : {e}")
            self.results.append({"error": str(e)})

        return self.results