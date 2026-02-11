#!/bin/bash

# Script d'installation simplifié et robuste pour caris-dashboard-app
# Usage: bash install_venv_fixed.sh

echo "======================================"
echo "CARIS MEAL APP - Installation Python"
echo "======================================"

# Fonction pour afficher les messages
print_message() {
    echo ">>> $1"
}

print_error() {
    echo "❌ ERREUR: $1"
}

print_success() {
    echo "✅ $1"
}

# Variables
VENV_NAME="venv"

# Vérifier Python avec une approche simple
print_message "Vérification de Python..."

# Test direct des commandes Python
if python --version >/dev/null 2>&1; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1)
elif python3 --version >/dev/null 2>&1; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1)
else
    print_error "Aucune installation Python trouvée. Veuillez installer Python 3.8+."
    echo "Téléchargez Python depuis: https://www.python.org/downloads/"
    exit 1
fi

print_success "Python détecté: $PYTHON_VERSION"

# Supprimer l'ancien venv s'il existe
if [ -d "$VENV_NAME" ]; then
    print_message "Suppression de l'ancien environnement virtuel..."
    rm -rf "$VENV_NAME"
fi

# Créer un nouvel environnement virtuel
print_message "Création de l'environnement virtuel..."
if ! $PYTHON_CMD -m venv "$VENV_NAME"; then
    print_error "Échec de la création de l'environnement virtuel"
    print_error "Vérifiez que le module venv est installé: $PYTHON_CMD -m pip install --user virtualenv"
    exit 1
fi

print_success "Environnement virtuel créé"

# Déterminer le script d'activation selon l'OS
print_message "Activation de l'environnement virtuel..."

# Détecter l'OS et définir le chemin d'activation
if [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]] || [[ -n "$WINDIR" ]]; then
    # Windows (Git Bash, MSYS2, Cygwin)
    ACTIVATE_SCRIPT="$VENV_NAME/Scripts/activate"
    if [ ! -f "$ACTIVATE_SCRIPT" ]; then
        print_error "Script d'activation introuvable: $ACTIVATE_SCRIPT"
        exit 1
    fi
else
    # Linux/macOS
    ACTIVATE_SCRIPT="$VENV_NAME/bin/activate"
    if [ ! -f "$ACTIVATE_SCRIPT" ]; then
        print_error "Script d'activation introuvable: $ACTIVATE_SCRIPT"
        exit 1
    fi
fi

# Activer l'environnement virtuel
if ! source "$ACTIVATE_SCRIPT"; then
    print_error "Échec de l'activation de l'environnement virtuel"
    exit 1
fi

print_success "Environnement virtuel activé"

# Vérifier que nous sommes dans le venv
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_error "L'environnement virtuel n'est pas correctement activé"
    exit 1
fi

# Mettre à jour pip
print_message "Mise à jour de pip..."
if ! python -m pip install --upgrade pip; then
    print_error "Échec de la mise à jour de pip"
    exit 1
fi

print_success "Pip mis à jour"

# Installer les dépendances de base
print_message "Installation des dépendances de base..."
BASE_PACKAGES=(
    "pandas"
    "numpy" 
    "openpyxl"
    "xlsxwriter"
    "python-dotenv"
    "requests"
)

for package in "${BASE_PACKAGES[@]}"; do
    print_message "Installation de $package..."
    if ! python -m pip install "$package"; then
        print_error "Échec de l'installation de $package"
        exit 1
    fi
done

print_success "Dépendances de base installées"

# Installer les dépendances optionnelles
print_message "Installation des dépendances optionnelles..."
OPTIONAL_PACKAGES=(
    "matplotlib"
    "seaborn"
    "pymysql"
    "sqlalchemy"
    "python-dateutil"
)

for package in "${OPTIONAL_PACKAGES[@]}"; do
    print_message "Installation de $package..."
    if ! python -m pip install "$package"; then
        echo "⚠️  Échec de l'installation de $package (optionnel)"
    fi
done

# Générer requirements.txt
print_message "Génération du fichier requirements.txt..."
python -m pip freeze > requirements.txt

print_success "Fichier requirements.txt créé"

echo ""
echo "======================================"
echo "✅ INSTALLATION TERMINÉE AVEC SUCCÈS"
echo "======================================"
echo ""
echo "Pour activer l'environnement virtuel dans le futur:"
if [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]] || [[ -n "$WINDIR" ]]; then
    echo "  source venv/Scripts/activate"
else
    echo "  source venv/bin/activate"
fi
echo ""
echo "Pour désactiver l'environnement:"
echo "  deactivate"
echo ""
echo "Pour exécuter vos scripts:"
echo "  python commcare_downloader.py"
echo ""
echo "======================================"