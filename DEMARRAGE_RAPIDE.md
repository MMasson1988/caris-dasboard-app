# 🚀 Démarrage Rapide - Exécution Locale

## En Bref

Pour exécuter le workflow localement dans VSCode, suivez ces 3 étapes simples:

## ⚡ Installation Rapide

```bash
# 1. Installer les dépendances Python
pip install -r requirements.txt

# 2. Installer les dépendances R
Rscript setup/install_r_dependencies.R

# 3. Installer Quarto (si pas déjà fait)
# Télécharger depuis: https://quarto.org/docs/get-started/
```

## 🎯 Exécution Rapide

### Option 1: Tout Exécuter en Une Commande

```bash
./run_local_workflow.sh
```

### Option 2: Étape par Étape

```bash
# Exécuter les pipelines
python script/nutrition_pipeline.py
python script/muso_pipeline.py
python script/garden_pipeline.py
python script/oev_pipeline.py
python script/ptme_pipeline.py
python script/call-pipeline.py

# Générer les rapports
quarto render tracking-nutrition.qmd
quarto render tracking-muso.qmd
quarto render tracking-gardening.qmd
quarto render tracking-oev.qmd
quarto render tracking-ptme.qmd
quarto render tracking-call.qmd
```

## 📂 Résultats

Après l'exécution:

```
outputs/
├── NUTRITION/*.xlsx    ← Données générées
├── MUSO/*.xlsx
├── GARDEN/*.xlsx
└── ...

tracking-*.html         ← Rapports HTML
_site/                  ← Site Quarto complet
```

## 👀 Visualiser

```bash
# Ouvrir les rapports dans le navigateur
open tracking-nutrition.html

# Ou démarrer un serveur web local
python -m http.server 8000
# Puis visitez: http://localhost:8000
```

## 📚 Documentation Complète

Pour plus de détails, consultez: **EXECUTION_LOCALE.md**

---

**Note:** Ce workflow local simule exactement ce que fait GitHub Actions automatiquement quand vous poussez vos changements!
