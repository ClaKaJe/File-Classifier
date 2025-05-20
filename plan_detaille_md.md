# Plan détaillé pour un outil CLI de gestion et classement de fichiers (Python, Ubuntu 22.04)

## 1. Définition des fonctionnalités

L'outil doit regrouper toutes les fonctions usuelles de gestion de fichiers : tri, renommage, déplacement, etc.
On implémente notamment :

- **Tri et classement** : trier les fichiers par type (extension), par taille ou par date de création/modification. Par exemple, classer automatiquement des fichiers dans des dossiers « Images », « Documents », « Vidéos » selon leur extension et date.

- **Renommage par lot** : renommer plusieurs fichiers selon un même motif (ex. ajouter un préfixe, numéroter séquentiellement, changer l'extension).

- **Déplacement/copier automatique** : déplacer ou copier des fichiers en fonction de règles prédéfinies (par ex. tous les fichiers >100 Mo vont dans `/media/large`, ou selon leur type).

- **Détection de doublons** : analyser un ou plusieurs dossiers pour identifier et gérer les fichiers identiques (par nom et/ou contenu).

- **Compression/décompression** : prendre en charge les formats courants (zip, tar, gz, etc.) pour compresser ou extraire des archives via la ligne de commande.

- **Génération de rapports** : produire un rapport (fichier texte ou JSON) listant les actions réalisées ou l'état des fichiers (par exemple, taille totale par dossier).

- **Nettoyage** : suppression automatisée de fichiers temporaires ou obsolètes (fichiers plus anciens qu'un certain délai, par exemple).

- **Surveillance de répertoires** : optionnellement, surveiller un dossier en continu (par ex. avec inotify) pour lancer des actions dès qu'un fichier y est ajouté.

- **Indexation locale** : maintenir un index local (base de données SQLite ou fichier JSON) des fichiers connus pour accélérer les recherches ultérieures.

Ces opérations seront accessibles via des options et sous-commandes CLI. On utilisera une bibliothèque Python de CLI (module standard `argparse` ou `click`) pour construire une interface robuste et conviviale.

## 2. Conception du projet Python

Structure générale : prévoir un dépôt Git contenant au minimum un dossier `package_name/` (avec le code source), un dossier `tests/` (tests unitaires), un fichier `README.md`, et les fichiers de configuration (`setup.py` ou `pyproject.toml`). Par exemple :

```
monoutil/
├── monoutil/              # code source du package Python
│   ├── __init__.py
│   ├── cli.py             # script principal CLI
│   ├── core.py            # logiques de tri et déplacement
│   └── utils.py           # fonctions utilitaires (scanner fichiers, etc.)
├── tests/                 # tests unitaires
│   └── test_core.py
├── setup.py (ou pyproject.toml)
├── README.md
└── LICENSE.txt
```

- **Gestion des dépendances** : on utilisera `setuptools` pour le packaging. Le fichier `setup.py` configure le projet (nom, version, dépendances, scripts d'entrée, etc.). Les dépendances externes (ex. `pathlib`, `click`/`argparse`, bibliothèques de compression) sont listées dans `install_requires` ou équivalent. On peut aussi adopter le format moderne `pyproject.toml` pour la configuration du projet.

- **Interface CLI** : implémenter un script principal (ex. `cli.py`) qui définit les commandes et options. Le module `argparse` (standard) permet de créer facilement des sous-commandes et messages d'aide. Alternativement, le package `click` offre une approche décorateur pour créer un CLI intuitif. Les scripts d'entrées (entry points) seront installés dans `/usr/bin` via le packaging Python.

- **Système de logging** : utiliser le module `logging` de Python pour consigner les opérations majeures (tri effectué, erreurs, actions de nettoyage). On configure des niveaux de log (INFO, DEBUG, ERROR) pour faciliter le débogage.

- **Tests unitaires** : écrire des tests (avec `pytest` ou `unittest`) pour chaque fonctionnalité principale (ex. la fonction de tri, la détection de doublons). Un coverage élevé et des tests automatisés assurent la fiabilité du code.

## 3. Création du paquet Debian (.deb)

Arborescence du paquet : créer un dossier `monoutil-VERSION/` (où VERSION est la version du programme) contenant la hiérarchie cible. Par exemple :

```
monoutil-1.0/
├── DEBIAN/
│   ├── control
│   ├── postinst (script post-install, si besoin)
│   └── prerem (script pré-suppression, si besoin)
└── usr/
    ├── bin/
    │   └── monoutil (le script CLI exécutable, sans extension)
    └── share/
        └── monoutil/
            ├── core.py
            └── utils.py
```

Le dossier DEBIAN (en majuscule) doit contenir au moins le fichier `control`. Les fichiers du programme sont installés sous `/usr/bin` ou `/usr/share/monoutil`, selon la logique de l'application.

- **Fichier control** : dans `DEBIAN/control`, définir les métadonnées du paquet (Package, Version, Architecture, Maintainer, Depends, Description, etc.). Par exemple :

```
Package: monoutil
Version: 1.0
Architecture: all
Maintainer: Nom <email@example.com>
Depends: python3
Description: Outil CLI de gestion de fichiers
 Cet outil permet de trier, renommer et organiser automatiquement des
 fichiers.
```

- **Scripts d'installation** : optionnellement, ajouter des scripts `postinst`, `preinst`, `prerm`, `postrm` dans `DEBIAN/` pour exécuter des tâches au moment de l'installation ou de la suppression (par ex. création d'un dossier, mise à jour d'un index). Les scripts doivent être exécutables (`chmod 0755`).

- **Permissions et propriété** : s'assurer que tous les fichiers appartiennent à root et ont les droits appropriés. Par exemple, on peut faire `chown root:root -R monoutil-1.0/` puis `chmod 0755` sur le binaire principal.

- **Construction du paquet** : une fois l'arborescence prête, exécuter `dpkg-deb --build monoutil-1.0/ monoutil_1.0_all.deb` (ou `dpkg -b monoutil-1.0/`) pour créer le fichier `.deb` final. On peut utiliser `fakeroot` pour conserver les droits root dans le paquet sans être root. L'option `--root-owner-group` de `dpkg-deb` attribue la propriété root aux fichiers.

## 4. Création d'un dépôt APT personnalisé

- **Hébergement du dépôt** : décider d'un emplacement (serveur web interne, NAS, ou serveur cloud). On peut simplement partager par HTTP un dossier `repo/` qui contiendra les paquets et métadonnées.

- **Outil de gestion du dépôt** : utiliser `reprepro` (recommandé) ou `dpkg-scanpackages`. Avec `reprepro`, on initialise un répertoire (`mkdir -p repo/conf`) et on configure le fichier `distributions` pour définir les dépôts (noms, versions, architectures). `reprepro` gère la génération des index (`Packages`, `Release`) automatiquement. Debian indique que « reprepro est un programme pour créer un dépôt Debian, bien adapté à des dépôts PPA personnels ».

- **Ajout des paquets** : importer le fichier `.deb` dans le dépôt avec `reprepro includedeb <distribution> monoutil_1.0_all.deb`. Cela génère ou met à jour les fichiers `Packages.gz` et `Release`.

- **Signature GPG** : créer une clé GPG (`gpg --gen-key`) pour signer le dépôt. Signer le fichier `Release` avec votre clé privée afin que les clients vérifient l'authenticité. Debian recommande cette étape : « créer un certificat de sécurité, signer les paquets avec sa clé, et laisser les utilisateurs vérifier avec la clé publique ». Publier la clé publique (URL ou paquet `.gpg`) pour que les clients l'ajoutent à leurs clés de confiance.

## 5. Installation et mise à jour via APT

- **Ajout du dépôt** : sur chaque machine cliente, créer un fichier `/etc/apt/sources.list.d/monoutil.list` contenant la ligne vers le dépôt, par exemple :

```
deb [signed-by=/etc/apt/trusted.gpg.d/monoutil.gpg] http://monrepo.local/ stable main
```

où `monrepo.local` est l'URL du dépôt. Cette démarche (ajout de fichier `.list`) est préconisée pour isoler chaque dépôt.

- **Clé de signature** : télécharger la clé GPG publique du dépôt et l'installer, par exemple via `curl <url_cle> | gpg --dearmor > /etc/apt/trusted.gpg.d/monoutil.gpg`.

- **Mises à jour automatiques** : après `sudo apt update`, le paquet monoutil devient installable par `sudo apt install monoutil`. Les utilisateurs pourront mettre à jour le logiciel avec `apt upgrade` dès qu'une nouvelle version du `.deb` sera ajoutée au dépôt. On peut configurer une tâche (cron) pour automatiser la mise à jour si besoin.

## 6. Bonnes pratiques et sécurité

- **Exécution en mode non-root** : l'outil CLI s'exécutera normalement sans privilèges élevés. On évite d'exiger `sudo` pour les opérations classiques (lecture, tri). Si des tâches (ex. installation, modification de fichiers système) nécessitent des droits root, seules les commandes d'installation du paquet les utiliseront. En général, on « crée le paquet en tant qu'utilisateur normal » et on utilise `--root-owner-group` pour les droits dans l'archive.

- **Permissions minimales** : les scripts et fichiers exécutables doivent avoir des droits restreints (ex. `0755`). Ne pas laisser de fichier sensible accessible en écriture par d'autres utilisateurs. Par défaut, exiger un mot de passe sudo pour les actions système.

- **Séparation utilisateur/root** : durant le développement et le packaging, travailler sous un compte non-root, et tester les installations avec un utilisateur normal ayant un accès sudo limité. Éviter d'exécuter le CLI avec root sauf nécessité (ex. nettoyage de dossiers système).

- **Documentation** : fournir une page de manuel (`man`) pour le logiciel. La documentation peut être rédigée en reST ou Markdown et convertie en troff avec `help2man` ou `rst2man`. On veillera aussi à ce que `monoutil --help` affiche les options principales et un bref usage.

- **Sécurité du code** : valider les entrées utilisateurs et limiter les injections de commandes. Par exemple, éviter d'appeler directement `os.system` sans précautions, préférer les API Python ou le module `subprocess` avec des listes d'arguments. Tenir le code à jour (utiliser Python 3.10+ sur Ubuntu 22.04) et appliquer les mises à jour de dépendances.

Cette approche modulaire et bien documentée, associée au packaging Debian correct et au dépôt APT privé, permettra de déployer et mettre à jour l'outil CLI de gestion de fichiers de manière fiable et sécurisée.

## Sources : documentation Debian et Python Packaging

1. [Build Command-Line Interfaces With Python's argparse – Real Python](https://realpython.com/command-line-interfaces-python-argparse/)
2. [Packaging and distributing projects - Python Packaging User Guide](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
3. [How do I do Debian packaging of a Python package? - Stack Overflow](https://stackoverflow.com/questions/1382569/how-do-i-do-debian-packaging-of-a-python-package)
4. [Debian package structure - Free Pascal wiki](https://wiki.freepascal.org/Debian_package_structure)
5. [DebianRepository/SetupWithReprepro - Debian Wiki](https://wiki.debian.org/DebianRepository/SetupWithReprepro)
6. [Adding repositories to sources.list.d manually - DEV Community](https://dev.to/tallesl/adding-repositories-to-sources-list-d-manually-15bj)
7. [Best Packaging Practices – developers-reference 13.18 documentation](https://www.debian.org/doc/manuals/developers-reference/best-pkging-practices.en.html)