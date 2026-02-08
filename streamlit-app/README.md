# Application MEAL Nutrition - CARIS Foundation

Application Streamlit pour le suivi MEAL (Monitoring, Evaluation, Accountability and Learning) du programme nutrition.

## 🚀 Démarrage Rapide

### 1. Installation des dépendances

```bash
cd streamlit-app
pip install -r requirements.txt
```

### 2. Configuration des secrets

Copiez le template et configurez vos credentials:

```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```

Éditez `.streamlit/secrets.toml` avec vos vraies valeurs.

### 3. Lancement de l'application

```bash
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

## 📁 Structure du Projet

```
streamlit-app/
├── app.py                      # Point d'entrée principal
├── config.yaml                 # Configuration authentification (dev)
├── requirements.txt            # Dépendances Python
├── README.md                   # Ce fichier
│
├── .streamlit/
│   └── secrets.toml.template   # Template pour les secrets
│
├── pages/
│   ├── dashboard.py            # Dashboard KPIs
│   ├── rapport_html.py         # Intégration rapport Quarto
│   ├── alertes.py              # Alertes MAS email
│   └── assistant_ia.py         # Chatbot Gemini
│
├── utils/
│   ├── data_loader.py          # Chargement données Excel
│   ├── kpi_calculator.py       # Calcul des métriques
│   ├── email_service.py        # Service SMTP
│   └── ai_chatbot.py           # Intégration Gemini
│
├── components/
│   └── charts.py               # Graphiques Plotly
│
└── assets/
    ├── style.css               # CSS personnalisé
    └── logo.png                # Logo CARIS (à ajouter)
```

## 🔐 Configuration

### Authentification

Générez des mots de passe hachés:

```python
import bcrypt
password = "votre_mot_de_passe"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(hashed)
```

### Email SMTP (Gmail)

1. Activez l'authentification à 2 facteurs sur votre compte Google
2. Créez un mot de passe d'application: https://myaccount.google.com/apppasswords
3. Utilisez ce mot de passe dans `secrets.toml`

### API Gemini

1. Obtenez une clé API: https://aistudio.google.com/app/apikey
2. Ajoutez-la dans `secrets.toml`

## 📊 Fonctionnalités

### Dashboard
- KPIs en temps réel (dépistages, enrôlements, taux d'admission)
- Filtres par période et bureau
- Visualisations interactives Plotly
- Export Excel des données

### Alertes MAS
- Détection automatique des cas de Malnutrition Aiguë Sévère
- Envoi d'emails aux responsables MEAL
- Validation manuelle obligatoire (Do No Harm)

### Assistant IA
- Chatbot basé sur Gemini 2.0 Flash
- Contexte MEAL intégré (définitions, KPIs, données)
- Questions suggérées
- Mode démonstration sans API

### Rapport HTML
- Intégration du rapport Quarto existant
- Génération à la demande

## 🔒 Sécurité

- Authentification obligatoire
- Sessions sécurisées avec cookies
- Credentials stockés dans secrets (jamais en clair)
- Conformité GDPR / Do No Harm

## 📝 Données Requises

L'application attend les fichiers suivants dans `../outputs/NUTRITION/`:
- `depistage_filtered.xlsx`
- `enroled_final.xlsx`

Ces fichiers sont générés par le pipeline de données existant.

## 🚀 Déploiement

### Streamlit Cloud (Recommandé)

1. Push le code sur GitHub
2. Connectez-vous à https://share.streamlit.io
3. Déployez depuis le repo
4. Configurez les secrets dans l'interface Streamlit Cloud

### Serveur Interne

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📧 Support

Pour toute question technique: M&E Department - CARIS Foundation International
