
import polars as pl
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
	# Lecture rapide avec Polars
	df_polars = pl.read_excel("../jaden.xlsx", columns=["username", "form.cycle_2_start_date", "form.cycle_1_start_date", "form.cycle_2_start_date", "form.cycle_3_start_date", "form.case.@case_id"])
	df_polars.write_csv("../jaden.csv")  # Sauvegarde au format CSV (syntaxe Polars)
	# Conversion en pandas pour les visualisations
	fiche = df_polars.to_pandas()
	fiche.columns = fiche.columns.str.replace("form.", "")  # Nettoyage des noms de colonnes
	#convertion des dates
	fiche["cycle_1_start_date"] = pd.to_datetime(fiche["cycle_1_start_date"], errors="coerce")
	fiche["cycle_2_start_date"] = pd.to_datetime(fiche["cycle_2_start_date"], errors="coerce")
	fiche["cycle_3_start_date"] = pd.to_datetime(fiche["cycle_3_start_date"], errors="coerce")
	# remplacer les "---" par NaN
	fiche.replace("---", pd.NA, inplace=True)
	# renommer la colonne case_id
	fiche.rename(columns={"case.@case_id": "caseid"}, inplace=True)
	# creer une colonne et cancatener les dates de cycle 1, 2 et 3 dans une nouvelle colonne et compter les occurrences
	# - une colonne all_cycle qui contient la date la plus recente de (cycle_1_start_date, cycle_2_start_date, cycle_3_start_date)
	# - une colonne cycle_count qui contient le nombre d'occuenrences des caseid dans la colonne all_cycle
	fiche["all_cycle"] = fiche[["cycle_1_start_date", "cycle_2_start_date", "cycle_3_start_date"]].max(axis=1)
	fiche["cycle_count"] = fiche.groupby("caseid")["all_cycle"].transform("count")

	# Sauvegarde en Excel et ouverture automatique
	excel_path = "../jaden_clean.xlsx"
	fiche.to_excel(excel_path, index=False)
	print(f"Fichier sauvegardé : {excel_path}")

	# Ouvrir le fichier Excel automatiquement (Windows)
	os.startfile(os.path.abspath(excel_path))
	print(fiche.head())

if __name__ == '__main__':
	main()

