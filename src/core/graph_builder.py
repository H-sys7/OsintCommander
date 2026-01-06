from pyvis.network import Network
import os
from src.processors.normalizer import DataNormalizer
from src.core.logger import logger

class GraphGenerator:
    def __init__(self, output_dir=None):
        from src.core.paths import get_app_temp_dir
        self.output_dir = output_dir or os.path.join(get_app_temp_dir(), "reports")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def build(self, target: str, normalizer: DataNormalizer):
        logger.info(f"[Graph] Génération du graphique pour {target}...")
        
        # 1. Config Réseau
        net = Network(height="750px", width="100%", bgcolor="#222222", select_menu=True, cdn_resources='in_line')
        net.force_atlas_2based(gravity=-50)
        
        # 2. Nœud Central
        net.add_node(target, label=target, color="#ff0000", size=40, shape="star", title="CIBLE")

        # 3. Boucle Données
        for entity in normalizer.unified_data:
            node_color = "#97c2fc"
            node_icon = "dot"
            
            # Code couleurs
            if entity.entity_type == "ip_address": node_color = "#ff6666"
            elif entity.entity_type == "email": node_color = "#66ff66"
            elif entity.entity_type == "subdomain": node_color = "#97c2fc"
            elif entity.entity_type == "vulnerability": node_color = "#ffbd33"
            elif entity.entity_type == "social_account": node_color = "#d633ff"
            elif entity.entity_type == "phone_number": node_color = "#00ffff"

            node_id = entity.value
            
            try:
                tooltip = f"Type: {entity.entity_type}\nSource: {entity.source}"
                # On ajoute le nœud avec une police blanche forcée
                net.add_node(
                    node_id, 
                    label=str(entity.value), 
                    title=tooltip, 
                    color=node_color, 
                    shape=node_icon, 
                    size=20,
                    font={'color': 'white'}
                )
                net.add_edge(target, node_id, color="#555555")
            except Exception:
                continue

        # 4. SAUVEGARDE FORCÉE (UTF-8)
        # On nettoie le nom de fichier
        safe_target = "".join([c for c in target if c.isalnum() or c in ('_', '-')])
        filename = f"{self.output_dir}/graph_{safe_target}.html"
        
        try:
            # GÉNÉRATION MANUELLE DU HTML
            html_content = net.generate_html()
            
            # Écriture avec encodage UTF-8 explicite
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            logger.info(f"[Graph] Sauvegardé : {filename}")
            return filename
        except Exception as e:
            logger.error(f"[Graph] Échec sauvegarde : {e}")
            return None