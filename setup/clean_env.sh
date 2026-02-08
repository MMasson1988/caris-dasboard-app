#!/bin/bash

# ============================================================================
# 🧹 NETTOYAGE ENVIRONNEMENT CARIS-MEAL-APP
# ============================================================================
# Ce script supprime tous les environnements et permet une réinstallation propre
# ============================================================================

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${CYAN}🧹 $1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_header "NETTOYAGE ENVIRONNEMENT CARIS-MEAL-APP"

echo -e "${RED}⚠️  ATTENTION: Cette opération va supprimer:${NC}"
echo "   - L'environnement virtuel Python (venv/)"
echo "   - L'environnement R (renv/, renv.lock)"
echo "   - Les fichiers générés automatiquement"
echo ""
read -p "Êtes-vous sûr de vouloir continuer? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Nettoyage annulé."
    exit 1
fi

print_header "SUPPRESSION ENVIRONNEMENT PYTHON"

# Supprimer l'environnement virtuel Python
if [ -d "venv" ]; then
    print_step "Suppression de l'environnement virtuel Python..."
    rm -rf venv/
else
    print_warning "Aucun environnement virtuel Python trouvé"
fi

print_header "SUPPRESSION ENVIRONNEMENT R"

# Supprimer l'environnement R
if [ -d "renv" ]; then
    print_step "Suppression de l'environnement R (renv)..."
    rm -rf renv/
fi

if [ -f "renv.lock" ]; then
    print_step "Suppression du fichier renv.lock..."
    rm -f renv.lock
fi

if [ -f ".Rprofile" ]; then
    print_step "Suppression du fichier .Rprofile..."
    rm -f .Rprofile
fi

print_header "SUPPRESSION FICHIERS GÉNÉRÉS"

# Supprimer les fichiers générés automatiquement
files_to_remove=(
    "install_r_packages_auto.R"
    "activate_env.bat"
    "activate_env.sh"
    "test_environment.py"
)

for file in "${files_to_remove[@]}"; do
    if [ -f "$file" ]; then
        print_step "Suppression de $file..."
        rm -f "$file"
    fi
done

print_header "NETTOYAGE OPTIONNEL"

echo "Voulez-vous également supprimer:"
echo ""

# Proposer de supprimer requirements.txt
read -p "📄 requirements.txt? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f requirements.txt
    print_step "requirements.txt supprimé"
fi

# Proposer de supprimer les outputs
read -p "📁 Dossier outputs/ et son contenu? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf outputs/
    print_step "Dossier outputs/ supprimé"
fi

# Proposer de supprimer les logs et temp
read -p "📁 Dossiers logs/ et outputs/OEV? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf logs/ outputs/OEV
    print_step "Dossiers logs/ et outputs/OEV supprimés"
fi

print_header "NETTOYAGE TERMINÉ"

echo -e "${GREEN}🎉 ENVIRONNEMENT NETTOYÉ!${NC}"
echo ""
echo -e "${CYAN}🚀 Pour reconfigurer l'environnement:${NC}"
echo "   ./setup_complete_env.sh"
echo ""
echo -e "${YELLOW}💡 Conseil:${NC}"
echo "   Commitez vos changements avant de reconfigurer"