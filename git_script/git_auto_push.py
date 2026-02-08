#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatise les opérations Git : add, commit, push.

Usage :
    python git_auto_push.py [message du commit] [path]

Exemple :
    python git_auto_push.py "Mise à jour du dashboard M&E" .
    python git_auto_push.py  # Utilise un message par défaut avec la date
"""

import subprocess
import sys
from datetime import datetime

def run_command(command: list):
    """Exécute une commande shell et gère les erreurs."""
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        if result.stdout.strip():
            print(result.stdout)
        # Afficher les warnings mais ne pas les traiter comme des erreurs
        if result.stderr.strip():
            # Filtrer les warnings LF/CRLF qui ne sont pas des erreurs critiques
            stderr_lines = result.stderr.strip().split('\n')
            critical_errors = [line for line in stderr_lines if not line.startswith('warning:')]
            if critical_errors:
                print('\n'.join(critical_errors))
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de : {' '.join(command)}")
        if e.stderr:
            print(e.stderr)
        sys.exit(1)

def main():
    # Date du jour pour le message par défaut
    today = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Vérification des arguments
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        # Message par défaut avec la date du jour
        commit_message = f"Mise à jour automatique du {today}"
        print(f"💬 Aucun message fourni, utilisation du message par défaut : {commit_message}")
    else:
        commit_message = sys.argv[1]

    path = sys.argv[2] if len(sys.argv) > 2 else "."

    # Vérifier s'il y a des changements à commiter
    try:
        result = subprocess.run(["git", "status", "--porcelain"], 
                              check=True, text=True, capture_output=True)
        if not result.stdout.strip():
            print("ℹ️ Aucun changement détecté, rien à commiter.")
            return
    except subprocess.CalledProcessError:
        print("❌ Erreur lors de la vérification du statut Git")
        sys.exit(1)

    # Étapes Git
    print("📦 Ajout des fichiers au staging area...")
    run_command(["git", "add", path])

    print(f"📝 Commit avec le message : {commit_message}")
    full_message = f"{commit_message} — {timestamp}"
    run_command(["git", "commit", "-m", full_message])

    print("🚀 Envoi vers le dépôt distant (git push)...")
    run_command(["git", "push"])

    print("✅ Synchronisation terminée avec succès !")

if __name__ == "__main__":
    main()

