#!/usr/bin/env python3
"""
moveme.py - Script interactif pour déplacer des fichiers vers un dossier spécifique
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


class Colors:
    """Codes couleur ANSI pour le terminal"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class GoBack(Exception):
    """Exception levée quand l'utilisateur veut revenir à l'étape précédente"""
    pass


def print_header():
    """Affiche l'en-tête du script"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}       📁 MOVEME - Transfert de Fichiers{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.WHITE}   'q' = quitter  |  'b' = étape précédente{Colors.RESET}\n")


def search_file(filename: str, start_path: str = ".") -> list:
    """Recherche un fichier dans le répertoire et ses sous-dossiers"""
    matches = []
    for root, dirs, files in os.walk(start_path):
        # Ignorer certains dossiers
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'nut_venv', 'oev_env', 'python_env', 'renv']]
        for file in files:
            if filename.lower() in file.lower():
                full_path = os.path.join(root, file)
                matches.append(full_path)
    return matches


def search_folder(foldername: str, start_path: str = ".") -> list:
    """Recherche un dossier dans le répertoire"""
    matches = []
    for root, dirs, files in os.walk(start_path):
        # Ignorer certains dossiers
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv', 'nut_venv', 'oev_env', 'python_env', 'renv']]
        for dir_name in dirs:
            if foldername.lower() in dir_name.lower():
                full_path = os.path.join(root, dir_name)
                matches.append(full_path)
    return matches


def get_file_info(filepath: str) -> str:
    """Retourne les informations sur un fichier"""
    try:
        stat = os.stat(filepath)
        size = stat.st_size
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size/1024:.1f} KB"
        else:
            size_str = f"{size/(1024*1024):.1f} MB"
        
        return f"{size_str}, modifié le {modified}"
    except:
        return "Info non disponible"


def select_from_list(items: list, item_type: str = "élément", allow_multiple: bool = False, allow_back: bool = True) -> list:
    """Permet à l'utilisateur de sélectionner un ou plusieurs éléments d'une liste"""
    if not items:
        return []
    
    if len(items) == 1 and not allow_multiple:
        return [items[0]]
    
    print(f"\n{Colors.YELLOW}Plusieurs {item_type}s trouvés:{Colors.RESET}")
    for i, item in enumerate(items, 1):
        if os.path.isfile(item):
            info = get_file_info(item)
            print(f"  {Colors.CYAN}{i}.{Colors.RESET} {item} ({info})")
        else:
            print(f"  {Colors.CYAN}{i}.{Colors.RESET} {item}")
    
    if allow_multiple:
        print(f"\n{Colors.WHITE}💡 Astuce: Entrez plusieurs numéros séparés par des virgules (ex: 1, 2, 3){Colors.RESET}")
        print(f"{Colors.WHITE}   Ou tapez 'all' pour tout sélectionner{Colors.RESET}")
    
    while True:
        try:
            if allow_multiple:
                choice = input(f"\n{Colors.GREEN}Sélectionnez (1-{len(items)}), 'b'=retour, 'q'=quitter: {Colors.RESET}")
            else:
                choice = input(f"\n{Colors.GREEN}Sélectionnez (1-{len(items)}), 'b'=retour, 'q'=quitter: {Colors.RESET}")
            
            if choice.lower() in ['q', 'quit', 'exit', 'annuler']:
                print(f"\n{Colors.YELLOW}⚠️ Opération annulée par l'utilisateur.{Colors.RESET}")
                exit(0)
            
            if allow_back and choice.lower() in ['b', 'back', 'retour', 'précédent']:
                raise GoBack()
            
            # Sélectionner tout
            if allow_multiple and choice.lower() in ['all', 'tout', '*']:
                return items.copy()
            
            # Gérer la sélection multiple (1, 2, 3, 4)
            if ',' in choice:
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                selected = []
                for idx in indices:
                    if 0 <= idx < len(items):
                        selected.append(items[idx])
                    else:
                        print(f"{Colors.RED}Numéro {idx + 1} invalide, ignoré.{Colors.RESET}")
                if selected:
                    return selected
                print(f"{Colors.RED}Aucune sélection valide.{Colors.RESET}")
            else:
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    return [items[idx]]
                print(f"{Colors.RED}Numéro invalide.{Colors.RESET}")
        except ValueError:
            print(f"{Colors.RED}Veuillez entrer un numéro valide.{Colors.RESET}")


def confirm(message: str, allow_back: bool = True) -> bool:
    """Demande une confirmation à l'utilisateur"""
    response = input(f"{Colors.YELLOW}{message} (o/n/b/q): {Colors.RESET}").strip().lower()
    if response in ['q', 'quit', 'exit', 'annuler']:
        print(f"\n{Colors.YELLOW}⚠️ Opération annulée par l'utilisateur.{Colors.RESET}")
        exit(0)
    if allow_back and response in ['b', 'back', 'retour', 'précédent']:
        raise GoBack()
    return response in ['o', 'oui', 'y', 'yes']


def get_input(prompt: str, allow_back: bool = True) -> str:
    """Demande une entrée à l'utilisateur avec option d'annulation et retour"""
    response = input(prompt).strip()
    if response.lower() in ['q', 'quit', 'exit', 'annuler']:
        print(f"\n{Colors.YELLOW}⚠️ Opération annulée par l'utilisateur.{Colors.RESET}")
        exit(0)
    if allow_back and response.lower() in ['b', 'back', 'retour', 'précédent']:
        raise GoBack()
    return response


def main():
    print_header()
    
    # État du workflow
    step = 1
    state = {
        'filename': None,
        'found_files': [],
        'selected_files': [],
        'foldername': None,
        'dest_folder': None
    }
    
    while True:
        try:
            if step == 1:
                # ÉTAPE 1: Demander le nom du fichier
                print(f"\n{Colors.BOLD}📄 ÉTAPE 1: Fichier(s) à transférer{Colors.RESET}")
                state['filename'] = get_input(f"{Colors.GREEN}Entrez le nom du fichier (ou partie du nom): {Colors.RESET}", allow_back=False)
                
                if not state['filename']:
                    print(f"{Colors.RED}❌ Aucun fichier spécifié.{Colors.RESET}")
                    continue
                
                # Rechercher le fichier
                print(f"\n{Colors.CYAN}🔍 Recherche de '{state['filename']}'...{Colors.RESET}")
                state['found_files'] = search_file(state['filename'])
                
                if not state['found_files']:
                    print(f"{Colors.RED}❌ Aucun fichier correspondant à '{state['filename']}' trouvé.{Colors.RESET}")
                    continue
                
                step = 2
                
            elif step == 2:
                # ÉTAPE 2: Sélectionner le(s) fichier(s)
                print(f"\n{Colors.BOLD}📄 ÉTAPE 2: Sélection des fichiers{Colors.RESET}")
                state['selected_files'] = select_from_list(state['found_files'], "fichier", allow_multiple=True)
                
                if not state['selected_files']:
                    print(f"{Colors.YELLOW}⚠️ Aucun fichier sélectionné.{Colors.RESET}")
                    step = 1
                    continue
                
                if len(state['selected_files']) == 1:
                    print(f"\n{Colors.GREEN}✓ Fichier sélectionné: {Colors.BOLD}{state['selected_files'][0]}{Colors.RESET}")
                else:
                    print(f"\n{Colors.GREEN}✓ {len(state['selected_files'])} fichiers sélectionnés:{Colors.RESET}")
                    for f in state['selected_files']:
                        print(f"  {Colors.CYAN}•{Colors.RESET} {f}")
                
                step = 3
                
            elif step == 3:
                # ÉTAPE 3: Demander le dossier de destination
                print(f"\n{Colors.BOLD}📁 ÉTAPE 3: Dossier de destination{Colors.RESET}")
                state['foldername'] = get_input(f"{Colors.GREEN}Entrez le nom du dossier de destination: {Colors.RESET}")
                
                if not state['foldername']:
                    print(f"{Colors.RED}❌ Aucun dossier spécifié.{Colors.RESET}")
                    continue
                
                # Rechercher le dossier
                print(f"\n{Colors.CYAN}🔍 Recherche du dossier '{state['foldername']}'...{Colors.RESET}")
                found_folders = search_folder(state['foldername'])
                
                state['dest_folder'] = None
                
                if found_folders:
                    print(f"{Colors.GREEN}✓ Dossier(s) trouvé(s):{Colors.RESET}")
                    selected_folders = select_from_list(found_folders, "dossier", allow_multiple=False)
                    state['dest_folder'] = selected_folders[0] if selected_folders else None
                
                if not state['dest_folder']:
                    # Le dossier n'existe pas, proposer de le créer
                    print(f"\n{Colors.YELLOW}⚠️ Aucun dossier '{state['foldername']}' trouvé.{Colors.RESET}")
                    
                    # Proposer des emplacements de création
                    print(f"\n{Colors.CYAN}Où voulez-vous créer le dossier?{Colors.RESET}")
                    print(f"  {Colors.CYAN}1.{Colors.RESET} À la racine du projet (./{state['foldername']})")
                    print(f"  {Colors.CYAN}2.{Colors.RESET} Dans outputs/ (outputs/{state['foldername']})")
                    print(f"  {Colors.CYAN}3.{Colors.RESET} Spécifier un chemin personnalisé")
                    print(f"  {Colors.CYAN}4.{Colors.RESET} Annuler")
                    
                    choice = get_input(f"\n{Colors.GREEN}Votre choix (1-4): {Colors.RESET}")
                    
                    if choice == '1':
                        state['dest_folder'] = f"./{state['foldername']}"
                    elif choice == '2':
                        state['dest_folder'] = f"outputs/{state['foldername']}"
                    elif choice == '3':
                        custom_path = get_input(f"{Colors.GREEN}Entrez le chemin complet: {Colors.RESET}")
                        state['dest_folder'] = custom_path
                    else:
                        continue
                    
                    # Créer le dossier
                    if not os.path.exists(state['dest_folder']):
                        if confirm(f"Créer le dossier '{state['dest_folder']}'?"):
                            try:
                                os.makedirs(state['dest_folder'], exist_ok=True)
                                print(f"{Colors.GREEN}✓ Dossier créé: {state['dest_folder']}{Colors.RESET}")
                            except Exception as e:
                                print(f"{Colors.RED}❌ Erreur lors de la création du dossier: {e}{Colors.RESET}")
                                continue
                        else:
                            continue
                
                step = 4
                
            elif step == 4:
                # ÉTAPE 4: Confirmation du chemin
                state['dest_folder'] = os.path.abspath(state['dest_folder'])
                print(f"\n{Colors.BOLD}📍 ÉTAPE 4: Confirmation du chemin{Colors.RESET}")
                print(f"  {Colors.CYAN}Destination:{Colors.RESET} {state['dest_folder']}")
                
                if len(state['selected_files']) == 1:
                    print(f"  {Colors.CYAN}Source:{Colors.RESET}      {os.path.abspath(state['selected_files'][0])}")
                    dest_file = os.path.join(state['dest_folder'], os.path.basename(state['selected_files'][0]))
                    print(f"  {Colors.CYAN}Résultat:{Colors.RESET}    {dest_file}")
                else:
                    print(f"\n  {Colors.CYAN}Fichiers à transférer ({len(state['selected_files'])}):{Colors.RESET}")
                    for f in state['selected_files']:
                        print(f"    {Colors.WHITE}•{Colors.RESET} {os.path.basename(f)}")
                
                # Vérifier les fichiers existants
                existing_files = []
                for f in state['selected_files']:
                    dest_file = os.path.join(state['dest_folder'], os.path.basename(f))
                    if os.path.exists(dest_file):
                        existing_files.append(os.path.basename(f))
                
                if existing_files:
                    print(f"\n{Colors.YELLOW}⚠️ {len(existing_files)} fichier(s) existe(nt) déjà à cette destination:{Colors.RESET}")
                    for f in existing_files:
                        print(f"    {Colors.YELLOW}•{Colors.RESET} {f}")
                    if not confirm("Voulez-vous les remplacer?"):
                        step = 3
                        continue
                
                step = 5
                
            elif step == 5:
                # ÉTAPE 5: Confirmation finale et transfert
                print(f"\n{Colors.BOLD}🚀 ÉTAPE 5: Confirmation du transfert{Colors.RESET}")
                if len(state['selected_files']) == 1:
                    if not confirm("Confirmer le transfert?"):
                        step = 4
                        continue
                else:
                    if not confirm(f"Confirmer le transfert de {len(state['selected_files'])} fichiers?"):
                        step = 4
                        continue
                
                # Effectuer le(s) transfert(s)
                success_count = 0
                error_count = 0
                
                for selected_file in state['selected_files']:
                    dest_file = os.path.join(state['dest_folder'], os.path.basename(selected_file))
                    try:
                        shutil.move(selected_file, dest_file)
                        success_count += 1
                        print(f"  {Colors.GREEN}✓{Colors.RESET} {os.path.basename(selected_file)}")
                    except Exception as e:
                        error_count += 1
                        print(f"  {Colors.RED}✗{Colors.RESET} {os.path.basename(selected_file)} - {e}")
                
                # Résumé
                print(f"\n{Colors.GREEN}{'='*60}{Colors.RESET}")
                if error_count == 0:
                    print(f"{Colors.GREEN}✅ TRANSFERT RÉUSSI!{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}⚠️ TRANSFERT PARTIEL{Colors.RESET}")
                print(f"{Colors.GREEN}{'='*60}{Colors.RESET}")
                print(f"  {Colors.CYAN}Réussis:{Colors.RESET}  {success_count}")
                if error_count > 0:
                    print(f"  {Colors.RED}Échecs:{Colors.RESET}   {error_count}")
                print(f"  {Colors.CYAN}Vers:{Colors.RESET}     {state['dest_folder']}")
                
                # Demander si on veut transférer un autre fichier
                print()
                if confirm("Transférer un autre fichier?", allow_back=False):
                    step = 1
                    state = {'filename': None, 'found_files': [], 'selected_files': [], 'foldername': None, 'dest_folder': None}
                else:
                    break
                    
        except GoBack:
            if step > 1:
                step -= 1
                print(f"\n{Colors.BLUE}⬅️ Retour à l'étape précédente...{Colors.RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Opération annulée par l'utilisateur.{Colors.RESET}")
