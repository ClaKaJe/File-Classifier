% FILE-CLASSIFIER(1) Version 0.1.0 | File-Classifier Documentation

# NAME

file-classifier - Outil CLI de gestion et classement de fichiers

# SYNOPSIS

**file-classifier** [*OPTIONS*] _COMMAND_ [*ARGS*]

# DESCRIPTION

File-Classifier est un outil en ligne de commande pour la gestion et le classement de fichiers. Il permet de trier, renommer, déplacer et analyser des fichiers selon différents critères.

# OPTIONS

**-v, --verbose**
: Active le mode verbeux.

**--version**
: Affiche la version du programme et quitte.

# COMMANDS

## sort

**file-classifier sort** _DIRECTORY_ [*OPTIONS*]

Trie les fichiers du répertoire spécifié selon un critère donné.

### Options

**-c, --criteria** _CRITERIA_
: Critère de tri (type, size, date). Par défaut: type.

**-r, --recursive**
: Traite également les sous-répertoires.

**--dry-run**
: Simule l'opération sans modifier les fichiers.

## rename

**file-classifier rename** _DIRECTORY_ _PATTERN_ _REPLACEMENT_ [*OPTIONS*]

Renomme des fichiers par lot selon un motif d'expression régulière.

### Options

**-r, --recursive**
: Traite également les sous-répertoires.

**--dry-run**
: Simule l'opération sans modifier les fichiers.

## move

**file-classifier move** _DIRECTORY_ [*OPTIONS*]

Déplace des fichiers selon des règles prédéfinies.

### Options

**--rule** _PATTERN_ _DESTINATION_
: Règle de déplacement (motif regex et destination). Peut être spécifiée plusieurs fois.

**-r, --recursive**
: Traite également les sous-répertoires.

**--dry-run**
: Simule l'opération sans modifier les fichiers.

## duplicates

**file-classifier duplicates** _DIRECTORIES..._ [*OPTIONS*]

Trouve les fichiers en double dans les répertoires spécifiés.

### Options

**-o, --output** _FILE_
: Fichier de sortie (défaut: stdout).

**--json**
: Sortie au format JSON.

## clean

**file-classifier clean** _DIRECTORY_ [*OPTIONS*]

Nettoie des fichiers selon différents critères.

### Options

**--temp**
: Supprime les fichiers temporaires.

**--old** _DAYS_
: Supprime les fichiers plus anciens que DAYS jours.

**-r, --recursive**
: Traite également les sous-répertoires.

**--dry-run**
: Simule l'opération sans modifier les fichiers.

## report

**file-classifier report** _DIRECTORY_ [*OPTIONS*]

Génère un rapport sur les fichiers d'un répertoire, incluant le nombre de fichiers, la taille totale, et des statistiques par type, taille et date.

### Options

**-r, --recursive**
: Traite également les sous-répertoires.

**-o, --output** _FILE_
: Fichier de sortie (défaut: stdout).

**--json**
: Sortie au format JSON.

**--human-readable**
: Inclut des tailles lisibles par l'homme dans la sortie JSON (ex: "5.2 MB" au lieu de 5242880).

## config

**file-classifier config** _SUBCOMMAND_ [*ARGS*]

Gère la configuration de l'outil.

### Sous-commandes

**get** _KEY_
: Obtient la valeur d'une clé de configuration.

**set** _KEY_ _VALUE_
: Définit la valeur d'une clé de configuration.

**list**
: Liste toutes les configurations.

## undo

**file-classifier undo** [*OPTIONS*]

Annule une ou plusieurs actions précédentes (déplacements, renommages).

### Options

**-c, --count** _N_
: Annule les N dernières actions (par défaut: 1).

**-a, --all**
: Annule toutes les actions enregistrées.

## history

**file-classifier history** [*OPTIONS*]

Affiche l'historique des actions effectuées.

### Options

**-c, --count** _N_
: Limite le nombre d'actions affichées.

**-j, --json**
: Sortie au format JSON.

# EXEMPLES

Trier les fichiers par type dans le répertoire Downloads:

```
file-classifier sort ~/Downloads
```

Renommer tous les fichiers commençant par "IMG*" en "Photo*":

```
file-classifier rename ~/Photos "IMG_(\d+)" "Photo_\1"
```

Trouver les fichiers en double entre deux répertoires:

```
file-classifier duplicates ~/Documents ~/Backup
```

Supprimer les fichiers temporaires:

```
file-classifier clean ~/Downloads --temp
```

# FICHIERS

_~/.config/file_classifier/config.json_
: Fichier de configuration principal.

_~/.local/share/file_classifier/logs/file_classifier.log_
: Fichier de logs par défaut.

_~/.local/share/file_classifier/db/file_index.sqlite_
: Base de données d'indexation des fichiers.

# AUTEUR

File-Classifier a été écrit par l'équipe de développement File-Classifier.

# BOGUES

Signaler les bugs à <https://github.com/clakaje/file-classifier/issues>

# COPYRIGHT

Copyright © 2025 File-Classifier. Licence MIT.

# VOIR AUSSI

**find**(1), **sort**(1), **mv**(1), **rm**(1)
