# ==========================================================
# Script d'installation assistée - OsintCommander
# Auteur : Projet étudiant OSINT
# ==========================================================

Write-Host ""
Write-Host "==============================================="
Write-Host " Installation assistée des dépendances OSINT"
Write-Host "==============================================="
Write-Host ""

function Test-Tool {
    param ($name)
    return Get-Command $name -ErrorAction SilentlyContinue
}

# ----------------------------------------------------------
# PYTHON
# ----------------------------------------------------------
if (-not (Check-Tool "python")) {
    Write-Host "[!] Python n'est pas installé."
    Write-Host "Téléchargement : https://www.python.org/downloads/"
    Start-Process "https://www.python.org/downloads/"
}
else {
    Write-Host "[OK] Python détecté"
}

# ----------------------------------------------------------
# NMAP
# ----------------------------------------------------------
if (-not (Check-Tool "nmap")) {
    Write-Host "[!] Nmap non détecté"
    Write-Host "Téléchargement : https://nmap.org/download.html"
    Start-Process "https://nmap.org/download.html"
}
else {
    Write-Host "[OK] Nmap détecté"
}

# ----------------------------------------------------------
# PROJECTDISCOVERY TOOLS
# ----------------------------------------------------------
$pd_tools = @("subfinder", "httpx", "nuclei")

foreach ($tool in $pd_tools) {
    if (-not (Check-Tool $tool)) {
        Write-Host "[!] $tool non détecté"
        Write-Host "Téléchargement : https://github.com/projectdiscovery/$tool/releases"
        Start-Process "https://github.com/projectdiscovery/$tool/releases"
    }
    else {
        Write-Host "[OK] $tool détecté"
    }
}

# ----------------------------------------------------------
# MAIGRET
# ----------------------------------------------------------
if (-not (Check-Tool "maigret")) {
    Write-Host "[!] Maigret non détecté"
    Write-Host "Installation via pip : pip install maigret"
}
else {
    Write-Host "[OK] Maigret détecté"
}

# ----------------------------------------------------------
# CENSYS (CLI facultatif)
# ----------------------------------------------------------
if (-not (Check-Tool "censys")) {
    Write-Host "[!] Censys CLI non détecté (optionnel)"
    Write-Host "Installation : pip install censys"
}
else {
    Write-Host "[OK] Censys CLI détecté"
}

# ----------------------------------------------------------
# FIN
# ----------------------------------------------------------
Write-Host ""
Write-Host "==============================================="
Write-Host " Vérification terminée"
Write-Host " Redémarrez le programme après installation"
Write-Host "==============================================="
Pause
