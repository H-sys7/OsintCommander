from .base import BaseCollector

class MetagoofilCollector(BaseCollector):
    def run(self, target):
        return [{"tool": "metagoofil", "target": target}]