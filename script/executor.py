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
from utils import get_commcare_odata
# Download charges virales database from "Charges_virales_pediatriques.sql file"
from caris_fonctions import execute_sql_query

# In[2]:
from utils import get_commcare_odata
from ptme_fonction import creer_colonne_match_conditional



# Download charges virales database from "Charges_virales_pediatriques.sql file"
"""from caris_fonctions import execute_sql_query
env_path = 'dot.env'
sql_file_path = './sql/specimen.sql'

ptme_enceinte = execute_sql_query(env_path, sql_file_path)
duplicates = ptme_enceinte.columns[ptme_enceinte.columns.duplicated()].tolist()
if duplicates:
    print("Attention : des colonnes en double ont été trouvées dans le DataFrame.")
    print("Colonnes en double :", duplicates)
else:
    print("Aucune colonne en double trouvée dans le DataFrame.")
# print the shape of the DataFrame
print(ptme_enceinte.shape[0])
# print the first few rows of the DataFrame
print(ptme_enceinte.head(2))

ptme_enceinte.to_excel('./outputs/PTME/specimen.xlsx', index=False)"""
#=====================================================================
import pandas as pd
# Remplacez 'mysql.connector' par le connecteur que vous utilisez (par exemple, 'pymysql')
import mysql.connector 

def get_pregnancy_data(start_date, end_date, db_config, sql_script=None):
    """
    Exécute la requête SQL complexe pour récupérer les données de grossesse 
    sur un intervalle de temps donné et les retourne sous forme de DataFrame.

    :param start_date: Date de début de l'intervalle (format 'YYYY-MM-DD').
    :param end_date: Date de fin de l'intervalle (format 'YYYY-MM-DD').
    :param db_config: Dictionnaire contenant les informations de connexion à la BDD.
    :param sql_script: Script SQL personnalisé (optionnel). Si None, utilise la requête par défaut.
    :return: DataFrame pandas des résultats.
    """
    # Sécuriser les dates
    start_date_sql = f"'{start_date}'"
    end_date_sql = f"'{end_date}'"

    # Utiliser le script SQL fourni ou la requête par défaut
    if sql_script is None:
        sql_query = f"""
SET @start_date={start_date_sql};
SET @end_date={end_date_sql};

SELECT 
    lhs.office,
    lhs.name as hosp,
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
    IF((viral_load_date + INTERVAL 12 MONTH) > @end_date,
        'yes',
        'no') AS has_valide_viral_load,
    IF(((tp.dpa >= @start_date)
            OR ((tp.ddr + INTERVAL 9 MONTH + INTERVAL 7 DAY) >= @start_date))
            AND ((tp.ddr <= @end_date)
            OR ((tp.dpa - INTERVAL 9 MONTH - INTERVAL 7 DAY) <= @end_date)),
        'yes',
        'no') AS is_pregnant_in_the_interval,
    IF(tp.actual_delivery_date BETWEEN @start_date AND @end_date,
        'yes',
        'no') AS has_delivery_in_the_interval,
    IF((tp.dpa BETWEEN '2025-07-01' AND '2025-09-30'
            OR (tp.ddr + INTERVAL 9 MONTH + INTERVAL 7 DAY) BETWEEN '2025-07-01' AND '2025-09-30'),
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
    IF(tp.created_at BETWEEN @start_date AND @end_date,
        'yes',
        'no') AS pregnancy_added_in_the_interval,
    b.viral_load_date,
    b.viral_load_count,
    IF(v.id_patient IS NOT NULL,
        'yes',
        'no') AS has_viral_load_in_the_interval,
    IF((b.viral_load_date + INTERVAL 12 MONTH) > @start_date,
        'yes',
        'no') AS valide_viral_load_for_interval,
    IF(tp.infant_has_no_pcr_test = 1,
        'yes',
        IF(tp.infant_has_no_pcr_test = 2,
            'no',
            tp.infant_has_no_pcr_test)) AS has_pcr_test,
    timestampdiff(DAY,tp.actual_delivery_date,NOW()) as nb_day
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
        viral_load_date BETWEEN @start_date AND @end_date
    GROUP BY tmf.id_patient) v ON v.id_patient = tp.id_patient_mother
WHERE
    (((tp.dpa >= @start_date)
        OR ((tp.ddr + INTERVAL 9 MONTH + INTERVAL 7 DAY) >= @start_date))
        AND ((tp.ddr <= @end_date)
        OR ((tp.dpa - INTERVAL 9 MONTH - INTERVAL 7 DAY) <= @end_date)))
        OR tp.actual_delivery_date BETWEEN @start_date AND @end_date
        OR tp.created_at BETWEEN @start_date AND @end_date
GROUP BY id_patient_mother
"""
    else:
        # Utiliser le script SQL fourni et remplacer les placeholders de dates
        sql_query = sql_script.replace("{start_date}", start_date_sql).replace("{end_date}", end_date_sql)    # La fonction read_sql_query de Pandas ne peut pas exécuter les commandes SET 
    # car elle attend une seule commande SELECT.
    # Nous devons donc exécuter SET séparément.
    
    # 2. Connexion et Exécution
    try:
        # Établir la connexion à la base de données avec SQLAlchemy
        from sqlalchemy import create_engine
        
        # Créer la chaîne de connexion SQLAlchemy
        connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
        engine = create_engine(connection_string)
        
        # Remplacer les variables @start_date et @end_date directement dans la requête
        select_query = sql_query.replace("@start_date", start_date_sql).replace("@end_date", end_date_sql)
        
        # Supprimer les commandes SET du début de la requête car elles ne sont plus nécessaires
        select_query = select_query.split("SELECT", 1)[1]
        select_query = "SELECT" + select_query
        
        df_result = pd.read_sql_query(select_query, engine)
        
        # Fermer la connexion
        engine.dispose()
        
        return df_result

    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {e}")
        return pd.DataFrame()

#==========================================================================================================
def get_club_session_data(start_date, end_date, db_config):
    """
    Récupère les données des sessions de club pour une période donnée.
    
    :param start_date: Date de début de l'intervalle (format 'YYYY-MM-DD').
    :param end_date: Date de fin de l'intervalle (format 'YYYY-MM-DD').
    :param db_config: Dictionnaire contenant les informations de connexion à la BDD.
    :return: DataFrame pandas des résultats.
    """
    
    # Sécuriser les dates
    start_date_sql = f"'{start_date}'"
    end_date_sql = f"'{end_date}'"
    
    # Requête SQL pour les sessions de club
    sql_query = f"""
    SELECT 
        p.patient_code,
        ti.first_name, 
        MAX(cs.date) as last_session_date, 
        lt.name as club_type, 
        SUM(s.is_present=1) as nb_presence 
    FROM 
        session s 
        INNER JOIN club_session cs ON cs.id = s.id_club_session
        INNER JOIN club c ON c.id = cs.id_club
        LEFT JOIN tracking_infant ti ON ti.id_patient = s.id_patient
        INNER JOIN patient p ON p.id = s.id_patient
        LEFT JOIN lookup_club_type lt ON lt.id = c.club_type
    WHERE 
        (cs.date BETWEEN {start_date_sql} AND {end_date_sql}) 
        AND (c.club_type != 1)
    GROUP BY s.id_patient
    """
    
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

#==========================================================================================================
def get_woman_child_pcr(start_date, end_date, db_config, sql_script=None):
    """
    Récupère les données des tests PCR avec les détails des patients mère-enfant.
    
    Parameters:
        start_date (str): Date de début au format 'YYYY-MM-DD'
        end_date (str): Date de fin au format 'YYYY-MM-DD'  
        db_config (dict): Configuration de la base de données
        sql_script (str, optional): Script SQL personnalisé. Si fourni, remplace le script par défaut.
    
    Returns:
        pandas.DataFrame: DataFrame contenant les données des tests PCR
    """
    
    # Sécuriser les dates pour l'insertion SQL
    start_date_sql = f"'{start_date}'"
    end_date_sql = f"'{end_date}'"
    
    # Script SQL par défaut pour les tests PCR
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

#==========================================================================================================
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

#==========================================================================================================
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

#==========================================================================================================
def get_club_attendance_data(start_date, end_date, db_config, sql_script=None):
    """
    Récupère les données détaillées de présence aux clubs avec agrégations mensuelles.
    
    Parameters:
        start_date (str): Date de début au format 'YYYY-MM-DD'
        end_date (str): Date de fin au format 'YYYY-MM-DD'  
        db_config (dict): Configuration de la base de données
        sql_script (str, optional): Script SQL personnalisé. Si fourni, remplace le script par défaut.
    
    Returns:
        pandas.DataFrame: DataFrame contenant les données de présence aux clubs avec agrégations mensuelles
    """
    
    # Sécuriser les dates pour l'insertion SQL
    start_date_sql = f"'{start_date}'"
    end_date_sql = f"'{end_date}'"
    
    # Script SQL par défaut pour les données de présence aux clubs
    default_sql = """
    SELECT 
        w.*, 
        SUM(MONTH(w.session_date) = 10) AS oct,
        SUM(MONTH(w.session_date) = 11) AS nov,
        SUM(MONTH(w.session_date) = 12) AS decem,
        SUM(MONTH(w.session_date) = 1)  AS jan,
        SUM(MONTH(w.session_date) = 2)  AS fev,
        SUM(MONTH(w.session_date) = 3)  AS mar,
        SUM(MONTH(w.session_date) = 4)  AS avr,
        SUM(MONTH(w.session_date) = 5)  AS mai,
        SUM(MONTH(w.session_date) = 6)  AS juin,
        SUM(MONTH(w.session_date) = 7)  AS juil,
        SUM(MONTH(w.session_date) = 8)  AS aout,
        SUM(MONTH(w.session_date) = 9)  AS sep 
    FROM (
        SELECT
            IF(p.linked_to_id_patient > 0, p.linked_to_id_patient, p.id) AS id_patient,
            lh.name AS hopital,
            CONCAT(lh.city_code, '/', lh.hospital_code) AS site_code,
            lh.office AS office,
            lce.name AS commune,
            lnt.name AS network,
            c.name AS club_name,
            lct.name AS club_type,
            p.patient_code,
            cs.date AS session_date,
            lctc.name_fr AS topic,
            a.date AS first_attendance_date,
            b.date AS last_attendance_date,
            aa.date AS first_attendance_date_by_club,
            COALESCE(ti.first_name, tm.first_name) AS first_name,
            COALESCE(ti.last_name, tm.last_name) AS last_name,
            COALESCE(ti.dob, tm.dob) AS dob,
            COALESCE(ti.is_abandoned, tm.is_abandoned) AS is_abandoned,
            COALESCE(ti.is_dead, tm.is_dead) AS is_dead,
            IF(tm.is_graduate = 1, 'Yes', 'No') AS graduation,
            tm.graduation_date AS graduation_date,
            IF(ti.gender = 1, 'male', IF(ti.gender = 2, 'female', 'unknown')) AS sex,
            ss.clore,
            ss.nbre_deparasitaires,
            ss.nbre_preservatifs,
            ss.nbre_vit_a,
            ss.nbre_moustiquaires,
            ss.code,
            ss.is_patient_tb,
            ss.is_patient_on_pf,
            ss.adh
        FROM session ss
        LEFT JOIN club_session cs ON cs.id = ss.id_club_session
        LEFT JOIN club c ON c.id = cs.id_club
        LEFT JOIN lookup_club_type lct ON lct.id = c.club_type
        LEFT JOIN lookup_club_topic lctc ON lctc.id = cs.topic
        LEFT JOIN patient p ON p.id = ss.id_patient
        LEFT JOIN tracking_motherbasicinfo tm 
            ON tm.id_patient = IF(p.linked_to_id_patient > 0, p.linked_to_id_patient, ss.id_patient)
        LEFT JOIN tracking_infant ti 
            ON ti.id_patient = IF(p.linked_to_id_patient > 0, p.linked_to_id_patient, ss.id_patient)
        LEFT JOIN lookup_hospital lh ON lh.id = c.id_hospital
        LEFT JOIN lookup_commune lce ON lce.id = lh.commune
        LEFT JOIN lookup_network lnt ON lnt.id = lh.network
        LEFT JOIN (
            SELECT 
                MIN(cs1.date) AS date, 
                pp.main_id
            FROM session s1
            LEFT JOIN club_session cs1 ON cs1.id = s1.id_club_session
            LEFT JOIN (
                SELECT p12.*, IF(p12.linked_to_id_patient > 0, p12.linked_to_id_patient, p12.id) AS main_id 
                FROM patient p12
            ) pp ON pp.id = s1.id_patient
            GROUP BY pp.main_id
        ) a ON a.main_id = IF(p.linked_to_id_patient > 0, p.linked_to_id_patient, p.id)
        LEFT JOIN (
            SELECT 
                MAX(cs2.date) AS date, 
                s2.id_patient
            FROM session s2
            LEFT JOIN club_session cs2 ON cs2.id = s2.id_club_session
            GROUP BY s2.id_patient
        ) b ON b.id_patient = ss.id_patient
        LEFT JOIN (
            SELECT 
                MIN(cs3.date) AS date, 
                s3.id_patient, 
                cs3.id_club
            FROM session s3
            LEFT JOIN club_session cs3 ON cs3.id = s3.id_club_session
            WHERE s3.is_present != 1
            GROUP BY cs3.id_club, s3.id_patient
        ) aa ON aa.id_patient = ss.id_patient AND c.id = aa.id_club
        WHERE 
            cs.date BETWEEN {start_date} AND {end_date}
            AND p.id IS NOT NULL
        ORDER BY 
            CONCAT(lh.city_code, '/', lh.hospital_code), 
            c.name, 
            p.patient_code, 
            cs.date
    ) AS w
    GROUP BY 
        w.patient_code
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

#==========================================================================================================
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


# --- 3. Exemple d'Utilisation ---

# Configuration de la base de données (À remplir avec vos informations réelles)
db_config_example = {
    'user': 'caris_readonly',
    'password': 'longlivecaris!!',
    'host': 'caris.cwyvkxmtzny2.us-east-1.rds.amazonaws.com',
    'database': 'caris_db'
}

# Définition des dates
date_debut = '2025-05-01'
date_fin = '2025-12-06'

# Exécution et récupération du DataFrame (sans script personnalisé - utilise le script par défaut)
df_data = get_pregnancy_data(date_debut, date_fin, db_config_example)

if not df_data.empty:
    print(f"\nDataFrame récupéré avec {len(df_data)} lignes et {len(df_data.columns)} colonnes.")
    print(df_data.head())
    df_data.to_excel('./outputs/PTME/pregnancy_data.xlsx', index=False)

# --- 4. Exemple d'utilisation pour les sessions de club ---

# Définition des dates pour les sessions de club
date_debut_club = '2025-11-01'
date_fin_club = '2025-11-30'

# Exécution et récupération du DataFrame des sessions de club
df_club_data = get_club_session_data(date_debut_club, date_fin_club, db_config_example)

if not df_club_data.empty:
    print(f"\nDataFrame des sessions de club récupéré avec {len(df_club_data)} lignes et {len(df_club_data.columns)} colonnes.")
    print(df_club_data.head())
    df_club_data.to_excel('./outputs//PTME/club_session_data.xlsx', index=False)
else:
    print("Aucune donnée de session de club trouvée pour la période spécifiée.")

# --- 5. Exemple d'utilisation pour les tests PCR ---

# Définition des dates pour les tests PCR
date_debut_pcr = '2025-05-01'
date_fin_pcr = '2025-12-06'

# Exécution et récupération du DataFrame des tests PCR
print("\n--- Test avec données PCR par défaut ---")
df_pcr_data = get_woman_child_pcr(date_debut_pcr, date_fin_pcr, db_config_example)

if not df_pcr_data.empty:
    print(f"\nDataFrame des tests PCR récupéré avec {len(df_pcr_data)} lignes et {len(df_pcr_data.columns)} colonnes.")
    print(df_pcr_data.head())
    df_pcr_data.to_excel('./outputs/PTME/pcr_test_data.xlsx', index=False)
else:
    print("Aucune donnée de test PCR trouvée pour la période spécifiée.")

# --- 6. Test avec un script SQL personnalisé ---

# Script SQL personnalisé simple pour tester
custom_sql_script = """
SELECT 
    p.patient_code,
    tmi.first_name,
    tmi.last_name,
    tp.dpa,
    tp.ddr,
    tp.actual_delivery_date AS delivery_date,
    tp.created_at AS pregnancy_added_at
FROM
    tracking_pregnancy tp
    LEFT JOIN tracking_motherbasicinfo tmi ON tmi.id_patient = tp.id_patient_mother
    LEFT JOIN patient p ON p.id = tp.id_patient_mother
WHERE
    tp.created_at BETWEEN {start_date} AND {end_date}
LIMIT 10
"""

# Test de la fonction avec le script SQL personnalisé
print("\n--- Test avec script SQL personnalisé ---")
df_custom = get_pregnancy_data('2025-11-01', '2025-11-30', db_config_example, custom_sql_script)

if not df_custom.empty:
    print(f"DataFrame personnalisé récupéré avec {len(df_custom)} lignes et {len(df_custom.columns)} colonnes.")
    print(df_custom.head())
else:
    print("Aucune donnée trouvée avec le script personnalisé.")

# --- 7. Test avec script PCR personnalisé ---

# Script PCR personnalisé avec le script fourni par l'utilisateur
custom_pcr_script = """
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

# Test de la fonction PCR avec le script personnalisé
print("\n--- Test avec script PCR personnalisé ---")
df_pcr_custom = get_woman_child_pcr('2025-05-01', '2025-09-30', db_config_example, custom_pcr_script)

if not df_pcr_custom.empty:
    print(f"DataFrame PCR personnalisé récupéré avec {len(df_pcr_custom)} lignes et {len(df_pcr_custom.columns)} colonnes.")
    print(df_pcr_custom.head())
else:
    print("Aucune donnée PCR trouvée avec le script personnalisé.")

# --- 8. Exemple d'utilisation pour les données de présence aux clubs ---

# Définition des dates pour les données de présence
date_debut_attendance = '2025-11-01'
date_fin_attendance = '2025-12-06'

# Exécution et récupération du DataFrame des données de présence
print("\n--- Test avec données de présence aux clubs ---")
df_attendance_data = get_club_attendance_data(date_debut_attendance, date_fin_attendance, db_config_example)

if not df_attendance_data.empty:
    print(f"\nDataFrame des présences aux clubs récupéré avec {len(df_attendance_data)} lignes et {len(df_attendance_data.columns)} colonnes.")
    print("Colonnes disponibles:", list(df_attendance_data.columns))
    print(df_attendance_data.head())
    df_attendance_data.to_excel('./outputs/PTME/club_attendance_data.xlsx', index=False)
else:
    print("Aucune donnée de présence aux clubs trouvée pour la période spécifiée.")

# --- 9. Test avec script de présence personnalisé ---

# Script personnalisé simplifié pour tester
custom_attendance_script = """
SELECT 
    w.*, 
    SUM(MONTH(w.session_date) = 11) AS nov,
    SUM(MONTH(w.session_date) = 12) AS decem
FROM (
    SELECT
        p.patient_code,
        c.name AS club_name,
        lct.name AS club_type,
        cs.date AS session_date,
        COALESCE(ti.first_name, tm.first_name) AS first_name,
        COALESCE(ti.last_name, tm.last_name) AS last_name,
        ss.is_patient_tb,
        ss.is_patient_on_pf
    FROM session ss
    LEFT JOIN club_session cs ON cs.id = ss.id_club_session
    LEFT JOIN club c ON c.id = cs.id_club
    LEFT JOIN lookup_club_type lct ON lct.id = c.club_type
    LEFT JOIN patient p ON p.id = ss.id_patient
    LEFT JOIN tracking_motherbasicinfo tm ON tm.id_patient = ss.id_patient
    LEFT JOIN tracking_infant ti ON ti.id_patient = ss.id_patient
    WHERE 
        cs.date BETWEEN {start_date} AND {end_date}
        AND p.id IS NOT NULL
    LIMIT 20
) AS w
GROUP BY 
    w.patient_code
"""

# Test de la fonction avec script personnalisé
print("\n--- Test avec script de présence personnalisé (limité à 20 résultats) ---")
df_attendance_custom = get_club_attendance_data('2025-11-01', '2025-11-30', db_config_example, custom_attendance_script)

if not df_attendance_custom.empty:
    print(f"DataFrame présence personnalisé récupéré avec {len(df_attendance_custom)} lignes et {len(df_attendance_custom.columns)} colonnes.")
    print(df_attendance_custom.head())
else:
    print("Aucune donnée de présence trouvée avec le script personnalisé.")

# --- 10. Exemple d'utilisation pour les sessions de club détaillées ---

# Définition des dates pour les sessions détaillées
date_debut_detailed = '2025-05-01'
date_fin_detailed = '2025-12-06'

# Exécution et récupération du DataFrame des sessions détaillées
print("\n--- Test avec données de sessions de club détaillées ---")
df_detailed_sessions = get_club_sessions_data(date_debut_detailed, date_fin_detailed, db_config_example)

if not df_detailed_sessions.empty:
    print(f"\nDataFrame des sessions détaillées récupéré avec {len(df_detailed_sessions)} lignes et {len(df_detailed_sessions.columns)} colonnes.")
    print("Colonnes disponibles:", list(df_detailed_sessions.columns))
    print(df_detailed_sessions.head())
    df_detailed_sessions.to_excel('./outputs/PTME/club_sessions_detailed.xlsx', index=False)
else:
    print("Aucune donnée de session détaillée trouvée pour la période spécifiée.")

# --- 11. Test avec script de sessions détaillées personnalisé ---

# Script personnalisé simplifié pour tester les sessions détaillées
custom_detailed_script = """
SELECT
    p.patient_code,
    c.name AS club_name,
    lct.name AS club_type,
    cs.date AS session_date_presence,
    COALESCE(ti.first_name, tm.first_name) AS first_name,
    COALESCE(ti.last_name, tm.last_name) AS last_name,
    ss.is_present AS present,
    lca.name AS raison_absence,
    ss.is_patient_tb,
    ss.is_patient_on_pf
FROM session ss
LEFT JOIN club_session cs ON cs.id = ss.id_club_session
LEFT JOIN club c ON c.id = cs.id_club
LEFT JOIN lookup_club_type lct ON lct.id = c.club_type
LEFT JOIN patient p ON p.id = ss.id_patient
LEFT JOIN tracking_motherbasicinfo tm ON tm.id_patient = ss.id_patient
LEFT JOIN tracking_infant ti ON ti.id_patient = ss.id_patient
LEFT JOIN lookup_club_attendance lca ON lca.id = ss.is_present
WHERE 
    ss.is_present IS NOT NULL AND
    p.id IS NOT NULL AND
    cs.date BETWEEN {start_date} AND {end_date}
LIMIT 15
"""

# Test de la fonction avec script personnalisé
print("\n--- Test avec script de sessions détaillées personnalisé (limité à 15 résultats) ---")
df_detailed_custom = get_club_sessions_data('2025-11-01', '2025-11-30', db_config_example, custom_detailed_script)

if not df_detailed_custom.empty:
    print(f"DataFrame sessions détaillées personnalisé récupéré avec {len(df_detailed_custom)} lignes et {len(df_detailed_custom.columns)} colonnes.")
    print(df_detailed_custom.head())
else:
    print("Aucune donnée de session détaillée trouvée avec le script personnalisé.")

# --- 12. Exemple d'utilisation pour l'analyse des spécimens PCR ---

# Définition des dates pour l'analyse des spécimens PCR
date_debut_specimens = '2025-11-01'
date_fin_specimens = '2025-12-06'

# Exécution et récupération du DataFrame des spécimens PCR
print("\n--- Test avec données d'analyse des spécimens PCR ---")
df_pcr_specimens = get_pcr_analysis(date_debut_specimens, date_fin_specimens, db_config_example)

if not df_pcr_specimens.empty:
    print(f"\nDataFrame des spécimens PCR récupéré avec {len(df_pcr_specimens)} lignes et {len(df_pcr_specimens.columns)} colonnes.")
    print("Colonnes disponibles:", list(df_pcr_specimens.columns))
    print(df_pcr_specimens.head())
    df_pcr_specimens.to_excel('./outputs/PTME/pcr_specimens_analysis.xlsx', index=False)
else:
    print("Aucune donnée d'analyse PCR trouvée pour la période spécifiée.")

# --- 13. Exemple d'utilisation pour les données PCR mère-enfant liées ---

# Définition des dates pour les données PCR mère-enfant
date_debut_mother_child = '2025-05-01'
date_fin_mother_child = '2025-12-06'

# Exécution et récupération du DataFrame des PCR mère-enfant
print("\n--- Test avec données PCR mère-enfant liées ---")
df_mother_child_pcr = get_mother_child_linked_pcr(date_debut_mother_child, date_fin_mother_child, db_config_example)

if not df_mother_child_pcr.empty:
    print(f"\nDataFrame des PCR mère-enfant récupéré avec {len(df_mother_child_pcr)} lignes et {len(df_mother_child_pcr.columns)} colonnes.")
    print("Colonnes disponibles:", list(df_mother_child_pcr.columns))
    print(df_mother_child_pcr.head())
    df_mother_child_pcr.to_excel('./outputs/PTME/mother_child_linked_pcr.xlsx', index=False)
else:
    print("Aucune donnée PCR mère-enfant trouvée pour la période spécifiée.")