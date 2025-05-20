"""Fonctions utilitaires pour File-Classifier."""

import hashlib
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Generator, Any

import magic
import logging

from file_classifier.file_classifier.config import get_config_value


def setup_logging(verbose: bool = False) -> None:
    """Configure le système de logging.
    
    Args:
        verbose: Si True, active le mode verbeux (DEBUG).
    """
    config = get_config_value("log_level")
    level = logging.DEBUG if verbose else getattr(logging, config, logging.INFO)
    log_file = get_config_value("log_file")
    
    # Créer le répertoire de logs s'il n'existe pas
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def get_file_type(file_path: Path) -> str:
    """Détermine le type de fichier en fonction de son extension.
    
    Args:
        file_path: Chemin vers le fichier.
        
    Returns:
        Le type de fichier (images, documents, videos, etc.) ou 'other' si non reconnu.
    """
    extension = file_path.suffix.lower()
    sort_criteria = get_config_value("sort_criteria")
    
    # Vérifier si l'extension correspond à un type connu
    for file_type, extensions in sort_criteria["type"].items():
        if extension in extensions:
            # Distinction spéciale entre text et documents
            if file_type == "documents" and extension in [".txt", ".md", ".csv", ".log"]:
                return "text"
            return file_type
    
    # Essayer de détecter le type MIME pour les fichiers sans extension reconnue
    try:
        mime_type = detect_mime_type(file_path)
        if mime_type.startswith("image/"):
            return "images"
        elif mime_type.startswith("video/"):
            return "videos"
        elif mime_type.startswith("audio/"):
            return "audio"
        elif mime_type.startswith("text/"):
            return "text"
        elif mime_type in ["application/pdf", "application/msword", 
                          "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            return "documents"
        elif mime_type in ["application/zip", "application/x-rar-compressed", 
                          "application/x-tar", "application/gzip"]:
            return "archives"
    except:
        pass
    
    return "other"


def get_file_size_category(file_path: Path) -> str:
    """Détermine la catégorie de taille d'un fichier.
    
    Args:
        file_path: Chemin vers le fichier.
        
    Returns:
        La catégorie de taille (tiny, small, medium, large, huge).
    """
    size = file_path.stat().st_size
    size_categories = get_config_value("sort_criteria")["size"]
    
    for category, max_size in sorted(size_categories.items(), key=lambda x: x[1]):
        if size < max_size:
            return category
    
    return "huge"  # Par défaut si aucune catégorie ne correspond


def get_file_date_category(file_path: Path) -> str:
    """Détermine la catégorie de date d'un fichier.
    
    Args:
        file_path: Chemin vers le fichier.
        
    Returns:
        La catégorie de date (today, this_week, this_month, this_year, older).
    """
    mtime = file_path.stat().st_mtime
    now = time.time()
    
    # Convertir en datetime pour faciliter les comparaisons de dates
    dt = datetime.fromtimestamp(mtime)
    today = datetime.fromtimestamp(now)
    
    if dt.date() == today.date():
        return "today"
    elif (today.date() - dt.date()).days <= 7:
        return "this_week"
    elif dt.year == today.year and dt.month == today.month:
        return "this_month"
    elif dt.year == today.year:
        return "this_year"
    else:
        return "older"


def calculate_file_hash(file_path: Path, block_size: int = 65536) -> str:
    """Calcule le hash SHA-256 d'un fichier.
    
    Args:
        file_path: Chemin vers le fichier.
        block_size: Taille des blocs à lire.
        
    Returns:
        Le hash SHA-256 du fichier sous forme hexadécimale.
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
        PermissionError: Si l'accès au fichier est refusé.
    """
    sha256 = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            sha256.update(block)
    
    return sha256.hexdigest()


def find_duplicate_files(directories: List[Path]) -> Dict[str, List[Path]]:
    """Trouve les fichiers en double dans les répertoires spécifiés.
    
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
                except (FileNotFoundError, PermissionError) as e:
                    logging.error(f"Erreur lors du calcul du hash de {file_path}: {e}")
    
    # Ne garder que les entrées avec des doublons
    return {h: files for h, files in hashes.items() if len(files) > 1}


def scan_files(directory: Path, recursive: bool = True) -> Generator[Path, None, None]:
    """Parcourt les fichiers d'un répertoire.
    
    Args:
        directory: Répertoire à parcourir.
        recursive: Si True, parcourt également les sous-répertoires.
        
    Yields:
        Les chemins des fichiers trouvés.
        
    Raises:
        FileNotFoundError: Si le répertoire n'existe pas.
        PermissionError: Si l'accès au répertoire est refusé.
    """
    if recursive:
        for item in directory.rglob("*"):
            yield item
    else:
        for item in directory.glob("*"):
            yield item


def safe_move(source: Path, destination: Path) -> Path:
    """Déplace un fichier en gérant les conflits de noms.
    
    Args:
        source: Chemin du fichier source.
        destination: Chemin de destination.
        
    Returns:
        Le chemin final du fichier déplacé.
        
    Raises:
        FileNotFoundError: Si le fichier source n'existe pas.
        PermissionError: Si l'accès au fichier est refusé.
    """
    # Créer le répertoire de destination s'il n'existe pas
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    # Gérer les conflits de noms
    final_destination = destination
    counter = 1
    
    while final_destination.exists():
        # Ajouter un suffixe numérique avant l'extension
        stem = destination.stem
        suffix = destination.suffix
        final_destination = destination.with_name(f"{stem}_{counter}{suffix}")
        counter += 1
    
    # Déplacer le fichier
    shutil.move(str(source), str(final_destination))
    logging.info(f"Fichier déplacé: {source} -> {final_destination}")
    
    return final_destination


def detect_mime_type(file_path: Path) -> str:
    """Détecte le type MIME d'un fichier.
    
    Args:
        file_path: Chemin vers le fichier.
        
    Returns:
        Le type MIME du fichier.
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas.
        PermissionError: Si l'accès au fichier est refusé.
    """
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(str(file_path))
    except Exception as e:
        logging.error(f"Erreur lors de la détection du type MIME de {file_path}: {e}")
        return "application/octet-stream"  # Type par défaut


def is_temp_file(file_path: Path) -> bool:
    """Détermine si un fichier est temporaire.
    
    Args:
        file_path: Chemin vers le fichier.
        
    Returns:
        True si le fichier est temporaire, False sinon.
    """
    # Motifs courants pour les fichiers temporaires
    temp_patterns = [
        "~$", ".tmp", ".temp", ".swp", ".bak", ".old", ".cache"
    ]
    
    name = file_path.name.lower()
    return any(name.endswith(pattern) or name.startswith(pattern) for pattern in temp_patterns)


def human_readable_size(size_bytes: int) -> str:
    """Convertit une taille en octets en une chaîne lisible par l'homme.
    
    Args:
        size_bytes: Taille en octets.
        
    Returns:
        Chaîne formatée (ex: "2.5 MB").
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}" 