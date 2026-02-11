# === COMPARAISON TEMPORELLE ===
def calculate_trend(current_val, previous_val):
    """Calcule le pourcentage de progression entre deux périodes."""
    if previous_val == 0:
        return 0.0
    return round(((current_val - previous_val) / previous_val) * 100, 2)

def get_comparison_metrics(df, start_date, end_date):
    """Compare les KPIs de la période actuelle sélectionnée vs la période précédente de même durée."""
    import pandas as pd
    # 1. Données de la période actuelle
    mask_curr = (df['date_enrollement'].dt.date >= start_date) & (df['date_enrollement'].dt.date <= end_date)
    df_curr = df[mask_curr]
    # 2. Calcul de la période précédente (même nombre de jours)
    delta = end_date - start_date
    prev_start = start_date - delta - pd.Timedelta(days=1)
    prev_end = start_date - pd.Timedelta(days=1)
    # 3. Données de la période précédente
    mask_prev = (df['date_enrollement'].dt.date >= prev_start) & (df['date_enrollement'].dt.date <= prev_end)
    df_prev = df[mask_prev]
    # 4. Calcul des métriques de comparaison (ex: Dépistages/Enrôlements)
    curr_total = len(df_curr)
    prev_total = len(df_prev)
    return {
        "depistages": curr_total,
        "trend_dep": calculate_trend(curr_total, prev_total),
        "period_label": f"vs {prev_start.strftime('%d/%m')} - {prev_end.strftime('%d/%m')}"
    }
"""
Calculateur de KPIs MEAL pour le programme nutrition
Métriques clés : dépistages, enrôlements, taux d'admission, etc.
"""
import pandas as pd
from datetime import date
from typing import Dict, Any, Optional
from utils.data_loader import (
    load_depistage, load_enrolled, 
    filter_by_date, current_month_bounds, previous_month_bounds,
    current_week_bounds, previous_week_bounds, last_three_months_bounds,
    get_mas_cases, get_mam_cases
)


def calculate_kpis(df_depistage: pd.DataFrame, 
                   df_enrolled: pd.DataFrame,
                   period: str = "current_month") -> Dict[str, Any]:
    """
    Calcule les KPIs MEAL principaux.
    
    Args:
        df_depistage: DataFrame des dépistages
        df_enrolled: DataFrame des enrôlements
        period: Période de calcul ("current_week", "current_month", "previous_month", "last_3_months", "all")
    
    Returns:
        Dictionnaire avec tous les KPIs
    """
    # Déterminer les bornes temporelles
    ref_date = date.today()
    
    if period == "current_week":
        start, end = current_week_bounds(ref_date)
    elif period == "current_month":
        start, end = current_month_bounds(ref_date)
    elif period == "previous_month":
        start, end = previous_month_bounds(ref_date)
    elif period == "previous_week":
        start, end = previous_week_bounds(ref_date)
    elif period == "last_3_months":
        start, end = last_three_months_bounds(ref_date)
    else:  # all
        start = date(2020, 1, 1)
        end = ref_date
    
    # Filtrer par période
    if period != "all":
        df_dep_filtered = filter_by_date(df_depistage, 'date_de_depistage', start, end)
        df_enr_filtered = filter_by_date(df_enrolled, 'date_enrollement', start, end)
    else:
        df_dep_filtered = df_depistage.copy()
        df_enr_filtered = df_enrolled.copy()
    
    # Calculs des KPIs
    kpis = {
        "period": period,
        "period_start": start,
        "period_end": end,
        
        # Dépistages
        "total_depistages": len(df_dep_filtered),
        "depistages_eligibles": len(df_dep_filtered[df_dep_filtered.get('eligible', pd.Series()) == 'yes']) if 'eligible' in df_dep_filtered.columns else 0,
        
        # Enrôlements
        "total_enrolled": len(df_enr_filtered),
        "enrolled_actifs": len(df_enr_filtered[df_enr_filtered.get('actif', pd.Series()) == True]) if 'actif' in df_enr_filtered.columns else len(df_enr_filtered),
        
        # Types de malnutrition
        "cas_mas": len(get_mas_cases(df_dep_filtered)),
        "cas_mam": len(get_mam_cases(df_dep_filtered)),
        "cas_normal": len(df_dep_filtered[df_dep_filtered.get('manutrition_type', pd.Series()) == 'Normal']) if 'manutrition_type' in df_dep_filtered.columns else 0,
        
        # Bureaux
        "nb_bureaux": df_dep_filtered['office'].nunique() if 'office' in df_dep_filtered.columns else 0,
        
        # Communes
        "nb_communes": df_dep_filtered['commune'].nunique() if 'commune' in df_dep_filtered.columns else 0,
    }
    
    # Taux d'admission (enrôlés / éligibles)
    if kpis["depistages_eligibles"] > 0:
        kpis["taux_admission"] = round((kpis["total_enrolled"] / kpis["depistages_eligibles"]) * 100, 1)
    else:
        kpis["taux_admission"] = 0.0
    
    # Proportion MAS
    if kpis["total_depistages"] > 0:
        kpis["proportion_mas"] = round((kpis["cas_mas"] / kpis["total_depistages"]) * 100, 1)
        kpis["proportion_mam"] = round((kpis["cas_mam"] / kpis["total_depistages"]) * 100, 1)
    else:
        kpis["proportion_mas"] = 0.0
        kpis["proportion_mam"] = 0.0
    
    return kpis


def calculate_kpis_by_office(df_depistage: pd.DataFrame,
                              df_enrolled: pd.DataFrame,
                              period: str = "current_month") -> pd.DataFrame:
    """
    Calcule les KPIs par bureau/office.
    
    Returns:
        DataFrame avec KPIs par bureau
    """
    ref_date = date.today()
    
    if period == "current_month":
        start, end = current_month_bounds(ref_date)
    elif period == "previous_month":
        start, end = previous_month_bounds(ref_date)
    else:
        start = date(2020, 1, 1)
        end = ref_date
    
    df_dep = filter_by_date(df_depistage, 'date_de_depistage', start, end) if period != "all" else df_depistage
    df_enr = filter_by_date(df_enrolled, 'date_enrollement', start, end) if period != "all" else df_enrolled
    
    if df_dep.empty or 'office' not in df_dep.columns:
        return pd.DataFrame()
    
    # Agrégation par bureau
    office_stats = df_dep.groupby('office').agg(
        depistages=('caseid', 'count'),
        eligibles=('eligible', lambda x: (x == 'yes').sum() if 'eligible' in df_dep.columns else 0),
        cas_mas=('manutrition_type', lambda x: (x == 'MAS').sum() if 'manutrition_type' in df_dep.columns else 0),
        cas_mam=('manutrition_type', lambda x: (x == 'MAM').sum() if 'manutrition_type' in df_dep.columns else 0),
    ).reset_index()
    
    # Enrôlements par bureau
    if not df_enr.empty and 'office' in df_enr.columns:
        enrolled_by_office = df_enr.groupby('office').size().reset_index(name='enrolled')
        office_stats = office_stats.merge(enrolled_by_office, on='office', how='left')
        office_stats['enrolled'] = office_stats['enrolled'].fillna(0).astype(int)
    else:
        office_stats['enrolled'] = 0
    
    # Calcul des taux
    office_stats['taux_admission'] = office_stats.apply(
        lambda row: round((row['enrolled'] / row['eligibles'] * 100), 1) if row['eligibles'] > 0 else 0,
        axis=1
    )
    
    office_stats['proportion_mas'] = office_stats.apply(
        lambda row: round((row['cas_mas'] / row['depistages'] * 100), 1) if row['depistages'] > 0 else 0,
        axis=1
    )
    
    return office_stats.sort_values('depistages', ascending=False)


def calculate_weekly_trend(df: pd.DataFrame, 
                            date_column: str = 'date_de_depistage',
                            weeks: int = 8) -> pd.DataFrame:
    """
    Calcule la tendance hebdomadaire des dépistages/enrôlements.
    
    Args:
        df: DataFrame source
        date_column: Colonne de date
        weeks: Nombre de semaines à inclure
    
    Returns:
        DataFrame avec comptages par semaine
    """
    if df.empty or date_column not in df.columns:
        return pd.DataFrame()
    
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column], errors='coerce')
    df_copy = df_copy.dropna(subset=[date_column])
    
    # Filtrer les dernières semaines
    end_date = date.today()
    start_date = end_date - pd.Timedelta(weeks=weeks)
    
    df_copy = df_copy[df_copy[date_column] >= pd.Timestamp(start_date)]
    
    # Créer colonne semaine
    df_copy['week'] = df_copy[date_column].dt.isocalendar().week
    df_copy['year'] = df_copy[date_column].dt.year
    df_copy['week_start'] = df_copy[date_column] - pd.to_timedelta(df_copy[date_column].dt.dayofweek, unit='d')
    
    # Agrégation par semaine
    weekly = df_copy.groupby('week_start').agg(
        count=('caseid', 'count') if 'caseid' in df_copy.columns else (df_copy.columns[0], 'count')
    ).reset_index()
    
    weekly = weekly.sort_values('week_start')
    weekly['week_label'] = weekly['week_start'].dt.strftime('%d %b')
    
    return weekly


def calculate_monthly_trend(df: pd.DataFrame,
                             date_column: str = 'date_de_depistage',
                             months: int = 12) -> pd.DataFrame:
    """
    Calcule la tendance mensuelle.
    
    Returns:
        DataFrame avec comptages par mois
    """
    if df.empty or date_column not in df.columns:
        return pd.DataFrame()
    
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column], errors='coerce')
    df_copy = df_copy.dropna(subset=[date_column])
    
    # Créer colonne mois
    df_copy['month'] = df_copy[date_column].dt.to_period('M')
    
    # Agrégation
    monthly = df_copy.groupby('month').agg(
        count=('caseid', 'count') if 'caseid' in df_copy.columns else (df_copy.columns[0], 'count')
    ).reset_index()
    
    monthly['month'] = monthly['month'].astype(str)
    monthly = monthly.tail(months)
    
    return monthly


def calculate_malnutrition_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule la distribution des types de malnutrition.
    
    Returns:
        DataFrame avec comptages par type
    """
    if df.empty or 'manutrition_type' not in df.columns:
        return pd.DataFrame()
    
    distribution = df['manutrition_type'].value_counts().reset_index()
    distribution.columns = ['type', 'count']
    
    total = distribution['count'].sum()
    distribution['percentage'] = round(distribution['count'] / total * 100, 1)
    
    return distribution


def get_mas_alert_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Prépare les données pour les alertes MAS.
    
    Returns:
        Dictionnaire avec info sur les cas MAS détectés
    """
    mas_cases = get_mas_cases(df)
    
    if mas_cases.empty:
        return {
            "has_mas": False,
            "count": 0,
            "cases": [],
            "offices_affected": []
        }
    
    return {
        "has_mas": True,
        "count": len(mas_cases),
        "cases": mas_cases[['caseid', 'fullname', 'office', 'commune', 'date_de_depistage']].to_dict('records') if all(col in mas_cases.columns for col in ['caseid', 'fullname', 'office']) else [],
        "offices_affected": mas_cases['office'].unique().tolist() if 'office' in mas_cases.columns else [],
        "by_office": mas_cases.groupby('office').size().to_dict() if 'office' in mas_cases.columns else {}
    }


def format_kpi_delta(current: float, previous: float) -> tuple:
    """
    Calcule le delta entre deux valeurs pour affichage.
    
    Returns:
        Tuple (delta_value, delta_color)
    """
    if previous == 0:
        return (None, "off")
    
    delta = current - previous
    delta_pct = round((delta / previous) * 100, 1)
    
    return (f"{'+' if delta >= 0 else ''}{delta_pct}%", "normal" if delta >= 0 else "inverse")


def get_period_label(period: str) -> str:
    """Retourne un libellé français pour la période."""
    labels = {
        "current_week": "Semaine courante",
        "previous_week": "Semaine précédente",
        "current_month": "Mois courant",
        "previous_month": "Mois précédent",
        "last_3_months": "3 derniers mois",
        "all": "Toutes les données"
    }
    return labels.get(period, period)
