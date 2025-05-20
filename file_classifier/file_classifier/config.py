"""Module de gestion de la configuration pour File-Classifier."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Chemin par défaut pour le fichier de configuration
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "file_classifier" / "config.json"

# Configuration par défaut
DEFAULT_CONFIG = {
    "sort_criteria": {
        "type": {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
            "documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".odt"],
            "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
            "audio": [".mp3", ".wav", ".flac", ".ogg", ".aac", ".m4a"],
            "archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
            "code": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".h", ".php", ".rb"]
        },
        "size": {
            "tiny": 1024 * 1024,  # < 1MB
            "small": 10 * 1024 * 1024,  # < 10MB
            "medium": 100 * 1024 * 1024,  # < 100MB
            "large": 1024 * 1024 * 1024,  # < 1GB
            "huge": float("inf")  # >= 1GB
        }
    },
    "default_sort_criteria": "type",
    "log_level": "INFO",
    "log_file": str(Path.home() / ".local" / "share" / "file_classifier" / "logs" / "file_classifier.log"),
    "db_path": str(Path.home() / ".local" / "share" / "file_classifier" / "db" / "file_index.sqlite"),
    "use_colors": True,
    "confirm_actions": True,
    "max_undo_history": 50
}


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Charge la configuration depuis un fichier JSON.
    
    Args:
        config_path: Chemin vers le fichier de configuration. Si None, utilise le chemin par défaut.
        
    Returns:
        Un dictionnaire contenant la configuration.
        
    Raises:
        FileNotFoundError: Si le fichier de configuration n'existe pas.
        json.JSONDecodeError: Si le fichier de configuration n'est pas un JSON valide.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    
    # Si le fichier de configuration n'existe pas, créer le répertoire parent et le fichier
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        save_config(DEFAULT_CONFIG, config_path)
        return DEFAULT_CONFIG.copy()
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # Fusionner avec la configuration par défaut pour s'assurer que toutes les clés sont présentes
    merged_config = DEFAULT_CONFIG.copy()
    merged_config.update(config)
    
    return merged_config


def save_config(config: Dict[str, Any], config_path: Optional[Path] = None) -> None:
    """Sauvegarde la configuration dans un fichier JSON.
    
    Args:
        config: Dictionnaire de configuration à sauvegarder.
        config_path: Chemin vers le fichier de configuration. Si None, utilise le chemin par défaut.
        
    Raises:
        PermissionError: Si l'écriture du fichier échoue en raison de permissions insuffisantes.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    
    # Créer le répertoire parent s'il n'existe pas
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def get_config_value(key: str, config: Optional[Dict[str, Any]] = None) -> Any:
    """Récupère une valeur de configuration par sa clé.
    
    Args:
        key: Clé de configuration à récupérer.
        config: Dictionnaire de configuration. Si None, charge la configuration par défaut.
        
    Returns:
        La valeur associée à la clé, ou None si la clé n'existe pas.
    """
    if config is None:
        config = load_config()
    
    return config.get(key, None)


def set_config_value(key: str, value: Any, config_path: Optional[Path] = None) -> None:
    """Modifie une valeur de configuration et sauvegarde le fichier.
    
    Args:
        key: Clé de configuration à modifier.
        value: Nouvelle valeur à affecter.
        config_path: Chemin vers le fichier de configuration. Si None, utilise le chemin par défaut.
    """
    config = load_config(config_path)
    config[key] = value
    save_config(config, config_path) 