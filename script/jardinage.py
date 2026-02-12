
import polars as pl
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
	# Lecture rapide avec Polars
	"""df_polars = pl.read_excel("../jaden.xlsx", columns=["username", "form.cycle_1_start_date", "form.cycle_2_start_date", "form.cycle_3_start_date", "form.case.@case_id"])
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
 # all_cycle between may 1th and today
	fiche = fiche[fiche["all_cycle"] >= pd.to_datetime("2025-01-01")]
	fiche["cycle_count"] = fiche.groupby("caseid")["all_cycle"].transform("count")

	# Sauvegarde en Excel et ouverture automatique
	excel_path = "../jaden_clean.xlsx"
	fiche.to_excel(excel_path, index=False)
	print(f"Fichier sauvegardé : {excel_path}")

	# Ouvrir le fichier Excel automatiquement (Windows)
	os.startfile(os.path.abspath(excel_path))
	print(fiche.head())"""
	df_fiche1 = pd.read_excel("../fiche1.xlsx")
	df_fiche2 = pd.read_excel("../fiche2.xlsx")
	site = pd.read_excel("../site.xlsx")
	# concaténer verticalement
	df_fiche = pd.concat([df_fiche1, df_fiche2], ignore_index=True)
	# Ajouter la colonne in_muso
	if "beneficiary_type" in df_fiche.columns:
		df_fiche["in_muso"] = df_fiche["beneficiary_type"].apply(lambda x: "yes" if x == "muso" else "no")
	# creer colone site avecles 8 premiers caractere de la colonne caris_site
	if "caris_site" in df_fiche.columns:
		df_fiche["site"] = df_fiche["caris_site"].astype(str).str[:8]
  # eliminer les duplicates
	df_fiche = df_fiche.drop_duplicates(subset=["caseid"], keep="first")
	# Afficher les colonnes pour debug si erreur
	print("Colonnes du DataFrame concaténé :", df_fiche.columns.tolist())
	"""# Vérifier que les colonnes existent avant de grouper
	group_cols = [col for col in ["caseid", "commune", "departement", "in_muso"] if col in df_fiche.columns]
	if not group_cols:
		print("Aucune des colonnes 'caseid', 'commune', 'departement' n'est présente dans le DataFrame.")
		return
	# Compter le nombre de caseid uniques pour chaque groupe
	if "caseid" in group_cols:
		# On retire caseid du groupby pour compter les caseid par groupe de commune/departement
		groupby_cols = [col for col in group_cols if col != "caseid"]
		if groupby_cols:
			df_fiche_grouped = df_fiche.groupby(groupby_cols)["caseid"].nunique().reset_index(name="count_caseid")
		else:
			df_fiche_grouped = pd.DataFrame({"count_caseid": [df_fiche["caseid"].nunique()]})
	else:
		df_fiche_grouped = df_fiche.groupby(group_cols).size().reset_index(name="count")"""
	# combiner df_fiche avec site par a colonnne site
	if "site" in df_fiche.columns:
		df_fiche = pd.merge(df_fiche, site, on="site", how="left")
		df_fiche = df_fiche.drop_duplicates(subset=["caseid"], keep="first")
	# sauvegarder en excel et ouvrir après l'exécution du script
	excel_path = "../fiche_grouped.xlsx"
	df_fiche.to_excel(excel_path, index=False)
	print(f"Fichier sauvegardé : {excel_path}")
	os.startfile(os.path.abspath(excel_path))
 
if __name__ == '__main__':
	main()

