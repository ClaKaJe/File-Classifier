#!/usr/bin/env python3
"""Tests pour le module utils."""

import os
import tempfile
import unittest
from pathlib import Path

from file_classifier.file_classifier.utils import (
    get_file_type,
    get_file_size_category,
    get_file_date_category,
    calculate_file_hash,
    is_temp_file,
    human_readable_size
)


class TestUtils(unittest.TestCase):
    """Tests pour les fonctions utilitaires."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        # Créer un répertoire temporaire pour les tests
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)
        
        # Créer quelques fichiers de test
        self.test_files = {
            "image": self.test_path / "test_image.jpg",
            "document": self.test_path / "test_document.pdf",
            "video": self.test_path / "test_video.mp4",
            "temp": self.test_path / "test_file.tmp",
            "other": self.test_path / "test_other.xyz"
        }
        
        for file_path in self.test_files.values():
            with open(file_path, "w") as f:
                f.write("Test content")
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        self.test_dir.cleanup()
    
    def test_get_file_type(self):
        """Teste la fonction get_file_type."""
        self.assertEqual(get_file_type(self.test_files["image"]), "images")
        self.assertEqual(get_file_type(self.test_files["document"]), "documents")
        self.assertEqual(get_file_type(self.test_files["video"]), "videos")
        # Notre fonction améliorée peut détecter les fichiers texte par leur contenu
        # même si l'extension n'est pas reconnue
        self.assertIn(get_file_type(self.test_files["other"]), ["other", "text"])
    
    def test_get_file_size_category(self):
        """Teste la fonction get_file_size_category."""
        # Les fichiers de test sont très petits
        self.assertEqual(get_file_size_category(self.test_files["image"]), "tiny")
    
    def test_get_file_date_category(self):
        """Teste la fonction get_file_date_category."""
        # Les fichiers de test viennent d'être créés
        self.assertEqual(get_file_date_category(self.test_files["image"]), "today")
    
    def test_calculate_file_hash(self):
        """Teste la fonction calculate_file_hash."""
        # Créer deux fichiers avec le même contenu
        file1 = self.test_path / "file1.txt"
        file2 = self.test_path / "file2.txt"
        
        with open(file1, "w") as f:
            f.write("Identical content")
        
        with open(file2, "w") as f:
            f.write("Identical content")
        
        # Les hashes doivent être identiques
        hash1 = calculate_file_hash(file1)
        hash2 = calculate_file_hash(file2)
        self.assertEqual(hash1, hash2)
        
        # Modifier le contenu du deuxième fichier
        with open(file2, "w") as f:
            f.write("Different content")
        
        # Les hashes doivent être différents
        hash2 = calculate_file_hash(file2)
        self.assertNotEqual(hash1, hash2)
    
    def test_is_temp_file(self):
        """Teste la fonction is_temp_file."""
        self.assertTrue(is_temp_file(self.test_files["temp"]))
        self.assertFalse(is_temp_file(self.test_files["image"]))
    
    def test_human_readable_size(self):
        """Teste la fonction human_readable_size."""
        self.assertEqual(human_readable_size(0), "0 B")
        self.assertEqual(human_readable_size(1023), "1023.00 B")
        self.assertEqual(human_readable_size(1024), "1.00 KB")
        self.assertEqual(human_readable_size(1024 * 1024), "1.00 MB")
        self.assertEqual(human_readable_size(1024 * 1024 * 1024), "1.00 GB")


if __name__ == "__main__":
    unittest.main() 