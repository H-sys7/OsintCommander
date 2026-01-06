import customtkinter as ctk
import threading
from datetime import datetime
import os

# Imports Configuration
from src.config.settings import settings
from src.core.logger import logger
from src.core.exporter import ReportExporter
from src.core.graph_builder import GraphGenerator
from src.processors.normalizer import DataNormalizer
from src.ai.agent import AiAnalyst

# Imports Collectors
from src.collectors.dns_analyzer import DnsCollector
from src.collectors.criminalip import CriminalIpCollector
from src.collectors.whois_info import WhoisCollector
from src.collectors.google_docs import GoogleDocsCollector
from src.collectors.subfinder import SubfinderCollector
from src.collectors.httpx_runner import HttpxCollector
from src.collectors.nmap_scanner import NmapCollector
from src.collectors.nuclei_runner import NucleiCollector
from src.collectors.maigret_runner import MaigretCollector
from src.collectors.holehe_runner import HoleheCollector
from src.collectors.phone_intel import PhoneCollector
from src.collectors.tech_stack import TechStackCollector
from src.collectors.ssl_analysis import SslCollector
from src.collectors.censys_search import CensysCollector
from src.collectors.breach_check import BreachCollector
from src.collectors.career_intel import CareerCollector

from src.processors.normalizer import DataNormalizer
from src.ai.agent import AiAnalyst

class OsintApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- CONFIGURATION FENÊTRE ---
        self.title(f"{settings.APP_NAME} v{settings.VERSION} | Command Center")
        self.geometry("1280x850")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.normalizer = DataNormalizer()
        self.ai_agent = AiAnalyst()
        self.is_scanning = False 

        self.setup_sidebar()
        self.setup_scan_view()
        self.setup_ai_view()
        
        self.show_scan_view()

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="OSINT\nCOMMANDER", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_nav_scan = ctk.CTkButton(self.sidebar_frame, text="📡  SCANNER", command=self.show_scan_view, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), font=ctk.CTkFont(size=14))
        self.btn_nav_scan.grid(row=1, column=0, padx=20, pady=10)

        self.btn_nav_ai = ctk.CTkButton(self.sidebar_frame, text="🧠  ANALYSTE IA", command=self.show_ai_view, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), font=ctk.CTkFont(size=14))
        self.btn_nav_ai.grid(row=2, column=0, padx=20, pady=10)

        self.btn_quick_export = ctk.CTkButton(self.sidebar_frame, text="💾  Export Rapide", command=self.on_export_click, fg_color="#2da44e", font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_quick_export.grid(row=5, column=0, padx=20, pady=10)
        
        self.btn_quick_graph = ctk.CTkButton(self.sidebar_frame, text="🕸️  Graphique", command=self.on_graph_click, fg_color="#8A2BE2", font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_quick_graph.grid(row=6, column=0, padx=20, pady=(10, 20))

    def setup_scan_view(self):
        self.scan_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        
        control_frame = ctk.CTkFrame(self.scan_frame, fg_color=("gray85", "gray17"))
        control_frame.pack(fill="x", padx=20, pady=20)

        self.scan_type_var = ctk.StringVar(value="Entreprise")
        self.seg_button = ctk.CTkSegmentedButton(control_frame, values=["Entreprise", "Personne", "Téléphone"], variable=self.scan_type_var, width=500, font=ctk.CTkFont(size=14))
        self.seg_button.pack(pady=15)

        input_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        input_frame.pack(pady=(0, 20))

        self.entry_target = ctk.CTkEntry(input_frame, placeholder_text="Cible (Domaine, Pseudo, Email...)", width=450, font=("Arial", 14))
        self.entry_target.pack(side="left", padx=10)
        
        self.btn_launch = ctk.CTkButton(input_frame, text="LANCER LE SCAN", command=self.start_scan_thread, font=("Arial", 14, "bold"), height=35, fg_color="#1f6aa5")
        self.btn_launch.pack(side="left", padx=10)

        self.progress_bar = ctk.CTkProgressBar(self.scan_frame, mode="indeterminate", width=900)
        
        # --- AMÉLIORATION LISIBILITÉ LOGS ---
        # Police Consolas (Monospace) taille 14 pour bien voir
        self.log_box = ctk.CTkTextbox(self.scan_frame, width=900, height=500, font=("Consolas", 14))
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Tags de couleurs (SANS option 'font' qui fait crasher)
        self.log_box.tag_config("INFO", foreground="white")
        self.log_box.tag_config("SUCCESS", foreground="#00ff00") # Vert
        self.log_box.tag_config("WARNING", foreground="orange")
        self.log_box.tag_config("ERROR", foreground="#ff3333") # Rouge
        self.log_box.tag_config("TITLE", foreground="#33ccff") # Cyan

        self.log_message("Système prêt.", "INFO")

    def setup_ai_view(self):
        self.ai_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        
        # 1. Sélecteur de Mode (Haut)
        mode_frame = ctk.CTkFrame(self.ai_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(mode_frame, text="Niveau d'analyse :", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        
        self.ai_mode_var = ctk.StringVar(value="Résumé")
        self.mode_selector = ctk.CTkSegmentedButton(
            mode_frame, 
            values=["Résumé", "Technique", "Éducatif"], 
            variable=self.ai_mode_var,
            width=300,
            font=("Arial", 13)
        )
        self.mode_selector.pack(side="left", padx=10)

        # 2. Chat Display
        self.chat_display = ctk.CTkTextbox(self.ai_frame, font=("Roboto", 15), wrap="word")
        self.chat_display.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.chat_display.configure(state="disabled")

        # 3. Input Zone
        input_frame = ctk.CTkFrame(self.ai_frame, height=60)
        input_frame.pack(fill="x", padx=20, pady=20)

        self.entry_question = ctk.CTkEntry(input_frame, placeholder_text="Posez votre question...", height=45, font=("Arial", 14))
        self.entry_question.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_question.bind("<Return>", lambda event: self.on_ask_ai())

        self.btn_ask = ctk.CTkButton(input_frame, text="ENVOYER", command=self.on_ask_ai, width=120, height=45, font=("Arial", 12, "bold"))
        self.btn_ask.pack(side="right")

    # --- NAVIGATION ---
    def show_scan_view(self):
        self.ai_frame.grid_forget()
        self.scan_frame.grid(row=0, column=1, sticky="nsew")
        self.btn_nav_scan.configure(fg_color=("gray75", "gray25"))
        self.btn_nav_ai.configure(fg_color="transparent")

    def show_ai_view(self):
        self.scan_frame.grid_forget()
        self.ai_frame.grid(row=0, column=1, sticky="nsew")
        self.btn_nav_ai.configure(fg_color=("gray75", "gray25"))
        self.btn_nav_scan.configure(fg_color="transparent")

    # --- LOGGING ---
    def log_message(self, message, level="INFO"):
        def _update():
            self.log_box.configure(state="normal")
            time_str = datetime.now().strftime("[%H:%M:%S] ")
            self.log_box.insert("end", time_str, "INFO")
            
            if level == "TITLE":
                self.log_box.insert("end", f"\n{message}\n", "TITLE")
                self.log_box.insert("end", "="*60 + "\n", "INFO")
            else:
                self.log_box.insert("end", f"{message}\n", level)
            
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(0, _update)

    # --- SCANNING ---
    def start_scan_thread(self):
        if self.is_scanning: return
        target = self.entry_target.get()
        if not target:
            self.log_message("Erreur: Cible vide", "ERROR")
            return

        self.entry_target.delete(0, "end")
        self.is_scanning = True
        self.btn_launch.configure(state="disabled", text="SCAN EN COURS...")
        self.progress_bar.pack(pady=(0, 10), padx=20)
        self.progress_bar.start()
        
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self.normalizer = DataNormalizer()

        threading.Thread(target=self.run_scan_logic, args=(target,), daemon=True).start()

    def run_scan_logic(self, target):
        mode = self.scan_type_var.get()
        try:
            self.log_message(f"🚀 DÉMARRAGE DE L'ANALYSE : {target}", "TITLE")

            if mode == "Entreprise":
                # Phase 1 : Identité
                self.log_message("\n--- PHASE 1 : IDENTITÉ & INFRASTRUCTURE ---", "INFO")
                
                self.log_message("🔄 OUTIL : Whois (Identification Propriétaire)", "INFO")
                self.normalizer.process("WhoisCollector", WhoisCollector().run(target))
                
                self.log_message("🔄 OUTIL : DNS & SSL (Configuration Réseau & Sécurité)", "INFO")
                self.normalizer.process("DNS", DnsCollector().run(target))
                self.normalizer.process("SslCollector", SslCollector().run(target))
                
                target_ip = None
                for e in self.normalizer.unified_data:
                    if e.entity_type == "ip_address": target_ip = e.value
                
                if target_ip:
                    self.log_message(f"✅ Cible Résolue : IP {target_ip}", "SUCCESS")
                    self.log_message("🔄 OUTIL : CriminalIP/Censys (Réputation IP)", "INFO")
                    self.normalizer.process("CriminalIP", CriminalIpCollector().run(target_ip))
                    self.normalizer.process("CensysCollector", CensysCollector().run(target_ip))

                self.log_message("🔄 OUTIL : TechStack (Technologies Web utilisées)", "INFO")
                self.normalizer.process("TechStackCollector", TechStackCollector().run(target))
                self.normalizer.process("GoogleDocsCollector", GoogleDocsCollector().run(target))

                # Phase 2 : Cartographie
                self.log_message("\n--- PHASE 2 : SURFACE D'ATTAQUE ---", "INFO")
                self.log_message("🔄 OUTIL : Subfinder (Recherche de sous-domaines cachés)", "INFO")
                sub_res = SubfinderCollector().run(target)
                self.normalizer.process("SubfinderCollector", sub_res)

                all_subs = [target]
                if sub_res:
                    for item in sub_res:
                        if "data" in item: all_subs.extend(item["data"])
                
                # Fichiers temporaires pour les outils Go
                temp_subs = "temp_subs_gui.txt"
                temp_live = "temp_live_gui.txt"
                with open(temp_subs, "w") as f: f.write("\n".join(all_subs))

                self.log_message(f"🔄 OUTIL : Httpx (Test d'accessibilité sur {len(all_subs)} domaines)", "INFO")
                httpx_res = HttpxCollector().run(temp_subs)
                self.normalizer.process("HttpxCollector", httpx_res)

                live_urls = [item["url"] for item in httpx_res if "url" in item]
                
                if live_urls:
                    with open(temp_live, "w") as f: f.write("\n".join(live_urls))
                    self.log_message(f"🔄 OUTIL : Nuclei (Scan de vulnérabilités sur {len(live_urls)} sites)", "WARNING")
                    self.normalizer.process("NucleiCollector", NucleiCollector().run(temp_live))
                
                if target_ip:
                    self.log_message("🔄 OUTIL : Nmap (Scan de Ports & Services)", "WARNING")
                    self.normalizer.process("NmapCollector", NmapCollector().run(target_ip))

                # Nettoyage
                try: 
                    if os.path.exists(temp_subs): os.remove(temp_subs)
                    if os.path.exists(temp_live): os.remove(temp_live)
                except: pass

            elif mode == "Personne":
                self.log_message("\n--- PHASE 1 : EMPREINTE NUMÉRIQUE ---", "INFO")
                if "@" in target:
                    self.log_message("📧 Type : Email détecté", "SUCCESS")
                    self.log_message("🔄 OUTIL : Holehe (Recherche de comptes enregistrés)", "INFO")
                    self.normalizer.process("HoleheCollector", HoleheCollector().run(target))
                    
                    self.log_message("🔄 OUTIL : HIBP (Recherche de fuites de données)", "INFO")
                    self.normalizer.process("BreachCollector", BreachCollector().run(target))
                    
                    self.log_message("🔄 OUTIL : CareerHunter (Recherche pro/LinkedIn)", "INFO")
                    self.normalizer.process("CareerCollector", CareerCollector().run(target))
                    
                    pseudo = target.split("@")[0]
                    self.log_message(f"🔄 OUTIL : Maigret (Pivot sur le pseudo '{pseudo}')", "INFO")
                    self.normalizer.process("MaigretCollector", MaigretCollector().run(pseudo))
                else:
                    self.log_message("👤 Type : Pseudo détecté", "SUCCESS")
                    self.log_message("🔄 OUTIL : Maigret (Recherche multi-plateformes)", "INFO")
                    self.normalizer.process("MaigretCollector", MaigretCollector().run(target))
                    self.normalizer.process("CareerCollector", CareerCollector().run(target))

            elif mode == "Téléphone":
                self.log_message("\n--- PHASE 1 : INTELLIGENCE TÉLÉPHONIQUE ---", "INFO")
                if not target.startswith("+"): 
                    target = "+" + target.strip()
                    self.log_message(f"⚠️ Formatage international appliqué : {target}", "WARNING")
                
                self.log_message(f"🔄 OUTIL : PhoneIntel (Analyse technique & Risque)", "INFO")
                res_phone = PhoneCollector().run(target)
                self.normalizer.process("PhoneCollector", res_phone)
                
                # Affichage Pédagogique des résultats
                for item in res_phone:
                    if "details" in item:
                        det = item["details"]
                        risk = det.get("analyse_risque", {})
                        
                        self.log_message(f"📍 Pays : {det.get('pays')}", "SUCCESS")
                        self.log_message(f"📞 Opérateur : {det.get('operateur')}", "SUCCESS")
                        self.log_message(f"📱 Type de Ligne : {det.get('type_ligne')}", "SUCCESS")
                        
                        # Affichage du Risque
                        risk_color = "ERROR" if "Élevé" in risk.get("niveau", "") else "SUCCESS"
                        self.log_message(f"🛡️ Niveau de Risque : {risk.get('niveau')}", risk_color)
                        if risk.get("raison"):
                             self.log_message(f"   Raison : {risk.get('raison')}", "INFO")

            summary = self.normalizer.get_summary()
            self.ai_agent.load_context(summary)
            self.log_message("\n✅ SCAN TERMINÉ. L'IA EST PRÊTE POUR L'ANALYSE PÉDAGOGIQUE.", "SUCCESS")

        except Exception as e:
            self.log_message(f"❌ Erreur Critique Scan: {e}", "ERROR")
            logger.error(f"Thread Error: {e}")
        finally:
            self.after(0, self.stop_scan_ui)

    def stop_scan_ui(self):
        self.is_scanning = False
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_launch.configure(state="normal", text="LANCER LE SCAN")

    def on_export_click(self):
        if not self.normalizer.unified_data:
            self.log_message("Rien à exporter.", "WARNING")
            return
        target = self.entry_target.get() or "Unknown"
        msg = ReportExporter().save(target, self.normalizer)
        self.log_message(f"Export : {msg}", "SUCCESS")

    def on_graph_click(self):
        if not self.normalizer.unified_data:
            self.log_message("Pas de données pour le graphique.", "WARNING")
            return
        target = self.entry_target.get() or "Unknown"
        self.log_message("Génération graphique...", "INFO")
        
        import webbrowser
        path = GraphGenerator().build(target, self.normalizer)
        if path:
            self.log_message("Ouverture navigateur...", "SUCCESS")
            # Ajout 'file:///' pour être sûr
            webbrowser.open(f"file:///{os.path.abspath(path).replace(os.sep, '/')}")
        else:
            self.log_message("Échec graphique.", "ERROR")

    def on_ask_ai(self):
        question = self.entry_question.get()
        if not question: return
        
        mode = self.ai_mode_var.get() # On récupère "Résumé", "Technique" ou "Éducatif"
        
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\n🛑 OPÉRATEUR ({mode.upper()}): {question}\n")
        self.chat_display.insert("end", "⏳ Analyse en cours...\n")
        self.chat_display.configure(state="disabled")
        
        threading.Thread(target=self.run_ai_thread, args=(question, mode), daemon=True).start()
        self.entry_question.delete(0, "end")

    def run_ai_thread(self, question, mode):
        # On passe le mode à l'agent
        response = self.ai_agent.ask(question, mode=mode)
        
        def _update():
            self.chat_display.configure(state="normal")
            self.chat_display.delete("end-2l", "end-1l")
            self.chat_display.insert("end", f"\n🎓 IA ({mode}): {response}\n")
            self.chat_display.insert("end", "_"*40 + "\n")
            self.chat_display.see("end")
            self.chat_display.configure(state="disabled")
        self.after(0, _update)

if __name__ == "__main__":
    app = OsintApp()
    app.mainloop()