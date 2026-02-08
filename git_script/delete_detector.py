#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Operations Manager - Interactive CLI for git pull, push, and delete operations.
Basé sur git_auto_pull.py et git_auto_push.py

Usage:
    python delete_detector.py
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path
from typing import List
from datetime import datetime

# Couleurs pour le terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Extensions supportées
SUPPORTED_EXTENSIONS = ['.xlsx', '.csv', '.py', '.ipynb', '.sh', '.log', '.png', '.bat', '.r', '.qmd', '.txt']


def run_command(command: list):
    """Exécute une commande shell et gère les erreurs (style git_auto_push.py)."""
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        if result.stdout.strip():
            print(result.stdout)
        # Afficher les warnings mais ne pas les traiter comme des erreurs
        if result.stderr.strip():
            stderr_lines = result.stderr.strip().split('\n')
            critical_errors = [line for line in stderr_lines if not line.startswith('warning:')]
            if critical_errors:
                print('\n'.join(critical_errors))
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de : {' '.join(command)}")
        if e.stderr:
            print(e.stderr)
        return False
    return True


def print_header(text: str):
    """Affiche un en-tête formaté."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_menu(title: str, options: List[str]) -> int:
    """Affiche un menu et retourne le choix de l'utilisateur."""
    print(f"{Colors.CYAN}{title}{Colors.ENDC}")
    for i, option in enumerate(options, 1):
        print(f"  {Colors.GREEN}{i}){Colors.ENDC} {option}")
    print(f"  {Colors.WARNING}0){Colors.ENDC} Quitter/Annuler")
    
    while True:
        try:
            choice = int(input(f"\n{Colors.BOLD}Votre choix: {Colors.ENDC}"))
            if 0 <= choice <= len(options):
                return choice
            print(f"{Colors.FAIL}Choix invalide. Réessayez.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Veuillez entrer un nombre.{Colors.ENDC}")


def search_items(search_term: str, is_folder: bool, extension: str = None) -> List[Path]:
    """Recherche des fichiers ou dossiers contenant le terme de recherche."""
    results = []
    root_path = Path(".")
    
    if is_folder:
        for item in root_path.rglob("*"):
            if item.is_dir() and search_term.lower() in item.name.lower():
                if not any(excluded in str(item) for excluded in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
                    results.append(item)
    else:
        for item in root_path.rglob("*"):
            if item.is_file() and search_term.lower() in item.name.lower():
                if not any(excluded in str(item) for excluded in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
                    if extension:
                        if item.suffix.lower() == extension.lower():
                            results.append(item)
                    else:
                        results.append(item)
    
    return sorted(results)


def display_search_results(results: List[Path], item_type: str) -> Path:
    """Affiche les résultats de recherche et permet à l'utilisateur de choisir."""
    if not results:
        print(f"{Colors.WARNING}Aucun {item_type} trouvé.{Colors.ENDC}")
        return None
    
    print(f"\n{Colors.CYAN}{item_type.capitalize()}s trouvé(e)s:{Colors.ENDC}")
    for i, item in enumerate(results, 1):
        size_info = ""
        if item.is_file():
            size = item.stat().st_size
            if size < 1024:
                size_info = f" ({size} B)"
            elif size < 1024 * 1024:
                size_info = f" ({size/1024:.1f} KB)"
            else:
                size_info = f" ({size/1024/1024:.1f} MB)"
        print(f"  {Colors.GREEN}{i}){Colors.ENDC} {item}{size_info}")
    print(f"  {Colors.WARNING}0){Colors.ENDC} Annuler")
    
    while True:
        try:
            choice = int(input(f"\n{Colors.BOLD}Choisissez un {item_type} (numéro): {Colors.ENDC}"))
            if choice == 0:
                return None
            if 1 <= choice <= len(results):
                return results[choice - 1]
            print(f"{Colors.FAIL}Choix invalide.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Veuillez entrer un nombre.{Colors.ENDC}")


def get_extension_choice() -> str:
    """Demande à l'utilisateur de choisir une extension de fichier."""
    print(f"\n{Colors.CYAN}Types de fichiers supportés:{Colors.ENDC}")
    for i, ext in enumerate(SUPPORTED_EXTENSIONS, 1):
        print(f"  {Colors.GREEN}{i}){Colors.ENDC} {ext}")
    print(f"  {Colors.GREEN}{len(SUPPORTED_EXTENSIONS) + 1}){Colors.ENDC} Tous les types")
    print(f"  {Colors.WARNING}0){Colors.ENDC} Annuler")
    
    while True:
        try:
            choice = int(input(f"\n{Colors.BOLD}Choisissez le type de fichier: {Colors.ENDC}"))
            if choice == 0:
                return None
            if 1 <= choice <= len(SUPPORTED_EXTENSIONS):
                return SUPPORTED_EXTENSIONS[choice - 1]
            if choice == len(SUPPORTED_EXTENSIONS) + 1:
                return ""
            print(f"{Colors.FAIL}Choix invalide.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Veuillez entrer un nombre.{Colors.ENDC}")


def confirm_action(action: str, target: str) -> bool:
    """Demande confirmation avant d'exécuter une action."""
    print(f"\n{Colors.WARNING}⚠️  Vous êtes sur le point de {action}:{Colors.ENDC}")
    print(f"   {Colors.BOLD}{target}{Colors.ENDC}")
    response = input(f"\n{Colors.BOLD}Confirmer? (oui/non): {Colors.ENDC}").strip().lower()
    return response in ['oui', 'o', 'yes', 'y']


# ============================================================================
# GIT PULL - Basé sur git_auto_pull.py
# ============================================================================
def git_pull():
    """Effectue un git pull sécurisé (style git_auto_pull.py)."""
    print_header("📥 GIT PULL")
    print("🔄 Mise à jour du dépôt local depuis le dépôt distant...")
    
    if run_command(["git", "pull", "--progress"]):
        print(f"{Colors.GREEN}✅ Dépôt mis à jour avec succès !{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Échec de la mise à jour.{Colors.ENDC}")


# ============================================================================
# GIT PUSH - Basé sur git_auto_push.py
# ============================================================================
def git_push():
    """Effectue un git push automatisé (style git_auto_push.py)."""
    print_header("📤 GIT PUSH")
    
    # Date du jour pour le message par défaut
    today = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Choix: fichier spécifique ou tous les changements
    choice = print_menu("Que voulez-vous pousser?", [
        "Un fichier spécifique",
        "Un dossier",
        "Tous les changements"
    ])
    
    if choice == 0:
        return
    
    # Déterminer le path à ajouter
    if choice == 3:
        path = "."
    else:
        is_folder = (choice == 2)
        item_type = "dossier" if is_folder else "fichier"
        
        extension = None
        if not is_folder:
            extension = get_extension_choice()
            if extension is None:
                return
        
        search_term = input(f"\n{Colors.BOLD}Entrez le nom à rechercher: {Colors.ENDC}").strip()
        if not search_term:
            print(f"{Colors.FAIL}Nom vide. Annulation.{Colors.ENDC}")
            return
        
        results = search_items(search_term, is_folder, extension)
        selected = display_search_results(results, item_type)
        
        if selected is None:
            return
        
        path = str(selected)
    
    # Vérifier s'il y a des changements à commiter
    try:
        result = subprocess.run(["git", "status", "--porcelain"], 
                              check=True, text=True, capture_output=True)
        if not result.stdout.strip():
            print(f"{Colors.CYAN}ℹ️ Aucun changement détecté, rien à commiter.{Colors.ENDC}")
            return
    except subprocess.CalledProcessError:
        print(f"{Colors.FAIL}❌ Erreur lors de la vérification du statut Git{Colors.ENDC}")
        return
    
    # Demander le message de commit
    commit_message = input(f"\n{Colors.BOLD}💬 Message de commit (laisser vide pour message par défaut): {Colors.ENDC}").strip()
    
    if not commit_message:
        commit_message = f"Mise à jour automatique du {today}"
        print(f"{Colors.CYAN}💬 Utilisation du message par défaut : {commit_message}{Colors.ENDC}")
    
    # Étapes Git
    print(f"\n{Colors.BLUE}📦 Ajout des fichiers au staging area...{Colors.ENDC}")
    if not run_command(["git", "add", path]):
        return
    
    print(f"{Colors.BLUE}📝 Commit avec le message : {commit_message}{Colors.ENDC}")
    full_message = f"{commit_message} — {timestamp}"
    if not run_command(["git", "commit", "-m", full_message]):
        return
    
    print(f"{Colors.BLUE}🚀 Envoi vers le dépôt distant (git push)...{Colors.ENDC}")
    if run_command(["git", "push"]):
        print(f"{Colors.GREEN}✅ Synchronisation terminée avec succès !{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ Échec du push.{Colors.ENDC}")


# ============================================================================
# GIT DELETE - Suppression avec recherche interactive
# ============================================================================
def git_delete():
    """Supprime un fichier/dossier du dépôt git."""
    print_header("🗑️ GIT DELETE")
    
    choice = print_menu("Que voulez-vous supprimer?", ["Un fichier", "Un dossier"])
    
    if choice == 0:
        return
    
    is_folder = (choice == 2)
    item_type = "dossier" if is_folder else "fichier"
    
    extension = None
    if not is_folder:
        extension = get_extension_choice()
        if extension is None:
            return
    
    search_term = input(f"\n{Colors.BOLD}Entrez le nom à rechercher: {Colors.ENDC}").strip()
    if not search_term:
        print(f"{Colors.FAIL}Nom vide. Annulation.{Colors.ENDC}")
        return
    
    results = search_items(search_term, is_folder, extension)
    selected = display_search_results(results, item_type)
    
    if selected is None:
        return
    
    print(f"\n{Colors.FAIL}⚠️  ATTENTION: Cette action peut être irréversible!{Colors.ENDC}")
    
    delete_choice = print_menu("Comment voulez-vous supprimer?", [
        "Supprimer du git ET du disque local",
        "Supprimer du git mais garder en local",
        "Supprimer seulement en local (pas de git)"
    ])
    
    if delete_choice == 0:
        return
    
    if not confirm_action("SUPPRIMER", str(selected)):
        print(f"{Colors.WARNING}Annulation.{Colors.ENDC}")
        return
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if delete_choice == 1:
        # Supprimer du git et du disque
        print(f"\n{Colors.BLUE}🗑️ Suppression de {selected} du git et du disque...{Colors.ENDC}")
        
        if is_folder:
            if not run_command(['git', 'rm', '-rf', str(selected)]):
                return
        else:
            if not run_command(['git', 'rm', str(selected)]):
                return
        
        commit_msg = f"Delete {selected.name} — {timestamp}"
        run_command(['git', 'commit', '-m', commit_msg])
        
        print(f"{Colors.BLUE}🚀 Push des modifications...{Colors.ENDC}")
        if run_command(['git', 'push']):
            print(f"{Colors.GREEN}✅ Supprimé du git et du disque !{Colors.ENDC}")
    
    elif delete_choice == 2:
        # Supprimer du git mais garder en local
        print(f"\n{Colors.BLUE}🗑️ Suppression de {selected} du suivi git (fichier conservé localement)...{Colors.ENDC}")
        
        if is_folder:
            if not run_command(['git', 'rm', '-rf', '--cached', str(selected)]):
                return
        else:
            if not run_command(['git', 'rm', '--cached', str(selected)]):
                return
        
        commit_msg = f"Remove {selected.name} from tracking — {timestamp}"
        run_command(['git', 'commit', '-m', commit_msg])
        
        print(f"{Colors.BLUE}🚀 Push des modifications...{Colors.ENDC}")
        if run_command(['git', 'push']):
            print(f"{Colors.GREEN}✅ Supprimé du git (fichier local conservé) !{Colors.ENDC}")
    
    elif delete_choice == 3:
        # Supprimer seulement en local
        print(f"\n{Colors.BLUE}🗑️ Suppression locale de {selected}...{Colors.ENDC}")
        try:
            if is_folder:
                shutil.rmtree(selected)
            else:
                selected.unlink()
            print(f"{Colors.GREEN}✅ Supprimé du disque local !{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}❌ Erreur: {e}{Colors.ENDC}")


# ============================================================================
# GIT STATUS
# ============================================================================
def show_git_status():
    """Affiche le statut git."""
    print_header("📊 GIT STATUS")
    run_command(['git', 'status'])


# ============================================================================
# MAIN
# ============================================================================
def main():
    """Fonction principale."""
    print_header("🔧 GIT OPERATIONS MANAGER 🔧")
    print(f"{Colors.CYAN}Bienvenue! Ce programme vous aide à gérer vos opérations git.{Colors.ENDC}")
    
    while True:
        choice = print_menu("\nQue voulez-vous faire?", [
            "📥 Git Pull (récupérer les modifications)",
            "📤 Git Push (envoyer les modifications)", 
            "🗑️  Delete (supprimer fichier/dossier)",
            "📊 Git Status (voir l'état du dépôt)"
        ])
        
        if choice == 0:
            print(f"\n{Colors.GREEN}Au revoir! 👋{Colors.ENDC}")
            break
        elif choice == 1:
            git_pull()
        elif choice == 2:
            git_push()
        elif choice == 3:
            git_delete()
        elif choice == 4:
            show_git_status()


if __name__ == "__main__":
    main()
