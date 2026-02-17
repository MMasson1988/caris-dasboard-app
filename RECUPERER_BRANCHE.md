# 🌿 Guide: Récupérer la Branche workflow-automation-fresh

## Situation Actuelle

La branche `workflow-automation-fresh` avec tous les fichiers de workflow automation a été créée dans l'environnement Emergent, mais elle n'existe pas encore sur votre machine locale ni sur GitHub.

## 📋 Deux Options

### Option 1: Pousser la Branche vers GitHub (Recommandé)

Cette option pousse d'abord la branche vers GitHub, puis vous la récupérez sur votre machine locale.

#### Étape 1: Pousser depuis Emergent vers GitHub

**Note:** Cette commande sera exécutée automatiquement pour vous, ou vous pouvez demander à l'administrateur de la pousser.

```bash
# Cette commande sera exécutée pour vous
git push origin workflow-automation-fresh
```

#### Étape 2: Récupérer sur Votre Machine Locale

Sur votre machine locale (VSCode):

```bash
# 1. Mettre à jour les références distantes
git fetch origin

# 2. Voir toutes les branches (y compris distantes)
git branch -a

# Vous devriez voir:
# * main
#   remotes/origin/main
#   remotes/origin/workflow-automation-fresh  ← La nouvelle branche!

# 3. Créer une branche locale qui suit la branche distante
git checkout -b workflow-automation-fresh origin/workflow-automation-fresh

# Ou simplement:
git checkout workflow-automation-fresh
# Git créera automatiquement la branche locale

# 4. Vérifier que vous êtes sur la bonne branche
git branch
# * workflow-automation-fresh  ← Vous êtes ici
#   main
```

---

### Option 2: Créer la Branche Manuellement en Local

Si vous préférez créer la branche vous-même localement:

#### Étape 1: Sur Votre Machine Locale (VSCode)

```bash
# 1. Assurez-vous d'être sur main et à jour
git checkout main
git pull origin main

# 2. Créer la nouvelle branche
git checkout -b workflow-automation-fresh

# 3. Vérifier
git branch
#   main
# * workflow-automation-fresh  ← Vous êtes ici
```

#### Étape 2: Ajouter les Fichiers

Vous devrez créer/copier ces fichiers manuellement:

**Fichiers à créer:**

1. `.github/workflows/unified-pipeline-deploy.yml`
2. `QUICK_START.md`
3. `EXECUTION_LOCALE.md`
4. `DEMARRAGE_RAPIDE.md`
5. `run_local_workflow.sh`

**Contenu disponible dans les messages précédents** ou vous pouvez les récupérer depuis cette conversation.

#### Étape 3: Commit et Push

```bash
# Ajouter les fichiers
git add .github/workflows/unified-pipeline-deploy.yml
git add QUICK_START.md
git add EXECUTION_LOCALE.md
git add DEMARRAGE_RAPIDE.md
git add run_local_workflow.sh

# Rendre le script exécutable
chmod +x run_local_workflow.sh

# Commit
git commit -m "feat: Add unified workflow automation

- Created unified GitHub Actions workflow for all pipelines
- Added documentation in French and English
- Created local execution script
- Supports 6 pipelines and 6 QMD reports
- Auto-commits results back to repository"

# Pousser vers GitHub
git push -u origin workflow-automation-fresh
```

---

## 🚀 Recommandation: Option 1

**Je recommande l'Option 1** car tous les fichiers sont déjà créés et testés dans l'environnement Emergent.

### Commande à Exécuter

Permettez-moi de pousser la branche vers GitHub maintenant:

```bash
git push origin workflow-automation-fresh
```

**Puis sur votre machine locale:**

```bash
git fetch origin
git checkout workflow-automation-fresh
```

---

## 📂 Fichiers dans la Branche

Une fois la branche récupérée, vous aurez:

```
📁 .github/workflows/
   └── unified-pipeline-deploy.yml    ← Workflow GitHub Actions

📄 QUICK_START.md                      ← Guide rapide (EN)
📄 DEMARRAGE_RAPIDE.md                 ← Guide rapide (FR)
📄 EXECUTION_LOCALE.md                 ← Guide complet (FR)
📄 run_local_workflow.sh               ← Script d'exécution locale
```

---

## ✅ Vérification

Pour vérifier que tout est bien là:

```bash
# Vérifier les fichiers
ls -la .github/workflows/unified-pipeline-deploy.yml
ls -la QUICK_START.md
ls -la EXECUTION_LOCALE.md
ls -la DEMARRAGE_RAPIDE.md
ls -la run_local_workflow.sh

# Vérifier le contenu du workflow
cat .github/workflows/unified-pipeline-deploy.yml

# Tester le script local
./run_local_workflow.sh
```

---

## 🔄 Workflow Complet

### 1. Récupérer la Branche

```bash
# Sur votre machine locale
git fetch origin
git checkout workflow-automation-fresh
```

### 2. Vérifier les Fichiers

```bash
ls -la
# Vous devriez voir les nouveaux fichiers
```

### 3. Tester Localement

```bash
# Installer les dépendances
pip install -r requirements.txt

# Exécuter le workflow local
./run_local_workflow.sh
```

### 4. Si Tout Fonctionne, Merger vers Main

```bash
git checkout main
git merge workflow-automation-fresh
git push origin main
```

---

## 🆘 En Cas de Problème

### Problème 1: La Branche N'existe Pas sur GitHub

```bash
git fetch origin
git branch -a
# Si vous ne voyez pas origin/workflow-automation-fresh:
```

**Solution:** Demandez-moi de pousser la branche d'abord!

### Problème 2: Conflits lors du Checkout

```bash
# Sauvegarder vos changements locaux d'abord
git stash

# Puis checkout
git checkout workflow-automation-fresh

# Réappliquer vos changements
git stash pop
```

### Problème 3: Fichiers Manquants

Si certains fichiers sont manquants après checkout:

```bash
# Vérifier l'état du repo
git status

# Récupérer tous les fichiers de la branche
git checkout workflow-automation-fresh -- .
```

---

## 📞 Prochaine Étape

**Voulez-vous que je pousse la branche vers GitHub maintenant?**

Si oui, dites-moi et je vais exécuter:
```bash
git push origin workflow-automation-fresh
```

Puis vous pourrez la récupérer sur votre machine locale avec:
```bash
git fetch origin
git checkout workflow-automation-fresh
```

---

**Date:** 2025-02-17
**Branche:** workflow-automation-fresh
**Statut:** ✅ Prête à être poussée vers GitHub
