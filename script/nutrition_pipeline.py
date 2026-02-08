"""
RAPPORT NUTRITION - Script Python exécutable avec python {MODULE}.py
"""
from __future__ import annotations

import pandas as pd
# from _helpers import ensure_dirs, read_excel, write_json, write_excel, print_context  # Module non disponible

import pandas as pd
import numpy as np
import os
import re
import time
import warnings
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import openpyxl
import xlsxwriter
import pymysql
from sqlalchemy import create_engine
from difflib import SequenceMatcher
import unicodedata
from typing import List
#from utils import today_str, load_excel_to_df, creer_colonne_match_conditional, commcare_match_person
from pathlib import Path

# Always resolve data directory relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'data'))
#=========================================================================================================
# Functions modules
from utils import is_screened_in_period,today_str,detect_duplicates_with_groups,load_excel_to_df,extraire_data, age_range,get_age_in_year, get_age_in_months, clean_column_names,creer_colonne_match_conditional,combine_columns, commcare_match_person
#=========================================================================================================
# PIPE-FRIENDLY WRAPPER FUNCTIONS
#=========================================================================================================


def save_to_excel(df, filename, index=False, **kwargs):
    """Fonction pipe-friendly pour sauvegarder un DataFrame en Excel."""
    df.to_excel(filename, index=index, **kwargs)
    print(f"Nombre de patients dans le fichier {filename}: {df.shape[0]}")
    print(f"✅ File saved: {filename}")
    return df

def rename_cols(df, mapping: dict):
    """Renomme les colonnes de manière pipe-friendly"""
    return df.rename(columns=mapping)


def assign_age_range(df, months_col="age_months"):
    """Assigne la tranche d'âge de manière pipe-friendly"""
    df['age_range'] = df[months_col].map(age_range)
    return df



def detect_duplicates(df, colonnes, threshold=95):
    """Détecte les doublons de manière pipe-friendly"""
    return detect_duplicates_with_groups(df, colonnes=colonnes, threshold=threshold)

def select_columns(df, cols):
    """Sélectionne les colonnes spécifiées de manière pipe-friendly"""
    available_cols = [col for col in cols if col in df.columns]
    if len(available_cols) != len(cols):
        missing = [col for col in cols if col not in df.columns]
        print(f"Warning: Missing columns {missing}")
    return df[available_cols]

def print_shape(df, message="DataFrame shape"):
    """Affiche la forme du DataFrame et le retourne (pipe-friendly)"""
    print(f"{message}: {df.shape[0]} lignes")
    return df

def print_message(df, message="Message"):
    """Affiche un message et le retourne (pipe-friendly)"""
    print(f"{message}")
    return df

def assign_age_range_from_months(df, months_col="age_months", out="age_range"):
    """Assigne age_range à partir de age_months de manière pipe-friendly"""
    df.loc[:, out] = df[months_col].map(age_range)
    return df

def capitalize_column(df, column_name):
    """Capitalise une colonne de type string de manière pipe-friendly"""
    df.loc[:, column_name] = df[column_name].astype(str).str.capitalize()
    return df

def load_excel_pipe(filename, usecols=None, parse_dates=True, **kwargs):
    """Charge un fichier Excel de manière pipe-friendly - retourne le DataFrame"""
    # If filename is not absolute, join with DATA_DIR
    if not os.path.isabs(filename):
        filename = os.path.join(DATA_DIR, filename)
    return pd.read_excel(filename, usecols=usecols, parse_dates=parse_dates, **kwargs)

def convert_datetime_column(df, column_name, errors='coerce', format=None):
    """Convertit une colonne en datetime de manière pipe-friendly"""
    import warnings
    
    # Supprimer temporairement les warnings pour cette conversion
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        if format:
            # Si un format est spécifié, l'utiliser
            df.loc[:, column_name] = pd.to_datetime(df[column_name], format=format, errors=errors)
        else:
            # Essayer de détecter automatiquement le format ou utiliser infer_datetime_format
            df.loc[:, column_name] = pd.to_datetime(df[column_name], errors=errors, infer_datetime_format=True)
    
    return df

def copy_dataframe(df, name="DataFrame", var_name=None):
    """Copie le DataFrame de manière pipe-friendly avec nom de variable optionnel"""
    if var_name:
        print(f"Copie du {name} → Nouveau DataFrame: {var_name}")
    else:
        print(f"Copie du {name} effectuée")
    return df.copy()

def clean_raison_sortie_column(df, column_name='raison_pour_la_sortie', fill_value='no_info'):
    """Nettoie la colonne raison_pour_la_sortie de manière pipe-friendly"""
    df.loc[:, column_name] = (df[column_name]
                              .fillna(fill_value)
                              .replace({'---': fill_value, '': fill_value}))
    return df

def convert_numeric_column(df, column_name, fill_value=0, replace_value='---'):
    """Convertit une colonne en numérique et remplace les valeurs manquantes"""
    df.loc[:, column_name] = (pd.to_numeric(df[column_name], errors='coerce')
                              .fillna(fill_value)
                              .replace(replace_value, fill_value))
    return df

def create_visit_mamba_column(df, quantity_col='mamba_quantity', output_col='visit_mamba'):
    """Crée la colonne visit_mamba basée sur mamba_quantity"""
    df.loc[:, output_col] = np.where(df[quantity_col] > 0, 'yes', 'no')
    return df

def create_conditional_column(df, condition_col, output_col, condition_value, true_value, false_value):
    """Fonction pipe-friendly générique utilisant np.where pour créer une colonne conditionnelle"""
    df.loc[:, output_col] = np.where(df[condition_col] == condition_value, true_value, false_value)
    return df

def create_numeric_conditional_column(df, condition_col, output_col, threshold, true_value, false_value, operator='>'):
    """Fonction pipe-friendly utilisant np.where avec conditions numériques"""
    if operator == '>':
        condition = df[condition_col] > threshold
    elif operator == '>=':
        condition = df[condition_col] >= threshold
    elif operator == '<':
        condition = df[condition_col] < threshold
    elif operator == '<=':
        condition = df[condition_col] <= threshold
    elif operator == '==':
        condition = df[condition_col] == threshold
    elif operator == '!=':
        condition = df[condition_col] != threshold
    else:
        raise ValueError("Operator must be one of: '>', '>=', '<', '<=', '==', '!='")
    
    df.loc[:, output_col] = np.where(condition, true_value, false_value)
    return df

def create_multiple_conditions_column(df, output_col, conditions_dict, default_value='other'):
    """Fonction pipe-friendly utilisant np.where avec conditions multiples"""
    result = pd.Series([default_value] * len(df), index=df.index)
    
    for condition_func, value in conditions_dict.items():
        mask = condition_func(df)
        result = np.where(mask, value, result)
    
    df.loc[:, output_col] = result
    return df

def fill_missing_values_by_type(df, col_date=None, col_numeric=None):
    """Remplit les valeurs manquantes selon le type de données de chaque colonne
    
    Args:
        df: DataFrame à traiter
        col_date: Liste des colonnes à traiter comme des dates (optionnel)
        col_numeric: Liste des colonnes à traiter comme numériques (optionnel)
    """
    df_filled = df.copy()
    
    # Initialiser les listes si elles ne sont pas fournies
    if col_date is None:
        col_date = []
    if col_numeric is None:
        col_numeric = []
    
    for col in df_filled.columns:
        if col in col_date or df_filled[col].dtype == 'datetime64[ns]':
            # Pour les colonnes datetime, remplir avec 1901-01-01
            df_filled[col] = df_filled[col].fillna(pd.Timestamp('1901-01-01'))
        elif col in col_numeric or pd.api.types.is_numeric_dtype(df_filled[col]):
            # Pour les colonnes numériques, remplir avec 0
            df_filled[col] = df_filled[col].fillna(0)
        else:
            # Pour les autres types (string/object), remplir avec 'no_info'
            df_filled[col] = df_filled[col].fillna('no_info')
    
    return df_filled

def convert_date_columns(df, date_cols, format=None):
    """Convertit les colonnes de date de manière pipe-friendly"""
    for col in date_cols:
        if col in df.columns:
            if format:
                df.loc[:, col] = pd.to_datetime(df[col], format=format, errors='coerce')
            else:
                df.loc[:, col] = pd.to_datetime(df[col], errors='coerce')
    return df

def filter_enrolled_with_visits(df, date_threshold="2025-05-01", enrolled_col="is_enrolled", 
                                   visit_col="nbr_visit_succeed", date_col1="enrollement_date_de_visite", 
                                   date_col2="date_admission"):
    """Filtre les patients enrôlés avec visites de manière pipe-friendly"""
    # Convert visit column to numeric
    df.loc[:, visit_col] = pd.to_numeric(df[visit_col], errors='coerce').fillna(0)
    
    # Define date limit
    date_limite = pd.to_datetime(date_threshold)
    
    # Filter condition
    condition = (
        ((df[enrolled_col] == "yes") | (df[visit_col] > 0))
        &
        ((df[date_col1] >= date_limite) | (df[date_col2] >= date_limite))
    )
    
    return df[condition]

def clean_enrolled_where(df, col="enrrolled_where", old_value="---", new_value="community"):
    """Nettoie la colonne enrrolled_where de manière pipe-friendly"""
    if col in df.columns:
        df.loc[:, col] = df[col].replace(old_value, new_value).fillna(new_value)
    return df

def extract_user_mamba(df, username_col='username', output_col='user_mamba'):
    """Extrait les chiffres du nom d'utilisateur de manière pipe-friendly"""
    if username_col in df.columns:
        df.loc[:, output_col] = df[username_col].str.extract(r'(\d+)')
    else:
        print(f'Warning: {username_col} column not found')
        df.loc[:, output_col] = None
    return df

def clean_username_column(df, username_col='username', output_col=None):
    """Nettoie le nom d'utilisateur: supprime @carisfoundationintl.org et remplace . par _"""
    if output_col is None:
        output_col = username_col
    
    if username_col in df.columns:
        # Supprimer @carisfoundationintl.org et remplacer . par _
        df.loc[:, output_col] = (df[username_col]
                                 .str.replace('@carisfoundationintl.org', '', regex=False)
                                 .str.replace('.', ' ', regex=False)
                                 .str.title())
    else:
        print(f'Warning: {username_col} column not found')
    return df

def fill_office_from_data_clerk(df, data_clerk_col='data_clerk', office_col='office'):
    """Crée la colonne office basée sur le mapping des data_clerk"""
    
    # Mapping des data_clerks vers les offices
    data_clerk_to_office = {
        '1fodney': 'CAP',
        'johane_jules': 'PAP', 
        'nadia_assaindor': 'GON',
        'elande_mondesir': 'CAP',
        'mdaniel_cazy': 'PAP'
    }
    
    # Vérifier que la colonne data_clerk existe
    if data_clerk_col not in df.columns:
        print(f'Warning: {data_clerk_col} column not found')
        return df
    
    # Créer ou remplacer la colonne office basée sur data_clerk mapping
    df.loc[:, office_col] = df[data_clerk_col].map(data_clerk_to_office)
    
    # Compter les valeurs mappées avec succès
    mapped_count = df[office_col].notna().sum()
    unmapped_count = df[office_col].isna().sum()
    
    print(f"✅ Created office column based on data_clerk mapping:")
    print(f"   Successfully mapped: {mapped_count} values")
    print(f"   Unmapped (will be NaN): {unmapped_count} values")
    
    return df

def merge_with_depistage(df, depistage_df, cols=None):
    """Merge DataFrame with depistage data, handling missing columns"""
    if cols is None:
        cols = ['caseid']
    
    # Only select columns that exist in both DataFrames
    available_cols = [col for col in cols if col in depistage_df.columns]
    missing_cols = [col for col in cols if col not in depistage_df.columns]
    
    if missing_cols:
        print(f"Warning: Missing columns in depistage_df: {missing_cols}")
    
    if not available_cols:
        print("Error: No common columns found for merge")
        return df
    
    print(f"Merging on columns: {available_cols}")
    return pd.merge(df, depistage_df[available_cols], on='caseid', how='left')

def create_date_enrollement(df, col1="enrollement_date_de_visite", col2="date_admission", out_col="date_enrollement"):
    """Crée la colonne date_enrollement avec le max des deux dates"""

    df.loc[:, out_col] = df[[col1, col2]].max(axis=1)
    return df

def replace_dates_before(df, date_col="date_enrollement", threshold="2025-05-01", replacement="2025-05-01"):
    """Remplace les dates antérieures au seuil de manière pipe-friendly"""

    threshold_date = pd.to_datetime(threshold)
    replacement_date = pd.to_datetime(replacement)
    mask = df[date_col] < threshold_date
    df.loc[mask, date_col] = replacement_date
    return df

def match_conditional(df, other_df, on="caseid", new_col="has_visit", 
                         mapping={'both': 'yes', 'left_only': 'no', 'right_only': 'no'}):
    """Crée une colonne de match conditionnel de manière pipe-friendly"""
    return creer_colonne_match_conditional(df1=df, df2=other_df, on=on, nouvelle_colonne=new_col, mapping=mapping)

def numeric_conversion(df, col, fill_value=0):
    """Convertit une colonne en numérique de manière pipe-friendly"""

    df.loc[:, col] = pd.to_numeric(df[col], errors='coerce').fillna(fill_value)
    return df

def filter_open_cases(df, closed_col='closed_date', closed_value='---'):
    """Filtre les cas non fermés de manière pipe-friendly"""
    return df.loc[df[closed_col] == closed_value]

def fix_datetime_columns(df, *columns, format='%Y-%m-%d'):
    """Corrige le format des colonnes datetime de manière pipe-friendly"""

    for col in columns:
        if col in df.columns:
            df.loc[:, col] = pd.to_datetime(df[col], format=format, errors='coerce')
    return df

def create_status_column(df, col1, col2, col3, threshold=0, operator='!=', 
                        output_col='status', true_value='exeat', false_value='enrole'):
    """
    Crée une colonne de statut basée sur la formule Excel =IF(OR(O2<>0, P2<>0, R2<>0), "exeat", "enrole")
    
    Args:
        df: DataFrame
        col1, col2, col3: Noms des colonnes à vérifier
        threshold: Valeur seuil pour la comparaison (par défaut 0)
        operator: Opérateur de comparaison ('!=', '>', '<', '>=', '<=', '==')
        output_col: Nom de la colonne de sortie
        true_value: Valeur si condition vraie (par défaut 'exeat')
        false_value: Valeur si condition fausse (par défaut 'enrole')
    
    Returns:
        DataFrame avec la nouvelle colonne
    """
    # Convertir les colonnes en numérique
    for col in [col1, col2, col3]:
        if col in df.columns:
            df.loc[:, col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Définir la condition selon l'opérateur
    if operator == '!=':
        condition = (
            (df[col1] != threshold) | 
            (df[col2] != threshold) | 
            (df[col3] != threshold)
        )
    elif operator == '>':
        condition = (
            (df[col1] > threshold) | 
            (df[col2] > threshold) | 
            (df[col3] > threshold)
        )
    elif operator == '<':
        condition = (
            (df[col1] < threshold) | 
            (df[col2] < threshold) | 
            (df[col3] < threshold)
        )
    elif operator == '>=':
        condition = (
            (df[col1] >= threshold) | 
            (df[col2] >= threshold) | 
            (df[col3] >= threshold)
        )
    elif operator == '<=':
        condition = (
            (df[col1] <= threshold) | 
            (df[col2] <= threshold) | 
            (df[col3] <= threshold)
        )
    elif operator == '==':
        condition = (
            (df[col1] == threshold) | 
            (df[col2] == threshold) | 
            (df[col3] == threshold)
        )
    else:
        raise ValueError("Operator must be one of: '!=', '>', '<', '>=', '<=', '=='")
    
    # Appliquer la condition avec np.where
    df.loc[:, output_col] = np.where(condition, true_value, false_value)
    
    print(f"Colonne '{output_col}' créée:")
    print(f"  - {true_value}: {(df[output_col] == true_value).sum()}")
    print(f"  - {false_value}: {(df[output_col] == false_value).sum()}")
    
    return df

def filter_enrolled_patients(
    df: pd.DataFrame,
    date_threshold: str = "2025-05-01",
    enrolled_col: str = "is_enrolled",
    visit_col: str = "nbr_visit_succeed",
    date_col1: str = "enrollement_date_de_visite",
    date_col2: str = "date_admission"
) -> pd.DataFrame:
        # Définir la date limite
    date_limite = pd.to_datetime(date_threshold)
    
    # Convertir le nombre de visites en numérique
    df.loc[:, visit_col] = pd.to_numeric(df[visit_col], errors='coerce').fillna(0)
    df.loc[:, date_col1] = pd.to_datetime(df[date_col1], errors='coerce')
    df.loc[:, date_col2] = pd.to_datetime(df[date_col2], errors='coerce')
    
    # Condition de filtrage
    condition = (
        ((df[enrolled_col] == "yes") | (df[visit_col] > 0))
        &
        ((df[date_col1] >= date_limite) | (df[date_col2] >= date_limite))
    )
    
    # Application du filtre
    filtered_df = df[condition]
    print(f"Nombre d'enrollement avec doublons possibles {filtered_df.shape[0]} lignes")
    
    return filtered_df

def fix_multiple_datetime_columns(df, col1, col2, format=None):
    """Corrige les colonnes datetime avec format explicite et .loc[]"""

    df.loc[:, col1] = pd.to_datetime(df[col1], format=format, errors="coerce")
    df.loc[:, col2] = pd.to_datetime(df[col2], format=format, errors="coerce")
    return df

def replace_dates_before_threshold(
    df: pd.DataFrame,
    date_col: str = "date_enrollement",
    threshold_date: str = "2025-05-01",
    replacement_date: str = "2025-09-30"
) -> pd.DataFrame:
         
    if date_col not in df.columns:
        raise KeyError(f"La colonne '{date_col}' est absente du DataFrame.")
    
    threshold = pd.Timestamp(threshold_date)
    replacement = pd.Timestamp(replacement_date)
    
    mask = df[date_col] < threshold
    df.loc[mask, date_col] = replacement
    
    return df

def filter_by_user_mamba(
    df: pd.DataFrame,
    user_mamba_col: str = 'user_mamba',
    exclude_values: list = ['5', '1', '6']
) -> pd.DataFrame:
    """
    Filtre un DataFrame en excluant certaines valeurs de la colonne user_mamba.
    
    Args:
        df (pd.DataFrame): DataFrame à filtrer.
        user_mamba_col (str): Nom de la colonne user_mamba.
        exclude_values (list): Liste des valeurs à exclure.
    
    Returns:
        pd.DataFrame: DataFrame filtré.
    """
    if user_mamba_col not in df.columns:
        raise KeyError(f"La colonne '{user_mamba_col}' est absente du DataFrame.")
    
    # Créer la condition d'exclusion
    condition = ~df[user_mamba_col].isin(exclude_values)
    #nut_filtered = pd.concat([condition_avant_septembre, condition_apres_septembre], ignore_index=True)
    
    return df[condition]

def filter_by_visit_mamba(
    df: pd.DataFrame,
    visit_mamba_col: str = 'visit_mamba',
    exclude_values: list = ['no', '---']
) -> pd.DataFrame:
    """
    Filtre un DataFrame en excluant certaines valeurs de la colonne user_mamba.
    
    Args:
        df (pd.DataFrame): DataFrame à filtrer.
        visit_mamba_col (str): Nom de la colonne visit_mamba.
        exclude_values (list): Liste des valeurs à exclure.
    
    Returns:
        pd.DataFrame: DataFrame filtré.
    """
    if visit_mamba_col not in df.columns:
        raise KeyError(f"La colonne '{visit_mamba_col}' est absente du DataFrame.")
    
    # Créer la condition d'exclusion
    condition = ~df[visit_mamba_col].isin(exclude_values)
    return df[condition]

# Créer une copie intermédiaire pour réutilisation
def create_backup_and_continue(df, backup_var_name="backup"):
    # Cette fonction crée une copie ET continue le pipeline
    globals()[backup_var_name] = df.copy()
    print(f"✅ Backup créé: {backup_var_name}")
    return df

def create_mamba_period_column(df, user_mamba_col='user_mamba', date_col='date_enrollement', 
                               output_col='mamba_period_eligible', 
                               target_values=[1, 5, 6], 
                               start_date='2025-05-01', end_date='2025-10-30'):
    """Crée une colonne conditionnelle basée sur user_mamba et période de dates"""
    # Convertir les dates en Timestamp
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    
    # Convertir user_mamba en numérique si nécessaire
    df.loc[:, user_mamba_col] = pd.to_numeric(df[user_mamba_col], errors='coerce')
    
    # Créer la condition combinée
    condition = (
        df[user_mamba_col].isin(target_values) & 
        (df[date_col] >= start_ts) & 
        (df[date_col] <= end_ts)
    )
    
    # Appliquer la condition
    df.loc[:, output_col] = np.where(condition, 'yes', 'no')
    
    print(f"Colonne {output_col} créée:")
    print(df[output_col].value_counts())
    
    return df


def calculate_visits_remaining(df, cat_col='manutrition_type', num_col='total_suivi_mamba', out_col='visits_remaining'):
    """Calcule les visites restantes selon la logique IFS Excel"""
    # Initialiser avec la valeur par défaut
    df[out_col] = 0
    
    # Condition 1: MAM avec total_suivi_mamba <= 12 -> 8 - total_suivi_mamba
    mam_condition = (df[cat_col] == 'MAM') & (df[num_col] <= 12)
    df.loc[mam_condition, out_col] = 8 - df.loc[mam_condition, num_col]
    df[out_col] = df[out_col].fillna(0).astype(int)
    # Condition 2: MAS avec total_suivi_mamba <= 18 -> 12 - total_suivi_mamba
    mas_condition = (df[cat_col] == 'MAS') & (df[num_col] <= 18)
    df.loc[mas_condition, out_col] = 12 - df.loc[mas_condition, num_col]
    
    return df

def groupby_keep_all_columns(df, group_col='caseid'):
    """Groupe par caseid en gardant toutes les colonnes avec des agrégations appropriées"""
    # Identifier les types de colonnes pour l'agrégation
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
    string_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
    
    # Retirer la colonne de groupement des listes
    if group_col in numeric_cols:
        numeric_cols.remove(group_col)
    if group_col in date_cols:
        date_cols.remove(group_col)
    if group_col in string_cols:
        string_cols.remove(group_col)
    
    # Créer le dictionnaire d'agrégation
    agg_dict = {}
    
    # Pour les colonnes numériques: somme
    for col in numeric_cols:
        agg_dict[col] = 'sum'
    
    # Pour les colonnes de dates: maximum (dernière date)
    for col in date_cols:
        agg_dict[col] = 'max'
    
    # Pour les colonnes string: première valeur
    for col in string_cols:
        agg_dict[col] = 'first'
    
    return df.groupby(group_col, as_index=False).agg(agg_dict)

def create_smart_aggregation_dict(df, group_col='caseid'):
    """Crée un dictionnaire d'agrégation intelligent selon le type de colonnes"""
    agg_dict = {}
    
    for col in df.columns:
        if col == group_col:
            continue  # Skip la colonne de groupement
        elif col == 'formid':
            agg_dict[col] = 'count'  # Compter les visites
        elif col in ['date_of_visit', 'session_date']:  # Gérer aussi session_date
            agg_dict[col] = ['min', 'max']  # Première ET dernière date
        elif col == 'nbr_visit_succeed_suivi':
            agg_dict[col] = 'last'  # Dernière valeur pour nbr_visit_succeed_suivi
        elif df[col].dtype == 'datetime64[ns]':
            agg_dict[col] = 'max'    # Dernière date pour les autres colonnes datetime
        elif pd.api.types.is_numeric_dtype(df[col]):
            # Pour les colonnes numériques (incluant les dummies 0/1)
            if df[col].isin([0, 1]).all():
                agg_dict[col] = 'sum'  # Sommer les variables dummy
            else:
                agg_dict[col] = 'sum'  # Sommer les quantités/mesures
        else:
            # Pour les colonnes string/object
            agg_dict[col] = 'first'  # Prendre la première valeur
    
    return agg_dict


# Cette ligne est maintenant inutile car le filtrage est déjà fait dans la fonction
# condition_avant_septembre = condition_avant_septembre[condition_user_mamba]
#=========================================================================================================
# etape_enroled #16


#=======================================================================================================
# OUTPUT DIRECTORY SETUP
# Créer le dossier de sortie
output_dir = os.path.join("outputs", "NUTRITION")
os.makedirs(output_dir, exist_ok=True)
print(f"✓ Dossier de sortie vérifié: {output_dir}")

#=======================================================================================================
# PERIOD PIPELINE
# Définir start_date avec une valeur par défaut si None
start_date = pd.Timestamp("2025-01-01")
end_date = pd.Timestamp.now()

start_date_nut = pd.Timestamp("2024-10-01")
end_date_nut = pd.Timestamp(datetime.today().date())
#=========================================================================================================
print("="*60)
print(f"DEBUT DE LA PIPELINE DE NUTRITION à {today_str}")
print(f"DE {start_date} à {end_date}")
print("="*60)
#=====================================================================================================================
# etape_depistage #1 - PIPELINE STYLE
dep_col = [
    "form.depistage.date_de_visite", "form.depistage.last_name", "form.depistage.first_name", "form.depistage.gender",
    "form.depistage.date_of_birth", "form.depistage.muac", "form.depistage.weight_kg", "form.depistage.height",
    
    "form.depistage.edema", "form.depistage.lesion_cutane", "form.depistage.diarrhea", "form.depistage.autres_symptomes",
    "form.depistage.phone_number", "form.depistage.photo_depistage", "form.depistage.office", "form.depistage.departement",

    "form.depistage.commune", "form.depistage.fullname", "form.depistage.eligible",
    "form.depistage.manutrition_type", "form.case.@case_id", "completed_time", "started_time",
    
    "username", "received_on", "form_link"
]

# DEBUG: Afficher le répertoire de travail actuel
print(f"Répertoire de travail actuel: {os.getcwd()}")

# Construire le chemin du fichier de dépistage
depistage_file = f"Caris Health Agent - NUTRITON[HIDDEN] - Dépistage Nutritionnel (created 2025-06-26) {today_str}.xlsx"
print(f"Chemin du fichier de dépistage: {depistage_file}")
print(f"Le fichier existe-t-il? {os.path.exists(depistage_file)}")


# If depistage_file is not absolute, join with DATA_DIR
file_path = depistage_file if os.path.isabs(depistage_file) else os.path.join(DATA_DIR, depistage_file)
depistage = (
    pd.read_excel(file_path, parse_dates=True)
    .pipe(select_columns, dep_col)
    .pipe(print_shape, "dépistage télechargés avec succes")
    .pipe(rename_cols, {'form.case.@case_id': 'caseid','form.depistage.date_de_visite':'date_de_depistage'})
    .pipe(clean_column_names, 'form.depistage.')
    .pipe(get_age_in_year, 'date_of_birth')
    .pipe(get_age_in_months, 'date_of_birth')
    .pipe(assign_age_range_from_months, months_col="age_months", out="age_range")
    .pipe(convert_numeric_column, 'muac', fill_value=0, replace_value='---')
    .pipe(lambda df: df.assign(depistage_code=(
        "NUT-" + df['caseid'].astype(str).str[:3] + "-" + df['caseid'].astype(str).str[-4:]
    ).str.upper()))
    .pipe(print_message, "Nombre depistage de janvier 2024 à aujourd'hui")
    .pipe(capitalize_column, 'departement')
)

depistage_filtered = (
    depistage
    .pipe(extraire_data, start_date=start_date_nut, end_date=end_date_nut, date_col='date_de_depistage')
    .pipe(save_to_excel, os.path.join(output_dir, "depistage_filtered.xlsx"), sheet_name="Janvier_a_aujourdhui", index=False)
)
#==========================================================================================================
# SECTION SUIVI - TRANSFORMATION AVEC PIPE
#==========================================================================================================
print("=== TRAITEMENT DES DONNÉES DE SUIVI ===")

suivi_nut = (
    load_excel_pipe(
        f"Caris Health Agent - Nutrition - Suivi nutritionel (created 2025-06-26) {today_str}.xlsx",
        usecols=[
            "formid", "form.date_of_visit", "form.type_of_visit", 
            "form.is_available_at_time_visit", "form.enfant_absent", 
            "form.nbr_visit", "form.nbr_visit_succeed", "form.case.@case_id",
            "username", "form_link", "form.discharge.raison_pour_la_sortie",
            "form.discharge.last_weight", "form.discharge.last_height", 
            "form.discharge.last_muac", 
            "form.followup_visit.Medicaments_Administres.mamba_quantity_given"
        ],
        parse_dates=True
    )
    .pipe(clean_column_names, expr_to_remove='form.')
    .pipe(rename_cols, {
        "case.@case_id": "caseid",
        "nbr_visit_succeed": "nbr_visit_succeed_suivi",
        "nbr_visit": "nbr_visit_suivi",
        "username": "username_suivi",
        "followup_visit.Medicaments_Administres.mamba_quantity_given": "mamba_quantity"
    })
    .pipe(convert_datetime_column, 'date_of_visit', errors='coerce')
    .pipe(clean_column_names, expr_to_remove='discharge.')
    .pipe(select_columns, [
        'formid', 'type_of_visit', 'date_of_visit', 'caseid', 'username_suivi', 
        'is_available_at_time_visit', 'enfant_absent', 'raison_pour_la_sortie',
        'last_weight', 'last_height', 'last_muac', 'nbr_visit_succeed_suivi', 
        'mamba_quantity'
    ])
    .pipe(clean_raison_sortie_column, 'raison_pour_la_sortie', 'no_info')
    .pipe(convert_numeric_column, 'mamba_quantity', fill_value=0, replace_value='---')
    .pipe(convert_numeric_column, 'last_weight', fill_value=0, replace_value='---')
    .pipe(convert_numeric_column, 'last_height', fill_value=0, replace_value='---')
    .pipe(convert_numeric_column, 'last_muac', fill_value=0, replace_value='---')
    .pipe(create_visit_mamba_column, 'mamba_quantity', 'visit_mamba')
    .pipe(extraire_data, start_date=start_date_nut, end_date=end_date_nut, date_col='date_of_visit')
    .pipe(print_shape, f"Nombre de suivi nutritionnel de janvier 2024 à aujourd'hui")
    .pipe(save_to_excel, os.path.join(output_dir, "suivi_nutritionel.xlsx"), sheet_name="Janvier_a_aujourdhui", index=False)
)
#=================================================================================================================
# Appliquer get_dummies sur tout le DataFrame en spécifiant la colonne
suivi_with_dummies = pd.get_dummies(
    suivi_nut, 
    columns=['type_of_visit','raison_pour_la_sortie','visit_mamba'], 
    dummy_na=True,
    prefix=['type_of_visit', 'raison_pour_la_sortie', 'visit_mamba']  # Pas de préfixe pour type_of_visit
)
suivi_with_dummies.to_excel(os.path.join(output_dir, 'suivi_with_dummies.xlsx'), index=False)

# Agrégation avec la fonction aggregate par caseid - GARDER TOUTES LES COLONNES
# Créer un dictionnaire d'agrégation intelligent selon le type de données

# Appliquer l'agrégation intelligente
agg_dict = create_smart_aggregation_dict(suivi_with_dummies)
suivi_aggregated = suivi_with_dummies.groupby('caseid', as_index=False).agg(agg_dict)

# Gérer les colonnes avec plusieurs agrégations (date_of_visit)
if ('date_of_visit', 'min') in suivi_aggregated.columns:
    # Aplatir les colonnes multi-niveau et créer des colonnes séparées
    suivi_aggregated = suivi_aggregated.copy()
    suivi_aggregated['first_visit_date'] = suivi_aggregated[('date_of_visit', 'min')]
    suivi_aggregated['last_visit_date'] = suivi_aggregated[('date_of_visit', 'max')]
    
    # Supprimer les colonnes multi-niveau
    suivi_aggregated.drop(columns=[('date_of_visit', 'min'), ('date_of_visit', 'max')], inplace=True)
    
    # Aplatir le reste des colonnes
    suivi_aggregated.columns = [col[0] if isinstance(col, tuple) else col for col in suivi_aggregated.columns]

# Renommer pour plus de clarté
suivi_aggregated = suivi_aggregated.rename(columns={
    'formid': 'total_visits'
})

# Supprimer la colonne type_of_visit_nan si elle existe
if 'type_of_visit_nan ' or 'visit_mamba_nan' in suivi_aggregated.columns:
    suivi_aggregated = suivi_aggregated.drop(columns=['type_of_visit_nan', 'visit_mamba_nan'])
    print("✅ Colonnes supprimées")

print(f"Agrégation terminée: {suivi_aggregated.shape[0]} patients uniques avec {suivi_aggregated.shape[1]} colonnes")
suivi_aggregated.to_excel(os.path.join(output_dir, 'suivi_aggregated_complete.xlsx'), index=False)
print(f"✅ Fichier sauvegardé: {os.path.join(output_dir, 'suivi_aggregated_complete.xlsx')}")
print(f"✅ Toutes les {suivi_aggregated.shape[1]} colonnes ont été conservées avec l'agrégation appropriée")

# Créer la colonne user_mamba en extrayant les chiffres du username
print("\n=== CRÉATION DE LA COLONNE USER_MAMBA ===")
suivi_aggregated['user_mamba_suivi'] = suivi_aggregated['username_suivi'].astype(str).str.extract(r'(\d+)')
suivi_aggregated['user_mamba_suivi'] = suivi_aggregated['user_mamba_suivi'].fillna('2').replace('', '2')

   
suivi_aggregated = (
    suivi_aggregated
    .pipe(create_mamba_period_column, 
          user_mamba_col='user_mamba_suivi',
          output_col='mamba_disponible_suivi',
          start_date='2025-05-01', 
          end_date='2025-10-30', 
          date_col='last_visit_date')
    .pipe(clean_column_names, 'type_of_visit_')
    .pipe(clean_column_names, 'raison_pour_la_sortie_')
)

# Créer la colonne sortie avec la condition dernière_visite
print("\n=== CRÉATION DE LA COLONNE SORTIE ===")
    
# Condition: si dernière_visite = 0 (pas de visite) alors 'yes', sinon 'no'
condition = suivi_aggregated['derniere_visite'] != 0 # 1 = pas de date de visite (NaT)

# Appliquer la condition avec np.where
suivi_aggregated['sortie'] = np.where(condition, 'yes', 'no')
# Créer la colonne raison_pour_la_sortie avec conditions hiérarchiques
print("\n=== CRÉATION DE LA COLONNE RAISON_POUR_LA_SORTIE ===")
# Vérifier si les colonnes existent
raison_cols = ['abandonne_programme', 'atteind_poids_projecte', 'pas_atteind_poids']
existing_cols = [col for col in raison_cols if col in suivi_aggregated.columns]
missing_cols = [col for col in raison_cols if col not in suivi_aggregated.columns]

if missing_cols:
    print(f"⚠️  Colonnes manquantes pour raison_pour_la_sortie: {missing_cols}")

if existing_cols:
    print(f"✓ Colonnes trouvées pour raison_pour_la_sortie: {existing_cols}")
    
    # Convertir les colonnes en numérique si elles ne le sont pas déjà
    for col in existing_cols:
        suivi_aggregated[col] = pd.to_numeric(suivi_aggregated[col], errors='coerce').fillna(0)
    
    # Créer la colonne avec conditions hiérarchiques
    # Initialiser avec une valeur par défaut
    suivi_aggregated['raison_pour_la_sortie'] = 'no_info'
    
    # Appliquer les conditions dans l'ordre de priorité
    if 'abandonne_programme' in suivi_aggregated.columns:
        mask = suivi_aggregated['abandonne_programme'] != 0
        suivi_aggregated.loc[mask, 'raison_pour_la_sortie'] = 'abandonne_programme'
    
    if 'atteind_poids_projecte' in suivi_aggregated.columns:
        mask = (suivi_aggregated['atteind_poids_projecte'] != 0) & (suivi_aggregated['raison_pour_la_sortie'] == 'no_info')
        suivi_aggregated.loc[mask, 'raison_pour_la_sortie'] = 'atteind_poids_projecte'
    
    if 'pas_atteind_poids' in suivi_aggregated.columns:
        mask = (suivi_aggregated['pas_atteind_poids'] != 0) & (suivi_aggregated['raison_pour_la_sortie'] == 'no_info')
        suivi_aggregated.loc[mask, 'raison_pour_la_sortie'] = 'pas_atteind_poids'
    
    print(f"✅ Colonne 'raison_pour_la_sortie' créée:")
    print(suivi_aggregated['raison_pour_la_sortie'].value_counts())
else:
    print("❌ Aucune colonne de raison trouvée, colonne 'raison_pour_la_sortie' non créée")
    
# Sauvegarder le fichier final avec user_mamba
suivi_aggregated.to_excel(os.path.join(output_dir, 'suivi_aggregated_final.xlsx'), index=False)
print(f"✅ Fichier final sauvegardé: {os.path.join(output_dir, 'suivi_aggregated_final.xlsx')}")
#=========================================================================================================
#===============================================================================================
# etape_enroled #1 - PIPELINE STYLE

enroled_col = [
    "caseid", "name", "eligible", "manutrition_type", "date_of_birth",
    "gender", "muac", "nbr_visit", "is_alive", "death_date",
    "death_reason", "nbr_visit_succeed", "admission_muac", "office", "commune",
    "departement", "household_collection_date", "household_number", "has_household", "closed",
    "closed_date", "last_modified_date", "opened_date", "case_link", "enrollement_date_de_visite",
    "enrollment_date", "enrollment_eligibility", "enrollment_manutrition_type", "is_enrolled", "hiv_test_done",
    "hiv_test_result", "club_id", "club_name","date_admission", "child_often_sick", "exclusive_breastfeeding_6months",
    "breastfeeding_received", "enrrolled_where", "has_mamba", "last_mamba_date", "nut_code","last_date_of_visit","is_approve_by_manager","raison_de_non_approbation",
    "last_modified_by_user_username","closed_by_username","approval_date","visit_reason_not_reachable"
]

start_date_nut = pd.Timestamp("2025-01-01")
end_date_nut = pd.Timestamp(datetime.today().date())
#==========================================================================================================
# Pipeline d'enrôlement avec .pipe()
nut_filtered = (
    pd.read_excel(os.path.join(DATA_DIR, f"Nutrition (created 2025-04-25) {today_str}.xlsx"), engine="openpyxl")
    .pipe(select_columns, enroled_col)
    .pipe(convert_datetime_column, "last_mamba_date", errors='coerce')
    .pipe(print_shape, "Fichier enrollement Télechargé avec succès")
    .pipe(convert_datetime_column, "enrollement_date_de_visite", errors='coerce')
    .pipe(convert_datetime_column, "date_admission", errors='coerce')
    .pipe(combine_columns, "enrollement_date_de_visite", "date_admission", col3="date_enrollement", na_value=None)
    .pipe(clean_enrolled_where,
          col="enrrolled_where", 
          old_value="---", 
          new_value="community")
    .pipe(capitalize_column, 'departement')
    .pipe(get_age_in_year, 'date_of_birth')
    .pipe(get_age_in_months, 'date_of_birth')
    .pipe(assign_age_range, months_col="age_months")
    .pipe(merge_with_depistage, depistage, ['date_de_depistage','caseid','username'])
    .pipe(extract_user_mamba, username_col='username', output_col='user_mamba')
    .pipe(create_mamba_period_column, 
          user_mamba_col='user_mamba', 
          date_col='date_enrollement',
          output_col='mamba_period_eligible',
          target_values=[1, 5, 6],
          start_date='2025-05-01', 
          end_date='2025-10-30')
    .pipe(create_backup_and_continue, backup_var_name="depistage_backup")
    .pipe(save_to_excel, os.path.join(output_dir, f"enrolés_global.xlsx"), index=False)
    .pipe(lambda df: df.drop_duplicates(subset=['caseid'], keep='first'))
)

# Séparer le DataFrame en deux selon enrrolled_where
nut_filtered_caris_itu = nut_filtered[nut_filtered['enrrolled_where'] == 'caris_itu'].copy()
nut_filtered_community = nut_filtered[nut_filtered['enrrolled_where'] == 'community'].copy()

print(f"✅ Séparation effectuée:")
print(f"  - Patients enrôlés à caris_itu: {nut_filtered_caris_itu.shape[0]}")
print(f"  - Patients enrôlés en community: {nut_filtered_community.shape[0]}")

# Sauvegarder les fichiers séparés
nut_filtered_caris_itu.to_excel(os.path.join(output_dir, f"enrolés_caris_itu.xlsx"), index=False)
nut_filtered_community.to_excel(os.path.join(output_dir, f"enrolés_community.xlsx"), index=False)

print(f"✅ Fichiers sauvegardés:")
print(f"  - {os.path.join(output_dir, f'enrolés_caris_itu.xlsx')}")
print(f"  - {os.path.join(output_dir, f'enrolés_community.xlsx')}")

#=========================================================================================================
# select where approval_date is betwenn start_date and end_date in enroled dataframe
nut_filtered['approval_date'] = pd.to_datetime(nut_filtered['approval_date'], errors='coerce')
aproval_filtered = nut_filtered[
    (nut_filtered['approval_date'] >= start_date_nut) &
    (nut_filtered['approval_date'] <= end_date_nut)
].copy()
print(f"✅ Filtrage par approval_date effectué:")
print(f"  - Patients approuvés entre {start_date_nut.date()} et {end_date_nut.date()}: {aproval_filtered.shape[0]}")
save_to_excel(aproval_filtered, os.path.join(output_dir, f"enrolés_approvés_{start_date_nut.date()}_à_{end_date_nut.date()}.xlsx"), index=False)
#=========================================================================================================
print("\n=== VÉRIFICATION DE L'ENRÔLEMENT DANS LE SUIVI ===")
#=========================================================================================================
suivi_enroled = creer_colonne_match_conditional(
    df1=suivi_aggregated[[
        'caseid', 'total_visits', 'username_suivi', 'is_available_at_time_visit', 
        'enfant_absent', 'last_weight', 'last_height', 'last_muac', 
        'nbr_visit_succeed_suivi', 'mamba_quantity', 'Visite_de_Suivi', 
        'derniere_visite', 'suivi_post_exeat', 'abandonne_programme', 
        'atteind_poids_projecte', 'pas_atteind_poids', 'visit_mamba_no', 
        'visit_mamba_yes', 'first_visit_date', 'last_visit_date', 
        'user_mamba_suivi', 'mamba_disponible_suivi', 'sortie', 'raison_pour_la_sortie'
    ]],
    df2=nut_filtered,
    on="caseid",
    nouvelle_colonne="suivi_exists",
    mapping={'both': 'yes', 'left_only': 'no', 'right_only': 'no'}
)

suivi_enroled_community = suivi_enroled[suivi_enroled['enrrolled_where'] != 'caris_itu'].copy()
suivi_enroled_ids = suivi_enroled['caseid'].unique()
nut_filtered_caris = nut_filtered_caris_itu[~nut_filtered_caris_itu['caseid'].isin(suivi_enroled_ids)].copy()
nut_filtered_caris_ids = nut_filtered_caris['caseid'].unique()
approval_filtered_final = aproval_filtered[(~aproval_filtered['caseid'].isin(nut_filtered_caris_ids)) & (~aproval_filtered['caseid'].isin(suivi_enroled_ids))].copy()
nut_filtered_caris_final = pd.concat([approval_filtered_final, nut_filtered_caris], ignore_index=True)
# Reset indexes to avoid concatenation issues
nut_filtered_caris_final = nut_filtered_caris_final.reset_index(drop=True)
suivi_enroled = suivi_enroled.reset_index(drop=True)
# Fix concatenation with proper index handling
print(f"Debug: nut_filtered_caris_final shape: {nut_filtered_caris_final.shape}")
print(f"Debug: suivi_enroled shape: {suivi_enroled.shape}")

nut_filtered_caris_final = nut_filtered_caris_final.reset_index(drop=True)
suivi_enroled = suivi_enroled.reset_index(drop=True)

# Concatenate with explicit parameters
enroled_total = pd.concat([nut_filtered_caris_final, suivi_enroled], ignore_index=True, sort=False)
print(f"✅ Concatenation successful: {enroled_total.shape[0]} total rows")
print(f"✅ Remplissage des valeurs NA pour nut_filtered_caris_final:")
print(f"  - Avant remplissage: {nut_filtered_caris_final.shape[0]} patients")

# Ajouter les colonnes manquantes avec des valeurs par défaut
columns_to_add = [
    'total_visits', 'username_suivi', 'is_available_at_time_visit', 
    'enfant_absent', 'last_weight', 'last_height', 'last_muac', 
    'nbr_visit_succeed_suivi', 'mamba_quantity', 'Visite_de_Suivi', 
    'derniere_visite', 'suivi_post_exeat', 'abandonne_programme', 
    'atteind_poids_projecte', 'pas_atteind_poids', 'visit_mamba_no', 
    'visit_mamba_yes', 'first_visit_date', 'last_visit_date', 
    'user_mamba_suivi', 'mamba_disponible_suivi', 'sortie', 'raison_pour_la_sortie'
]

for col in columns_to_add:
    if col not in nut_filtered_caris_final.columns:
        nut_filtered_caris_final[col] = None

# Remplissage selon les règles spécifiées
# Colonnes numériques = 0
numeric_cols = ['total_visits', 'last_weight', 'last_height', 'nbr_visit_succeed_suivi', 
                'mamba_quantity', 'Visite_de_Suivi', 'derniere_visite', 'suivi_post_exeat', 
                'abandonne_programme', 'atteind_poids_projecte', 'pas_atteind_poids', 
                'visit_mamba_no', 'visit_mamba_yes','last_muac']

for col in numeric_cols:
    if col in enroled_total.columns:
        enroled_total[col] = enroled_total[col].fillna(0).infer_objects(copy=False)
        print(f"✅ Colonne {col} remplie avec 0")
    else:
        print(f"⚠️ Colonne {col} manquante dans enroled_total")

# username_suivi = equivalent à username (si disponible)
if 'username' in enroled_total.columns:
    enroled_total['username_suivi'] = enroled_total['username_suivi'].fillna(enroled_total['username']).infer_objects(copy=False)
else:
    enroled_total['username_suivi'] = enroled_total['username_suivi'].fillna('no_info')

# user_mamba_suivi = equivalent à user_mamba (si disponible)
if 'user_mamba' in enroled_total.columns:
    enroled_total['user_mamba_suivi'] = enroled_total['user_mamba_suivi'].fillna(enroled_total['user_mamba']).infer_objects(copy=False)
else:
    enroled_total['user_mamba_suivi'] = enroled_total['user_mamba_suivi'].fillna('1')

# mamba_disponible_suivi = mamba_period_eligible (si disponible)
if 'mamba_period_eligible' in enroled_total.columns:
    enroled_total['mamba_disponible_suivi'] = enroled_total['mamba_disponible_suivi'].fillna(enroled_total['mamba_period_eligible'])
else:
    enroled_total['mamba_disponible_suivi'] = enroled_total['mamba_disponible_suivi'].fillna('no')

# Colonnes texte avec valeurs spécifiques
enroled_total['sortie'] = enroled_total['sortie'].fillna('no')
enroled_total['raison_pour_la_sortie'] = enroled_total['raison_pour_la_sortie'].fillna('no_info')

# Dates: first_visit_date et last_visit_date = opened_date (si disponible)
if 'opened_date' in enroled_total.columns:
    enroled_total['opened_date'] = pd.to_datetime(enroled_total['opened_date'], errors='coerce')
    enroled_total['first_visit_date'] = enroled_total['first_visit_date'].fillna(enroled_total['opened_date'])
    enroled_total['last_visit_date'] = enroled_total['last_visit_date'].fillna(enroled_total['opened_date'])
else:
    # Si opened_date n'existe pas, utiliser une date par défaut
    default_date = pd.Timestamp('1901-01-01')
    enroled_total['first_visit_date'] = enroled_total['first_visit_date'].fillna(default_date)
    enroled_total['last_visit_date'] = enroled_total['last_visit_date'].fillna(default_date)
# Colonnes texte avec valeurs spécifiques
enroled_total['is_available_at_time_visit'] = enroled_total['is_available_at_time_visit'].fillna('1')
enroled_total['enfant_absent'] = enroled_total['enfant_absent'].fillna('---')
enroled_total['suivi_exists'] = enroled_total['suivi_exists'].fillna('no')
#'enfant_absent',

print(f"✅ Remplissage des NA terminé pour nut_filtered_caris_final")

# Créer la colonne 'enroled' selon les conditions spécifiées
print("=== CRÉATION DE LA COLONNE ENROLED ===")

# Définir les dates de la période
start_date_enroled = pd.Timestamp("2024-12-01")
end_date_enroled = pd.Timestamp.now()

# Vérifier que les colonnes nécessaires existent
required_cols = ['closed_date', 'date_enrollement', 'mamba_disponible_suivi']
missing_cols = [col for col in required_cols if col not in enroled_total.columns]

if missing_cols:
    print(f"⚠️  Colonnes manquantes: {missing_cols}")
    # Créer les colonnes manquantes avec des valeurs par défaut si nécessaire
    for col in missing_cols:
        if col == 'closed_date':
            enroled_total[col] = '---'
        elif col == 'date_enrollement':
            enroled_total[col] = pd.Timestamp('1901-01-01')
        elif col == 'mamba_disponible_suivi':
            enroled_total[col] = 'no'

# Convertir date_enrollement en datetime si ce n'est pas déjà fait
enroled_total['date_enrollement'] = pd.to_datetime(enroled_total['date_enrollement'], errors='coerce')

# Créer la condition combinée pour enroled = 'yes'
condition_enroled = (
    (enroled_total['closed_date'] == '---') &
    (enroled_total['date_enrollement'] >= start_date_enroled) &
    (enroled_total['date_enrollement'] <= end_date_enroled) &
    (enroled_total['mamba_disponible_suivi'] == 'no')
)

# Appliquer la condition avec np.where
enroled_total['enroled'] = np.where(condition_enroled, 'yes', 'no')
enroled_total = calculate_visits_remaining(df=enroled_total, cat_col='manutrition_type', num_col='nbr_visit_succeed_suivi', out_col='visits_remaining')
enroled_total = calculate_visits_remaining(df=enroled_total, cat_col='manutrition_type', num_col='visit_mamba_yes', out_col='mamba_remaining')
# Créer la condition pour child_to_be_exited avec une meilleure lisibilité
enroled_total['child_to_be_exited'] = np.where(
    (enroled_total['enrrolled_where'] != 'caris_itu') & 
    (enroled_total['mamba_remaining'] == 0) & 
    (enroled_total['derniere_visite'] == 0), 
    'yes', 
    'no'
)


# convert household_collection_date in datetime
enroled_total = convert_datetime_column(enroled_total, 'household_collection_date', errors='coerce')
enroled_total = convert_datetime_column(enroled_total, 'approval_date', errors='coerce')
# repalce "---" in has_household by "no"
enroled_total['has_household'] = enroled_total['has_household'].replace('---', 'no')
enroled_total['has_mamba'] = enroled_total['has_mamba'].replace('---', 'no')
# fillna has_mamba with 'no'
enroled_total['has_mamba'] = enroled_total['has_mamba'].fillna('no')
enroled_total['is_approve_by_manager'] = enroled_total['is_approve_by_manager'].replace('---', 'no')
# convert household_number in numeric
enroled_total = convert_numeric_column(enroled_total, 'household_number', fill_value=0, replace_value='---')
# create column visit_mamba where visit_mamba_yes > 0 then 'yes' else 'no'
enroled_total['visit_mamba'] = np.where(
    (enroled_total['visit_mamba_yes'] > 0) | 
    (enroled_total['has_mamba'] == 'yes'),
    'yes',
    'no'
)

# create column visit_mamba where visit_mamba_yes > 0 then 'yes' else 'no'
enroled_total['actif'] = np.where(
    (enroled_total['derniere_visite'] == 0) & 
    (enroled_total['suivi_post_exeat'] == 0),
    'yes',
    'no'
)
# drop where visit_reason_not_reachable is not = '---' and visit_mamba == 'no'
enroled_total = enroled_total[~((enroled_total['visit_reason_not_reachable'] != '---') & (enroled_total['visit_mamba'] == 'no'))].copy()
# Sauvegarder le fichier final de suivi_enroled
save_to_excel(
    enroled_total, 
    os.path.join(output_dir, f"suivi_enroled_total.xlsx"), 
    sheet_name="enrole_avec_visite", 
    index=False
)

# Sauvegarder le fichier des enrolés de suivi_enroled
save_to_excel(
    enroled:=enroled_total[enroled_total['enroled'] == 'yes'], 
    os.path.join(output_dir, f"enroled_final.xlsx"), 
    sheet_name="enrole_final", 
    index=False
)

print("=== LES ELIGIBLES EN ATTENTE ===")
# Filtrer les éligibles en attente
eligibles = depistage_filtered[depistage_filtered['eligible'] == 'yes']
suivi_aggregated_ids = suivi_aggregated['caseid'].unique()
# les caseids des eligibles qui ne sont pas dans suivi_aggregated
eligible_sans_suivi = eligibles[~eligibles['caseid'].isin(suivi_aggregated_ids)].copy()
print(f"Nombre d'éligibles sans suivi: {eligible_sans_suivi.shape[0]}")
eligible_sans_suivi_ids = eligible_sans_suivi['caseid'].unique()
# les caseids des eligible_sans_suivi qui sont dans nut_filtered
eligible_filtered = nut_filtered[nut_filtered['caseid'].isin(eligible_sans_suivi_ids)].copy()
print(f"Nombre d'éligibles après filtrage: {eligible_filtered.shape[0]}")

print("=== CRÉATION DE LA COLONNE EN_ATTENTE ===")

# Vérifier que les colonnes nécessaires existent
required_cols_attente = ['date_admission', 'closed_date', 'date_enrollement', 'club_id', 'enrrolled_where']
missing_cols_attente = [col for col in required_cols_attente if col not in eligible_filtered.columns]

if missing_cols_attente:
    print(f"⚠️  Colonnes manquantes pour en_attente: {missing_cols_attente}")
    # Créer les colonnes manquantes avec des valeurs par défaut
    for col in missing_cols_attente:
        eligible_filtered[col] = '---'

# Vérifier si approval_date existe, sinon la créer
if 'approval_date' not in eligible_filtered.columns:
    eligible_filtered['approval_date'] = '---'
    print("✓ Colonne 'approval_date' créée avec valeur par défaut '---'")
eligible_filtered['date_enrollement'] = eligible_filtered['date_enrollement'].fillna('---')
# Créer la condition combinée pour en_attente = 'yes'
condition_en_attente = (
    (eligible_filtered['closed_date'] == '---') &
    (eligible_filtered['date_enrollement'] == '---') &
    (eligible_filtered['club_id'] == '---') &
    (eligible_filtered['enrrolled_where'] == 'community') &
    (eligible_filtered['is_approve_by_manager'] == '---')
)

# Appliquer la condition avec np.where
eligible_filtered['en_attente'] = np.where(condition_en_attente, 'yes', 'no')

print(f"✅ Colonne 'en_attente' créée:")
print(f"  - en_attente = yes: {(eligible_filtered['en_attente'] == 'yes').sum()}")
print(f"  - en_attente = no: {(eligible_filtered['en_attente'] == 'no').sum()}")

save_to_excel(
    eligible_filtered, 
    os.path.join(output_dir, f"eligible_filtered.xlsx"), 
    sheet_name="eligible_filtered", 
    index=False
)

save_to_excel(
    en_attente := eligible_filtered[eligible_filtered['en_attente'] == 'yes'], 
    os.path.join(output_dir, f"en_attente.xlsx"), 
    sheet_name="en_attente", 
    index=False
)

# sans_suivi = caseids qui ne sont ni dans enroled ni dans en_attente
enroled_ids = enroled['caseid'].unique()
en_attente_ids = en_attente['caseid'].unique()
all_excluded_ids = set(enroled_ids) | set(en_attente_ids)
sans_suivi = eligible_filtered[~eligible_filtered['caseid'].isin(all_excluded_ids)].copy()

save_to_excel(
    sans_suivi, 
    os.path.join(output_dir, f"sans_suivi.xlsx"), 
    sheet_name="sans_suivi", 
    index=False
)

print("=== LES CLUBS DE NUTRITION ===")
club_filename = f"ht_nutrition_presence (created 2025-08-18) {today_str}.xlsx"
club_file_path = os.path.join(DATA_DIR, club_filename)
print(f"Chemin du fichier de club: {club_file_path}")
print(f"Le fichier existe-t-il? {os.path.exists(club_file_path)}")
clubs = pd.read_excel(club_file_path, parse_dates=True)
club_columns = [
    "nutrition_case_id", "caseid", "name", "is_member_present", "member_type", "indices.ht_club_nutrition",
    "last_modified_by_user_username", "owner_name", "session_date","form_link"
]
club_nutrition = (
    clubs
    .pipe(select_columns, club_columns)
    .pipe(rename_cols, {'caseid':'session_id','indices.ht_club_nutrition': 'club_id', 'last_modified_by_user_username': 'data_clerk', 'owner_name': 'commune', 'nutrition_case_id':'caseid'})
    .pipe(convert_datetime_column, 'session_date', errors='coerce')
    .pipe(convert_numeric_column, 'is_member_present', fill_value=1, replace_value='---')
    .pipe(clean_username_column, 'data_clerk')
)

# Lesclub avec date inferieure ou egal a aujourd'hui
club_nutrition_filtered = (
    club_nutrition
    .pipe(extraire_data, start_date=start_date_nut, end_date=end_date_nut, date_col='session_date')
    .pipe(merge_with_depistage, depistage, ['date_de_depistage','caseid','username'])
    .pipe(fill_office_from_data_clerk, 'data_clerk', 'office')
    .pipe(merge_with_depistage, enroled, ['date_enrollement','caseid'])
    .pipe(merge_with_depistage, suivi_aggregated, ['first_visit_date','last_visit_date','caseid'])
    .pipe(print_shape, f"Nombre de clubs de nutrition de mai 2025 à aujourd'hui")
    .pipe(save_to_excel, os.path.join(output_dir, "club_nutrition_filtered.xlsx"), sheet_name="Mai_a_aujourdhui", index=False)
)

# Lesclub avec date superieure a aujourd'hui
club_future = (
    club_nutrition
    .pipe(select_columns, club_columns)
    .pipe(rename_cols, {'caseid':'session_id','indices.ht_club_nutrition': 'club_id', 'last_modified_by_user_username': 'username', 'owner_name': 'commune', 'nutrition_case_id':'caseid'})
    .pipe(convert_datetime_column, 'session_date', errors='coerce')
    .pipe(convert_numeric_column, 'is_member_present', fill_value=1, replace_value='---')
)
clubs_future = club_future[club_future['session_date'] > end_date_nut].copy()
print(f"Nombre de clubs avec date de session future: {clubs_future.shape[0]}")
if not clubs_future.empty:
    print("⚠️  Attention: Des sessions de club ont des dates futures:")
    save_to_excel(
        clubs_future, 
        os.path.join(output_dir, "clubs_future.xlsx"), 
        sheet_name="Clubs_Futurs", 
        index=False
    )
else:
    print("✓ Aucune session de club avec date future trouvée.")

#=================================================================================================================
# Appliquer get_dummies sur tout le DataFrame en spécifiant la colonne
club_with_dummies = pd.get_dummies(
    club_nutrition_filtered, 
    columns=['member_type'], 
    dummy_na=False,
    prefix=['member_type']  # Pas de préfixe pour type_of_visit
)
club_with_dummies.to_excel(os.path.join(output_dir, 'club_with_dummies.xlsx'), index=False)

# Agrégation avec la fonction aggregate par caseid - GARDER TOUTES LES COLONNES
# Créer un dictionnaire d'agrégation intelligent selon le type de données

# Appliquer l'agrégation intelligente
agg_dict = create_smart_aggregation_dict(club_with_dummies)
club_aggregated = club_with_dummies.groupby('caseid', as_index=False).agg(agg_dict)

# Gérer les colonnes avec plusieurs agrégations (date_of_visit)
if ('session_date', 'min') in club_aggregated.columns:
    # Aplatir les colonnes multi-niveau et créer des colonnes séparées
    club_aggregated = club_aggregated.copy()
    club_aggregated['first_session_date'] = club_aggregated[('session_date', 'min')]
    club_aggregated['last_session_date'] = club_aggregated[('session_date', 'max')]
    
    # Supprimer les colonnes multi-niveau
    club_aggregated.drop(columns=[('session_date', 'min'), ('session_date', 'max')], inplace=True)
    
    # Aplatir le reste des colonnes
    club_aggregated.columns = [col[0] if isinstance(col, tuple) else col for col in club_aggregated.columns]

# Renommer pour plus de clarté
club_aggregated = club_aggregated.rename(columns={
    'is_member_present': 'total_sessions'
})

club_aggregated = clean_column_names(club_aggregated, 'member_type_')
club_aggregated = merge_with_depistage(club_aggregated, club_nutrition, ['member_type','caseid'])
print(f"Agrégation terminée: {club_aggregated.shape[0]} patients uniques avec {club_aggregated.shape[1]} colonnes")
club_aggregated.to_excel(os.path.join(output_dir, 'club_nutrition.xlsx'), index=False)
print(f"✅ Fichier sauvegardé: {os.path.join(output_dir, 'club_nutrition.xlsx')}")
print(f"✅ Toutes les {club_aggregated.shape[1]} colonnes ont été conservées avec l'agrégation appropriée")