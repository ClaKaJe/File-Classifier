#!/bin/bash

set -e

# Vérifier les dépendances
echo "Vérification des dépendances..."
command -v dpkg-buildpackage >/dev/null 2>&1 || { echo "dpkg-buildpackage est requis mais n'est pas installé. Installez-le avec 'sudo apt install dpkg-dev'." >&2; exit 1; }
command -v dh_make >/dev/null 2>&1 || { echo "dh_make est requis mais n'est pas installé. Installez-le avec 'sudo apt install dh-make'." >&2; exit 1; }
command -v pandoc >/dev/null 2>&1 || { echo "pandoc est requis mais n'est pas installé. Installez-le avec 'sudo apt install pandoc'." >&2; exit 1; }

# Nettoyer les anciens builds
echo "Nettoyage des anciens builds..."
rm -rf build/ dist/ *.egg-info/ debian/file-classifier/ debian/.debhelper/ debian/files debian/debhelper-build-stamp

# Construire le paquet source
echo "Construction du paquet source..."
python3 setup.py sdist

# Construire le paquet Debian
echo "Construction du paquet Debian..."
dpkg-buildpackage -us -uc -b

# Déplacer le paquet Debian dans le répertoire courant
echo "Déplacement du paquet Debian..."
mv ../file-classifier_*.deb .

echo "Terminé ! Le paquet Debian est prêt."
echo "Pour l'installer : sudo dpkg -i file-classifier_*.deb"
echo "Pour créer un dépôt APT local, consultez la documentation dans docs/" 