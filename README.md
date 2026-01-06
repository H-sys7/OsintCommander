# 👁️ OsintCommander

L’Open Source Intelligence (OSINT) désigne l’ensemble des techniques permettant de collecter et d’analyser des informations accessibles publiquement.
Toutefois, le volume et l’hétérogénéité des données disponibles rendent l’analyse manuelle longue, fastidieuse et sujette aux erreurs. 
Il devient nécessaire de disposer d’outils capables d’automatiser la collecte d’informations tout en proposant une synthèse claire et exploitable.

Ce projet a pour objectif la conception et la réalisation d’un outil OSINT modulaire, capable d’orchestrer plusieurs sources de collecte, de normaliser les résultats et de proposer une analyse assistée par intelligence artificielle.
L’outil vise à être pédagogique, extensible et utilisable dans un cadre académique ou d’initiation à l’OSINT.

---

📦 Installation du projet
1. Prérequis
 - Python 3.10 ou plus récent
 - Système : Windows (WSL recommandé) / Linux
 - Accès administrateur pour certains outils (Nmap)

2. Installation des dépendances Python

```bash
  python -m venv venv
  venv\Scripts\activate   # Windows
  # source venv/bin/activate  # Linux / WSL
  pip install -r requirements.txt
```

🧰 Installation des outils externes
  🔍 Nmap
  https://nmap.org/download.html

  🟦 Go (Golang)
  https://go.dev/dl/
    Pour vérifier 
    ```bash
        go version
    ```
  🔎 Outils OSINT basés sur Go
   ```bash
    go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest
    go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
  ```

🐧 Installation de TheHarvester (via WSL)

Recommandé pour éviter les conflits Windows
  ```bash
    wsl --install
    wsl --install -d Ubuntu
  ```

Puis dans Ubuntu :
  ```bash
    sudo apt update
    sudo apt install -y git python3 python3-pip python3-venv
    git clone https://github.com/laramies/theHarvester.git
    cd theHarvester
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
  ```

⚙️ Configuration du fichier .env

Créer un fichier .env à la racine du projet :
  ```bash
    # --- API OSINT ---
    HIBP_API_KEY=xxxxxxxx
    CENSYS_API_ID=xxxxxxxx
    CENSYS_API_SECRET=xxxxxxxx
    CRIMINALIP_API_KEY=xxxxxxxx
    
    # --- IA ---
    GROQ_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
    
    # --- Outils externes ---
    THEHARVESTER_PATH=/home/user/theHarvester
  ```
⚠️ # ---Assurer vous que le chemin de theharvester est bien conforme a celui de votre appareil ---

▶️ Lancement du projet
 ```bash
    python main.py
```   
