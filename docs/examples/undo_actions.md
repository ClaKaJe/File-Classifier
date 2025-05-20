# Exemple : Utiliser l'historique et annuler des actions

Cet exemple montre comment utiliser les fonctionnalités d'historique et d'annulation de File-Classifier.

## Scénario

Vous avez effectué plusieurs opérations de tri et de renommage sur vos fichiers, mais vous souhaitez maintenant revenir en arrière sur certaines de ces actions.

## Afficher l'historique des actions

Pour voir toutes les actions effectuées précédemment :

```bash
file-classifier history
```

Exemple de sortie :

```
Historique des actions (5 actions):
--------------------------------------------------------------------------------
12 | 2025-05-20 15:45:23 | DÉPLACEMENT: /home/user/Downloads/rapport.pdf → /home/user/Downloads/documents/rapport.pdf
11 | 2025-05-20 15:45:23 | DÉPLACEMENT: /home/user/Downloads/photo.jpg → /home/user/Downloads/images/photo.jpg
10 | 2025-05-20 15:30:12 | RENOMMAGE: document.txt → rapport_final.txt
9 | 2025-05-20 15:15:05 | DÉPLACEMENT: /home/user/Documents/old_file.txt → /home/user/Archives/old_file.txt
8 | 2025-05-20 14:55:18 | SUPPRESSION: /home/user/Downloads/temp.bak
--------------------------------------------------------------------------------
Utilisez 'file-classifier undo -c N' pour annuler les N dernières actions
Utilisez 'file-classifier undo -a' pour annuler toutes les actions
```

## Limiter le nombre d'actions affichées

Pour voir seulement les 3 dernières actions :

```bash
file-classifier history -c 3
```

## Format JSON

Pour obtenir l'historique au format JSON :

```bash
file-classifier history --json
```

## Annuler la dernière action

Pour annuler uniquement la dernière action effectuée :

```bash
file-classifier undo
```

Exemple de sortie :

```
Dernière action annulée avec succès
```

## Annuler plusieurs actions

Pour annuler les 3 dernières actions :

```bash
file-classifier undo -c 3
```

Avant d'exécuter cette commande, File-Classifier affichera les actions qui vont être annulées et demandera confirmation :

```
Les actions suivantes vont être annulées (3 actions):
--------------------------------------------------------------------------------
12 | 2025-05-20 15:45:23 | DÉPLACEMENT: /home/user/Downloads/rapport.pdf → /home/user/Downloads/documents/rapport.pdf
11 | 2025-05-20 15:45:23 | DÉPLACEMENT: /home/user/Downloads/photo.jpg → /home/user/Downloads/images/photo.jpg
10 | 2025-05-20 15:30:12 | RENOMMAGE: document.txt → rapport_final.txt
--------------------------------------------------------------------------------
Voulez-vous continuer ? (o/N)
```

Si vous confirmez, vous obtiendrez :

```
Les 3 dernières actions ont été annulées avec succès.
```

## Annuler toutes les actions

Pour annuler toutes les actions enregistrées :

```bash
file-classifier undo -a
```

Cette commande affichera également une liste des actions qui vont être annulées et demandera confirmation avant de procéder.

Exemple de sortie après confirmation :

```
Toutes les actions ont été annulées avec succès.
```

## Notes importantes

- Les actions de suppression (**SUPPRESSION**) ne peuvent pas être annulées car les fichiers ont été définitivement supprimés.
- L'annulation fonctionne uniquement si les fichiers n'ont pas été modifiés entre-temps par d'autres programmes.
- Chaque annulation est elle-même enregistrée comme une nouvelle action (déplacement ou renommage).
- Si vous annulez une action puis effectuez une nouvelle opération, vous ne pourrez plus "refaire" l'action annulée.

## Cas d'utilisation

- **Correction d'erreurs** : Annuler une opération de tri ou de renommage qui a donné des résultats inattendus
- **Test de configurations** : Essayer différentes organisations de fichiers et revenir facilement à l'état précédent
- **Audit** : Examiner l'historique des actions pour comprendre les modifications apportées aux fichiers
