#!/usr/bin/env python3
"""
Automatic Git Conflict Resolution Script

This script helps you resolve git merge conflicts by prompting for each conflicted file.
It provides options to keep local changes, remote changes, or manually edit the file.
"""

import subprocess
import sys
import os

def run_git_command(command):
    """Execute a git command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def get_conflicted_files():
    """Get list of files with merge conflicts"""
    output = run_git_command("git diff --name-only --diff-filter=U")
    if output:
        return output.split('\n')
    return []

def show_file_conflict(filepath):
    """Show the conflict in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n{'='*60}")
        print(f"CONFLICT IN: {filepath}")
        print('='*60)
        
        lines = content.split('\n')
        conflict_start = None
        
        for i, line in enumerate(lines):
            if line.startswith('<<<<<<<'):
                conflict_start = i
                print(f"\n🔴 LOCAL CHANGES (yours):")
            elif line.startswith('======='):
                print(f"\n🔵 REMOTE CHANGES (theirs):")
            elif line.startswith('>>>>>>>'):
                print(f"\n{'='*40}")
                break
            elif conflict_start is not None:
                print(f"{i+1:4d}: {line}")
        
        return True
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return False

def resolve_file_conflict(filepath):
    """Resolve conflict for a single file"""
    while True:
        print(f"\nHow do you want to resolve '{filepath}'?")
        print("1. Keep LOCAL changes (yours)")
        print("2. Keep REMOTE changes (theirs)")
        print("3. Open file for MANUAL editing")
        print("4. Show conflict again")
        print("5. Skip this file (resolve later)")
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            # Keep local version
            if run_git_command(f"git checkout --ours '{filepath}'"):
                print(f"✅ Kept LOCAL version of {filepath}")
                return 'resolved'
            else:
                print(f"❌ Failed to resolve {filepath}")
                return 'failed'
        
        elif choice == '2':
            # Keep remote version
            if run_git_command(f"git checkout --theirs '{filepath}'"):
                print(f"✅ Kept REMOTE version of {filepath}")
                return 'resolved'
            else:
                print(f"❌ Failed to resolve {filepath}")
                return 'failed'
        
        elif choice == '3':
            # Open for manual editing
            print(f"\n📝 Opening {filepath} for manual editing...")
            print("After editing, save the file and remove all conflict markers:")
            print("  - <<<<<<< HEAD")
            print("  - =======")
            print("  - >>>>>>> branch_name")
            
            # Try different editors
            editors = ['code', 'notepad', 'nano', 'vim']
            opened = False
            
            for editor in editors:
                try:
                    subprocess.run([editor, filepath], check=True)
                    opened = True
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            if not opened:
                print(f"Could not open editor. Please manually edit: {filepath}")
            
            input("Press Enter after you've saved your changes...")
            
            # Check if conflict markers are still present
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if any(marker in content for marker in ['<<<<<<<', '=======', '>>>>>>>']):
                    print("⚠️  Warning: Conflict markers still found in the file!")
                    print("Please remove all <<<<<<, =======, and >>>>>>> lines")
                    continue
                else:
                    print(f"✅ Manual resolution completed for {filepath}")
                    return 'resolved'
            except Exception as e:
                print(f"Error checking file: {e}")
                return 'failed'
        
        elif choice == '4':
            # Show conflict again
            show_file_conflict(filepath)
            continue
        
        elif choice == '5':
            # Skip file
            print(f"⏭️  Skipped {filepath}")
            return 'skipped'
        
        else:
            print("❌ Invalid choice. Please enter 1-5.")

def main():
    """Main function to resolve all conflicts"""
    print("🔧 Git Conflict Resolution Tool")
    print("="*40)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository!")
        sys.exit(1)
    
    # Check git status
    status = run_git_command("git status --porcelain")
    if not status:
        print("✅ No conflicts detected!")
        return
    
    # Get conflicted files
    conflicted_files = get_conflicted_files()
    
    if not conflicted_files:
        print("✅ No merge conflicts found!")
        return
    
    print(f"📋 Found {len(conflicted_files)} conflicted files:")
    for i, file in enumerate(conflicted_files, 1):
        print(f"  {i}. {file}")
    
    resolved_files = []
    skipped_files = []
    failed_files = []
    
    # Process each file
    for filepath in conflicted_files:
        if not os.path.exists(filepath):
            print(f"⚠️  File {filepath} not found, skipping...")
            continue
        
        # Show the conflict
        if show_file_conflict(filepath):
            result = resolve_file_conflict(filepath)
            
            if result == 'resolved':
                # Add resolved file to staging
                run_git_command(f"git add '{filepath}'")
                resolved_files.append(filepath)
            elif result == 'skipped':
                skipped_files.append(filepath)
            else:
                failed_files.append(filepath)
        else:
            failed_files.append(filepath)
    
    # Summary
    print(f"\n📊 RESOLUTION SUMMARY:")
    print(f"✅ Resolved: {len(resolved_files)}")
    print(f"⏭️  Skipped: {len(skipped_files)}")
    print(f"❌ Failed: {len(failed_files)}")
    
    if resolved_files:
        print(f"\n✅ Resolved files:")
        for f in resolved_files:
            print(f"  - {f}")
    
    if skipped_files:
        print(f"\n⏭️  Skipped files (resolve manually):")
        for f in skipped_files:
            print(f"  - {f}")
    
    if failed_files:
        print(f"\n❌ Failed files:")
        for f in failed_files:
            print(f"  - {f}")
    
    # Offer to commit if all conflicts resolved
    if resolved_files and not skipped_files and not failed_files:
        commit = input("\n🎉 All conflicts resolved! Commit changes? (y/n): ").lower()
        if commit in ['y', 'yes']:
            message = input("Commit message (default: 'Resolve merge conflicts'): ").strip()
            if not message:
                message = "Resolve merge conflicts"
            
            if run_git_command(f"git commit -m '{message}'"):
                print("✅ Changes committed successfully!")
            else:
                print("❌ Failed to commit changes")
        else:
            print("📝 You can commit manually with: git commit -m 'Resolve merge conflicts'")
    
    elif resolved_files:
        print("\n📝 Some conflicts resolved. You can:")
        print("  1. Resolve remaining conflicts manually")
        print("  2. Run this script again")
        print("  3. Commit with: git commit -m 'Resolve merge conflicts'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)