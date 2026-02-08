import os
import sys
import subprocess
from datetime import datetime
import time

# ===========================================================================
# SCRIPT D'EXÉCUTION AUTOMATIQUE PYTHON
# - Reproduction de la logique Bash (venv, Quarto double tentative, Git)
# ===========================================================================

# --- Configuration ---
PY_SCRIPTS = [
    "script/oev_pipeline.py", 
    "script/garden_pipeline.py", 
    "script/muso_pipeline.py", 
    "script/nutrition_pipeline.py", 
    "script/call-pipeline.py", 
    "script/ptme_pipeline.py" 
]
QMD_FILES = [
    "tracking-oev.qmd", 
    "tracking-gardening.qmd", 
    "tracking-muso.qmd", 
    "tracking-nutrition.qmd", 
    "tracking-call.qmd", 
    "tracking-ptme.qmd"
]
# ---------------------

def run_command(command, check=False, shell=False):
    """Exécute une commande et retourne (succès, sortie)"""
    try:
        # Utilisation de Popen pour gérer la sortie et les erreurs
        result = subprocess.run(
            command, 
            check=check, 
            shell=shell,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()
    except FileNotFoundError:
        # Pour les commandes comme 'quarto' ou 'git'
        return False, f"Commande non trouvée: {command[0] if isinstance(command, list) else command.split()[0]}"
    except Exception as e:
        return False, str(e)


def find_python_executable():
    """Détermine la commande Python à utiliser (python, python3, py, ou venv)"""
    
    # 1. Vérification de l'environnement virtuel (venv)
    if os.path.isdir("venv"):
        # Unix/macOS/Linux
        if os.path.exists("venv/bin/activate"):
            print("Activation de l'environnement virtuel Unix détecté (venv/bin/python)")
            return "venv/bin/python"
        # Windows
        elif os.path.exists("venv/Scripts/activate"):
            print("Activation de l'environnement virtuel Windows détecté (venv/Scripts/python.exe)")
            return "venv/Scripts/python.exe"
        
    # 2. Recherche des commandes Python globales
    for cmd in ["python", "python3", "py"]:
        if run_command([cmd, "--version"], check=False)[0]:
            print(f"Interpréteur global trouvé: {cmd}")
            return cmd

    print("Erreur: Aucun interpréteur Python trouvé (ni python, ni python3, ni py).")
    return None

def install_dependencies(python_cmd):
    """Installe les dépendances via requirements.txt"""
    if os.path.exists("requirements.txt"):
        print("Installation des modules Python requis...")
        
        # Mise à jour de pip
        success, _ = run_command([python_cmd, "-m", "pip", "install", "--upgrade", "pip"])
        if not success:
            print("Erreur lors de la mise à jour de pip.")
            return False

        # Installation des dépendances
        success, error_msg = run_command([python_cmd, "-m", "pip", "install", "-r", "requirements.txt"])
        if not success:
            print(f"Erreur lors de l'installation des modules Python:\n{error_msg}")
            return False
        
        print("Installation des modules réussie.")
        return True
    else:
        print("Fichier requirements.txt introuvable, installation des modules ignorée.")
        return True

def execute_python_scripts(python_cmd):
    """Exécute tous les scripts Python dans la liste PY_SCRIPTS"""
    print("\n[1/3] Exécution des scripts Python...")
    failed_py = []
    
    for file in PY_SCRIPTS:
        if os.path.exists(file):
            print(f"Execution : {file}")
            # Utiliser python_cmd pour garantir l'utilisation du bon interpréteur (venv ou global)
            success, error_msg = run_command([python_cmd, file])
            
            if success:
                print(f"Succès : {file}")
            else:
                print(f"Échec : {file}")
                # print(f"Détails de l'erreur:\n{error_msg}") # Optionnel pour plus de logs
                failed_py.append(file)
        else:
            print(f"Fichier introuvable : {file} - ignoré")
            
    return failed_py

def render_quarto_files():
    """Rend tous les fichiers Quarto avec double tentative en cas d'échec"""
    print("\n[2/3] Rendu des fichiers Quarto...")
    failed_qmd = []
    
    for file in QMD_FILES:
        if os.path.exists(file):
            print(f"Rendu : {file}")
            
            # Première tentative
            success, _ = run_command(["quarto", "render", file, "--quiet"])
            
            if not success:
                print(f"Première tentative échouée pour {file}, nouvelle tentative...")
                time.sleep(1) # Pause entre les tentatives
                
                # Deuxième tentative
                print(f"Deuxième tentative pour {file}...")
                success_2, error_msg_2 = run_command(["quarto", "render", file, "--quiet"])
                
                if not success_2:
                    print(f"Échec définitif : {file}")
                    # print(f"Détails de l'erreur:\n{error_msg_2}") # Optionnel pour plus de logs
                    failed_qmd.append(file)
                else:
                    print(f"Succès (2ème tentative) : {file}")
            else:
                print(f"Succès : {file}")
                
            time.sleep(0.5) # Petit délai entre les fichiers
        else:
            print(f"Fichier introuvable : {file} - ignoré")
            
    return failed_qmd

def run_git_operations():
    """Exécute les opérations Git (pull, add, commit, push)"""
    print("\n[3/3] Opérations Git...")
    failed_git = False
    
    # Vérifier si on est dans un repository Git
    success_repo, _ = run_command(["git", "rev-parse", "--is-inside-work-tree"])
    
    if not success_repo:
        print("Pas un repository Git - opérations Git ignorées")
        print("Pour initialiser un repo Git, exécutez: git init")
        return False
        
    print("Repository Git détecté")
    
    # Obtenir la branche actuelle
    success, current_branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if not success or current_branch == 'HEAD':
        current_branch = "main" # Par défaut si détaché ou erreur

    commit_message = f"Update automatique du {datetime.now().strftime('%Y-%m-%d')}"

    # 1) Fetch (pour comparer)
    print("Vérification du statut avec origin...")
    run_command(["git", "fetch", "origin"])

    # 2) Pull automatique (si des changements distants existent)
    local, _ = run_command(["git", "rev-parse", "HEAD"])
    remote, _ = run_command(["git", "rev-parse", f"origin/{current_branch}"])

    if remote and local != remote:
        print(f"Mise à jour nécessaire - git pull sur {current_branch}...")
        success_pull, error_pull = run_command(["git", "pull", "origin", current_branch])
        if success_pull:
            print("git pull réussi")
        else:
            print("Échec de 'git pull' - possible conflit")
            print("Résolvez les conflits manuellement et relancez le script")
            failed_git = True
            return failed_git # Arrêter les opérations Git
    else:
        print("Branche à jour avec origin")
        
    # 3) Stager tous les changements
    if not failed_git:
        success_add, error_add = run_command(["git", "add", "-A"])
        if not success_add:
            print(f"Échec de 'git add -A': {error_add}")
            failed_git = True
        else:
            print("git add -A réussi")

            # 4) Commiter uniquement s'il y a des changements indexés
            success_diff, _ = run_command(["git", "diff", "--cached", "--quiet"])
            
            # success_diff est True si les changements sont vides
            if success_diff:
                print("Aucun changement à committer")
            else:
                print(f"Commit avec le message: '{commit_message}'")
                success_commit, error_commit = run_command(["git", "commit", "-m", commit_message])
                
                if success_commit:
                    print("Git commit réussi")
                    commit_hash, _ = run_command(["git", "rev-parse", "--short", "HEAD"])
                    print(f"Hash du commit: {commit_hash}")

                    # 5) Push automatique
                    success_push, error_push = run_command(["git", "push", "origin", current_branch])
                    
                    if success_push:
                        print(f"git push réussi vers origin/{current_branch}")
                    else:
                        print(f"Échec de 'git push': {error_push}")
                        failed_git = True
                else:
                    print(f"Échec du git commit: {error_commit}")
                    failed_git = True

    return failed_git

# --- Logique Principale ---
def main():
    """Fonction principale du pipeline"""
    
    print("Début de l'exécution globale")
    print(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-------------------------------")

    # 1. Configuration Python
    python_cmd = find_python_executable()
    if not python_cmd:
        sys.exit(1)

    if not install_dependencies(python_cmd):
        sys.exit(1)

    # 2. Exécution des scripts Python
    failed_py = execute_python_scripts(python_cmd)
    
    # 3. Rendu Quarto
    failed_qmd = render_quarto_files()
    
    # 4. Opérations Git
    failed_git = run_git_operations()
    
    # 5. Rapport Final
    print("\n===============================")
    print("RAPPORT D'EXÉCUTION FINALE")
    print("===============================")
    
    total_success = (len(failed_py) == 0 and len(failed_qmd) == 0 and not failed_git)
    
    if total_success:
        print("Tous les processus ont été exécutés avec succès!")
        print("\nRésumé:")
        print(f"  Scripts Python: {len(PY_SCRIPTS)} réussis")
        print(f"  Fichiers Quarto: {len(QMD_FILES)} rendus")
        print("  Opérations Git: terminées")
    else:
        print("Certains processus ont échoué:")
        
        if failed_py:
            print(f"\nScripts Python échoués ({len(failed_py)}/{len(PY_SCRIPTS)}):")
            for f in failed_py: print(f"  - {f}")
        else:
            print(f"\nScripts Python: tous réussis ({len(PY_SCRIPTS)}/{len(PY_SCRIPTS)})")
            
        if failed_qmd:
            print(f"\nFichiers Quarto échoués ({len(failed_qmd)}/{len(QMD_FILES)}):")
            for f in failed_qmd: print(f"  - {f}")
        else:
            print(f"\nFichiers Quarto: tous réussis ({len(QMD_FILES)}/{len(QMD_FILES)})")
            
        if failed_git:
            print("\nOpérations Git: échouées")
        else:
            print("\nOpérations Git: réussies")

    print(f"\nFin d'exécution: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Script terminé.")
    
    # Code de sortie basé sur le succès global
    sys.exit(0 if total_success else 1)


if __name__ == "__main__":
    main()