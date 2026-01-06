import os
from groq import Groq
from src.config.settings import settings
from src.core.logger import logger

class AiAnalyst:
    def __init__(self):
        self.client = None
        self.model_name = "llama-3.3-70b-versatile"
        self.context_data = ""
        
        if settings.GROQ_API_KEY:
            try:
                self.client = Groq(api_key=settings.GROQ_API_KEY)
                logger.info(f"[IA] Moteur Groq initialisé (Modèle: {self.model_name})")
            except Exception as e:
                logger.error(f"[IA] Erreur d'initialisation Groq : {e}")
        else:
            logger.warning("[IA] Pas de clé API Groq configurée.")

    def load_context(self, data: str):
        """Charge les données du scan pour analyse"""
        self.context_data = data
        logger.info(f"[IA] Contexte chargé ({len(data)} caractères).")

    def ask(self, user_question: str, mode: str = "Résumé") -> str:
        if not self.client:
            return "⚠️ Erreur : Clé API Groq non configurée."

        if not self.context_data:
            return "⚠️ Le contexte est vide. Veuillez lancer un scan d'abord."

        # 1. DÉFINITION DYNAMIQUE DU MODE (Lié aux boutons de l'interface)
        instruction_mode = ""
        if mode == "Résumé":
            instruction_mode = (
                "🛑 MODE ACTUEL : SYNTHÉTIQUE (MANAGEMENT)\n"
                "- Priorité : L'essentiel en quelques lignes.\n"
                "- Ton : Direct, décisionnel.\n"
                "- Évite le jargon technique excessif."
            )
        elif mode == "Technique":
            instruction_mode = (
                "🛑 MODE ACTUEL : EXPERT TECHNIQUE (RED TEAM)\n"
                "- Priorité : Précision et vecteurs d'attaque.\n"
                "- Ton : Hacker, précis, vocabulaire technique (CVE, exploits, flags).\n"
                "- Détaille les preuves techniques."
            )
        elif mode == "Éducatif":
            instruction_mode = (
                "🛑 MODE ACTUEL : ENSEIGNANT (PÉDAGOGIE)\n"
                "- Priorité : Compréhension et apprentissage.\n"
                "- Ton : Bienveillant, explicatif.\n"
                "- Définit les termes complexes et utilise des analogies."
            )

        # 2. TON PROMPT (Intégré et structuré)
        system_prompt = (
            "CONTEXTE : Tu es une IA experte en OSINT et Cybersécurité (Red Team & Blue Team), "
            "intégrée dans un outil d’analyse nommé 'OsintCommander'.\n"
            "\n"
            f"{instruction_mode}\n"  # <--- INSERTION CRUCIALE DU MODE ICI
            "\n"
            "OBJECTIF GLOBAL :\n"
            "Analyser les données fournies pour produire une réponse :\n"
            "- OPÉRATIONNELLE : faits clairs, exploitables.\n"
            "- PÉDAGOGIQUE : expliquer le POURQUOI (impact/risque).\n"
            "\n"
            "RÈGLES DE COMPORTEMENT (OBLIGATOIRES) :\n"
            "1. SYNTHÈSE INITIALE : Commence par une analyse factuelle des données.\n"
            "2. CONTEXTUALISATION : Ne cite jamais une donnée brute sans expliquer son impact "
            "(surface d’attaque, exposition, risque).\n"
            "3. TRANSPARENCE : Cite toujours la source entre crochets (ex: [Whois], [Nmap]).\n"
            "4. PROFONDEUR : Donne l'essentiel, puis propose d'approfondir.\n"
            "5. ADAPTATION : Vulnérabilité = Risque + Principe; Défense = Mesures concrètes.\n"
            "6. ÉTHIQUE : Rappelle le cadre légal si nécessaire.\n"
            "7. GUIDAGE : Termine par une question engageante pour la suite.\n"
            "\n"
            "FORMAT DE RÉPONSE SOUHAITÉ (Sauf pour conversation simple) :\n"
            "📊 ANALYSE : Résumé clair basé sur les données.\n"
            "🎓 CONTEXTE : Concepts clés ou implications.\n"
            "🛡️ RECOMMANDATION : Actions concrètes.\n"
            "\n"
            "DONNÉES DU SCAN (CONTEXTE TECHNIQUE) :\n"
            "---------------------\n"
            f"{self.context_data}\n"
            "---------------------\n"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                temperature=0.4, # Assez précis, un peu créatif pour la pédagogie
                max_tokens=1500
            )

            # Extraction sécurisée
            content = ""
            try:
                choice = response.choices[0]
                msg = choice.message
                content = msg.content
            except Exception:
                content = str(response)

            try:
                choice = response.choices[0]
                msg = choice.message
                content = msg.content or ""
            except Exception:
                content = str(response)
            
            return content

        except Exception as e:
            logger.error(f"[IA] Erreur API Groq : {e}")
            return f"❌ Erreur de communication avec Groq : {str(e)}"