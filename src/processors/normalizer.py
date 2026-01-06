import json
from typing import List, Dict, Any, Optional
from src.core.logger import logger

class OsintEntity:
    def __init__(self, value: str, entity_type: str, source: str, metadata: Optional[Dict[str, Any]] = None):
        self.value = value
        self.entity_type = entity_type
        self.source = source
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "value": self.value,
            "type": self.entity_type,
            "source": self.source,
            "metadata": self.metadata
        }

class DataNormalizer:
    def __init__(self):
        self.unified_data: List[OsintEntity] = []

    def add_entity(self, entity: OsintEntity):
        """Ajoute une entité en évitant les doublons et en fusionnant les métadonnées"""
        for e in self.unified_data:
            if e.value == entity.value and e.entity_type == entity.entity_type:
                # Fusion des métadonnées si nouvelle source apporte des détails
                if entity.metadata:
                    e.metadata.update(entity.metadata)
                return
        self.unified_data.append(entity)

    def process(self, tool_name: str, raw_data: list):
        """Transforme les sorties brutes en Entités standards avec Logging (Mode Robuste)"""
        logger.info(f"Normalisation des données de {tool_name}...")

        # 1. Validation de l'entrée
        if not raw_data:
            return self.unified_data

        if isinstance(raw_data, dict) and "error" in raw_data:
            raw_data = [raw_data] # On transforme l'erreur unique en liste pour la traiter

        if not isinstance(raw_data, list):
            logger.warning(f"Format inattendu pour {tool_name} (ni liste ni dict)")
            return self.unified_data

        for item in raw_data:
            # 2. Gestion des erreurs explicites (Pour que l'IA le sache)
            if isinstance(item, dict) and "error" in item:
                self.add_entity(OsintEntity(
                    value="Erreur Outil",
                    entity_type="tool_error",
                    source=tool_name,
                    metadata={"error": item["error"]}
                ))
                continue

            processed = False # Flag pour le fallback

            try:
                # === LOGIQUE PAR OUTIL ===
                
                # 1. DNS (Corection Robuste)
                if tool_name == "DNS":
                    # On cherche une IP (format 'A' ou juste une clé 'value' qui ressemble à une IP)
                    record_type = item.get("type", "").upper()
                    value = item.get("value", "")
                    
                    # Si c'est un enregistrement A OU si ça ressemble à une IP
                    import re
                    is_ip = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", value)
                    
                    if record_type == "A" or (is_ip and record_type != "MX"):
                        self.add_entity(OsintEntity(
                            value=value, 
                            entity_type="ip_address", 
                            source="DNS", 
                            metadata={"desc": "IP Principale"}
                        ))
                        processed = True
                    
                    elif record_type == "MX":
                         self.add_entity(OsintEntity(value=value, entity_type="mail_server", source="DNS"))
                         processed = True

                # 2. CriminalIP
                elif tool_name == "CriminalIP":
                    if "details" in item:
                        self.add_entity(OsintEntity(
                            value=item["value"],
                            entity_type="infrastructure_risk",
                            source="CriminalIP",
                            metadata=item["details"]
                        ))
                        processed = True

                # 3. TheHarvester
                elif tool_name in ["TheHarvester", "HarvesterCollector"]:
                    type_data = item.get("type")
                    
                    if type_data == "emails_found":
                        emails = item.get("data", [])
                        for email in emails:
                            self.add_entity(OsintEntity(value=email, entity_type="email", source="TheHarvester"))
                        processed = True
                    
                    elif type_data == "subdomains_found":
                        hosts = item.get("data", [])
                        for host in hosts:
                            clean_host = str(host).split(":")[0]
                            self.add_entity(OsintEntity(value=clean_host, entity_type="subdomain", source="TheHarvester"))
                        processed = True

                # 4. Whois
                elif tool_name == "WhoisCollector":
                    if "domain_name" in item:
                        self.add_entity(OsintEntity(
                            value=str(item["domain_name"]),
                            entity_type="domain",
                            source="Whois",
                            metadata={"registrar": item.get("registrar"), "country": item.get("country")}
                        ))
                        processed = True
                        if "emails" in item and item["emails"]:
                            emails = item["emails"] if isinstance(item["emails"], list) else [item["emails"]]
                            for email in emails:
                                self.add_entity(OsintEntity(value=email, entity_type="email", source="Whois", metadata={"role": "admin/tech"}))

                # 5. GoogleDocs
                elif tool_name == "GoogleDocsCollector":
                     if "data" in item:
                        for doc in item["data"]:
                            self.add_entity(OsintEntity(value=doc, entity_type="exposed_file", source="GoogleDorks"))
                        processed = True

                # 6. Maigret
                elif tool_name == "MaigretCollector":
                    if "data" in item:
                        for account in item["data"]:
                            if isinstance(account, dict):
                                self.add_entity(OsintEntity(
                                    value=account["url"],
                                    entity_type="social_account",
                                    source=f"Maigret ({account.get('site', 'Unknown')})",
                                    metadata={"tags": account.get("tags"), "site": account.get("site")}
                                ))
                            else:
                                self.add_entity(OsintEntity(value=str(account), entity_type="social_account", source="Maigret"))
                        processed = True

                # 7. Subfinder
                elif tool_name == "SubfinderCollector":
                    if "data" in item:
                        for sub in item["data"]:
                            self.add_entity(OsintEntity(value=sub, entity_type="subdomain", source="Subfinder"))
                        processed = True

                # 8. Httpx
                elif tool_name == "HttpxCollector":
                    if "url" in item:
                        self.add_entity(OsintEntity(
                            value=item["url"],
                            entity_type="web_service",
                            source="Httpx",
                            metadata={"status": item.get("status"), "title": item.get("title"), "tech": item.get("tech")}
                        ))
                        processed = True

                # 9. Nmap
                elif tool_name == "NmapCollector":
                    if item.get("type") == "open_port":
                         self.add_entity(OsintEntity(value=item["value"], entity_type="open_port", source="Nmap", metadata=item.get("metadata")))
                         processed = True
                    elif item.get("type") == "os_detected":
                         self.add_entity(OsintEntity(value=item["value"], entity_type="operating_system", source="Nmap", metadata=item.get("metadata")))
                         processed = True

                # 10. Nuclei
                elif tool_name == "NucleiCollector":
                    if "value" in item:
                        self.add_entity(OsintEntity(value=item["value"], entity_type="vulnerability", source="Nuclei", metadata=item.get("metadata")))
                        processed = True

                # 11. Holehe
                elif tool_name == "HoleheCollector":
                    if "data" in item:
                        for site in item["data"]:
                            self.add_entity(OsintEntity(value=site, entity_type="account_registered", source="Holehe"))
                        processed = True

                # 12. TechStack
                elif tool_name == "TechStackCollector":
                    if "data" in item:
                        for tech in item["data"]:
                            self.add_entity(OsintEntity(value=tech, entity_type="technology", source="BuiltWith"))
                        processed = True
     
                # 13. Phone Intel
                elif tool_name == "PhoneCollector":
                    if "details" in item:
                        self.add_entity(OsintEntity(
                            value=item["value"], 
                            entity_type="phone_number", 
                            source="PhoneIntel", 
                            metadata=item["details"]
                        ))
                        processed = True

                # 14. BreachCollector
                elif tool_name == "BreachCollector":
                    if "count" in item and item["count"] > 0:
                        for breach in item["data"]:
                            self.add_entity(OsintEntity(
                                value=breach,
                                entity_type="leaked_credential",
                                source="HaveIBeenPwned",
                                metadata={"target_email": "Cible"}
                            ))
                        processed = True
                    elif "data" in item and isinstance(item["data"], list): # Fallback si format different
                        for breach in item["data"]:
                            self.add_entity(OsintEntity(value=breach, entity_type="leaked_credential", source="HIBP"))
                        processed = True

                # 15. SSL
                elif tool_name == "SslCollector":
                    if "details" in item:
                        self.add_entity(OsintEntity(value=item["value"], entity_type="ssl_certificate", source="SSL_Analyzer", metadata=item["details"]))
                        processed = True
                    if "data" in item and item["type"] == "subdomains_found":
                        for san in item["data"]:
                            self.add_entity(OsintEntity(value=san, entity_type="subdomain", source="SSL_SANs"))
                        processed = True

                # 16. Censys
                elif tool_name == "CensysCollector":
                    if item.get("type") == "related_ips":
                        for ip in item.get("data", []):
                            self.add_entity(OsintEntity(value=ip, entity_type="ip_address", source="Censys"))
                        processed = True

                # 17. Career Hunter
                elif tool_name == "CareerCollector":
                    if "data" in item:
                        for link in item["data"]:
                            self.add_entity(OsintEntity(value=link["url"], entity_type="professional_profile", source="CareerHunter", metadata={"platform": link["site"]}))
                        processed = True

                # === FILET DE SÉCURITÉ (FALLBACK) ===
                # Si l'outil a renvoyé quelque chose mais qu'aucun 'if' ne l'a attrapé
                # On l'ajoute comme donnée brute pour ne pas la perdre.
                if not processed:
                    val = item.get("value") or item.get("url") or item.get("ip") or item.get("domain") or "Donnée Brute"
                    self.add_entity(OsintEntity(
                        value=str(val),
                        entity_type="raw_data",
                        source=f"{tool_name}_Raw",
                        metadata={"content": str(item)}
                    ))

            except Exception as e:
                logger.error(f"Erreur lors de la normalisation ({tool_name}): {e}")
                continue

        return self.unified_data

    def get_summary(self) -> str:
        """
        Génère un résumé calibré pour ~5000 Tokens (Safe Mode).
        Limite : ~150-200 items max affichés + Statistiques complètes.
        """
        lines = []
        
        # 1. INVENTAIRE COMPLET (Très peu de tokens, haute valeur)
        lines.append("=== 📊 STATISTIQUES GLOBALES ===")
        counts = {}
        for e in self.unified_data:
            counts[e.entity_type] = counts.get(e.entity_type, 0) + 1
        
        if not counts:
            return "Aucune donnée significative trouvée."
            
        for type_name, count in counts.items():
            lines.append(f"- {count} élément(s) de type '{type_name}'")

        # 2. EXTRAIT DES DONNÉES (Calibrage 5000 Tokens)
        lines.append("\n=== 🔍 EXTRAIT DES DONNÉES CLÉS ===")
        
        shown_counts = {}
        
        # QUOTA PAR TYPE (Ajusté pour ~5k tokens)
        # Priorité aux failles et aux ports, limitation des listes massives (subs/urls)
        limits = {
            "vulnerability": 40,      # Priorité critique
            "leaked_credential": 30,  # Priorité critique
            "open_port": 40,          # Important pour la surface d'attaque
            "infrastructure_risk": 20,# Important (CriminalIP)
            
            "subdomain": 25,          # Suffisant pour voir le pattern (dev, api...)
            "web_service": 25,        # Résultats Httpx
            "social_account": 20,     # Maigret
            "email": 20,              # Whois/Harvester
            
            "ip_address": 15,
            "technology": 15,
            "ssl_certificate": 5,     # Souvent verbeux
            "raw_data": 5,            # Souvent très gros
            "tool_error": 5
        }
        
        default_limit = 10 # Pour tout autre type imprévu

        for e in self.unified_data:
            ctype = e.entity_type
            current_count = shown_counts.get(ctype, 0)
            limit = limits.get(ctype, default_limit)

            if current_count < limit:
                meta_str = str(e.metadata) if e.metadata else ""
                
                # TRONCATION INTELLIGENTE
                # On coupe les métadonnées > 250 caractères pour économiser les tokens
                # (Une métadonnée brute peut faire 5000 chars à elle seule !)
                if len(meta_str) > 250: 
                    meta_str = meta_str[:250] + "...(tronqué)"
                
                # Construction de la ligne
                line = f"[{ctype.upper()}] {e.value}"
                if e.source: 
                    line += f" | Src: {e.source}"
                if meta_str and meta_str != "{}": 
                    line += f" | Det: {meta_str}"
                
                lines.append(line)
                shown_counts[ctype] = current_count + 1
            
            elif current_count == limit:
                # Indicateur de coupure pour que l'IA sache qu'il y en a plus
                remaining = counts[ctype] - limit
                lines.append(f"... (Il reste {remaining} autres entrées '{ctype}' masquées pour respecter la limite de tokens) ...")
                shown_counts[ctype] = current_count + 1 # Stop

        return "\n".join(lines)