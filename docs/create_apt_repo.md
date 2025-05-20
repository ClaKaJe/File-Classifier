# Création d'un dépôt APT local pour File-Classifier

Ce guide explique comment créer un dépôt APT local pour distribuer File-Classifier sur plusieurs machines.

## Prérequis

- Un serveur web (Apache, Nginx, etc.) ou un serveur de fichiers accessible par HTTP
- L'outil `reprepro` pour la gestion du dépôt
- Une clé GPG pour signer le dépôt

## Installation des outils nécessaires

```bash
sudo apt install reprepro gnupg apache2
```

## Création d'une clé GPG

```bash
# Générer une paire de clés GPG
gpg --full-generate-key

# Choisir les options suivantes :
# - Type de clé : RSA et RSA (par défaut)
# - Taille de clé : 4096 bits
# - Durée de validité : 0 = clé n'expire pas
# - Nom réel : File-Classifier Repository
# - Adresse e-mail : votre.email@example.com
# - Commentaire : File-Classifier APT Repository Signing Key
```

## Structure du dépôt

```bash
# Créer la structure du dépôt
mkdir -p /var/www/html/repo/{conf,incoming}
cd /var/www/html/repo
```

## Configuration de reprepro

Créer le fichier `/var/www/html/repo/conf/distributions` :

```
Origin: File-Classifier
Label: File-Classifier
Suite: stable
Codename: stable
Version: 1.0
Architectures: amd64 i386 all
Components: main
Description: Dépôt APT pour File-Classifier
SignWith: yes
```

Créer le fichier `/var/www/html/repo/conf/options` :

```
verbose
basedir /var/www/html/repo
ask-passphrase
```

## Ajout du paquet au dépôt

```bash
# Copier le paquet Debian dans le répertoire incoming
cp file-classifier_*.deb /var/www/html/repo/incoming/

# Ajouter le paquet au dépôt
cd /var/www/html/repo
reprepro includedeb stable incoming/file-classifier_*.deb
```

## Exportation de la clé publique

```bash
# Exporter la clé publique
gpg --armor --export "File-Classifier Repository" > /var/www/html/repo/file-classifier-apt.gpg
```

## Configuration des clients

Sur chaque machine cliente :

```bash
# Télécharger la clé GPG
wget -O /tmp/file-classifier-apt.gpg http://votre-serveur/repo/file-classifier-apt.gpg
sudo cp /tmp/file-classifier-apt.gpg /etc/apt/trusted.gpg.d/

# Ajouter le dépôt
echo "deb [signed-by=/etc/apt/trusted.gpg.d/file-classifier-apt.gpg] http://votre-serveur/repo stable main" | sudo tee /etc/apt/sources.list.d/file-classifier.list

# Mettre à jour la liste des paquets
sudo apt update

# Installer File-Classifier
sudo apt install file-classifier
```

## Mise à jour du paquet

Lorsqu'une nouvelle version de File-Classifier est disponible :

1. Construire le nouveau paquet Debian
2. Copier le paquet dans le répertoire incoming
3. Mettre à jour le dépôt :

```bash
cd /var/www/html/repo
reprepro includedeb stable incoming/file-classifier_nouvelle-version.deb
```

Les clients pourront alors mettre à jour le paquet avec :

```bash
sudo apt update
sudo apt upgrade
```

## Automatisation avec cron

Pour automatiser les mises à jour du dépôt, vous pouvez créer un script et le planifier avec cron.

Exemple de script `/usr/local/bin/update-repo.sh` :

```bash
#!/bin/bash

set -e

# Répertoire du dépôt
REPO_DIR="/var/www/html/repo"
# Répertoire où les nouveaux paquets sont déposés
INCOMING_DIR="${REPO_DIR}/incoming"

# Vérifier s'il y a de nouveaux paquets
if [ -z "$(ls -A ${INCOMING_DIR})" ]; then
    echo "Aucun nouveau paquet trouvé."
    exit 0
fi

# Ajouter les paquets au dépôt
cd ${REPO_DIR}
for pkg in ${INCOMING_DIR}/*.deb; do
    echo "Ajout du paquet ${pkg} au dépôt..."
    reprepro includedeb stable "${pkg}"
    # Déplacer le paquet traité
    mv "${pkg}" "${INCOMING_DIR}/processed/"
done

echo "Mise à jour du dépôt terminée."
```

Rendre le script exécutable :

```bash
sudo chmod +x /usr/local/bin/update-repo.sh
```

Ajouter une tâche cron pour exécuter le script toutes les heures :

```bash
sudo crontab -e
```

Ajouter la ligne suivante :

```
0 * * * * /usr/local/bin/update-repo.sh >> /var/log/update-repo.log 2>&1
```
