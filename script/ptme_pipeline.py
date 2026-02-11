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
#from caris_fonctions import execute_sql_query
#from ptme_fonction import creer_colonne_match_conditional

# Charger les variables d'environnement
load_dotenv(os.path.join('variables', 'dot.env'))

# Définition des dates pour les sessions détaillées
date_debut = '2025-01-01'
# date_fin==today
date_fin = datetime.now().strftime('%Y-%m-%d')

# Créer le répertoire de sortie s'il n'existe pas
os.makedirs('outputs/PTME', exist_ok=True)

#===============================================================================
print("\n\n=== DATABASE DES FEMMES ENCEINTES ===")
#===============================================================================
def fetch_sql_from_gist(url, token=None):
    headers = {"Authorization": f"token {token}"} if token else {}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.text

def run_query_from_gist(url, db_uri, token=None):
    sql = fetch_sql_from_gist(url, token)
    engine = create_engine(db_uri)
    df = pd.read_sql(sql, engine)
    return df

gist_sql_url = "https://gist.githubusercontent.com/MMasson1988/cd22e60e69527b34ded0dd2631cd5975/raw"
token = None  # Pas besoin de token pour un gist public

# Construction de l'URI de base de données à partir du fichier .env
mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_host = os.getenv('MYSQL_HOST')
mysql_db = os.getenv('MYSQL_DB')

db_uri = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"

print(f"Connexion à la base : {mysql_user}@{mysql_host}/{mysql_db}")

# Exécuter la requête
try:
    df = run_query_from_gist(gist_sql_url, db_uri, token)
    print(f"Requête exécutée avec succès!")
    print(f"Nombre de lignes récupérées : {len(df)}")
    print("\nPremières lignes :")
    print(df.head())
    
    # Sauvegarder les résultats
    output_file = "outputs/PTME/pregnancy_tracking.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\nRésultats sauvegardés dans {output_file}")
    
except Exception as e:
    print(f"Erreur lors de l'exécution : {e}")
    

#===============================================================================
print("\n\n=== DATABASE DES SESSIONS DES CLUBS ===")
#===============================================================================
def get_club_sessions_data(start_date, end_date, db_config, sql_script=None):
    """
    Récupère les données détaillées des sessions de club avec informations de présence et raisons d'absence.
    
    Parameters:
        start_date (str): Date de début au format 'YYYY-MM-DD'
        end_date (str): Date de fin au format 'YYYY-MM-DD'  
        db_config (dict): Configuration de la base de données
        sql_script (str, optional): Script SQL personnalisé. Si fourni, remplace le script par défaut.
    
    Returns:
        pandas.DataFrame: DataFrame contenant les données détaillées des sessions de club
    """
    
    # Sécuriser les dates pour l'insertion SQL
    start_date_sql = f"'{start_date}'"
    end_date_sql = f"'{end_date}'"
    
    # Script SQL par défaut pour les sessions de club détaillées
    default_sql = """
    SELECT
        IF(p.linked_to_id_patient > 0, p.linked_to_id_patient, p.id) AS id_patient,
        lh.name AS hopital,
        lh.office AS office,
        CONCAT(lh.city_code, '/', lh.hospital_code) AS site_code,
        c.name AS club_name,
        lct.name AS club_type,
        p.patient_code,
        cs.date AS session_date_presence,
        lctc.name_fr AS topic,
        a.date AS first_attendance_date,
        b.date AS last_attendance_date,
        aa.date AS first_attendance_date_by_club,
        COALESCE(ti.first_name, tm.first_name) AS first_name,
        COALESCE(ti.last_name, tm.last_name) AS last_name,
        COALESCE(ti.dob, tm.dob) AS dob,
        COALESCE(ti.is_abandoned, tm.is_abandoned) AS is_abandoned,
        COALESCE(ti.is_dead, tm.is_dead) AS is_dead,
        IF(tm.is_graduate=1, 'Yes', 'Non') AS graduation,
        tm.graduation_date,
        CASE ti.gender
            WHEN 1 THEN 'male'
            WHEN 2 THEN 'female'
            WHEN 3 THEN 'unknown'
            ELSE ti.gender END AS sex,
        ss.clore,
        ss.nbre_deparasitaires,
        ss.nbre_preservatifs,
        ss.nbre_vit_a,
        ss.nbre_moustiquaires,
        ss.code,
        ss.is_patient_tb,
        ss.is_patient_on_pf,
        ss.adh,
        ss.is_present AS present,
        lca.name AS raison_absence
    FROM session ss
    LEFT JOIN club_session cs ON cs.id = ss.id_club_session
    LEFT JOIN club c ON c.id = cs.id_club
    LEFT JOIN lookup_club_type lct ON lct.id = c.club_type
    LEFT JOIN lookup_club_topic lctc ON lctc.id = cs.topic
    LEFT JOIN patient p ON p.id = ss.id_patient
    LEFT JOIN tracking_motherbasicinfo tm ON tm.id_patient = IF(p.linked_to_id_patient > 0, p.linked_to_id_patient, ss.id_patient)
    LEFT JOIN tracking_infant ti ON ti.id_patient = IF(p.linked_to_id_patient > 0, p.linked_to_id_patient, ss.id_patient)
    LEFT JOIN lookup_hospital lh ON lh.id = c.id_hospital
    LEFT JOIN (
        SELECT MIN(cs1.date) AS date, s1.id_patient, main_id
        FROM session s1
        LEFT JOIN club_session cs1 ON cs1.id = s1.id_club_session
        LEFT JOIN (SELECT p12.*, IF(p12.linked_to_id_patient > 0, p12.linked_to_id_patient, p12.id) AS main_id FROM patient p12) pp ON pp.id = s1.id_patient
        WHERE s1.is_present IS NOT NULL
        GROUP BY pp.main_id
    ) a ON a.main_id = IF(p.linked_to_id_patient > 0, p.linked_to_id_patient, p.id)
    LEFT JOIN (
        SELECT MAX(cs2.date) AS date, s2.id_patient
        FROM session s2
        LEFT JOIN club_session cs2 ON cs2.id = s2.id_club_session
        WHERE s2.is_present IS NOT NULL
        GROUP BY s2.id_patient
    ) b ON b.id_patient = ss.id_patient
    LEFT JOIN (
        SELECT MIN(cs3.date) AS date, s3.id_patient, cs3.id_club
        FROM session s3
        LEFT JOIN club_session cs3 ON cs3.id = s3.id_club_session
        WHERE s3.is_present IS NOT NULL
        GROUP BY cs3.id_club, s3.id_patient
    ) aa ON aa.id_patient = ss.id_patient AND c.id = aa.id_club
    LEFT JOIN lookup_club_attendance lca ON lca.id = ss.is_present
    WHERE
        ss.is_present IS NOT NULL AND
        p.id IS NOT NULL AND
        cs.date BETWEEN {start_date} AND {end_date}
    ORDER BY CONCAT(lh.city_code, '/', lh.hospital_code) , c.name , p.patient_code , cs.date
    LIMIT 100000000
    """
    
    # Utiliser le script fourni ou le script par défaut
    sql_query = sql_script.format(start_date=start_date_sql, end_date=end_date_sql) if sql_script else default_sql.format(start_date=start_date_sql, end_date=end_date_sql)
    
    try:
        # Établir la connexion à la base de données avec SQLAlchemy
        from sqlalchemy import create_engine
        
        # Créer la chaîne de connexion SQLAlchemy
        connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        engine = create_engine(connection_string)
        
        # Exécuter la requête
        df_result = pd.read_sql_query(sql_query, engine)
        
        # Fermer la connexion
        engine.dispose()
        
        return df_result

    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {e}")
        return pd.DataFrame()
    
    # Configuration de la base de données (À remplir avec vos informations réelles)
db_config_example = {
    'user': 'caris_readonly',
    'password': 'longlivecaris!!',
    'host': 'caris.cwyvkxmtzny2.us-east-1.rds.amazonaws.com',
    'database': 'caris_db'
}
# Définition des dates pour les sessions détaillées
date_debut = '2025-01-01'
# date_fin==today
date_fin = datetime.now().strftime('%Y-%m-%d')
# For consistent testing, we can set a fixed end date
#date_fin = '2025-12-06'

# Exécution et récupération du DataFrame des sessions détaillées
print("\n--- Test avec données de sessions de club détaillées ---")
df_detailed_sessions = get_club_sessions_data(start_date='2025-01-01', end_date=date_fin, db_config=db_config_example)

if not df_detailed_sessions.empty:
    print(f"\nDataFrame des sessions détaillées récupéré avec {len(df_detailed_sessions)} lignes et {len(df_detailed_sessions.columns)} colonnes.")
    print("Colonnes disponibles:", list(df_detailed_sessions.columns))
    print(df_detailed_sessions.head())
    df_detailed_sessions.to_excel('./outputs/PTME/club_sessions_detailed.xlsx', index=False)
else:
    print("Aucune donnée de session détaillée trouvée pour la période spécifiée.")

#===============================================================================
print("\n\n=== PCR DATABASE ANALYSIS ===")
#===============================================================================
def get_pcr_analysis(start_date, end_date, db_config, sql_script=None):
    """
    Récupère les données d'analyse des spécimens PCR avec âge et résultats détaillés.
    
    Parameters:
        start_date (str): Date de début au format 'YYYY-MM-DD'
        end_date (str): Date de fin au format 'YYYY-MM-DD'  
        db_config (dict): Configuration de la base de données
        sql_script (str, optional): Script SQL personnalisé. Si fourni, remplace le script par défaut.
    
    Returns:
        pandas.DataFrame: DataFrame contenant les données d'analyse des spécimens PCR
    """
    
    # Sécuriser les dates pour l'insertion SQL
    start_date_sql = f"'{start_date}'"
    end_date_sql = f"'{end_date}'"
    
    # Script SQL par défaut pour l'analyse des spécimens PCR
    default_sql = """
    WITH base AS (
      SELECT
        id_patient,
        date_blood_taken,
        date_of_birth,
        pcr_result,
        pcr_result_date,
        which_pcr,
        date_caris_received_sample,
        -- Âge en mois au moment du prélèvement
        TIMESTAMPDIFF(MONTH, date_of_birth, date_blood_taken) AS age_month
      FROM testing_specimen
      WHERE
        date_blood_taken BETWEEN {start_date} AND {end_date}
        AND which_pcr = 1
    )
    SELECT
    p.patient_code,
      b.id_patient,
      b.date_blood_taken,
      b.date_of_birth,
      b.pcr_result,                     -- valeur brute existante
      b.pcr_result_date,
      b.which_pcr,
      b.date_caris_received_sample,

      /* 1) résultat dans l'intervalle calendrier */
      CASE
        WHEN b.pcr_result_date BETWEEN {start_date} AND {end_date} THEN 'yes'
        ELSE 'no'
      END AS result_in_the_interval,

      /* 2) indicateur "a un résultat non nul et non 0" */
      CASE
        WHEN b.pcr_result IS NOT NULL AND b.pcr_result <> 0 THEN 'with_result'
        ELSE 'no_result'
      END AS nb_avec_resultat,

      /* 3) âge en mois + classe d'âge */
      b.age_month,
      CASE
        WHEN b.date_of_birth IS NULL OR b.date_blood_taken IS NULL THEN NULL
        WHEN b.age_month BETWEEN 0 AND 2 THEN '0_2 mois'
        WHEN b.age_month > 2 AND b.age_month <= 12 THEN '2_12 mois'
        WHEN b.age_month > 12 THEN '+12 mois'
        ELSE NULL
      END AS age_range,

      /* 4) binaire du résultat PCR (1 si positif, 0 sinon) */
      CASE
        WHEN b.pcr_result = 1 THEN 'positif'
        ELSE 'no_positif'
      END AS nb_positif

    FROM base AS b
    LEFT JOIN patient AS p
      ON p.id = b.id_patient
    """
    
    # Utiliser le script fourni ou le script par défaut
    sql_query = sql_script.format(start_date=start_date_sql, end_date=end_date_sql) if sql_script else default_sql.format(start_date=start_date_sql, end_date=end_date_sql)
    
    try:
        # Établir la connexion à la base de données avec SQLAlchemy
        from sqlalchemy import create_engine
        
        # Créer la chaîne de connexion SQLAlchemy
        connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        engine = create_engine(connection_string)
        
        # Exécuter la requête
        df_result = pd.read_sql_query(sql_query, engine)
        
        # Fermer la connexion
        engine.dispose()
        
        return df_result

    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {e}")
        return pd.DataFrame()
# exemple d'application
#date_debut_pcr = '2025-01-01'
#date_fin_pcr = datetime.now().strftime('%Y-%m-%d')
# Pour des tests cohérents, on peut fixer une date de fin
#date_fin_pcr = '2025-12-06'
# Exécution et récupération du DataFrame des spécimens PCR
print("\n--- Test avec données d'analyse des spécimens PCR ---")
df_pcr_specimens = get_pcr_analysis(date_debut, date_fin, db_config_example)

if not df_pcr_specimens.empty:
    print(f"\nDataFrame des spécimens PCR récupéré avec {len(df_pcr_specimens)} lignes et {len(df_pcr_specimens.columns)} colonnes.")
    print("Colonnes disponibles:", list(df_pcr_specimens.columns))
    print(df_pcr_specimens.head())
    df_pcr_specimens.to_excel('./outputs/PTME/pcr_analysis.xlsx', index=False)
else:
    print("Aucune donnée d'analyse PCR trouvée pour la période spécifiée.")
#=======================================================================================
print("\n\n=== MOTHER LINKED TO CHILD DATABASE ANALYSIS ===")
#=======================================================================================
def get_mother_child_linked_pcr(start_date, end_date, db_config, sql_script=None):
    """
    Récupère les données des tests PCR avec liaison mère-enfant détaillée.
    
    Parameters:
        start_date (str): Date de début au format 'YYYY-MM-DD'
        end_date (str): Date de fin au format 'YYYY-MM-DD'  
        db_config (dict): Configuration de la base de données
        sql_script (str, optional): Script SQL personnalisé. Si fourni, remplace le script par défaut.
    
    Returns:
        pandas.DataFrame: DataFrame contenant les données des tests PCR avec liaison mère-enfant
    """
    
    # Sécuriser les dates pour l'insertion SQL
    start_date_sql = f"'{start_date}'"
    end_date_sql = f"'{end_date}'"
    
    # Script SQL par défaut pour les tests PCR avec liaison mère-enfant
    default_sql = """
    WITH ranked AS (
      SELECT 
          ts.*,
          ROW_NUMBER() OVER (
              PARTITION BY ts.id_patient
              ORDER BY ts.date_blood_taken DESC, ts.id DESC
          ) AS rn
      FROM testing_specimen ts
      WHERE ts.date_blood_taken > {start_date}
    )

    SELECT 
        mp.patient_code AS mother_patient_code,
        p.patient_code AS child_patient_code,
        MIN(ts.date_blood_taken) AS first_blood_taken_date,
        tp.actual_delivery_date,
        ts.date_of_birth AS specimen_dob,
        ts.id_patient,
        tc.id_patient_mother,
        ts.created_at AS specimen_added_at,
        ts.pcr_result,
        lts.name AS pcr_result_name,
        ts.which_pcr,
        ts.pcr_result_date,
        ts.pcr_result_date_added,
        sau.email
    FROM 
        ranked ts
    LEFT JOIN tracking_children tc 
        ON tc.id_patient_child = ts.id_patient
    LEFT JOIN patient mp 
        ON mp.id = tc.id_patient_mother
    LEFT JOIN patient p 
        ON p.id = tc.id_patient_child
    LEFT JOIN tracking_pregnancy tp 
        ON tp.id_patient_mother = tc.id_patient_mother
    LEFT JOIN auth_users sau 
        ON sau.id = ts.created_by
    LEFT JOIN lookup_testing_specimen_result lts 
        ON lts.id = ts.pcr_result
    WHERE 
        ts.rn = 1
        AND ts.date_blood_taken > {start_date}
        AND tc.id_patient_mother IS NOT NULL
        AND tp.actual_delivery_date IS NOT NULL
        AND tp.actual_delivery_date != '0000-00-00'
        AND tp.actual_delivery_date > {start_date}
        AND tp.actual_delivery_date < {end_date}
    GROUP BY 
        ts.id_patient,
        mp.patient_code,
        p.patient_code,
        tp.actual_delivery_date,
        ts.date_of_birth,
        ts.id_patient,
        tc.id_patient_mother,
        ts.created_at,
        ts.pcr_result,
        lts.name,
        ts.which_pcr,
        ts.pcr_result_date,
        ts.pcr_result_date_added,
        sau.email
    """
    
    # Utiliser le script fourni ou le script par défaut
    sql_query = sql_script.format(start_date=start_date_sql, end_date=end_date_sql) if sql_script else default_sql.format(start_date=start_date_sql, end_date=end_date_sql)
    
    try:
        # Établir la connexion à la base de données avec SQLAlchemy
        from sqlalchemy import create_engine
        
        # Créer la chaîne de connexion SQLAlchemy
        connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        engine = create_engine(connection_string)
        
        # Exécuter la requête
        df_result = pd.read_sql_query(sql_query, engine)
        
        # Fermer la connexion
        engine.dispose()
        
        return df_result

    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {e}")
        return pd.DataFrame()

# Exécution et récupération du DataFrame des PCR mère-enfant
print("\n--- Test avec données PCR mère-enfant liées ---")
df_mother_child_pcr = get_mother_child_linked_pcr(date_debut, date_fin, db_config_example)

if not df_mother_child_pcr.empty:
    print(f"\nDataFrame des PCR mère-enfant récupéré avec {len(df_mother_child_pcr)} lignes et {len(df_mother_child_pcr.columns)} colonnes.")
    print("Colonnes disponibles:", list(df_mother_child_pcr.columns))
    print(df_mother_child_pcr.head())
    df_mother_child_pcr.to_excel('./outputs/PTME/mother_child_linked_pcr.xlsx', index=False)
else:
    print("Aucune donnée PCR mère-enfant trouvée pour la période spécifiée.")

#=======================================================================================
print("\n\n=== PTME REPORT DATABASE ===")
#=======================================================================================
def load_database_config(env_file='dot.env'):
    """
    Charge la configuration de la base de données depuis le fichier .env.
    
    Returns:
        dict: Configuration de la base de données
    """
    # Charger les variables d'environnement
    load_dotenv(env_file)
    
    return {
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'host': os.getenv('MYSQL_HOST'),
        'database': os.getenv('MYSQL_DB')
    }

def get_pregnancy_tracking_data(start_date, end_date, db_config):
    """
    Récupère les données de suivi de grossesse avec sessions de club et charges virales.
    
    Parameters:
        start_date (str): Date de début au format 'YYYY-MM-DD'
        end_date (str): Date de fin au format 'YYYY-MM-DD'  
        db_config (dict): Configuration de la base de données
    
    Returns:
        pandas.DataFrame: DataFrame contenant les données de suivi de grossesse
    """
    
    # Script SQL pour les données de suivi de grossesse
    sql_query = f"""
    SELECT 
        lhs.office,
        lhs.name as hospital,
        p.patient_code,
        tmi.first_name,
        tmi.last_name,
        tmi.is_abandoned,
        tmi.is_dead,
        tmi.dob,
        tp.dpa,
        tp.ddr,
        tp.actual_delivery_date AS delivery_date,
        tp.termination_of_pregnancy,
        MIN(c.date) AS first_date_in_club_session_during_pregnancy,
        MAX(c.date) AS last_date_in_club_session_during_pregnancy,
        IF(MIN(c.date) IS NOT NULL, 'yes', 'no') AS has_session_during_pregnancy,
        IF(v.id_patient IS NOT NULL,
            'yes',
            'no') AS has_viral_load_for_interval,
        IF((viral_load_date + INTERVAL 12 MONTH) > '{end_date}',
            'yes',
            'no') AS has_valide_viral_load,
        IF(((tp.dpa >= '{start_date}')
                OR ((tp.ddr + INTERVAL 9 MONTH + INTERVAL 7 DAY) >= '{start_date}'))
                AND ((tp.ddr <= '{end_date}')
                OR ((tp.dpa - INTERVAL 9 MONTH - INTERVAL 7 DAY) <= '{end_date}')),
            'yes',
            'no') AS is_pregnant_in_the_interval,
        IF(tp.actual_delivery_date BETWEEN '{start_date}' AND '{end_date}',
            'yes',
            'no') AS has_delivery_in_the_interval,
        IF((tp.dpa BETWEEN '{start_date}' AND '{end_date}'
                OR (tp.ddr + INTERVAL 9 MONTH + INTERVAL 7 DAY) BETWEEN '{start_date}' AND '{end_date}'),
            'yes',
            'no') AS expected_delivery_in_period,
        ll.name AS planned_place_of_birth_name,
        lh.name AS planned_place_of_birth_hospital_name,
        IF(tp.planned_place_of_birth_hospital_know = 1,
            'yes',
            IF(tp.planned_place_of_birth_hospital_know,
                'no',
                tp.planned_place_of_birth_hospital_know)) AS planned_place_of_birth_hospital_know_name,
        tp.created_at AS pregnancy_added_at,
        IF(tp.created_at BETWEEN '{start_date}' AND '{end_date}',
            'yes',
            'no') AS pregnancy_added_in_the_interval,
        b.viral_load_date,
        b.viral_load_count,
        IF(v.id_patient IS NOT NULL,
            'yes',
            'no') AS has_viral_load_in_the_interval,
        IF((b.viral_load_date + INTERVAL 12 MONTH) > '{start_date}',
            'yes',
            'no') AS valide_viral_load_for_interval,
        IF(tp.infant_has_no_pcr_test = 1,
            'yes',
            IF(tp.infant_has_no_pcr_test = 2,
                'no',
                tp.infant_has_no_pcr_test)) AS has_pcr_test,
                
                timestampdiff(DAY,tp.actual_delivery_date,NOW()) as actual_delivery_nb_day
    FROM
        tracking_pregnancy tp
            LEFT JOIN
        lookup_testing_birth_location ll ON ll.id = tp.planned_place_of_birth
            LEFT JOIN
        lookup_hospital lh ON lh.id = tp.planned_place_of_birth_hospital
            LEFT JOIN
        tracking_motherbasicinfo tmi ON tmi.id_patient = tp.id_patient_mother
            LEFT JOIN
        patient p ON p.id = tp.id_patient_mother
        LEFT JOIN lookup_hospital lhs on lhs.city_code=p.city_code and lhs.hospital_code=p.hospital_code
            LEFT JOIN
        (SELECT 
            s.id_patient, cs.date
        FROM
            session s
        JOIN club_session cs ON cs.id = s.id_club_session
        WHERE
            s.is_present = 1) c ON c.id_patient = tp.id_patient_mother
            AND ((c.date BETWEEN tp.ddr AND (tp.ddr + INTERVAL 9 MONTH + INTERVAL 7 DAY))
            OR (c.date BETWEEN (tp.dpa - INTERVAL 9 MONTH - INTERVAL 7 DAY) AND tp.dpa))
            LEFT JOIN
        (SELECT 
            tmf.id_patient, tmf.viral_load_date, tmf.viral_load_count
        FROM
            tracking_motherfollowup tmf
        INNER JOIN (SELECT 
            id_patient, MAX(viral_load_date) AS max_viral_load_date
        FROM
            tracking_motherfollowup
        GROUP BY id_patient) latest ON tmf.id_patient = latest.id_patient
            AND tmf.viral_load_date = latest.max_viral_load_date
        GROUP BY tmf.id_patient) b ON b.id_patient = tp.id_patient_mother
            LEFT JOIN
        (SELECT 
            tmf.id_patient
        FROM
            tracking_motherfollowup tmf
        WHERE
            viral_load_date BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY tmf.id_patient) v ON v.id_patient = tp.id_patient_mother
    WHERE
        (((tp.dpa >= '{start_date}')
            OR ((tp.ddr + INTERVAL 9 MONTH + INTERVAL 7 DAY) >= '{start_date}'))
            AND ((tp.ddr <= '{end_date}')
            OR ((tp.dpa - INTERVAL 9 MONTH - INTERVAL 7 DAY) <= '{end_date}')))
            OR tp.actual_delivery_date BETWEEN '{start_date}' AND '{end_date}'
            OR tp.created_at BETWEEN '{start_date}' AND '{end_date}'
    GROUP BY id_patient_mother
    """
    
    try:
        # Établir la connexion à la base de données avec SQLAlchemy
        connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        engine = create_engine(connection_string)
        
        # Exécuter la requête
        df_result = pd.read_sql_query(sql_query, engine)
        
        # Fermer la connexion
        engine.dispose()
        
        return df_result

    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {e}")
        return pd.DataFrame()

def main():
    """Fonction principale du script."""
    
    # Charger la configuration de la base de données
    print("Chargement de la configuration de la base de données...")
    db_config = load_database_config()
    
    # Vérifier que toutes les variables sont chargées
    if not all(db_config.values()):
        print("Erreur: Certaines variables d'environnement sont manquantes dans le fichier dot.env")
        print(f"Variables chargées: {db_config}")
        return
    
    # Définition des dates (modifiez selon vos besoins)
    start_date = '2025-01-01'
    end_date = datetime.now().date()
    
    print(f"Récupération des données de grossesse entre {start_date} et {end_date}...")
    
    # Récupération des données
    df_pregnancy = get_pregnancy_tracking_data(start_date, end_date, db_config)
    
    if not df_pregnancy.empty:
        print(f"\n✅ Données récupérées avec succès!")
        print(f"📊 Nombre d'enregistrements: {len(df_pregnancy)}")
        print(f"📋 Nombre de colonnes: {len(df_pregnancy.columns)}")
        
        # Afficher les premières lignes
        print("\n📋 Aperçu des données:")
        print(df_pregnancy.head())
        
        # Afficher quelques statistiques
        print("\n📈 Statistiques rapides:")
        
        # Compter les différents statuts
        if 'has_session_during_pregnancy' in df_pregnancy.columns:
            sessions_stats = df_pregnancy['has_session_during_pregnancy'].value_counts()
            print(f"Sessions pendant la grossesse: {sessions_stats.to_dict()}")
        
        if 'has_viral_load_for_interval' in df_pregnancy.columns:
            viral_load_stats = df_pregnancy['has_viral_load_for_interval'].value_counts()
            print(f"Charge virale dans l'intervalle: {viral_load_stats.to_dict()}")
        
        if 'has_delivery_in_the_interval' in df_pregnancy.columns:
            delivery_stats = df_pregnancy['has_delivery_in_the_interval'].value_counts()
            print(f"Accouchements dans l'intervalle: {delivery_stats.to_dict()}")
        
        # Sauvegarder dans un fichier Excel avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/PTME/pregnancy_report.xlsx"
        
        # Créer le dossier s'il n'existe pas
        os.makedirs('outputs/PTME', exist_ok=True)
        
        df_pregnancy.to_excel(filename, index=False)
        print(f"\n💾 Données sauvegardées dans: {filename}")
        
        # Afficher les colonnes disponibles
        print(f"\n📋 Colonnes disponibles ({len(df_pregnancy.columns)}):")
        for i, col in enumerate(df_pregnancy.columns, 1):
            print(f"  {i:2d}. {col}")
            
    else:
        print("❌ Aucune donnée trouvée pour la période spécifiée.")
        print("Vérifiez les dates et la connectivité à la base de données.")
        
if __name__ == "__main__":
    main()


#=======================================================================================
print("\n\n=== FIN DU PIPELINE ===")
#=======================================================================================