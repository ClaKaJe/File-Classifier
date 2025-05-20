# Exemple : Tri de fichiers par type

Cet exemple montre comment utiliser File-Classifier pour trier des fichiers par type dans un répertoire.

## Scénario

Vous avez un répertoire `~/Downloads` contenant des fichiers de différents types (images, documents, vidéos, etc.) et vous souhaitez les organiser automatiquement dans des sous-répertoires selon leur type.

## Commande simple

Pour trier les fichiers par type dans le répertoire courant :

```bash
file-classifier sort ~/Downloads
```

Cette commande va :

1. Analyser tous les fichiers du répertoire `~/Downloads`
2. Créer des sous-répertoires pour chaque type de fichier (images, documents, videos, etc.)
3. Déplacer les fichiers dans les sous-répertoires correspondants

## Options avancées

### Tri récursif

Pour trier également les fichiers dans les sous-répertoires :

```bash
file-classifier sort ~/Downloads -r
```

### Mode simulation

Pour voir ce qui serait fait sans réellement déplacer les fichiers :

```bash
file-classifier sort ~/Downloads --dry-run
```

### Mode verbeux

Pour afficher des informations détaillées sur chaque fichier traité :

```bash
file-classifier sort ~/Downloads -v
```

## Résultat

Après l'exécution de la commande, votre répertoire `~/Downloads` sera organisé comme suit :

```
~/Downloads/
├── images/
│   ├── photo1.jpg
│   ├── screenshot.png
│   └── ...
├── documents/
│   ├── rapport.pdf
│   ├── lettre.docx
│   └── ...
├── videos/
│   ├── video1.mp4
│   ├── film.mkv
│   └── ...
├── audio/
│   ├── musique.mp3
│   └── ...
└── other/
    └── ... (fichiers non reconnus)
```

## Critères de tri alternatifs

Vous pouvez également trier les fichiers par taille ou par date :

```bash
# Tri par taille
file-classifier sort ~/Downloads -c size

# Tri par date
file-classifier sort ~/Downloads -c date
```

## Annulation

Si vous souhaitez annuler le tri, vous pouvez utiliser la commande `undo` :

```bash
# Annuler la dernière action
file-classifier undo

# Annuler les 3 dernières actions
file-classifier undo -c 3

# Annuler toutes les actions
file-classifier undo -a
```

Vous pouvez également consulter l'historique des actions avant d'annuler :

```bash
file-classifier history
```
