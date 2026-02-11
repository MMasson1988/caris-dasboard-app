#=======================================================================================
print("\n\n=== RAPPORT ANNUEL PTME ===")
#=======================================================================================
# Standard library imports
import requests
# Standard library imports
import os
import re
import time
import warnings
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse

# Third-party imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import openpyxl
import xlsxwriter
import pymysql
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
# import functions
from utils import execute_sql_query,creer_colonne_match_conditional
# Download charges virales database from "Charges_virales_pediatriques.sql file"
# from caris_fonctions import execute_sql_query
# from ptme_fonction import creer_colonne_match_conditional

# Charger les variables d'environnement
load_dotenv('dot.env')

# Définition des dates pour les sessions détaillées
date_debut = '2025-01-01'
# date_fin==today
date_fin = datetime.now().strftime('%Y-%m-%d')
fin_decembre ='2025-12-31'
#=======================================================================================
print("\n\n=== DEBUT DU PIPELINE ===")
#=======================================================================================
# Génération du rapport annuel de grossesse
print("\n--- Génération du rapport annuel de grossesse ---")
annual_pregnancy = pd.read_excel('../outputs/PTME/pregnancy_report.xlsx')
print(f'Nombre de lignes dans le rapport de grossesse: {len(annual_pregnancy)}')
print(annual_pregnancy.head(2))

# Conversion en datetime des colonnes pertinentes
date_cols = ['pregnancy_added_at', 'ddr', 'dpa', 'delivery_date', 'dob', 'viral_load_date']
annual_pregnancy[date_cols] = annual_pregnancy[date_cols].apply(pd.to_datetime, errors='coerce')

# database appels
appel_visit = pd.read_excel('../outputs/SERVICES/data_cleaned.xlsx')
appel_visit = appel_visit[appel_visit['Trouvé'] == 'Oui']
# Convertir les dates
appel_visit['date'] = pd.to_datetime(appel_visit['date'], errors='coerce')
# choisir les valeurs unqiues de  patient_code en gardant la ou date  est plus recente
appel_visit = appel_visit.sort_values(by='date', ascending=False).drop_duplicates(subset=['patient_code'], keep='first')
pregnancy_report = creer_colonne_match_conditional(
    df1=annual_pregnancy,
    df2=appel_visit[[
        'date', 'Trouvé', 'Type', 
        'mois', 'username', 'patient_code']],
    on="patient_code",
    nouvelle_colonne="service_type",
    mapping={'both': 'yes', 'left_only': 'no', 'right_only': 'no'}
)
# creer une ne variable service_after_pregnancy qui verifie si la date d'appel est superieur a la date de ddr. si oui c'yes no sinon
pregnancy_report['service_during_pregnancy'] = np.where(
    (pregnancy_report['service_type'] == 'yes') & 
    (pregnancy_report['date'] >= pregnancy_report['ddr']),
    'yes', 'no'
)

# database club session
club_attendance = pd.read_excel('../outputs/PTME/club_sessions_detailed.xlsx')
# filter only club mere
club_attendance = club_attendance[club_attendance['club_type'] == 'Club Mere']
# fill n/A in raison_absence by 11-autre
club_attendance['raison_absence'] = club_attendance['raison_absence'].fillna('11-autre')
# remplace le vide par 11-autre
club_attendance['raison_absence'] = club_attendance['raison_absence'].replace('', '11-autre')
# remplace les valeur 1 par Present et 0 par absent
club_attendance['raison_absence'] = club_attendance['raison_absence'].replace('0', '11-autre')
# replace 1
club_attendance['session_date_presence'] = pd.to_datetime(club_attendance['session_date_presence'])

club_presence = club_attendance[club_attendance['raison_absence'] == '1- Present']
# Convertir les dates

# choisir les valeurs unqiues de  patient_code en gardant la ou date  est plus recente
club_presence = club_presence.sort_values(by='session_date_presence', ascending=False).drop_duplicates(subset=['patient_code'], keep='first')
club_presence.to_excel('outputs/YEARLY/pregnant_club_attendance.xlsx', index=False)
pregnancy_report = creer_colonne_match_conditional(
    df1=pregnancy_report,
    df2=club_presence[[
        'last_attendance_date', 'first_attendance_date', 'club_name', 'club_type', 'session_date_presence', 'present', 'raison_absence', 'patient_code']],
    on="patient_code",
    nouvelle_colonne="mother_in_club",
    mapping={'both': 'yes', 'left_only': 'no', 'right_only': 'no'}
).copy()

# creer une ne variable service_after_pregnancy qui verifie si la date d'appel est superieur a la date de ddr. si oui c'yes no sinon
pregnancy_report['club_during_pregnancy'] = np.where(
    (pregnancy_report['mother_in_club'] == 'yes') & 
    (pregnancy_report['last_attendance_date'] >= pregnancy_report['ddr']),
    'yes', 'no'
)

# remplir raison_absence N/A par not_in_club
pregnancy_report['raison_absence'] = pregnancy_report['raison_absence'].fillna('not_in_club')
pregnancy_report['Trouvé'] = pregnancy_report['Trouvé'].fillna('not_found')
pregnancy_report['Type'] = pregnancy_report['Type'].fillna('no_service')
# filtrer les femmes qui ont eu un service apres la grossesse
pregnancy_report.to_excel('outputs/YEARLY/pregnant_served_in_club.xlsx', index=False)

# filtrer les lignes ou office n'est pas egale à (CAY & PDP) and is_abandoned ! 1 and is_dead ! 1
filtered_report = pregnancy_report[(pregnancy_report['office'] != 'CAY') & 
                                   (pregnancy_report['office'] != 'PDP') & 
                                   (pregnancy_report['is_abandoned'] != 1) & 
                                   (pregnancy_report['is_dead'] != 1)]

# filtrez dpa entre date_debut et date_fin & (dpa null & dpa =='0000-00-00' si pregnancy_added_at est entre date_debut et date_fin)
filtered_report = filtered_report[
    ((filtered_report['dpa'] >= date_debut)) |
    (((filtered_report['dpa'].isnull()) | (filtered_report['dpa'] == '0000-00-00')) & 
     (filtered_report['pregnancy_added_at'] >= date_debut) & 
     (filtered_report['pregnancy_added_at'] <= date_fin))
]
# pour tout date ddr >= 2025-01-01, remplacer sa correspondance dans pregnancy_added_at par ddr- 1 mois et remplacer son equivalent no dans pregnancy_added_in_the_interval yes
filtered_report.loc[filtered_report['ddr'] >= pd.to_datetime(date_debut), 'pregnancy_added_at'] = \
    filtered_report['ddr'] - pd.DateOffset(months=1)
filtered_report.loc[filtered_report['pregnancy_added_at'] >= pd.to_datetime(date_debut), 'pregnancy_added_in_the_interval'] = 'yes'
filtered_report.loc[filtered_report['pregnancy_added_at'] < pd.to_datetime(date_debut), 'pregnancy_added_in_the_interval'] = 'no'

# filtrez en retirant les lignes ou delivery_date est < date_debut - 2 ans & non null
two_years_before_debut = pd.to_datetime(date_debut) - relativedelta(years=2)
filtered_ptme = filtered_report[(filtered_report['delivery_date'] >= two_years_before_debut) | (filtered_report['delivery_date'].isnull()) & (filtered_report['delivery_date'] == '0000-00-00')]
# filtrez les lignes dans filtered_report qui ne sont pas dans filtered_ptme et non null delivery_date
filtered_prob_delivery_date = filtered_report[
    (~filtered_report['patient_code'].isin(filtered_ptme['patient_code'])) & 
    (filtered_report['delivery_date'].notnull())
]

# filtrez les lignes dans filtered_report qui ne sont pas dans filtered_prob_delivery_date
filtered_pregnancy = filtered_report[
    (~filtered_report['patient_code'].isin(filtered_prob_delivery_date['patient_code'])) 
]

# filretirez les lignes ou delivery_date est <= date_debut - 3 mois avec dpa et ddr null
three_months_before_debut = pd.to_datetime(date_debut) - relativedelta(months=3)
filtered_pregnancy = filtered_pregnancy[(filtered_pregnancy['delivery_date'] > three_months_before_debut) |
                                      (filtered_pregnancy['dpa'].notnull()) |
                                      (filtered_pregnancy['ddr'].notnull())] 
# save filtered_prob_delivery_date to excel file
filtered_prob_delivery_date.to_excel('../outputs/YEARLY/filtered_delivery_with_two_years_after_debut.xlsx', index=False)

#=======================================================================================
# save filtered_report to excel file
filtered_report.to_excel('../outputs/YEARLY/annual_pregnancy_report_filtered.xlsx', index=False)
#filtered_ptme.to_excel('../outputs/YEARLY/annual_ptme_filtered.xlsx', index=False)
filtered_pregnancy.to_excel('../outputs/YEARLY/annual_pregnancy_filtered.xlsx', index=False)
print("Rapport annuel de grossesse généré et sauvegardé avec succès.")
#=======================================================================================
print("\n\n=== FEMMES ENCEINTES ===")
#=======================================================================================
# filtrer les lignes ou delivery_date est null
pregnant_women = filtered_pregnancy[(filtered_pregnancy['delivery_date'].isnull()) & (filtered_pregnancy['termination_of_pregnancy']!=1)]
print(f'Nombre de femmes enceintes: {len(pregnant_women)}')
pregnant_women.to_excel('../outputs/YEARLY/annual_femmes_enceintes.xlsx', index=False)

#=======================================================================================
print("\n\n=== FEMMES ALLAINTANTES ===")
#=======================================================================================
# filtrer les lignes ou delivery_date est NON null
femmes_allaitantes = filtered_pregnancy[(filtered_pregnancy['delivery_date'].notnull()) & (filtered_pregnancy['termination_of_pregnancy']!=1)]

print(f'Nombre de femmes allaitantes: {len(femmes_allaitantes)}')
femmes_allaitantes.to_excel('../outputs/YEARLY/annual_femmes_allaitantes.xlsx', index=False)
#=======================================================================================
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import re
#=======================================================================================
def get_last_backup_date_ymd(name, folder="../outputs/YEARLY"):
    path = Path(folder)
    if not path.exists():
        return None

    pattern = re.compile(rf"{name}_(\d{{4}}-\d{{2}}-\d{{2}})\.parquet")
    dates = []

    for f in path.glob(f"{name}_*.parquet"):
        match = pattern.match(f.name)
        if match:
            dates.append(
                datetime.strptime(match.group(1), "%Y-%m-%d")
            )

    return max(dates) if dates else None


def save_df_to_backup(df, name, folder="../outputs/YEARLY", max_days=7):
    today = datetime.today().date()
    last_date = get_last_backup_date_ymd(name, folder)

    # Cas 1 : aucune sauvegarde existante
    if last_date is None:
        authorized = True
    else:
        delta_days = (today - last_date.date()).days
        authorized = delta_days > max_days

    if not authorized:
        print("Sauvegarde refusée : dernière version ≤ 7 jours")
        return None

    # Sauvegarde autorisée
    Path(folder).mkdir(exist_ok=True)
    filename = f"{name}_{today.strftime('%Y-%m-%d')}.parquet"
    file_path = Path(folder) / filename

    if file_path.exists():
        print(f"Le fichier {filename} existe déjà, sauvegarde annulée.")
        return None

    df.to_parquet(file_path)
    print(f"Sauvegarde effectuée : {filename}")
    return filename

save_df_to_backup(pregnant_women, "ptme_indicateurs_femmes_enceintes")

def load_latest_df_ymd(name, folder="backup"):
    path = Path(folder)
    if not path.exists():
        raise FileNotFoundError("Dossier de backup inexistant")

    pattern = re.compile(rf"{name}_(\d{{4}}-\d{{2}}-\d{{2}})\.parquet")
    latest_file = None
    latest_date = None

    for f in path.glob(f"{name}_*.parquet"):
        match = pattern.match(f.name)
        if match:
            file_date = datetime.strptime(match.group(1), "%Y-%m-%d").date()
            if latest_date is None or file_date > latest_date:
                latest_date = file_date
                latest_file = f

    if latest_file is None:
        raise FileNotFoundError("Aucune version valide trouvée")

    return pd.read_parquet(latest_file)


df_latest = load_latest_df_ymd("ptme_indicateurs_femmes_enceintes", "../outputs/YEARLY")
print(f"Nombre de lignes dans la dernière version chargée: {len(df_latest)}")
#=======================================================================================
print("\n\n=== FIN DU PIPELINE ===")
#=======================================================================================

# Génération du rapport annuel des participations en club de grossesse
print("\n--- Génération du rapport annuel des participations en club de grossesse ---")
club_report = pd.read_excel('../outputs/PTME/club_sessions_detailed.xlsx')
print(f'Nombre de lignes dans le rapport des clubs: {len(club_report)}')
print(club_report.head(2))
# grouper par patient_code et compter le nombre de sessions par patient_code
club_participation = club_report.groupby('patient_code').size().reset_index(name='num_sessions')
# save club_participation to excel file
club_participation.to_excel('../outputs/YEARLY/annual_club_participation.xlsx', index=False)
print("Rapport annuel des participations en club de grossesse généré et sauvegardé avec succès.")
#=======================================================================================
# utilise club_attendance pour calculer le nombre patients presents et absents par patient_code
club_attendance['presence'] = np.where(club_attendance['raison_absence'] == '1- Present', 'present', 'absent')
club_attendance = club_attendance[club_attendance['club_type']=='Club Mere']
attendance_summary = club_attendance.groupby(['patient_code', 'presence']).size().unstack(fill_value=0).reset_index()
#attendance_summary.columns.name = None
# save attendance_summary to excel file
attendance_summary.to_excel('../outputs/YEARLY/annual_club_attendance_summary.xlsx', index=False)

if __name__ == '__main__':
    print("Module annual_reports.py chargé. Ajoutez une fonction main() pour exécuter le pipeline.")