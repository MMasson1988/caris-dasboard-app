import subprocess
import sys

# Nombre de runs à supprimer à chaque exécution (modifiable)
LIMIT = 100

def main():
    # Commande pour lister les databaseId des runs
    list_cmd = [
        "gh", "run", "list", f"--limit", str(LIMIT), "--json", "databaseId", "-q", ".[].databaseId"
    ]
    try:
        result = subprocess.run(list_cmd, capture_output=True, text=True, check=True)
        run_ids = [rid.strip() for rid in result.stdout.splitlines() if rid.strip()]
        if not run_ids:
            print("Aucun workflow run à supprimer.")
            return
        print(f"{len(run_ids)} workflow runs trouvés. Suppression en cours...")
        for run_id in run_ids:
            del_cmd = ["gh", "run", "delete", run_id, "-y"]
            del_result = subprocess.run(del_cmd, capture_output=True, text=True)
            if del_result.returncode == 0:
                print(f"✓ Run {run_id} supprimé.")
            else:
                print(f"✗ Erreur suppression run {run_id}: {del_result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la récupération des runs: {e.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    main()
