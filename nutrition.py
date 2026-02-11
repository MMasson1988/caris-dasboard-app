from __future__ import annotations
import os
import pandas as pd
import numpy as np
import warnings
from datetime import datetime, date
from pathlib import Path

# Suppression des alertes de formatage Excel
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# =============================================================================
# CONFIGURATION DES CHEMINS (COMPATIBLE CI/CD)
# =============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs" / "NUTRITION"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Import dynamique des utilitaires (doit être dans le même dossier ou PYTHONPATH)
try:
    from utils import (
        today_str, clean_column_names, get_age_in_year, 
        get_age_in_months, age_range, combine_columns,
        creer_colonne_match_conditional, extraire_data
    )
except ImportError:
    # Définition minimale si utils.py est manquant pour éviter le crash
    def today_str(): return datetime.now().strftime("%Y-%m-%d")
    print("⚠️ utils.py non détecté. Certaines fonctions de nettoyage seront limitées.")

# =============================================================================
# FONCTIONS WRAPPERS & LOGIQUE MÉTIER
# =============================================================================

def log_step(df, message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message} | Lignes: {len(df)}")
    return df

def calculate_visits_remaining(df, cat_col='manutrition_type', num_col='nbr_visit_succeed_suivi', out_col='visits_remaining'):
    df[out_col] = 0
    # Logique MAM : 8 visites cibles
    mam_mask = (df[cat_col] == 'MAM') & (df[num_col] <= 12)
    df.loc[mam_mask, out_col] = (8 - df.loc[mam_mask, num_col]).clip(lower=0)
    # Logique MAS : 12 visites cibles
    mas_mask = (df[cat_col] == 'MAS') & (df[num_col] <= 18)
    df.loc[mas_mask, out_col] = (12 - df.loc[mas_mask, num_col]).clip(lower=0)
    return df

def smart_aggregate(df, group_col='caseid'):
    """Agrégation intelligente basée sur le type de données."""
    agg_dict = {}
    for col in df.columns:
        if col == group_col: continue
        if df[col].dtype == 'datetime64[ns]':
            agg_dict[col] = ['min', 'max']
        elif pd.api.types.is_numeric_dtype(df[col]):
            agg_dict[col] = 'sum'
        else:
            agg_dict[col] = 'first'
    
    res = df.groupby(group_col).agg(agg_dict).reset_index()
    # Aplatissement des colonnes multi-niveaux
    res.columns = [f"{c[0]}_{c[1]}" if isinstance(c, tuple) and c[1] else c[0] for c in res.columns]
    return res

# =============================================================================
# PIPELINES PRINCIPAUX
# =============================================================================

def run_nutrition_pipeline():
    print(f"🚀 Démarrage Pipeline Nutrition | Date source : {today_str()}")
    
    # --- ETAPE 1 : DEPISTAGE ---
    dep_file = DATA_DIR / f"Caris Health Agent - NUTRITON[HIDDEN] - Dépistage Nutritionnel (created 2025-06-26) {today_str()}.xlsx"
    if dep_file.exists():
        dep_df = (
            pd.read_excel(dep_file)
            .pipe(log_step, "Chargement Dépistage")
            .rename(columns={'form.case.@case_id': 'caseid', 'form.depistage.date_de_visite': 'date_de_depistage'})
            .pipe(clean_column_names, 'form.depistage.')
            .assign(muac=lambda x: pd.to_numeric(x['muac'], errors='coerce').fillna(0))
            .pipe(get_age_in_year, 'date_of_birth')
            .pipe(get_age_in_months, 'date_of_birth')
        )
        dep_df.to_excel(OUTPUT_DIR / "depistage_filtered.xlsx", index=False)
    else:
        print(f"⚠️ Fichier dépistage absent : {dep_file.name}")
        dep_df = pd.DataFrame()

    # --- ETAPE 2 : SUIVI ---
    suivi_file = DATA_DIR / f"Caris Health Agent - Nutrition - Suivi nutritionel (created 2025-06-26) {today_str()}.xlsx"
    if suivi_file.exists():
        suivi_df = (
            pd.read_excel(suivi_file)
            .pipe(log_step, "Chargement Suivi")
            .pipe(clean_column_names, 'form.')
            .rename(columns={'case.@case_id': 'caseid'})
        )
        
        # Agrégation et calcul de sortie
        suivi_agg = smart_aggregate(suivi_df)
        suivi_agg['sortie'] = np.where(suivi_agg.get('date_of_visit_max', 0) != 0, 'yes', 'no')
        suivi_agg.to_excel(OUTPUT_DIR / "suivi_aggregated_final.xlsx", index=False)
    else:
        suivi_agg = pd.DataFrame()

    # --- ETAPE 3 : ENROLEMENT (FINAL) ---
    enrol_file = DATA_DIR / f"Nutrition (created 2025-04-25) {today_str()}.xlsx"
    if enrol_file.exists():
        enrol_df = (
            pd.read_excel(enrol_file)
            .pipe(log_step, "Chargement Enrôlement")
            .pipe(combine_columns, "enrollement_date_de_visite", "date_admission", col3="date_enrollement")
        )
        
        # Calcul Enrôlé et Visites
        enrol_df['date_enrollement'] = pd.to_datetime(enrol_df['date_enrollement'], errors='coerce')
        enrol_df['enroled'] = np.where(
            (enrol_df['closed_date'].isna() | (enrol_df['closed_date'] == '---')) & 
            (enrol_df['date_enrollement'] >= pd.Timestamp("2025-01-01")), 'yes', 'no'
        )
        
        enrol_df = calculate_visits_remaining(enrol_df)
        
        # Merge avec Suivi pour l'état actif
        if not suivi_agg.empty:
            enrol_df = enrol_df.merge(suivi_agg[['caseid', 'sortie']], on='caseid', how='left')
            enrol_df['actif'] = np.where(enrol_df['sortie'] == 'no', 'yes', 'no')
        
        enrol_df.to_excel(OUTPUT_DIR / "enroled_final.xlsx", index=False)
        
        # Filtrage "En Attente"
        en_attente = enrol_df[
            (enrol_df['enroled'] == 'no') & 
            (enrol_df['eligible'] == 'yes') & 
            (enrol_df['enrrolled_where'] == 'community')
        ]
        en_attente.to_excel(OUTPUT_DIR / "en_attente.xlsx", index=False)

    # --- ETAPE 4 : CLUBS ---
    club_file = DATA_DIR / f"ht_nutrition_presence (created 2025-08-18) {today_str()}.xlsx"
    if club_file.exists():
        club_df = (
            pd.read_excel(club_file)
            .pipe(log_step, "Chargement Clubs")
            .rename(columns={'nutrition_case_id': 'caseid', 'indices.ht_club_nutrition': 'club_id'})
        )
        club_df.to_excel(OUTPUT_DIR / "club_nutrition_filtered.xlsx", index=False)

    print(f"✅ Pipeline terminé avec succès à {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    run_nutrition_pipeline()