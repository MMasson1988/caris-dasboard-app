# 🖥️ Guide d'Exécution Locale sur VSCode

## Vue d'ensemble

Ce guide vous montre comment exécuter les pipelines et générer les rapports localement sur votre machine avec VSCode, **avant** de pousser vers GitHub.

---

## 📋 Prérequis

### 1. Logiciels Requis

#### Python 3.11+
```bash
# Vérifier la version
python --version
# ou
python3 --version
```

#### R 4.3+
```bash
# Vérifier la version
Rscript --version
```

#### Quarto
```bash
# Vérifier l'installation
quarto --version

# Si non installé, télécharger depuis:
# https://quarto.org/docs/get-started/
```

#### Git
```bash
git --version
```

---

## 🚀 Installation et Configuration

### Étape 1: Cloner le Projet

```bash
# Cloner depuis GitHub
git clone https://github.com/MMasson1988/caris-dasboard-app.git
cd caris-dasboard-app

# Basculer vers la branche workflow-automation-fresh
git checkout workflow-automation-fresh
```

### Étape 2: Ouvrir dans VSCode

```bash
# Ouvrir le projet dans VSCode
code .
```

### Étape 3: Installer les Dépendances Python

#### Option A: Environnement Virtuel (Recommandé)

```bash
# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

#### Option B: Installation Globale

```bash
pip install -r requirements.txt
```

### Étape 4: Installer les Dépendances R

```bash
# Exécuter le script d'installation R
Rscript setup/install_r_dependencies.R
```

---

## 🔧 Exécution des Pipelines

### Méthode 1: Exécuter UN Pipeline Spécifique

#### Dans le Terminal VSCode:

```bash
# Pipeline Nutrition
python script/nutrition_pipeline.py

# Pipeline MUSO
python script/muso_pipeline.py

# Pipeline Garden
python script/garden_pipeline.py

# Pipeline OEV
python script/oev_pipeline.py

# Pipeline PTME
python script/ptme_pipeline.py

# Pipeline Call
python script/call-pipeline.py
```

#### Avec le Débogueur VSCode:

1. Ouvrir le fichier pipeline (ex: `script/nutrition_pipeline.py`)
2. Appuyer sur **F5** ou cliquer sur "Run and Debug"
3. Sélectionner "Python File"

### Méthode 2: Exécuter TOUS les Pipelines

Créez un script helper:

```bash
# Créer le script
cat > run_all_pipelines.sh << 'EOF'
#!/bin/bash
echo "🚀 Exécution de tous les pipelines..."
echo ""

pipelines=(
    "script/call-pipeline.py"
    "script/garden_pipeline.py"
    "script/muso_pipeline.py"
    "script/nutrition_pipeline.py"
    "script/oev_pipeline.py"
    "script/ptme_pipeline.py"
)

for pipeline in "${pipelines[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "▶️  Exécution: $pipeline"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if python "$pipeline"; then
        echo "✅ Succès: $pipeline"
    else
        echo "❌ Échec: $pipeline"
        exit 1
    fi
    echo ""
done

echo "🎉 Tous les pipelines ont été exécutés avec succès!"
EOF

# Rendre exécutable
chmod +x run_all_pipelines.sh

# Exécuter
./run_all_pipelines.sh
```

#### Windows (PowerShell):

```powershell
# Créer run_all_pipelines.ps1
$pipelines = @(
    "script/call-pipeline.py",
    "script/garden_pipeline.py",
    "script/muso_pipeline.py",
    "script/nutrition_pipeline.py",
    "script/oev_pipeline.py",
    "script/ptme_pipeline.py"
)

foreach ($pipeline in $pipelines) {
    Write-Host "▶️  Exécution: $pipeline" -ForegroundColor Cyan
    python $pipeline
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Succès: $pipeline" -ForegroundColor Green
    } else {
        Write-Host "❌ Échec: $pipeline" -ForegroundColor Red
        exit 1
    }
}

Write-Host "🎉 Tous les pipelines ont été exécutés!" -ForegroundColor Green
```

---

## 📄 Génération des Rapports QMD

### Méthode 1: Générer UN Rapport

```bash
# Rapport Nutrition
quarto render tracking-nutrition.qmd

# Rapport MUSO
quarto render tracking-muso.qmd

# Rapport Garden
quarto render tracking-gardening.qmd

# Rapport OEV
quarto render tracking-oev.qmd

# Rapport PTME
quarto render tracking-ptme.qmd

# Rapport Call
quarto render tracking-call.qmd
```

### Méthode 2: Générer TOUS les Rapports

```bash
# Linux/macOS
for file in tracking-*.qmd; do
    echo "📄 Génération: $file"
    quarto render "$file"
done

# Windows PowerShell
Get-ChildItem tracking-*.qmd | ForEach-Object {
    Write-Host "📄 Génération: $_"
    quarto render $_
}
```

### Méthode 3: Mode Preview (Avec Rechargement Auto)

```bash
# Ouvre le rapport dans le navigateur avec rechargement automatique
quarto preview tracking-nutrition.qmd

# Arrêter avec Ctrl+C
```

---

## 🎯 Workflow Complet Local

### Script Automatisé (Recommandé)

Créez `run_local_workflow.sh`:

```bash
#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Workflow Local - Pipelines + Rapports QMD             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Étape 1: Exécuter tous les pipelines
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ÉTAPE 1: Exécution des Pipelines Python"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

pipelines=(
    "script/call-pipeline.py"
    "script/garden_pipeline.py"
    "script/muso_pipeline.py"
    "script/nutrition_pipeline.py"
    "script/oev_pipeline.py"
    "script/ptme_pipeline.py"
)

for pipeline in "${pipelines[@]}"; do
    echo "▶️  $pipeline"
    if python "$pipeline"; then
        echo "   ✅ Succès"
    else
        echo "   ❌ Échec"
        exit 1
    fi
    echo ""
done

# Étape 2: Générer tous les rapports QMD
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ÉTAPE 2: Génération des Rapports QMD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for qmd in tracking-*.qmd; do
    echo "📄 $qmd"
    if quarto render "$qmd"; then
        echo "   ✅ Succès"
    else
        echo "   ❌ Échec"
        exit 1
    fi
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Workflow Local Terminé avec Succès!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Résultats:"
echo "   - Fichiers Excel: outputs/*/\*.xlsx"
echo "   - Rapports HTML: tracking-*.html"
echo "   - Site Quarto: _site/"
```

Puis exécutez:

```bash
chmod +x run_local_workflow.sh
./run_local_workflow.sh
```

---

## 📂 Structure des Fichiers Générés

Après l'exécution, vous aurez:

```
votre-projet/
├── outputs/
│   ├── NUTRITION/
│   │   ├── depistage_filtered.xlsx
│   │   ├── enroled_final.xlsx
│   │   ├── suivi_nutritionel.xlsx
│   │   └── ...
│   ├── MUSO/
│   ├── GARDEN/
│   ├── OEV/
│   └── PTME/
│
├── tracking-nutrition.html     ← Rapport HTML
├── tracking-muso.html
├── tracking-gardening.html
├── tracking-oev.html
├── tracking-ptme.html
├── tracking-call.html
│
└── _site/                      ← Site Quarto complet
    ├── index.html
    └── ...
```

---

## 🔍 Visualiser les Résultats

### Ouvrir les Rapports HTML

#### Option 1: Double-clic
- Naviguer vers le fichier `.html` dans l'explorateur
- Double-cliquer pour ouvrir dans le navigateur

#### Option 2: VSCode Live Server
1. Installer l'extension "Live Server" dans VSCode
2. Clic droit sur un fichier `.html`
3. Sélectionner "Open with Live Server"

#### Option 3: Ligne de Commande
```bash
# macOS
open tracking-nutrition.html

# Linux
xdg-open tracking-nutrition.html

# Windows
start tracking-nutrition.html
```

---

## 🐛 Dépannage

### Problème 1: Module Python Manquant

**Erreur:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### Problème 2: Erreur R

**Erreur:**
```
Error in library(DT) : there is no package called 'DT'
```

**Solution:**
```bash
Rscript setup/install_r_dependencies.R
```

### Problème 3: Quarto Non Trouvé

**Erreur:**
```
quarto: command not found
```

**Solution:**
1. Télécharger Quarto: https://quarto.org/docs/get-started/
2. Installer selon votre OS
3. Redémarrer VSCode

### Problème 4: Fichiers de Données Manquants

**Erreur:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/...'
```

**Solution:**
```bash
# Vérifier que le dossier data/ existe et contient les fichiers
ls -la data/

# Si vide, télécharger les données depuis le serveur
# ou demander les fichiers à l'équipe
```

### Problème 5: Erreur de Chemin

**Erreur:**
```
FileNotFoundError: outputs/NUTRITION/
```

**Solution:**
```bash
# Créer les dossiers de sortie
mkdir -p outputs/{NUTRITION,MUSO,GARDEN,OEV,PTME,CALL}
```

---

## ⚙️ Configuration VSCode

### Fichier `.vscode/settings.json`

Créez ce fichier pour une meilleure expérience:

```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".venv": false
    },
    "python.analysis.extraPaths": [
        "./script"
    ]
}
```

### Fichier `.vscode/tasks.json`

Pour exécuter les pipelines avec Ctrl+Shift+B:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run All Pipelines",
            "type": "shell",
            "command": "./run_local_workflow.sh",
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        },
        {
            "label": "Run Nutrition Pipeline",
            "type": "shell",
            "command": "python script/nutrition_pipeline.py"
        },
        {
            "label": "Render All QMD",
            "type": "shell",
            "command": "for file in tracking-*.qmd; do quarto render \"$file\"; done"
        }
    ]
}
```

### Extensions VSCode Recommandées

Installez ces extensions:

1. **Python** (Microsoft) - Support Python
2. **Pylance** (Microsoft) - IntelliSense Python
3. **Quarto** (quarto.org) - Support Quarto/QMD
4. **R** (REditorSupport) - Support R
5. **Live Server** - Prévisualisation HTML
6. **GitLens** - Gestion Git avancée

---

## 📊 Exemples d'Utilisation

### Cas 1: Tester un Seul Pipeline

```bash
# 1. Activer l'environnement virtuel
source .venv/bin/activate

# 2. Exécuter le pipeline
python script/nutrition_pipeline.py

# 3. Vérifier les sorties
ls -la outputs/NUTRITION/

# 4. Générer le rapport
quarto render tracking-nutrition.qmd

# 5. Ouvrir le résultat
open tracking-nutrition.html
```

### Cas 2: Développement avec Rechargement Auto

```bash
# Terminal 1: Mode preview pour QMD
quarto preview tracking-nutrition.qmd

# Terminal 2: Exécuter le pipeline quand nécessaire
python script/nutrition_pipeline.py
# Le rapport se rechargera automatiquement!
```

### Cas 3: Workflow Complet Avant Git Push

```bash
# 1. Exécuter tout localement
./run_local_workflow.sh

# 2. Vérifier les résultats
ls outputs/*/
ls tracking-*.html

# 3. Si tout est OK, pousser vers GitHub
git add .
git commit -m "Update: data and reports"
git push

# Le workflow GitHub s'exécutera automatiquement!
```

---

## 🎓 Conseils Pro

### 1. Utiliser un Makefile

Créez `Makefile`:

```makefile
.PHONY: pipelines reports all clean

pipelines:
	@echo "🚀 Exécution des pipelines..."
	@python script/call-pipeline.py
	@python script/garden_pipeline.py
	@python script/muso_pipeline.py
	@python script/nutrition_pipeline.py
	@python script/oev_pipeline.py
	@python script/ptme_pipeline.py

reports:
	@echo "📄 Génération des rapports..."
	@for file in tracking-*.qmd; do \
		quarto render "$$file"; \
	done

all: pipelines reports

clean:
	@echo "🧹 Nettoyage..."
	@rm -f tracking-*.html
	@rm -rf _site/
```

Puis utilisez:
```bash
make pipelines  # Seulement les pipelines
make reports    # Seulement les rapports
make all        # Tout
make clean      # Nettoyer
```

### 2. Logs Détaillés

```bash
# Rediriger les logs vers un fichier
python script/nutrition_pipeline.py 2>&1 | tee logs/nutrition_$(date +%Y%m%d_%H%M%S).log
```

### 3. Mode Debug

```bash
# Exécuter avec plus d'informations
python -v script/nutrition_pipeline.py
```

---

## 📞 Aide

Si vous rencontrez des problèmes:

1. **Vérifier les prérequis:**
   ```bash
   python --version
   Rscript --version
   quarto --version
   ```

2. **Vérifier l'environnement virtuel:**
   ```bash
   which python  # Doit pointer vers .venv/
   ```

3. **Vérifier les dépendances:**
   ```bash
   pip list | grep pandas
   ```

4. **Consulter les logs d'erreur** et rechercher les messages spécifiques

---

**Dernière mise à jour:** 2025-02-17
**Auteur:** Documentation Projet Caris
