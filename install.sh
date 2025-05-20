#!/bin/bash

# Script d'installation pour File-Classifier
# Ce script installe l'exécutable file-classifier dans /usr/local/bin

# Vérifier si l'utilisateur a les droits sudo
if [ "$EUID" -ne 0 ]; then
  echo "Ce script doit être exécuté avec les droits sudo."
  echo "Utilisation: sudo ./install.sh"
  exit 1
fi

# Vérifier si l'exécutable existe
if [ ! -f "./dist/file-classifier" ]; then
  echo "Erreur: L'exécutable file-classifier n'existe pas dans le répertoire dist/."
  echo "Veuillez d'abord exécuter PyInstaller pour créer l'exécutable."
  exit 1
fi

# Copier l'exécutable dans /usr/local/bin
echo "Installation de file-classifier dans /usr/local/bin..."
cp ./dist/file-classifier /usr/local/bin/
chmod 755 /usr/local/bin/file-classifier

# Vérifier si l'installation a réussi
if [ $? -eq 0 ]; then
  echo "Installation réussie !"
  echo "Vous pouvez maintenant exécuter 'file-classifier' depuis n'importe quel répertoire."
else
  echo "Erreur lors de l'installation."
  exit 1
fi

exit 0 