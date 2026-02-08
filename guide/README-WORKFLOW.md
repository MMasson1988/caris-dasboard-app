# CONFIGURATION GITHUB ACTIONS - RAPPORTS NUTRITION

## 📋 Description du Workflow

Le workflow `nutrition-reports.yml` génère automatiquement les rapports de nutrition deux fois par jour :
- **8h00 AM UTC** (9h00 AM heure de Paris en hiver)
- **2h00 PM UTC** (3h00 PM heure de Paris en hiver)

## 🔧 Configuration requise

### 1. Secrets GitHub à configurer

Allez dans **Settings → Secrets and variables → Actions** de votre repository et ajoutez :

```
DB_HOST=your_database_host
DB_USER=your_database_username  
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
COMMCARE_USERNAME=your_commcare_username
COMMCARE_PASSWORD=your_commcare_password
```

### 2. GitHub Pages (optionnel)

Pour activer la publication automatique :
1. Allez dans **Settings → Pages**
2. Sélectionnez **GitHub Actions** comme source

## 🚀 Fonctionnalités

### Exécution automatique
- **Cron jobs** : `0 8 * * *` et `0 14 * * *`
- **Exécution manuelle** : Via l'onglet Actions

### Génération de rapports
- `nutrition_dashboard.qmd` → Dashboard principal
- `tracking-nutrition.qmd` → Rapport de tracking détaillé

### Archivage
- Sauvegarde des rapports précédents avec timestamp
- Conservation de 30 jours des artifacts

### Notifications
- Logs de statut du job
- Possibilité d'ajouter Slack/Email

## 📁 Structure des outputs

```
archives/
├── 20241201_080000/
│   ├── nutrition_dashboard_20241201_080000.html
│   └── tracking-nutrition_20241201_080000.html
└── 20241201_140000/
    ├── nutrition_dashboard_20241201_140000.html
    └── tracking-nutrition_20241201_140000.html

_site/
├── nutrition_dashboard.html    # Version courante
└── tracking-nutrition.html    # Version courante
```

## 🛠️ Mode de test

Si les données réelles ne sont pas disponibles, le workflow génère automatiquement des données de test pour éviter les erreurs.

## ⏰ Personnalisation des horaires

Pour modifier les heures d'exécution, changez les valeurs cron :
```yaml
schedule:
  - cron: '0 6 * * *'   # 6h AM UTC = 7h AM hiver
  - cron: '0 18 * * *'  # 6h PM UTC = 7h PM hiver
```

## 🔍 Monitoring

1. **Actions tab** : Voir l'historique des exécutions
2. **Artifacts** : Télécharger les rapports générés  
3. **GitHub Pages** : Voir les rapports publiés (si activé)

## 🚨 Dépannage

### Erreur de dépendances
- Vérifiez que `requirements.txt` est à jour
- Les packages R sont installés automatiquement

### Erreur de données
- Vérifiez les secrets GitHub
- Le mode test génère des données si nécessaire

### Erreur de permissions
- Vérifiez que `GITHUB_TOKEN` a les bonnes permissions
- Pour GitHub Pages, activez les permissions d'écriture

## 📧 Notifications (optionnel)

Pour ajouter des notifications Slack :
1. Créez un webhook Slack
2. Ajoutez `SLACK_WEBHOOK_URL` dans les secrets
3. Décommentez la section notification dans le workflow