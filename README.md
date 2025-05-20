# File-Classifier

Outil CLI de gestion et classement de fichiers pour Linux.

## Fonctionnalités

- **Tri et classement** : trier les fichiers par type (extension), par taille ou par date de création/modification
- **Renommage par lot** : renommer plusieurs fichiers selon un motif (expressions régulières)
- **Déplacement automatique** : déplacer des fichiers selon des règles prédéfinies
- **Détection de doublons** : identifier les fichiers identiques par leur contenu
- **Nettoyage** : supprimer les fichiers temporaires ou obsolètes
- **Génération de rapports** : produire des rapports sur l'état des fichiers
- **Historique et annulation** : annuler la dernière action effectuée

## Installation

### Depuis les sources

```bash
git clone https://github.com/clakaje/file-classifier.git
cd file-classifier
pip install -e .
```

### Via pip

```bash
pip install file-classifier
```

### Exécutable autonome

Vous pouvez créer un exécutable autonome qui ne nécessite pas d'installation Python :

```bash
# Installation de PyInstaller
pip install pyinstaller

# Création de l'exécutable
pyinstaller --onefile file_classifier_entry.py --name file-classifier

# L'exécutable se trouve dans le dossier dist/
./dist/file-classifier --version
```

Pour installer l'exécutable sur votre système :

```bash
# Installation dans /usr/local/bin (nécessite les droits sudo)
sudo ./install.sh
```

## Utilisation

### Commandes principales

```
file-classifier --help                   # Afficher l'aide générale
file-classifier sort DIRECTORY           # Trier les fichiers par type
file-classifier rename DIR PATTERN REPL  # Renommer des fichiers par lot
file-classifier duplicates DIR1 [DIR2]   # Trouver les fichiers en double
file-classifier clean DIR --temp         # Supprimer les fichiers temporaires
file-classifier report DIR               # Générer un rapport sur les fichiers
file-classifier undo                     # Annuler la dernière action
```

### Exemples

#### Trier des fichiers par type

```bash
file-classifier sort ~/Downloads -r
```

Cette commande trie récursivement tous les fichiers du dossier Downloads par type (images, documents, vidéos, etc.).

#### Renommer des fichiers par lot

```bash
file-classifier rename ~/Photos "IMG_(\d+)" "Vacances_\1"
```

Cette commande renomme tous les fichiers comme "IMG_1234.jpg" en "Vacances_1234.jpg".

#### Trouver et gérer les doublons

```bash
file-classifier duplicates ~/Documents ~/Backup -o duplicates.json --json
```

Cette commande trouve les fichiers en double entre les dossiers Documents et Backup, et sauvegarde le résultat au format JSON.

#### Nettoyer les fichiers anciens

```bash
file-classifier clean ~/Downloads --old 30 -r
```

Cette commande supprime récursivement tous les fichiers de plus de 30 jours dans le dossier Downloads.

#### Générer un rapport

```bash
file-classifier report ~/Documents -r -o report.txt
```

Cette commande génère un rapport détaillé sur tous les fichiers du dossier Documents et ses sous-dossiers.

## Configuration

La configuration est stockée dans `~/.config/file_classifier/config.json`. Vous pouvez la modifier avec les commandes suivantes :

```bash
file-classifier config list              # Afficher la configuration actuelle
file-classifier config get log_level     # Afficher une valeur spécifique
file-classifier config set log_level DEBUG  # Modifier une valeur
```

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
