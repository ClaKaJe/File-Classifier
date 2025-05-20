#!/usr/bin/env python3
"""Module principal de l'outil de classement de fichiers."""

import hashlib
import json
import logging
import os
import re
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

from file_classifier.file_classifier.config import get_config_value, load_config
from file_classifier.file_classifier.utils import (
    get_file_date_category,
    get_file_size_category,
    get_file_type,
    is_temp_file,
    safe_move,
    scan_files,
    calculate_file_hash,
    human_readable_size,
)


class FileManager:
    """Classe principale pour la gestion des fichiers."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialise le gestionnaire de fichiers.
        
        Args:
            config_path: Chemin vers le fichier de configuration.
        """
        self.config = load_config(config_path)
        self.db_path = Path(self.config["db_path"])
        self._ensure_db_exists()
    
    def _ensure_db_exists(self) -> None:
        """Crée la base de données si elle n'existe pas."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Créer la table des fichiers
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            path TEXT UNIQUE,
            hash TEXT,
            size INTEGER,
            mtime REAL,
            type TEXT,
            indexed_at REAL
        )
        ''')
        
        # Créer la table des actions (pour l'historique)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY,
            action_type TEXT,
            source TEXT,
            destination TEXT,
            timestamp REAL,
            metadata TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def sort_files(self, directory: Union[str, Path], criteria: str = "type", 
                  recursive: bool = False, dry_run: bool = False) -> Dict[str, List[Path]]:
        """Trie les fichiers selon le critère spécifié.
        
        Args:
            directory: Chemin du répertoire à traiter.
            criteria: Critère de tri ("type", "size", "date").
            recursive: Si True, traite également les sous-répertoires.
            dry_run: Si True, simule l'opération sans déplacer les fichiers.
            
        Returns:
            Un dictionnaire associant les catégories aux listes de fichiers.
            
        Raises:
            FileNotFoundError: Si le répertoire n'existe pas.
            ValueError: Si le critère n'est pas valide.
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Le répertoire {directory} n'existe pas.")
        
        if criteria not in ["type", "size", "date"]:
            raise ValueError(f"Critère de tri invalide: {criteria}. Valeurs acceptées: type, size, date.")
        
        result: Dict[str, List[Path]] = {}
        
        for file_path in scan_files(directory, recursive):
            if not file_path.is_file():
                continue
            
            # Déterminer la catégorie selon le critère
            if criteria == "type":
                category = get_file_type(file_path)
            elif criteria == "size":
                category = get_file_size_category(file_path)
            elif criteria == "date":
                category = get_file_date_category(file_path)
            
            # Ajouter le fichier à sa catégorie
            if category not in result:
                result[category] = []
            result[category].append(file_path)
            
            # Déplacer le fichier si ce n'est pas un dry run
            if not dry_run:
                target_dir = directory / category
                target_dir.mkdir(exist_ok=True)
                
                target_path = target_dir / file_path.name
                try:
                    safe_move(file_path, target_path)
                    
                    # Enregistrer l'action dans la base de données
                    self._record_action("move", file_path, target_path)
                except (FileNotFoundError, PermissionError) as e:
                    logging.error(f"Erreur lors du déplacement de {file_path}: {e}")
        
        return result
    
    def rename_batch(self, directory: Union[str, Path], pattern: str, replacement: str,
                    recursive: bool = False, dry_run: bool = False) -> Dict[Path, Path]:
        """Renomme des fichiers par lot selon un motif.
        
        Args:
            directory: Chemin du répertoire à traiter.
            pattern: Expression régulière pour la recherche.
            replacement: Chaîne de remplacement (peut contenir des groupes capturés).
            recursive: Si True, traite également les sous-répertoires.
            dry_run: Si True, simule l'opération sans renommer les fichiers.
            
        Returns:
            Un dictionnaire associant les anciens noms aux nouveaux noms.
            
        Raises:
            FileNotFoundError: Si le répertoire n'existe pas.
            re.error: Si l'expression régulière est invalide.
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Le répertoire {directory} n'existe pas.")
        
        try:
            regex = re.compile(pattern)
        except re.error as e:
            raise re.error(f"Expression régulière invalide: {e}")
        
        result: Dict[Path, Path] = {}
        
        for file_path in scan_files(directory, recursive):
            if not file_path.is_file():
                continue
            
            # Appliquer le motif au nom du fichier
            old_name = file_path.name
            new_name = regex.sub(replacement, old_name)
            
            # Si le nom a changé
            if new_name != old_name:
                new_path = file_path.parent / new_name
                result[file_path] = new_path
                
                # Renommer le fichier si ce n'est pas un dry run
                if not dry_run:
                    try:
                        # Gérer les conflits de noms
                        final_path = new_path
                        counter = 1
                        
                        while final_path.exists():
                            stem = new_path.stem
                            suffix = new_path.suffix
                            final_path = new_path.with_name(f"{stem}_{counter}{suffix}")
                            counter += 1
                        
                        file_path.rename(final_path)
                        logging.info(f"Fichier renommé: {file_path} -> {final_path}")
                        
                        # Enregistrer l'action dans la base de données
                        self._record_action("rename", file_path, final_path)
                    except (FileNotFoundError, PermissionError) as e:
                        logging.error(f"Erreur lors du renommage de {file_path}: {e}")
        
        return result
    
    def move_by_rules(self, directory: Union[str, Path], rules: Dict[str, str],
                     recursive: bool = False, dry_run: bool = False) -> Dict[str, List[Path]]:
        """Déplace des fichiers selon des règles prédéfinies.
        
        Args:
            directory: Chemin du répertoire à traiter.
            rules: Dictionnaire associant des motifs (regex) à des destinations.
            recursive: Si True, traite également les sous-répertoires.
            dry_run: Si True, simule l'opération sans déplacer les fichiers.
            
        Returns:
            Un dictionnaire associant les destinations aux listes de fichiers.
            
        Raises:
            FileNotFoundError: Si le répertoire n'existe pas.
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Le répertoire {directory} n'existe pas.")
        
        # Compiler les expressions régulières
        compiled_rules = []
        for pattern, dest in rules.items():
            try:
                compiled_rules.append((re.compile(pattern), dest))
            except re.error as e:
                logging.error(f"Expression régulière invalide '{pattern}': {e}")
        
        result: Dict[str, List[Path]] = {}
        
        for file_path in scan_files(directory, recursive):
            if not file_path.is_file():
                continue
            
            # Vérifier si le fichier correspond à une règle
            for regex, dest in compiled_rules:
                if regex.search(file_path.name):
                    dest_path = Path(dest)
                    
                    # Ajouter le fichier à sa destination
                    if dest not in result:
                        result[dest] = []
                    result[dest].append(file_path)
                    
                    # Déplacer le fichier si ce n'est pas un dry run
                    if not dry_run:
                        dest_path.mkdir(parents=True, exist_ok=True)
                        target_path = dest_path / file_path.name
                        
                        try:
                            safe_move(file_path, target_path)
                            
                            # Enregistrer l'action dans la base de données
                            self._record_action("move", file_path, target_path)
                        except (FileNotFoundError, PermissionError) as e:
                            logging.error(f"Erreur lors du déplacement de {file_path}: {e}")
                    
                    # On s'arrête à la première règle qui correspond
                    break
        
        return result
    
    def find_duplicates(self, directories: List[Union[str, Path]]) -> Dict[str, List[Path]]:
        """Trouve les fichiers en double dans les répertoires spécifiés.
        
        Args:
            directories: Liste des répertoires à analyser.
            
        Returns:
            Un dictionnaire avec les hashes comme clés et les listes de fichiers comme valeurs.
            
        Raises:
            FileNotFoundError: Si un répertoire n'existe pas.
        """
        dir_paths = [Path(d) for d in directories]
        
        for d in dir_paths:
            if not d.exists():
                raise FileNotFoundError(f"Le répertoire {d} n'existe pas.")
        
        return self._find_duplicates_by_content(dir_paths)
    
    def _find_duplicates_by_content(self, directories: List[Path]) -> Dict[str, List[Path]]:
        """Trouve les fichiers en double en comparant leur contenu (hash).
        
        Args:
            directories: Liste des répertoires à analyser.
            
        Returns:
            Un dictionnaire avec les hashes comme clés et les listes de fichiers comme valeurs.
        """
        hashes: Dict[str, List[Path]] = {}
        
        for directory in directories:
            for file_path in scan_files(directory):
                if file_path.is_file():
                    try:
                        file_hash = calculate_file_hash(file_path)
                        
                        if file_hash in hashes:
                            hashes[file_hash].append(file_path)
                        else:
                            hashes[file_hash] = [file_path]
                        
                        # Mettre à jour l'index
                        self._update_file_index(file_path, file_hash)
                    except (FileNotFoundError, PermissionError) as e:
                        logging.error(f"Erreur lors du calcul du hash de {file_path}: {e}")
        
        # Ne garder que les entrées avec des doublons
        return {h: files for h, files in hashes.items() if len(files) > 1}
    
    def clean_temp_files(self, directory: Union[str, Path], recursive: bool = True,
                        dry_run: bool = False) -> List[Path]:
        """Supprime les fichiers temporaires.
        
        Args:
            directory: Chemin du répertoire à traiter.
            recursive: Si True, traite également les sous-répertoires.
            dry_run: Si True, simule l'opération sans supprimer les fichiers.
            
        Returns:
            La liste des fichiers supprimés.
            
        Raises:
            FileNotFoundError: Si le répertoire n'existe pas.
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Le répertoire {directory} n'existe pas.")
        
        removed_files = []
        
        for file_path in scan_files(directory, recursive):
            if file_path.is_file() and is_temp_file(file_path):
                removed_files.append(file_path)
                
                if not dry_run:
                    try:
                        file_path.unlink()
                        logging.info(f"Fichier temporaire supprimé: {file_path}")
                        
                        # Enregistrer l'action dans la base de données
                        self._record_action("delete", file_path, None)
                    except (FileNotFoundError, PermissionError) as e:
                        logging.error(f"Erreur lors de la suppression de {file_path}: {e}")
        
        return removed_files
    
    def clean_old_files(self, directory: Union[str, Path], days: int, recursive: bool = True,
                       dry_run: bool = False) -> List[Path]:
        """Supprime les fichiers plus anciens qu'un certain nombre de jours.
        
        Args:
            directory: Chemin du répertoire à traiter.
            days: Nombre de jours.
            recursive: Si True, traite également les sous-répertoires.
            dry_run: Si True, simule l'opération sans supprimer les fichiers.
            
        Returns:
            La liste des fichiers supprimés.
            
        Raises:
            FileNotFoundError: Si le répertoire n'existe pas.
            ValueError: Si days est négatif.
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Le répertoire {directory} n'existe pas.")
        
        if days < 0:
            raise ValueError("Le nombre de jours doit être positif.")
        
        now = datetime.now().timestamp()
        threshold = now - days * 86400  # 86400 secondes = 1 jour
        
        removed_files = []
        
        for file_path in scan_files(directory, recursive):
            if file_path.is_file():
                mtime = file_path.stat().st_mtime
                
                if mtime < threshold:
                    removed_files.append(file_path)
                    
                    if not dry_run:
                        try:
                            file_path.unlink()
                            logging.info(f"Ancien fichier supprimé: {file_path}")
                            
                            # Enregistrer l'action dans la base de données
                            self._record_action("delete", file_path, None)
                        except (FileNotFoundError, PermissionError) as e:
                            logging.error(f"Erreur lors de la suppression de {file_path}: {e}")
        
        return removed_files
    
    def generate_report(self, directory: Union[str, Path], recursive: bool = True,
                       output_format: str = "text", human_readable: bool = False) -> str:
        """Génère un rapport sur les fichiers d'un répertoire.
        
        Args:
            directory: Chemin du répertoire à traiter.
            recursive: Si True, traite également les sous-répertoires.
            output_format: Format de sortie ("text" ou "json").
            human_readable: Si True et output_format est "json", inclut des tailles lisibles par l'homme.
            
        Returns:
            Le rapport généré.
            
        Raises:
            FileNotFoundError: Si le répertoire n'existe pas.
            ValueError: Si le format de sortie est invalide.
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Le répertoire {directory} n'existe pas.")
        
        if output_format not in ["text", "json"]:
            raise ValueError(f"Format de sortie invalide: {output_format}. Valeurs acceptées: text, json.")
        
        stats = {
            "total_files": 0,
            "total_size": 0,
            "by_type": {},
            "by_size": {},
            "by_date": {}
        }
        
        # Récupérer les catégories de tri depuis la configuration
        sort_criteria = get_config_value("sort_criteria")
        size_categories = sort_criteria["size"]
        
        # Initialiser les catégories de type
        type_categories = ["images", "documents", "videos", "audio", "archives", "code", "text", "other"]
        for category in type_categories:
            stats["by_type"][category] = {"count": 0, "size": 0}
        
        # Initialiser les catégories de taille dans l'ordre
        for category in sorted(size_categories.keys(), 
                              key=lambda x: size_categories[x]):
            stats["by_size"][category] = {"count": 0, "size": 0}
        
        # Initialiser les catégories de date dans un ordre chronologique
        for category in ["today", "this_week", "this_month", "this_year", "older"]:
            stats["by_date"][category] = {"count": 0, "size": 0}
        
        # Parcourir les fichiers
        for file_path in scan_files(directory, recursive):
            if file_path.is_file():
                stats["total_files"] += 1
                size = file_path.stat().st_size
                stats["total_size"] += size
                
                # Stats par type
                file_type = get_file_type(file_path)
                if file_type not in stats["by_type"]:
                    stats["by_type"][file_type] = {"count": 0, "size": 0}
                stats["by_type"][file_type]["count"] += 1
                stats["by_type"][file_type]["size"] += size
                
                # Stats par taille
                size_category = get_file_size_category(file_path)
                stats["by_size"][size_category]["count"] += 1
                stats["by_size"][size_category]["size"] += size
                
                # Stats par date
                date_category = get_file_date_category(file_path)
                stats["by_date"][date_category]["count"] += 1
                stats["by_date"][date_category]["size"] += size
        
        # Supprimer les catégories vides
        stats["by_type"] = {k: v for k, v in stats["by_type"].items() if v["count"] > 0}
        stats["by_size"] = {k: v for k, v in stats["by_size"].items() if v["count"] > 0}
        stats["by_date"] = {k: v for k, v in stats["by_date"].items() if v["count"] > 0}
        
        if output_format == "json":
            # Ajouter des tailles lisibles par l'homme si demandé
            if human_readable:
                stats["total_size_hr"] = human_readable_size(stats["total_size"])
                
                for category, type_stats in stats["by_type"].items():
                    type_stats["size_hr"] = human_readable_size(type_stats["size"])
                
                for category, size_stats in stats["by_size"].items():
                    size_stats["size_hr"] = human_readable_size(size_stats["size"])
                
                for category, date_stats in stats["by_date"].items():
                    date_stats["size_hr"] = human_readable_size(date_stats["size"])
            
            return json.dumps(stats, indent=4)
        else:
            # Format texte
            lines = [
                f"Rapport pour {directory}",
                f"Total des fichiers: {stats['total_files']}",
                f"Taille totale: {human_readable_size(stats['total_size'])}",
                "",
                "Par type:",
            ]
            
            # Trier les types par nombre de fichiers (décroissant)
            sorted_types = sorted(stats["by_type"].items(), key=lambda x: x[1]["count"], reverse=True)
            for file_type, type_stats in sorted_types:
                lines.append(f"  {file_type}: {type_stats['count']} fichiers, {human_readable_size(type_stats['size'])}")
            
            lines.append("")
            lines.append("Par taille:")
            
            # Conserver l'ordre des catégories de taille
            size_order = ["tiny", "small", "medium", "large", "huge"]
            sorted_sizes = sorted(stats["by_size"].items(), 
                                 key=lambda x: size_order.index(x[0]) if x[0] in size_order else 999)
            for size_category, size_stats in sorted_sizes:
                lines.append(f"  {size_category}: {size_stats['count']} fichiers, {human_readable_size(size_stats['size'])}")
            
            lines.append("")
            lines.append("Par date:")
            
            # Conserver l'ordre chronologique des catégories de date
            date_order = ["today", "this_week", "this_month", "this_year", "older"]
            sorted_dates = sorted(stats["by_date"].items(), 
                                 key=lambda x: date_order.index(x[0]) if x[0] in date_order else 999)
            for date_category, date_stats in sorted_dates:
                lines.append(f"  {date_category}: {date_stats['count']} fichiers, {human_readable_size(date_stats['size'])}")
            
            return "\n".join(lines)
    
    def _format_size(self, size_bytes: int) -> str:
        """Formate une taille en octets en une chaîne lisible.
        
        Args:
            size_bytes: Taille en octets.
            
        Returns:
            Chaîne formatée.
        """
        return human_readable_size(size_bytes)
    
    def _update_file_index(self, file_path: Path, file_hash: str) -> None:
        """Met à jour l'index des fichiers.
        
        Args:
            file_path: Chemin du fichier.
            file_hash: Hash du fichier.
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            stat = file_path.stat()
            cursor.execute(
                "INSERT OR REPLACE INTO files (path, hash, size, mtime, type, indexed_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    str(file_path),
                    file_hash,
                    stat.st_size,
                    stat.st_mtime,
                    get_file_type(file_path),
                    datetime.now().timestamp()
                )
            )
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erreur SQLite lors de la mise à jour de l'index: {e}")
        finally:
            conn.close()
    
    def _record_action(self, action_type: str, source: Path, destination: Optional[Path]) -> None:
        """Enregistre une action dans la base de données.
        
        Args:
            action_type: Type d'action (move, rename, delete).
            source: Chemin source.
            destination: Chemin de destination (None pour les suppressions).
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO actions (action_type, source, destination, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
                (
                    action_type,
                    str(source),
                    str(destination) if destination else None,
                    datetime.now().timestamp(),
                    None
                )
            )
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Erreur SQLite lors de l'enregistrement de l'action: {e}")
        finally:
            conn.close()
    
    def undo_last_action(self, count: Optional[int] = 1) -> bool:
        """Annule la ou les dernières actions enregistrées.
        
        Args:
            count: Nombre d'actions à annuler. Si None, annule toutes les actions.
                  Si un entier positif, annule ce nombre d'actions.
        
        Returns:
            True si au moins une annulation a réussi, False sinon.
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # Si count est None, récupérer toutes les actions
            if count is None:
                cursor.execute(
                    "SELECT COUNT(*) FROM actions"
                )
                count = cursor.fetchone()[0]
                if count == 0:
                    logging.info("Aucune action à annuler.")
                    return False
            
            # Récupérer les dernières actions, limitées par count
            cursor.execute(
                "SELECT id, action_type, source, destination FROM actions ORDER BY timestamp DESC LIMIT ?",
                (count,)
            )
            actions = cursor.fetchall()
            
            if not actions:
                logging.info("Aucune action à annuler.")
                return False
            
            success = False
            action_ids_to_delete = []
            
            # Traiter chaque action à annuler
            for action_id, action_type, source, destination in actions:
                # Annuler l'action selon son type
                if action_type == "move" or action_type == "rename":
                    # Déplacer le fichier de destination vers source
                    src_path = Path(source)
                    dest_path = Path(destination)
                    
                    if dest_path.exists() and not src_path.exists():
                        src_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(dest_path), str(src_path))
                        logging.info(f"Action annulée: {dest_path} -> {src_path}")
                        action_ids_to_delete.append(action_id)
                        success = True
                    else:
                        logging.error(f"Impossible d'annuler l'action: fichier source ou destination invalide.")
                
                elif action_type == "delete":
                    # On ne peut pas restaurer un fichier supprimé
                    logging.warning(f"Impossible d'annuler une suppression: {source}")
                    action_ids_to_delete.append(action_id)  # Quand même supprimer l'action de l'historique
            
            # Supprimer les actions annulées de l'historique
            if action_ids_to_delete:
                placeholders = ','.join('?' for _ in action_ids_to_delete)
                cursor.execute(f"DELETE FROM actions WHERE id IN ({placeholders})", action_ids_to_delete)
                conn.commit()
            
            return success
        
        except (sqlite3.Error, FileNotFoundError, PermissionError) as e:
            logging.error(f"Erreur lors de l'annulation des actions: {e}")
            return False
        
        finally:
            conn.close()
    
    def get_action_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Récupère l'historique des actions.
        
        Args:
            limit: Nombre maximum d'actions à récupérer. Si None, récupère toutes les actions.
        
        Returns:
            Une liste de dictionnaires représentant les actions, du plus récent au plus ancien.
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            if limit:
                cursor.execute(
                    "SELECT id, action_type, source, destination, timestamp FROM actions ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
            else:
                cursor.execute(
                    "SELECT id, action_type, source, destination, timestamp FROM actions ORDER BY timestamp DESC"
                )
            
            actions = []
            for action_id, action_type, source, destination, timestamp in cursor.fetchall():
                actions.append({
                    "id": action_id,
                    "type": action_type,
                    "source": source,
                    "destination": destination,
                    "timestamp": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                })
            
            return actions
            
        except sqlite3.Error as e:
            logging.error(f"Erreur lors de la récupération de l'historique: {e}")
            return []
            
        finally:
            conn.close() 