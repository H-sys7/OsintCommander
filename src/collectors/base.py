from abc import ABC, abstractmethod

class BaseCollector(ABC):
    """
    Ceci est le modèle que TOUS les outils devront respecter.
    Cela garantit que le 'main.py' sait comment leur parler.
    """
    
    def __init__(self):
        self.results = []

    @abstractmethod
    def run(self, target: str) -> list:
        """
        Chaque outil doit avoir cette méthode.
        Elle prend une cible (str) et renvoie une liste de résultats.
        """
        pass