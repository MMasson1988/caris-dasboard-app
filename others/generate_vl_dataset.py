"""
Générateur de dataset fictif basé sur matrice_indicateurs_vl.xlsx
Génère 1200 observations pour l'étude sur la couverture de la charge virale
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Paramètres
N_OBSERVATIONS = 1200
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# Date de référence pour l'étude
STUDY_DATE = datetime(2026, 1, 21)

print("🔬 Génération du dataset fictif de charge virale...")
print(f"Nombre d'observations: {N_OBSERVATIONS}")
print("-" * 60)

# 1. INDICATEUR PRINCIPAL
print("📊 Génération des indicateurs principaux...")
vl_coverage = np.random.choice([0, 1], N_OBSERVATIONS, p=[0.35, 0.65])  # 65% ont eu un test VL
vl_value = []
vl_date = []

for has_vl in vl_coverage:
    if has_vl == 1:
        # Valeur de charge virale (distribution log-normale)
        vl = int(np.random.lognormal(mean=6, sigma=3))
        vl_value.append(max(20, min(vl, 1000000)))  # Entre 20 et 1M copies/ml
        # Date dans les 12 derniers mois
        days_back = np.random.randint(1, 365)
        vl_date.append(STUDY_DATE - timedelta(days=days_back))
    else:
        vl_value.append(np.nan)
        vl_date.append(pd.NaT)

# 2. DÉMOGRAPHIE
print("👥 Génération des données démographiques...")
patient_id = [f"PAT{str(i+1).zfill(5)}" for i in range(N_OBSERVATIONS)]
age = np.random.randint(13, 26, N_OBSERVATIONS)  # 13-25 ans
age_group = pd.cut(age, bins=[12, 17, 21, 25], labels=['13-17', '18-21', '22-25'])
sex = np.random.choice(['M', 'F'], N_OBSERVATIONS, p=[0.45, 0.55])
school_status = np.random.choice(
    ['Scolarisé', 'Non scolarisé', 'Abandonné'], 
    N_OBSERVATIONS, 
    p=[0.60, 0.25, 0.15]
)

# Sites/communes (basé sur les communes du Mali)
communes = [
    'Bamako', 'Kayes', 'Koulikoro', 'Sikasso', 'Ségou', 
    'Mopti', 'Tombouctou', 'Gao', 'Kidal'
]
residence = np.random.choice(communes, N_OBSERVATIONS, p=[0.25, 0.12, 0.15, 0.13, 0.12, 0.10, 0.05, 0.05, 0.03])

# 3. MÉNAGE
print("🏠 Génération des données de ménage...")
child_in_household = np.random.poisson(lam=2.5, size=N_OBSERVATIONS)  # Moyenne 2-3 enfants
female_headed_household = np.random.choice([0, 1], N_OBSERVATIONS, p=[0.60, 0.40])

# 4. CLINIQUE / ART
print("💊 Génération des données cliniques et ART...")
# Date de début ART (entre 3 mois et 10 ans avant)
art_start_date = [STUDY_DATE - timedelta(days=np.random.randint(90, 3650)) for _ in range(N_OBSERVATIONS)]
art_duration_months = [(STUDY_DATE - date).days // 30 for date in art_start_date]

# Dernière consultation (dans les 6 derniers mois)
last_clinical_visit = [STUDY_DATE - timedelta(days=np.random.randint(1, 180)) for _ in range(N_OBSERVATIONS)]

# CD4 count (distribution réaliste)
cd4_count = np.random.gamma(shape=5, scale=100, size=N_OBSERVATIONS).astype(int)
cd4_count = np.clip(cd4_count, 50, 1500)  # Plage réaliste

# Suppression virale
viral_suppression = []
for vl in vl_value:
    if pd.isna(vl):
        viral_suppression.append(np.nan)
    else:
        viral_suppression.append(1 if vl < 1000 else 0)

# Comorbidités (30% ont des comorbidités)
comorbidities_list = ['Tuberculose', 'Hépatite B', 'Hépatite C', 'Diabète', 'Hypertension', 'Aucune']
comorbidities = np.random.choice(comorbidities_list, N_OBSERVATIONS, p=[0.08, 0.05, 0.03, 0.04, 0.10, 0.70])

# 5. PROGRAMME / INTERVENTIONS
print("🎯 Génération des données d'interventions...")
# Participation club pairs (corrélée avec vl_coverage)
club_participation = []
for has_vl in vl_coverage:
    # Si VL fait, 75% sont au club; sinon 40%
    prob_club = 0.75 if has_vl == 1 else 0.40
    club_participation.append(np.random.choice([0, 1], p=[1-prob_club, prob_club]))

club_participation = np.array(club_participation)

# Fréquence de participation (pour ceux qui participent)
club_frequency = [np.random.randint(1, 5) if cp == 1 else 0 for cp in club_participation]

# Visites à domicile (corrélées avec vl_coverage)
home_visit = []
for has_vl in vl_coverage:
    prob_visit = 0.70 if has_vl == 1 else 0.45
    home_visit.append(np.random.choice([0, 1], p=[1-prob_visit, prob_visit]))

home_visit = np.array(home_visit)
home_visit_count = [np.random.poisson(lam=3) if hv == 1 else 0 for hv in home_visit]

# Appels téléphoniques
phone_call = np.random.choice([0, 1], N_OBSERVATIONS, p=[0.45, 0.55])
phone_call_count = [np.random.poisson(lam=4) if pc == 1 else 0 for pc in phone_call]

# Suivi médical normal
medical_followup = np.random.choice([0, 1], N_OBSERVATIONS, p=[0.25, 0.75])

# Interventions nutritionnelles et scolaires
abdominal_prophylaxis = np.random.choice([0, 1], N_OBSERVATIONS, p=[0.35, 0.65])
vitamin_a = np.random.choice([0, 1], N_OBSERVATIONS, p=[0.40, 0.60])
school_grant = []
for status in school_status:
    if status == 'Scolarisé':
        school_grant.append(np.random.choice([0, 1], p=[0.50, 0.50]))
    else:
        school_grant.append(0)

# Date d'entrée au programme (pour ceux au club)
program_enrollment_date = []
for i, cp in enumerate(club_participation):
    if cp == 1:
        # Entrée entre la date de début ART et aujourd'hui
        days_range = (STUDY_DATE - art_start_date[i]).days
        days_after_art = np.random.randint(0, days_range) if days_range > 0 else 0
        program_enrollment_date.append(art_start_date[i] + timedelta(days=days_after_art))
    else:
        program_enrollment_date.append(pd.NaT)

# 6. CONSTRUCTION DU DATAFRAME
print("📋 Construction du dataset final...")
df = pd.DataFrame({
    # Indicateur principal
    'vl_coverage': vl_coverage,
    'vl_value': vl_value,
    'vl_date': vl_date,
    
    # Démographie
    'patient_id': patient_id,
    'age': age,
    'age_group': age_group,
    'sex': sex,
    'school_status': school_status,
    'residence': residence,
    
    # Ménage
    'child_in_household': child_in_household,
    'female_headed_household': female_headed_household,
    
    # Clinique / ART
    'art_start_date': art_start_date,
    'art_duration_months': art_duration_months,
    'last_clinical_visit': last_clinical_visit,
    'cd4_count': cd4_count,
    'viral_suppression': viral_suppression,
    'comorbidities': comorbidities,
    
    # Programme / Interventions
    'club_participation': club_participation,
    'club_frequency': club_frequency,
    'home_visit': home_visit,
    'home_visit_count': home_visit_count,
    'phone_call': phone_call,
    'phone_call_count': phone_call_count,
    'medical_followup': medical_followup,
    'abdominal_prophylaxis': abdominal_prophylaxis,
    'vitamin_a': vitamin_a,
    'school_grant': school_grant,
    'program_enrollment_date': program_enrollment_date
})

# 7. SAUVEGARDER LE DATASET
print("💾 Sauvegarde du dataset...")
output_excel = 'dataset_vl_fictif_1200obs.xlsx'
output_csv = 'dataset_vl_fictif_1200obs.csv'

df.to_excel(output_excel, index=False)
df.to_csv(output_csv, index=False)

print("\n✅ Dataset généré avec succès!")
print("-" * 60)
print(f"📊 Fichiers créés:")
print(f"   - {output_excel}")
print(f"   - {output_csv}")
print("\n📈 Statistiques descriptives:")
print(f"   - Nombre total d'observations: {len(df)}")
print(f"   - Couverture VL: {df['vl_coverage'].mean():.1%}")
print(f"   - Suppression virale: {df['viral_suppression'].sum()}/{df['viral_suppression'].notna().sum()} ({df['viral_suppression'].mean():.1%})")
print(f"   - Participation club: {df['club_participation'].mean():.1%}")
print(f"   - Visites à domicile: {df['home_visit'].mean():.1%}")
print(f"   - Âge moyen: {df['age'].mean():.1f} ans")
print(f"\n📊 Distribution par groupe d'âge:")
print(df['age_group'].value_counts().sort_index())
print(f"\n📍 Distribution par résidence:")
print(df['residence'].value_counts().head())
print(f"\n🎓 Statut scolaire:")
print(df['school_status'].value_counts())

# 8. RÉSUMÉ STATISTIQUE COMPLET
print("\n" + "=" * 60)
print("RÉSUMÉ STATISTIQUE DÉTAILLÉ")
print("=" * 60)
print(df.describe())

print("\n📊 Dataset prêt pour l'analyse!")
