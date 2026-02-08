"""
Module de chargement des données nutrition
Charge les fichiers Excel depuis outputs/NUTRITION/
"""
import pandas as pd
from pathlib import Path
from datetime import date, timedelta
from typing import Optional, Tuple
import streamlit as st


def get_data_path() -> Path:
    """Retourne le chemin vers le dossier de données."""
    # Remonter d'un niveau depuis streamlit-app/ vers la racine du projet
    base_path = Path(__file__).parent.parent.parent
    return base_path / "outputs" / "NUTRITION"


@st.cache_data(ttl=3600)  # Cache pendant 1 heure
def load_depistage() -> pd.DataFrame:
    """
    Charge le fichier depistage_filtered.xlsx
    
    Returns:
        DataFrame avec les données de dépistage
    """
    data_path = get_data_path() / "depistage_filtered.xlsx"
    
    if not data_path.exists():
        st.error(f"⚠️ Fichier non trouvé: {data_path}")
        return pd.DataFrame()
    
    df = pd.read_excel(data_path)
    
    # Conversion des dates
    date_columns = ['date_de_depistage', 'date_of_birth']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df


@st.cache_data(ttl=3600)
def load_enrolled() -> pd.DataFrame:
    """
    Charge le fichier enroled_final.xlsx
    
    Returns:
        DataFrame avec les données des enfants enrôlés
    """
    data_path = get_data_path() / "enroled_final.xlsx"
    
    if not data_path.exists():
        st.error(f"⚠️ Fichier non trouvé: {data_path}")
        return pd.DataFrame()
    
    df = pd.read_excel(data_path)
    
    # Exclure le cas de test
    if 'nut_code' in df.columns:
        df = df[df['nut_code'] != 'NUT-8D3-D8CC']
    
    # Conversion des dates
    date_columns = ['date_enrollement', 'enrollment_date', 'date_admission', 
                    'approval_date', 'closed_date', 'death_date', 'last_mamba_date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df


@st.cache_data(ttl=3600)
def load_waiting_list() -> pd.DataFrame:
    """Charge les enfants en attente d'enrôlement."""
    data_path = get_data_path() / "waiting_list.xlsx"
    
    if not data_path.exists():
        return pd.DataFrame()
    
    return pd.read_excel(data_path)


@st.cache_data(ttl=3600)
def load_club_data() -> pd.DataFrame:
    """Charge les données de participation aux clubs."""
    data_path = get_data_path() / "club_participation.xlsx"
    
    if not data_path.exists():
        return pd.DataFrame()
    
    return pd.read_excel(data_path)


@st.cache_data(ttl=3600)
def load_suivi() -> pd.DataFrame:
    """Charge les données de suivi nutritionnel."""
    data_path = get_data_path() / "suivi_nutritionel.xlsx"
    
    if not data_path.exists():
        return pd.DataFrame()
    
    return pd.read_excel(data_path)


# ============================================
# FONCTIONS DE FILTRAGE TEMPOREL
# ============================================

def previous_week_bounds(ref: date = None) -> Tuple[date, date]:
    """Retourne (lundi, dimanche) de la semaine précédente."""
    if ref is None:
        ref = date.today()
    current_monday = ref - timedelta(days=ref.weekday())
    prev_monday = current_monday - timedelta(days=7)
    prev_sunday = prev_monday + timedelta(days=6)
    return prev_monday, prev_sunday


def current_week_bounds(ref: date = None) -> Tuple[date, date]:
    """Retourne (lundi, dimanche) de la semaine courante."""
    if ref is None:
        ref = date.today()
    monday = ref - timedelta(days=ref.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def previous_month_bounds(ref: date = None) -> Tuple[date, date]:
    """Retourne (premier_jour, dernier_jour) du mois précédent."""
    if ref is None:
        ref = date.today()
    first_this_month = date(ref.year, ref.month, 1)
    last_prev = first_this_month - timedelta(days=1)
    first_prev = date(last_prev.year, last_prev.month, 1)
    return first_prev, last_prev


def current_month_bounds(ref: date = None) -> Tuple[date, date]:
    """Retourne (premier jour, dernier jour) du mois courant."""
    if ref is None:
        ref = date.today()
    first = date(ref.year, ref.month, 1)
    
    if ref.month == 12:
        first_next = date(ref.year + 1, 1, 1)
    else:
        first_next = date(ref.year, ref.month + 1, 1)
    
    last = first_next - timedelta(days=1)
    return first, last


def last_three_months_bounds(ref: date = None) -> Tuple[date, date]:
    """
    Retourne (premier_jour, dernier_jour) des 3 derniers mois
    COMPLETS avant le mois courant.
    """
    if ref is None:
        ref = date.today()
    
    first_this_month = date(ref.year, ref.month, 1)
    end = first_this_month - timedelta(days=1)
    
    # Helper pour soustraire n mois
    def subtract_months(y, m, n):
        total = y * 12 + (m - 1) - n
        ny = total // 12
        nm = total % 12 + 1
        return ny, nm
    
    y3, m3 = subtract_months(ref.year, ref.month, 3)
    start = date(y3, m3, 1)
    
    return start, end


def filter_by_date(df: pd.DataFrame, date_column: str, 
                   start_date: date, end_date: date) -> pd.DataFrame:
    """
    Filtre un DataFrame par plage de dates.
    
    Args:
        df: DataFrame à filtrer
        date_column: Nom de la colonne de date
        start_date: Date de début (incluse)
        end_date: Date de fin (incluse)
    
    Returns:
        DataFrame filtré
    """
    if df.empty or date_column not in df.columns:
        return df
    
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column], errors='coerce')
    
    mask = (
        (df_copy[date_column] >= pd.Timestamp(start_date)) & 
        (df_copy[date_column] <= pd.Timestamp(end_date))
    )
    
    return df_copy[mask]


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def get_unique_offices(df: pd.DataFrame) -> list:
    """Retourne la liste des bureaux uniques."""
    if 'office' in df.columns:
        return sorted(df['office'].dropna().unique().tolist())
    return []


def get_unique_communes(df: pd.DataFrame) -> list:
    """Retourne la liste des communes uniques."""
    if 'commune' in df.columns:
        return sorted(df['commune'].dropna().unique().tolist())
    return []


def get_malnutrition_types(df: pd.DataFrame) -> list:
    """Retourne les types de malnutrition présents."""
    if 'manutrition_type' in df.columns:
        return df['manutrition_type'].dropna().unique().tolist()
    return []


def get_mas_cases(df: pd.DataFrame) -> pd.DataFrame:
    """Filtre les cas de Malnutrition Aiguë Sévère (MAS)."""
    if 'manutrition_type' in df.columns:
        return df[df['manutrition_type'] == 'MAS']
    return pd.DataFrame()


def get_mam_cases(df: pd.DataFrame) -> pd.DataFrame:
    """Filtre les cas de Malnutrition Aiguë Modérée (MAM)."""
    if 'manutrition_type' in df.columns:
        return df[df['manutrition_type'] == 'MAM']
    return pd.DataFrame()


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Génère un résumé des données pour l'assistant IA.
    
    Returns:
        Dictionnaire avec colonnes, stats descriptives, etc.
    """
    if df.empty:
        return {"error": "DataFrame vide"}
    
    summary = {
        "columns": list(df.columns),
        "shape": df.shape,
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_stats": {}
    }
    
    # Stats pour colonnes numériques
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        summary["numeric_stats"] = df[numeric_cols].describe().to_dict()
    
    # Valeurs uniques pour colonnes catégorielles clés
    categorical_cols = ['office', 'commune', 'manutrition_type', 'eligible', 'gender']
    for col in categorical_cols:
        if col in df.columns:
            summary[f"{col}_values"] = df[col].value_counts().to_dict()
    
    return summary


def refresh_data():
    """Force le rechargement des données en vidant le cache."""
    st.cache_data.clear()
    st.success("✅ Données rafraîchies avec succès!")
