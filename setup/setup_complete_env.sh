#!/bin/bash

# ============================================================================
# 🚀 SETUP COMPLET ENVIRONNEMENT CARIS-MEAL-APP
# ============================================================================
# Ce script analyse automatiquement tous les packages Python et R utilisés
# dans le projet et configure un environnement complet pour l'exécution
# ============================================================================

set -e  # Arrêter en cas d'erreur

# Configuration pour Windows - Créer alias python si py existe
if command -v py &> /dev/null && ! command -v python &> /dev/null; then
    alias python='py'
    echo "📝 Alias python='py' créé pour Windows"
fi

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonction d'affichage stylé
print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${CYAN}🔧 $1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header "CONFIGURATION ENVIRONNEMENT CARIS-MEAL-APP"

# ============================================================================
# 🔍 ANALYSE DES PACKAGES PYTHON
# ============================================================================
print_header "ANALYSE DES PACKAGES PYTHON"

# Créer le fichier requirements.txt
cat > requirements.txt << 'EOF'
# ============================================================================
# REQUIREMENTS.TXT GÉNÉRÉ AUTOMATIQUEMENT - CARIS-MEAL-APP
# ============================================================================
# Packages Python identifiés dans le projet

# === TRAITEMENT DE DONNÉES ===
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0              # Pour lire/écrire Excel
xlsxwriter>=3.1.0            # Pour écrire Excel avec formatting

# === BASE DE DONNÉES ===
sqlalchemy>=2.0.0
pymysql>=1.1.0
psycopg2-binary>=2.9.0       # PostgreSQL

# === API ET REQUÊTES WEB ===
requests>=2.31.0
urllib3>=2.0.0
httpx>=0.24.0

# === INTERFACE UTILISATEUR ===
streamlit>=1.28.0
# tkinter fait partie de la bibliothèque standard Python
customtkinter>=5.2.0

# === TRAITEMENT TEXTE ET FUZZY MATCHING ===
fuzzywuzzy>=0.18.0
python-levenshtein>=0.21.0   # Accélère fuzzywuzzy
thefuzz>=0.19.0              # Version moderne de fuzzywuzzy

# === VISUALISATION ===
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.15.0

# === UTILITAIRES SYSTÈME ===
python-dotenv>=1.0.0         # Variables d'environnement
# pathlib, os, sys, glob font partie de la bibliothèque standard Python

# === SELENIUM ET AUTOMATION ===
selenium>=4.15.0
webdriver-manager>=4.0.0
beautifulsoup4>=4.12.0

# === DATES ET TEMPS ===
# datetime fait partie de la bibliothèque standard Python
python-dateutil>=2.8.2      # Extensions pour datetime (pour relativedelta)
pytz>=2023.3

# === MATH ET STATISTIQUES ===
scipy>=1.11.0
scikit-learn>=1.3.0

# === JUPYTER ET QUARTO ===
jupyter>=1.0.0
ipykernel>=6.25.0
nbformat>=5.9.0

# === DÉVELOPPEMENT ===
pytest>=7.4.0
black>=23.7.0
flake8>=6.1.0

# === PACKAGES SPÉCIFIQUES DÉTECTÉS ===
# commcare-export>=2.0.0    # Décommenter si utilisé pour CommCare
python-docx>=0.8.11         # Traitement documents Word
EOF

print_step "Fichier requirements.txt généré avec tous les packages détectés"

# ============================================================================
# 🔍 ANALYSE DES PACKAGES R
# ============================================================================
print_header "ANALYSE DES PACKAGES R"

# Analyser tous les fichiers R et Quarto pour détecter les packages
echo "📊 Recherche des packages R utilisés..."

# Créer le fichier renv.lock de base si il n'existe pas
if [ ! -f "renv.lock" ]; then
    cat > renv.lock << 'EOF'
{
  "R": {
    "Version": "4.3.0",
    "Repositories": [
      {
        "Name": "CRAN",
        "URL": "https://cran.rstudio.com"
      }
    ]
  },
  "Packages": {
    "renv": {
      "Package": "renv",
      "Version": "1.0.3",
      "Source": "Repository",
      "Repository": "CRAN"
    }
  }
}
EOF
    print_step "Fichier renv.lock de base créé"
fi

# Créer un script R pour installer les packages détectés
cat > install_r_packages_auto.R << 'EOF'
# ============================================================================
# INSTALLATION AUTOMATIQUE DES PACKAGES R - CARIS-MEAL-APP
# ============================================================================

# Packages R détectés dans le projet
required_packages <- c(
  # === BASE R ET DONNÉES ===
  "base", "utils", "stats", "graphics", "datasets",
  
  # === TRAITEMENT DONNÉES ===
  "dplyr", "tidyr", "readr", "readxl", "writexl",
  "data.table", "tibble", "purrr", "stringr",
  
  # === VISUALISATION ===
  "ggplot2", "plotly", "DT", "htmlwidgets",
  "leaflet", "shiny", "shinydashboard",
  
  # === QUARTO ET RAPPORTS ===
  "rmarkdown", "knitr", "quarto", "flexdashboard",
  
  # === DATES ET TEMPS ===
  "lubridate", "hms",
  
  # === BASE DE DONNÉES ===
  "DBI", "RMySQL", "odbc", "RODBC",
  
  # === STATISTIQUES ===
  "broom", "modelr", "forcats",
  
  # === UTILITAIRES ===
  "here", "fs", "glue", "magrittr",
  
  # === DÉVELOPPEMENT ===
  "devtools", "usethis", "testthat"
)

# Installer renv si nécessaire
if (!require(renv, quietly = TRUE)) {
  install.packages("renv")
}

# Initialiser renv si nécessaire
if (!file.exists("renv.lock") || !dir.exists("renv")) {
  cat("🔧 Initialisation de renv...\n")
  renv::init(restart = FALSE)
}

# Activer renv
renv::activate()

# Fonction pour installer les packages manquants
install_if_missing <- function(packages) {
  for (pkg in packages) {
    if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
      cat(paste("📦 Installation de", pkg, "...\n"))
      try({
        renv::install(pkg)
      }, silent = FALSE)
    } else {
      cat(paste("✅", pkg, "déjà installé\n"))
    }
  }
}

# Installer tous les packages
cat("🚀 Installation des packages R...\n")
install_if_missing(required_packages)

# Sauvegarder l'état
cat("💾 Sauvegarde de l'environnement renv...\n")
renv::snapshot()

cat("✅ Configuration R terminée!\n")
EOF

print_step "Script d'installation R généré"

# ============================================================================
# 🐍 CONFIGURATION ENVIRONNEMENT PYTHON
# ============================================================================
print_header "CONFIGURATION ENVIRONNEMENT PYTHON"

# Vérifier si Python est installé
if ! command -v python &> /dev/null; then
    print_error "Python n'est pas installé ou pas accessible!"
    echo "Veuillez installer Python 3.8+ et l'ajouter au PATH."
    echo "Windows: https://python.org/downloads/"
    echo "Ou désactiver l'alias Microsoft Store dans Settings > Apps > App execution aliases"
    exit 1
fi

# Vérifier la version Python
print_step "Version Python détectée: $(python --version)"

# Créer l'environnement virtuel
if [ ! -d "venv" ]; then
    print_step "Création de l'environnement virtuel Python..."
    python -m venv venv
else
    print_warning "Environnement virtuel existant détecté"
fi

# Activer l'environnement virtuel
print_step "Activation de l'environnement virtuel..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows/Git Bash
    source venv/Scripts/activate
else
    # Linux/macOS
    source venv/bin/activate
fi

# Mettre à jour pip
print_step "Mise à jour de pip..."
python -m pip install --upgrade pip

# Installer les requirements
print_step "Installation des packages Python..."
pip install -r requirements.txt

print_step "Environnement Python configuré!"

# ============================================================================
# 📊 CONFIGURATION ENVIRONNEMENT R
# ============================================================================
print_header "CONFIGURATION ENVIRONNEMENT R"

# Vérifier si R est installé
if command -v R &> /dev/null; then
    print_step "Exécution du script d'installation R..."
    R --vanilla < install_r_packages_auto.R
    print_step "Environnement R configuré!"
else
    print_warning "R n'est pas installé - configuration R ignorée"
    echo "Pour installer R: https://cran.r-project.org/"
fi

# ============================================================================
# 📁 CRÉATION DE LA STRUCTURE DES DOSSIERS
# ============================================================================
print_header "CRÉATION STRUCTURE DOSSIERS"

# Créer tous les dossiers nécessaires
mkdir -p outputs/{PTME,NUTRITION,OEV,MUSO,GARDEN,CALL}
mkdir -p data inputs logs temp

# Créer les fichiers .gitkeep pour préserver la structure
touch outputs/.gitkeep
touch outputs/PTME/.gitkeep
touch outputs/NUTRITION/.gitkeep
touch outputs/OEV/.gitkeep
touch outputs/MUSO/.gitkeep
touch outputs/GARDEN/.gitkeep
touch outputs/CALL/.gitkeep
touch data/.gitkeep
touch logs/.gitkeep
touch outputs/OEV.gitkeep

print_step "Structure des dossiers créée"

# ============================================================================
# 🔧 CRÉATION SCRIPTS D'ACTIVATION
# ============================================================================
print_header "CRÉATION SCRIPTS D'ACTIVATION"

# Script d'activation pour Windows
cat > activate_env.bat << 'EOF'
@echo off
echo 🚀 Activation environnement CARIS-MEAL-APP...
call venv\Scripts\activate.bat
echo ✅ Environnement Python activé!
echo 📊 Pour R, utilisez RStudio ou R console
echo 💡 Pour désactiver: deactivate
cmd /k
EOF

# Script d'activation pour Linux/macOS/Git Bash
cat > activate_env.sh << 'EOF'
#!/bin/bash
echo "🚀 Activation environnement CARIS-MEAL-APP..."

# Créer alias python pour Windows si nécessaire
if command -v py &> /dev/null && ! command -v python &> /dev/null; then
    alias python='py'
    echo "📝 Alias python='py' créé pour Windows"
fi

source venv/bin/activate
echo "✅ Environnement Python activé!"
echo "📊 Pour R, utilisez RStudio ou R console"  
echo "💡 Pour désactiver: deactivate"
exec bash
EOF

chmod +x activate_env.sh

# Script de test
cat > test_environment.py << 'EOF'
#!/usr/bin/env python3
"""
🧪 SCRIPT DE TEST ENVIRONNEMENT CARIS-MEAL-APP
Vérifie que tous les packages essentiels sont installés
"""

import sys

def test_package(package_name, import_name=None):
    """Test si un package peut être importé"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - MANQUANT!")
        return False

def main():
    print("🧪 TEST ENVIRONNEMENT CARIS-MEAL-APP")
    print("=" * 50)
    
    # Packages essentiels à tester
    packages = [
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('openpyxl', 'openpyxl'),
        ('requests', 'requests'),
        ('streamlit', 'streamlit'),
        ('selenium', 'selenium'),
        ('fuzzywuzzy', 'fuzzywuzzy'),
        ('matplotlib', 'matplotlib'),
        ('sqlalchemy', 'sqlalchemy'),
    ]
    
    success_count = 0
    for pkg_name, import_name in packages:
        if test_package(pkg_name, import_name):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 RÉSULTAT: {success_count}/{len(packages)} packages OK")
    
    if success_count == len(packages):
        print("🎉 ENVIRONNEMENT PRÊT!")
        return 0
    else:
        print("⚠️  Certains packages sont manquants")
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x test_environment.py

print_step "Scripts d'activation créés"

# ============================================================================
# 🧪 TEST FINAL
# ============================================================================
print_header "TEST ENVIRONNEMENT"

echo "🧪 Test de l'environnement Python..."
python test_environment.py

# ============================================================================
# 📋 RÉSUMÉ
# ============================================================================
print_header "CONFIGURATION TERMINÉE"

echo -e "${GREEN}🎉 ENVIRONNEMENT CARIS-MEAL-APP CONFIGURÉ!${NC}"
echo ""
echo -e "${CYAN}📁 Fichiers créés:${NC}"
echo "  ✅ requirements.txt        - Packages Python"
echo "  ✅ renv.lock              - Environnement R"
echo "  ✅ venv/                  - Environnement virtuel Python"
echo "  ✅ activate_env.sh/.bat   - Scripts d'activation"
echo "  ✅ test_environment.py    - Script de test"
echo ""
echo -e "${CYAN}🚀 Pour utiliser l'environnement:${NC}"
echo "  Windows: activate_env.bat"
echo "  Linux/macOS: ./activate_env.sh"
echo ""
echo -e "${CYAN}📊 Pour exécuter les scripts:${NC}"
echo "  Python: python script/nom_du_script.py"
echo "  Quarto: quarto render report/nom_du_rapport.qmd"
echo ""
echo -e "${PURPLE}🔧 Environnement prêt pour l'exécution complète!${NC}"