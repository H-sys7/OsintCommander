from pydantic import BaseModel
from typing import Optional, List

class OsintEntity(BaseModel):
    """
    Ceci est l'unité atomique de notre logiciel.
    Peu importe d'où vient l'info, elle finira dans ce format.
    """
    value: str          # La donnée (ex: "admin@tesla.com" ou "192.168.1.1")
    entity_type: str    # Le type (ex: "email", "ip", "domain", "vulnerability")
    source: str         # Qui l'a trouvé ? (ex: "TheHarvester")
    confidence: int = 100 # Pour plus tard
    metadata: Optional[dict] = {} # Pour stocker des détails (ex: ports ouverts)

    def to_string(self):
        """Format lisible pour l'IA"""
        meta_str = f" | Details: {self.metadata}" if self.metadata else ""
        return f"[{self.entity_type.upper()}] {self.value} (Source: {self.source}){meta_str}"