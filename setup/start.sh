#!/bin/bash

# Toujours exécuter depuis la racine du projet
cd "$(dirname "$0")"/..

# ============================================================================
# 🚀 DÉMARRAGE RAPIDE caris-dashboard-app
# ============================================================================
# Script de démarrage intelligent qui configure automatiquement l'environnement
# si nécessaire et active les environnements Python et R
# ============================================================================

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${CYAN}🚀 $1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_header "DÉMARRAGE caris-dashboard-app"

# Configuration pour Windows - Créer alias python si py existe
if command -v py &> /dev/null && ! command -v python &> /dev/null; then
    alias python='py'
    echo "📝 Alias python='py' créé pour Windows"
fi

# Vérifier si l'environnement est configuré
ENV_CONFIGURED=true

if [ ! -d "venv" ]; then
    print_warning "Environnement Python non configuré"
    ENV_CONFIGURED=false
fi

if [ ! -f "requirements.txt" ]; then
    print_warning "Fichier requirements.txt manquant"
    ENV_CONFIGURED=false
fi

if [ ! -d "outputs" ]; then
    print_warning "Structure de dossiers manquante"
    ENV_CONFIGURED=false
fi

# Configuration automatique si nécessaire
if [ "$ENV_CONFIGURED" = false ]; then
    echo -e "${YELLOW}🔧 Configuration automatique de l'environnement...${NC}"
    
    if [ ! -f "setup_complete_env.sh" ]; then
        echo -e "${RED}❌ Fichier setup_complete_env.sh manquant!${NC}"
        echo "Veuillez vous assurer d'être dans le bon répertoire du projet."
        exit 1
    fi
    
    # Exécuter la configuration
    chmod +x setup_complete_env.sh
    ./setup_complete_env.sh
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Échec de la configuration automatique${NC}"
        exit 1
    fi
fi

print_header "ACTIVATION ENVIRONNEMENT"

# Activer l'environnement Python
if [ -d "venv" ]; then
    print_step "Activation environnement Python..."
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows/Git Bash
        source venv/Scripts/activate
    else
        # Linux/macOS
        source venv/bin/activate
    fi
    
    # Vérifier l'activation
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_step "Environnement Python activé: $(basename "$VIRTUAL_ENV")"
    else
        print_warning "Problème d'activation de l'environnement Python"
    fi
else
    print_warning "Environnement virtuel Python non trouvé"
fi

# Test rapide de l'environnement
print_header "VÉRIFICATION ENVIRONNEMENT"

echo "🧪 Test rapide des packages essentiels..."

# Test Python
python -c "
import sys
packages = ['pandas', 'numpy', 'openpyxl', 'requests', 'streamlit']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        print(f'❌ {pkg} - MANQUANT')
        missing.append(pkg)

if missing:
    print(f'⚠️  {len(missing)} packages manquants')
    sys.exit(1)
else:
    print('🎉 Tous les packages essentiels sont installés!')
" 2>/dev/null

if [ $? -eq 0 ]; then
    print_step "Environnement Python validé"
else
    print_warning "Problèmes détectés dans l'environnement Python"
    echo "💡 Essayez: pip install -r requirements.txt"
fi

print_header "MENU PRINCIPAL"

echo "Que voulez-vous faire ?"
echo ""
echo "📊 PIPELINES DE DONNÉES:"
echo "  1) Pipeline Nutrition"
echo "  2) Pipeline PTME" 
echo "  3) Pipeline OEV"
echo "  4) Pipeline MUSO"
echo "  5) Pipeline Garden"
echo "  6) Pipeline Call/Appels"
echo ""
echo "📋 RAPPORTS:"
echo "  7) Générer rapport Nutrition"
echo "  8) Générer rapport PTME"
echo "  9) Générer rapport OEV"
echo "  10) Générer tous les rapports"
echo ""
echo "🔧 UTILITAIRES:"
echo "  11) Test complet environnement"
echo "  12) Interface Streamlit"
echo "  13) Shell interactif Python"
echo "  14) Ouvrir RStudio (si installé)"
echo ""
echo "  0) Quitter"
echo ""

read -p "Votre choix (0-14): " choice

case $choice in
    1)
        print_step "Exécution pipeline Nutrition..."
        python script/nutrition_pipeline.py
        ;;
    2)
        print_step "Exécution pipeline PTME..."
        python script/ptme_pipeline.py
        ;;
    3)
        print_step "Exécution pipeline OEV..."
        python script/oev_pipeline.py
        ;;
    4)
        print_step "Exécution pipeline MUSO..."
        python script/muso_pipeline.py
        ;;
    5)
        print_step "Exécution pipeline Garden..."
        python script/garden_pipeline.py
        ;;
    6)
        print_step "Exécution pipeline Call..."
        python script/call-pipeline.py
        ;;
    7)
        print_step "Génération rapport Nutrition..."
        quarto render report/tracking-nutrition.qmd
        ;;
    8)
        print_step "Génération rapport PTME..."
        quarto render report/tracking-ptme.qmd
        ;;
    9)
        print_step "Génération rapport OEV..."
        quarto render report/tracking-oev.qmd
        ;;
    10)
        print_step "Génération de tous les rapports..."
        quarto render report/
        ;;
    11)
        print_step "Test complet environnement..."
        if [ -f "test_environment.py" ]; then
            python test_environment.py
        else
            print_warning "Script de test non trouvé"
        fi
        ;;
    12)
        print_step "Démarrage interface Streamlit..."
        echo "💡 Interface sera accessible sur: http://localhost:8501"
        if [ -f "script/caris.py" ]; then
            streamlit run script/caris.py
        else
            print_warning "Interface Streamlit non trouvée"
        fi
        ;;
    13)
        print_step "Ouverture shell Python interactif..."
        python
        ;;
    14)
        print_step "Tentative d'ouverture RStudio..."
        if command -v rstudio &> /dev/null; then
            rstudio .
        else
            print_warning "RStudio non trouvé. Ouverture R console..."
            R
        fi
        ;;
    0)
        print_step "Au revoir!"
        exit 0
        ;;
    *)
        print_warning "Choix invalide"
        exit 1
        ;;
esac

print_header "TERMINÉ"
echo -e "${GREEN}🎉 Opération terminée!${NC}"
echo -e "${CYAN}💡 Pour désactiver l'environnement Python: deactivate${NC}"