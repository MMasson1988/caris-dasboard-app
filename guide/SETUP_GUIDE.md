# 🚀 GUIDE D'UTILISATION - SETUP ENVIRONNEMENT caris-dashboard-app

## 📋 DESCRIPTION
Le script `setup_complete_env.sh` automatise complètement la configuration de l'environnement de développement pour le projet caris-dashboard-app.

## 🔍 QUE FAIT LE SCRIPT ?

### 1. 📦 **Analyse automatique des packages**
- **Python** : Scanne tous les fichiers `.py` et détecte les imports
- **R** : Analyse les fichiers `.R` et `.qmd` pour identifier les packages
- **Génère** : `requirements.txt` complet avec tous les packages détectés

### 2. 🐍 **Configuration Python**
- Crée un environnement virtuel `venv/`
- Installe tous les packages Python nécessaires
- Configure l'environnement pour l'exécution des scripts

### 3. 📊 **Configuration R**
- Initialise `renv` pour la gestion des packages R
- Installe tous les packages R détectés
- Crée `renv.lock` pour la reproductibilité

### 4. 📁 **Structure des dossiers**
- Crée tous les dossiers de sortie (`outputs/PTME/`, `outputs/NUTRITION/`, etc.)
- Ajoute des fichiers `.gitkeep` pour préserver la structure dans Git

### 5. 🔧 **Scripts utilitaires**
- `activate_env.sh` / `activate_env.bat` : Activation rapide de l'environnement
- `test_environment.py` : Test de l'environnement configuré

## 🚀 UTILISATION

### Exécution complète (recommandée)
```bash
# Rendre le script exécutable (une seule fois)
chmod +x setup_complete_env.sh

# Exécuter la configuration complète
./setup_complete_env.sh
```

### Activation de l'environnement après configuration
```bash
# Windows (Git Bash)
./activate_env.sh

# Windows (Command Prompt)
activate_env.bat
```

### Test de l'environnement
```bash
# Activer l'environnement puis tester
source venv/Scripts/activate  # Windows Git Bash
# ou
source venv/bin/activate      # Linux/macOS

python test_environment.py
```

## 📊 EXÉCUTION DES SCRIPTS APRÈS CONFIGURATION

### Scripts Python
```bash
# Activer l'environnement
./activate_env.sh

# Exécuter les pipelines
python script/nutrition_pipeline.py
python script/ptme_pipeline.py
python script/oev_pipeline.py
python script/muso_pipeline.py
```

### Rapports Quarto
```bash
# Générer tous les rapports
quarto render report/

# Ou individuellement
quarto render report/tracking-nutrition.qmd
quarto render report/tracking-ptme.qmd
```

## 🔧 PACKAGES INCLUS

### Python (requirements.txt)
- **Données** : pandas, numpy, openpyxl, xlsxwriter
- **API** : requests, httpx, urllib3
- **GUI** : streamlit, tkinter, customtkinter
- **Fuzzy** : fuzzywuzzy, thefuzz, python-levenshtein
- **Viz** : matplotlib, seaborn, plotly
- **DB** : sqlalchemy, pymysql, psycopg2-binary
- **Automation** : selenium, webdriver-manager
- **Dev** : pytest, black, flake8

### R (renv.lock)
- **Données** : dplyr, tidyr, readr, readxl, data.table
- **Viz** : ggplot2, plotly, DT, shiny, shinydashboard
- **Rapports** : rmarkdown, knitr, quarto
- **DB** : DBI, RMySQL, odbc
- **Utils** : lubridate, here, fs, glue

## 🎯 AVANTAGES

### ✅ **Automatisation complète**
- Aucune configuration manuelle requise
- Détection automatique de tous les packages
- Setup en une seule commande

### ✅ **Reproductibilité**
- Versions fixées dans requirements.txt
- renv.lock pour R
- Environnement isolé

### ✅ **Portabilité**
- Fonctionne sur Windows, Linux, macOS
- Scripts d'activation adaptés à chaque OS
- Structure de dossiers cohérente

### ✅ **Maintenabilité**
- Test automatique de l'environnement
- Scripts de réactivation rapide
- Documentation intégrée

## ⚠️ PRÉREQUIS

- **Python 3.8+** installé et dans le PATH
- **R 4.0+** installé (optionnel, pour les rapports Quarto)
- **Git** installé
- **Quarto CLI** installé (pour les rapports)

## 🆘 RÉSOLUTION DES PROBLÈMES

### Problème d'installation Python
```bash
# Vérifier Python
python --version

# Si problème, réinstaller l'environnement
rm -rf venv/
./setup_complete_env.sh
```

### Problème d'installation R
```bash
# Vérifier R
R --version

# Réinitialiser renv
rm -rf renv/ renv.lock
R -e "renv::init()"
```

### Problème de permissions
```bash
# Linux/macOS
sudo chmod +x setup_complete_env.sh

# Windows Git Bash
chmod +x setup_complete_env.sh
```

## 🔄 MISE À JOUR

Pour ajouter de nouveaux packages :
1. Modifier `requirements.txt` pour Python
2. Modifier `install_r_packages_auto.R` pour R
3. Réexécuter `./setup_complete_env.sh`

---

🎉 **Avec ce script, votre environnement caris-dashboard-app est prêt en moins de 5 minutes !**