#!/usr/bin/env python3
"""Interface en ligne de commande pour File-Classifier."""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from file_classifier.file_classifier import __version__
from file_classifier.file_classifier.config import load_config, save_config, get_config_value, set_config_value
from file_classifier.file_classifier.core import FileManager
from file_classifier.file_classifier.utils import setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Crée le parseur d'arguments pour l'interface CLI.
    
    Returns:
        Le parseur d'arguments configuré.
    """
    parser = argparse.ArgumentParser(
        description="File-Classifier - Outil de gestion et classement de fichiers",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbeux")
    parser.add_argument("--version", action="version", version=f"File-Classifier v{__version__}")
    
    # Sous-commandes
    subparsers = parser.add_subparsers(dest="command", help="Commande à exécuter")
    
    # Commande 'sort'
    sort_parser = subparsers.add_parser("sort", help="Trier des fichiers")
    sort_parser.add_argument("directory", help="Répertoire à traiter")
    sort_parser.add_argument("-c", "--criteria", choices=["type", "size", "date"], 
                           default="type", help="Critère de tri (défaut: type)")
    sort_parser.add_argument("-r", "--recursive", action="store_true", 
                           help="Traiter les sous-répertoires")
    sort_parser.add_argument("--dry-run", action="store_true", 
                           help="Simuler l'opération sans modifier les fichiers")
    
    # Commande 'rename'
    rename_parser = subparsers.add_parser("rename", help="Renommer des fichiers par lot")
    rename_parser.add_argument("directory", help="Répertoire à traiter")
    rename_parser.add_argument("pattern", help="Expression régulière pour la recherche")
    rename_parser.add_argument("replacement", help="Chaîne de remplacement")
    rename_parser.add_argument("-r", "--recursive", action="store_true", 
                             help="Traiter les sous-répertoires")
    rename_parser.add_argument("--dry-run", action="store_true", 
                             help="Simuler l'opération sans modifier les fichiers")
    
    # Commande 'move'
    move_parser = subparsers.add_parser("move", help="Déplacer des fichiers selon des règles")
    move_parser.add_argument("directory", help="Répertoire à traiter")
    move_parser.add_argument("--rule", action="append", nargs=2, metavar=("PATTERN", "DESTINATION"),
                           help="Règle de déplacement (motif regex et destination)")
    move_parser.add_argument("-r", "--recursive", action="store_true", 
                           help="Traiter les sous-répertoires")
    move_parser.add_argument("--dry-run", action="store_true", 
                           help="Simuler l'opération sans modifier les fichiers")
    
    # Commande 'duplicates'
    dup_parser = subparsers.add_parser("duplicates", help="Trouver les fichiers en double")
    dup_parser.add_argument("directories", nargs="+", help="Répertoires à analyser")
    dup_parser.add_argument("-o", "--output", help="Fichier de sortie (défaut: stdout)")
    dup_parser.add_argument("--json", action="store_true", help="Sortie au format JSON")
    
    # Commande 'clean'
    clean_parser = subparsers.add_parser("clean", help="Nettoyer des fichiers")
    clean_parser.add_argument("directory", help="Répertoire à traiter")
    clean_parser.add_argument("--temp", action="store_true", 
                            help="Supprimer les fichiers temporaires")
    clean_parser.add_argument("--old", type=int, metavar="DAYS",
                            help="Supprimer les fichiers plus anciens que DAYS jours")
    clean_parser.add_argument("-r", "--recursive", action="store_true", 
                            help="Traiter les sous-répertoires")
    clean_parser.add_argument("--dry-run", action="store_true", 
                            help="Simuler l'opération sans modifier les fichiers")
    
    # Commande 'report'
    report_parser = subparsers.add_parser("report", help="Générer un rapport sur les fichiers")
    report_parser.add_argument("directory", help="Répertoire à analyser")
    report_parser.add_argument("-r", "--recursive", action="store_true", 
                             help="Traiter les sous-répertoires")
    report_parser.add_argument("-o", "--output", help="Fichier de sortie (défaut: stdout)")
    report_parser.add_argument("--json", action="store_true", help="Sortie au format JSON")
    
    # Commande 'config'
    config_parser = subparsers.add_parser("config", help="Gérer la configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="Action de configuration")
    
    # Sous-commande 'config get'
    config_get_parser = config_subparsers.add_parser("get", help="Obtenir une valeur de configuration")
    config_get_parser.add_argument("key", help="Clé de configuration")
    
    # Sous-commande 'config set'
    config_set_parser = config_subparsers.add_parser("set", help="Définir une valeur de configuration")
    config_set_parser.add_argument("key", help="Clé de configuration")
    config_set_parser.add_argument("value", help="Valeur à affecter")
    
    # Sous-commande 'config list'
    config_list_parser = config_subparsers.add_parser("list", help="Lister toutes les configurations")
    
    # Commande 'undo'
    undo_parser = subparsers.add_parser("undo", help="Annuler la dernière action")
    
    return parser


def handle_sort(args: argparse.Namespace) -> int:
    """Gère la commande 'sort'.
    
    Args:
        args: Arguments de la ligne de commande.
        
    Returns:
        Code de retour (0 pour succès, autre pour erreur).
    """
    try:
        manager = FileManager()
        result = manager.sort_files(
            args.directory,
            criteria=args.criteria,
            recursive=args.recursive,
            dry_run=args.dry_run
        )
        
        # Afficher les résultats
        print(f"Fichiers triés par {args.criteria}:")
        for category, files in result.items():
            print(f"  {category}: {len(files)} fichiers")
            if args.verbose:
                for file_path in files:
                    print(f"    - {file_path}")
        
        if args.dry_run:
            print("\nMode simulation: aucun fichier n'a été déplacé.")
        
        return 0
    
    except (FileNotFoundError, ValueError) as e:
        logging.error(str(e))
        return 1
    except Exception as e:
        logging.exception(f"Erreur inattendue: {e}")
        return 2


def handle_rename(args: argparse.Namespace) -> int:
    """Gère la commande 'rename'.
    
    Args:
        args: Arguments de la ligne de commande.
        
    Returns:
        Code de retour (0 pour succès, autre pour erreur).
    """
    try:
        manager = FileManager()
        result = manager.rename_batch(
            args.directory,
            args.pattern,
            args.replacement,
            recursive=args.recursive,
            dry_run=args.dry_run
        )
        
        # Afficher les résultats
        print(f"Fichiers renommés:")
        for old_path, new_path in result.items():
            print(f"  {old_path.name} -> {new_path.name}")
        
        if args.dry_run:
            print("\nMode simulation: aucun fichier n'a été renommé.")
        
        return 0
    
    except (FileNotFoundError, ValueError, Exception) as e:
        logging.error(str(e))
        return 1


def handle_move(args: argparse.Namespace) -> int:
    """Gère la commande 'move'.
    
    Args:
        args: Arguments de la ligne de commande.
        
    Returns:
        Code de retour (0 pour succès, autre pour erreur).
    """
    if not args.rule:
        logging.error("Aucune règle spécifiée. Utilisez --rule PATTERN DESTINATION.")
        return 1
    
    try:
        # Convertir les règles en dictionnaire
        rules = {pattern: dest for pattern, dest in args.rule}
        
        manager = FileManager()
        result = manager.move_by_rules(
            args.directory,
            rules,
            recursive=args.recursive,
            dry_run=args.dry_run
        )
        
        # Afficher les résultats
        print(f"Fichiers déplacés:")
        for dest, files in result.items():
            print(f"  {dest}: {len(files)} fichiers")
            if args.verbose:
                for file_path in files:
                    print(f"    - {file_path}")
        
        if args.dry_run:
            print("\nMode simulation: aucun fichier n'a été déplacé.")
        
        return 0
    
    except (FileNotFoundError, ValueError) as e:
        logging.error(str(e))
        return 1
    except Exception as e:
        logging.exception(f"Erreur inattendue: {e}")
        return 2


def handle_duplicates(args: argparse.Namespace) -> int:
    """Gère la commande 'duplicates'.
    
    Args:
        args: Arguments de la ligne de commande.
        
    Returns:
        Code de retour (0 pour succès, autre pour erreur).
    """
    try:
        manager = FileManager()
        result = manager.find_duplicates(args.directories)
        
        # Préparer la sortie
        if args.json:
            import json
            # Convertir les chemins Path en chaînes pour la sérialisation JSON
            json_result = {h: [str(p) for p in paths] for h, paths in result.items()}
            output = json.dumps(json_result, indent=4)
        else:
            lines = ["Fichiers en double:"]
            for hash_value, files in result.items():
                lines.append(f"\nGroupe (hash: {hash_value[:8]}...):")
                for file_path in files:
                    lines.append(f"  - {file_path}")
            output = "\n".join(lines)
        
        # Écrire la sortie
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Résultats écrits dans {args.output}")
        else:
            print(output)
        
        return 0
    
    except FileNotFoundError as e:
        logging.error(str(e))
        return 1
    except Exception as e:
        logging.exception(f"Erreur inattendue: {e}")
        return 2


def handle_clean(args: argparse.Namespace) -> int:
    """Gère la commande 'clean'.
    
    Args:
        args: Arguments de la ligne de commande.
        
    Returns:
        Code de retour (0 pour succès, autre pour erreur).
    """
    if not args.temp and args.old is None:
        logging.error("Aucune action de nettoyage spécifiée. Utilisez --temp ou --old.")
        return 1
    
    try:
        manager = FileManager()
        removed_files = []
        
        if args.temp:
            temp_files = manager.clean_temp_files(
                args.directory,
                recursive=args.recursive,
                dry_run=args.dry_run
            )
            removed_files.extend(temp_files)
            print(f"Fichiers temporaires: {len(temp_files)} fichiers à supprimer")
        
        if args.old is not None:
            old_files = manager.clean_old_files(
                args.directory,
                days=args.old,
                recursive=args.recursive,
                dry_run=args.dry_run
            )
            removed_files.extend(old_files)
            print(f"Fichiers anciens (>{args.old} jours): {len(old_files)} fichiers à supprimer")
        
        if args.verbose:
            for file_path in removed_files:
                print(f"  - {file_path}")
        
        if args.dry_run:
            print("\nMode simulation: aucun fichier n'a été supprimé.")
        
        return 0
    
    except (FileNotFoundError, ValueError) as e:
        logging.error(str(e))
        return 1
    except Exception as e:
        logging.exception(f"Erreur inattendue: {e}")
        return 2


def handle_report(args: argparse.Namespace) -> int:
    """Gère la commande 'report'.
    
    Args:
        args: Arguments de la ligne de commande.
        
    Returns:
        Code de retour (0 pour succès, autre pour erreur).
    """
    try:
        manager = FileManager()
        output_format = "json" if args.json else "text"
        report = manager.generate_report(
            args.directory,
            recursive=args.recursive,
            output_format=output_format
        )
        
        # Écrire la sortie
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"Rapport écrit dans {args.output}")
        else:
            print(report)
        
        return 0
    
    except (FileNotFoundError, ValueError) as e:
        logging.error(str(e))
        return 1
    except Exception as e:
        logging.exception(f"Erreur inattendue: {e}")
        return 2


def handle_config(args: argparse.Namespace) -> int:
    """Gère la commande 'config'.
    
    Args:
        args: Arguments de la ligne de commande.
        
    Returns:
        Code de retour (0 pour succès, autre pour erreur).
    """
    try:
        if args.config_command == "get":
            value = get_config_value(args.key)
            if value is None:
                print(f"La clé '{args.key}' n'existe pas dans la configuration.")
                return 1
            print(f"{args.key} = {value}")
        
        elif args.config_command == "set":
            # Tenter de convertir la valeur en type approprié
            try:
                if args.value.lower() == "true":
                    value = True
                elif args.value.lower() == "false":
                    value = False
                elif args.value.isdigit():
                    value = int(args.value)
                elif args.value.replace(".", "", 1).isdigit():
                    value = float(args.value)
                else:
                    value = args.value
            except:
                value = args.value
            
            set_config_value(args.key, value)
            print(f"Configuration mise à jour: {args.key} = {value}")
        
        elif args.config_command == "list":
            config = load_config()
            import json
            print(json.dumps(config, indent=4))
        
        else:
            print("Commande de configuration non reconnue.")
            return 1
        
        return 0
    
    except Exception as e:
        logging.exception(f"Erreur lors de la gestion de la configuration: {e}")
        return 2


def handle_undo(args: argparse.Namespace) -> int:
    """Gère la commande 'undo'.
    
    Args:
        args: Arguments de la ligne de commande.
        
    Returns:
        Code de retour (0 pour succès, autre pour erreur).
    """
    try:
        manager = FileManager()
        success = manager.undo_last_action()
        
        if success:
            print("Dernière action annulée avec succès.")
            return 0
        else:
            print("Impossible d'annuler la dernière action.")
            return 1
    
    except Exception as e:
        logging.exception(f"Erreur lors de l'annulation: {e}")
        return 2


def main() -> int:
    """Point d'entrée principal du programme.
    
    Returns:
        Code de retour (0 pour succès, autre pour erreur).
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Configurer le logging
    setup_logging(args.verbose)
    
    # Si aucune commande n'est spécifiée, afficher l'aide
    if not args.command:
        parser.print_help()
        return 0
    
    # Dispatcher vers la fonction appropriée
    handlers = {
        "sort": handle_sort,
        "rename": handle_rename,
        "move": handle_move,
        "duplicates": handle_duplicates,
        "clean": handle_clean,
        "report": handle_report,
        "config": handle_config,
        "undo": handle_undo,
    }
    
    handler = handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        logging.error(f"Commande non reconnue: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 