# Exemple : Générer des rapports sur les fichiers

Cet exemple montre comment utiliser File-Classifier pour générer des rapports détaillés sur les fichiers d'un répertoire.

## Scénario

Vous souhaitez analyser le contenu d'un répertoire pour comprendre comment l'espace disque est utilisé et quels types de fichiers sont présents.

## Rapport au format texte

Pour générer un rapport simple au format texte :

```bash
file-classifier report ~/Documents
```

Exemple de sortie :

```
Rapport pour /home/user/Documents
Total des fichiers: 156
Taille totale: 1.25 GB

Par type:
  documents: 87 fichiers, 750.45 MB
  images: 42 fichiers, 350.20 MB
  text: 18 fichiers, 12.50 MB
  code: 9 fichiers, 1.85 MB

Par taille:
  tiny: 45 fichiers, 25.30 MB
  small: 89 fichiers, 350.70 MB
  medium: 20 fichiers, 650.00 MB
  large: 2 fichiers, 225.00 MB

Par date:
  today: 12 fichiers, 45.20 MB
  this_week: 38 fichiers, 320.50 MB
  this_month: 65 fichiers, 550.30 MB
  this_year: 35 fichiers, 280.00 MB
  older: 6 fichiers, 55.00 MB
```

## Rapport récursif

Pour inclure tous les sous-répertoires dans l'analyse :

```bash
file-classifier report ~/Documents -r
```

## Rapport au format JSON

Pour générer un rapport au format JSON :

```bash
file-classifier report ~/Documents --json
```

Cette commande produit une sortie structurée qui peut être facilement traitée par d'autres programmes.

Exemple de sortie :

```json
{
  "total_files": 156,
  "total_size": 1342177280,
  "by_type": {
    "documents": {
      "count": 87,
      "size": 786432000
    },
    "images": {
      "count": 42,
      "size": 367001600
    },
    "text": {
      "count": 18,
      "size": 13107200
    },
    "code": {
      "count": 9,
      "size": 1939865
    }
  },
  "by_size": {
    "tiny": {
      "count": 45,
      "size": 26525696
    },
    "small": {
      "count": 89,
      "size": 367656755
    },
    "medium": {
      "count": 20,
      "size": 681574400
    },
    "large": {
      "count": 2,
      "size": 235929600
    }
  },
  "by_date": {
    "today": {
      "count": 12,
      "size": 47382528
    },
    "this_week": {
      "count": 38,
      "size": 336101376
    },
    "this_month": {
      "count": 65,
      "size": 576716800
    },
    "this_year": {
      "count": 35,
      "size": 293601280
    },
    "older": {
      "count": 6,
      "size": 57671680
    }
  }
}
```

## Rapport JSON avec tailles lisibles

Pour inclure des tailles lisibles par l'homme dans la sortie JSON :

```bash
file-classifier report ~/Documents --json --human-readable
```

Exemple de sortie :

```json
{
  "total_files": 156,
  "total_size": 1342177280,
  "total_size_hr": "1.25 GB",
  "by_type": {
    "documents": {
      "count": 87,
      "size": 786432000,
      "size_hr": "750.45 MB"
    },
    "images": {
      "count": 42,
      "size": 367001600,
      "size_hr": "350.20 MB"
    },
    "text": {
      "count": 18,
      "size": 13107200,
      "size_hr": "12.50 MB"
    },
    "code": {
      "count": 9,
      "size": 1939865,
      "size_hr": "1.85 MB"
    }
  },
  "by_size": {
    "tiny": {
      "count": 45,
      "size": 26525696,
      "size_hr": "25.30 MB"
    },
    "small": {
      "count": 89,
      "size": 367656755,
      "size_hr": "350.70 MB"
    },
    "medium": {
      "count": 20,
      "size": 681574400,
      "size_hr": "650.00 MB"
    },
    "large": {
      "count": 2,
      "size": 235929600,
      "size_hr": "225.00 MB"
    }
  },
  "by_date": {
    "today": {
      "count": 12,
      "size": 47382528,
      "size_hr": "45.20 MB"
    },
    "this_week": {
      "count": 38,
      "size": 336101376,
      "size_hr": "320.50 MB"
    },
    "this_month": {
      "count": 65,
      "size": 576716800,
      "size_hr": "550.30 MB"
    },
    "this_year": {
      "count": 35,
      "size": 293601280,
      "size_hr": "280.00 MB"
    },
    "older": {
      "count": 6,
      "size": 57671680,
      "size_hr": "55.00 MB"
    }
  }
}
```

## Enregistrer le rapport dans un fichier

Pour sauvegarder le rapport dans un fichier :

```bash
file-classifier report ~/Documents -o rapport.txt
file-classifier report ~/Documents --json -o rapport.json
```

## Cas d'utilisation

- **Analyse d'espace disque** : Identifier quels types de fichiers occupent le plus d'espace
- **Audit de fichiers** : Comprendre la répartition des fichiers par type, taille et date
- **Documentation** : Créer un inventaire des fichiers présents dans un répertoire
- **Préparation au nettoyage** : Analyser avant de décider quels fichiers supprimer
