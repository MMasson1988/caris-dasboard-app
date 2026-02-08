# 🍽️ CARIS-MEAL-APP

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![R](https://img.shields.io/badge/R-4.0+-blue.svg)](https://r-project.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Description

Application complète de traitement et d'analyse des données pour le programme **CARIS** (Comprehensive AIDS Resources International). Cette application automatise le traitement des données de santé, la génération de rapports et le suivi des programmes nutritionnels, PTME, OEV, MUSO et jardinage.

## 🚀 Démarrage Rapide (Recommandé)

### Installation automatique complète
```bash
# 1. Cloner le repository
git clone https://github.com/MMasson1988/caris-meal-app.git
cd caris-meal-app

# 2. Configuration automatique (une seule commande!)
./config/setup_complete_env.sh

# 3. Démarrage avec menu interactif
./config/start.sh
```

### ⚡ Démarrage ultra-rapide
```bash
# Démarrage avec configuration automatique si nécessaire
./config/start.sh
```

## 📁 Structure du Projet

```
caris-meal-app/
├── 🐍 script/                    # Scripts Python
│   ├── nutrition_pipeline.py     # Pipeline nutrition
│   ├── ptme_pipeline.py          # Pipeline PTME
│   ├── oev_pipeline.py           # Pipeline OEV
│   ├── muso_pipeline.py          # Pipeline MUSO
│   ├── garden_pipeline.py        # Pipeline jardinage
│   └── call-pipeline.py          # Pipeline appels/visites
│
├── 📊 report/                    # Rapports Quarto
│   ├── tracking-nutrition.qmd    # Rapport nutrition
│   ├── tracking-ptme.qmd         # Rapport PTME
│   ├── tracking-oev.qmd          # Rapport OEV
│   └── tracking-*.qmd            # Autres rapports
│
├── 📂 data/                     # Données d'entrée
├── 📂 input/                    # Fichiers de référence Excel
├── 📈 outputs/                  # Résultats générés
│   ├── NUTRITION/               # Sorties nutrition
│   ├── PTME/                    # Sorties PTME
│   ├── OEV/                     # Sorties OEV
│   ├── MUSO/                    # Sorties MUSO
│   ├── GARDEN/                  # Sorties jardinage
│   └── CALL/                    # Sorties appels
│
├── 🔧 config/                   # Scripts shell et batch
│   ├── setup_complete_env.sh     # 🚀 Setup automatique
│   ├── start.sh                  # 🎯 Démarrage rapide
│   ├── clean_env.sh              # 🧹 Nettoyage
│   └── *.bat, *.sh              # Autres scripts config
│
├── requirements.txt              # 🐍 Packages Python
└── renv.lock                    # 📊 Packages R
```

## 🛠️ Scripts de Configuration

### 🚀 `setup_complete_env.sh` - Configuration Automatique
**Le script principal qui fait tout automatiquement :**
- ✅ Analyse tous les packages Python/R utilisés
- ✅ Génère `requirements.txt` complet
- ✅ Crée environnement virtuel Python
- ✅ Configure environnement R avec renv
- ✅ Crée structure de dossiers
- ✅ Installe tous les packages
- ✅ Génère scripts d'activation

### 🎯 `start.sh` - Démarrage Rapide
**Script intelligent avec menu interactif :**
- 🔍 Détecte automatiquement si l'environnement est configuré
- ⚙️ Lance la configuration automatique si nécessaire
- 🎮 Menu interactif pour exécuter pipelines et rapports
- 🧪 Test de l'environnement intégré

### 🧹 `clean_env.sh` - Nettoyage
**Pour réinitialiser complètement l'environnement :**
- 🗑️ Supprime environnements Python et R
- 🧹 Nettoie les fichiers générés
- 🔄 Permet une réinstallation propre

## 📊 Pipelines Disponibles

| Pipeline | Script | Description |
|----------|--------|-------------|
| **Nutrition** | `nutrition_pipeline.py` | Traitement données nutritionnelles |
| **PTME** | `ptme_pipeline.py` | Prévention transmission mère-enfant |
| **OEV** | `oev_pipeline.py` | Orphelins et enfants vulnérables |
| **MUSO** | `muso_pipeline.py` | Mutuelles de santé |
| **Jardinage** | `garden_pipeline.py` | Programme jardinage |
| **Appels** | `call-pipeline.py` | Suivi appels et visites |

## 📋 Rapports Générés

| Rapport | Fichier | Format |
|---------|---------|---------|
| **Nutrition** | `tracking-nutrition.html` | HTML interactif |
| **PTME** | `tracking-ptme.html` | HTML interactif |
| **OEV** | `tracking-oev.html` | HTML interactif |
| **MUSO** | `tracking-muso.html` | HTML interactif |
| **Jardinage** | `tracking-gardening.html` | HTML interactif |
| **Appels** | `tracking-call.html` | HTML interactif |

## 🔧 Installation Manuelle (Avancée)

Si vous préférez configurer manuellement :

### Prérequis
- **Python 3.8+**
- **R 4.0+** (optionnel)
- **Quarto CLI** (pour rapports)
- **Git**

### Python
```bash
# Créer environnement virtuel
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
# ou source venv/bin/activate # Linux/macOS

# Installer packages
pip install -r requirements.txt
```

### R (optionnel)
```bash
# Dans R console
install.packages("renv")
renv::init()
renv::restore()
```

## 🎮 Utilisation

### Menu Interactif (Recommandé)
```bash
./config/start.sh
```

### Exécution Directe
```bash
# Activer l'environnement
./config/activate_env.sh

# Exécuter un pipeline
python script/nutrition_pipeline.py

# Générer un rapport
quarto render report/tracking-nutrition.qmd
```

### Interface Web Streamlit
```bash
streamlit run script/caris.py
```

## 🧪 Test et Validation

### Test automatique
```bash
python test_environment.py
```

### Validation complète
```bash
# Via le menu interactif
./config/start.sh
# Choisir option "11) Test complet environnement"
```

## 🆘 Résolution des Problèmes

### Réinstallation complète
```bash
# Nettoyer complètement
./clean_env.sh

# Reconfigurer
./setup_complete_env.sh
```

### Problème spécifique Python
```bash
# Réinstaller seulement Python
rm -rf venv/
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

### Problème spécifique R
```bash
# Réinitialiser renv
rm -rf renv/ renv.lock
R -e "renv::init()"
```

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** : Guide détaillé de configuration
- **[Wiki](../../wiki)** : Documentation complète du projet
- **Code** : Documentation inline dans tous les scripts

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Push vers la branche
5. Ouvrir une Pull Request

## 📄 License

MIT License - voir [LICENSE](LICENSE) pour plus de détails.

## 📞 Support

- **Issues** : [GitHub Issues](../../issues)
- **Discussions** : [GitHub Discussions](../../discussions)
- **Email** : [moise.masson@example.com](mailto:moise.masson@example.com)

---

🎉 **Avec CARIS-MEAL-APP, votre analyse de données de santé est automatisée et prête en quelques minutes !**
