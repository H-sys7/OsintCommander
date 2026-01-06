import json
import os
from datetime import datetime
from src.core.logger import logger
from src.processors.normalizer import DataNormalizer
from typing import Optional

class ReportExporter:
    def __init__(self, output_dir=None):
        from src.core.paths import get_app_temp_dir
        self.output_dir = output_dir or os.path.join(get_app_temp_dir(), "reports")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save(self, target: str, normalizer: DataNormalizer, ai_summary: Optional[str] = None):
        """
        Sauvegarde les données sous format JSON et Markdown.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_target = target.replace(".", "_")
        base_filename = f"{self.output_dir}/{sanitized_target}_{timestamp}"

        # 1. Export JSON (Données structurées)
        json_data = [
            {
                "type": entity.entity_type,
                "value": entity.value,
                "source": entity.source,
                "metadata": entity.metadata
            }
            for entity in normalizer.unified_data
        ]
        
        json_path = f"{base_filename}.json"
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)
            logger.info(f"[Export] JSON sauvegardé : {json_path}")
        except Exception as e:
            logger.error(f"[Export] Erreur sauvegarde JSON : {e}")

        # 2. Export Markdown (Pour lecture humaine)
        md_path = f"{base_filename}.md"
        try:
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(f"# Rapport OSINT : {target}\n")
                f.write(f"**Date :** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
                
                f.write("## 1. Résumé Technique\n")
                f.write(normalizer.get_summary())
                
                if ai_summary:
                    f.write("\n\n## 2. Analyse IA (Dernière réponse)\n")
                    f.write(ai_summary)
                
                f.write("\n\n---\n*Généré par OsintAI Tool*")
            
            logger.info(f"[Export] Markdown sauvegardé : {md_path}")
            return f"Rapport sauvegardé dans le dossier '{self.output_dir}'"

        except Exception as e:
            return f"Erreur lors de l'export : {e}"