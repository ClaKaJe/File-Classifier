#!/usr/bin/env python3
"""Tests pour le module core."""

import os
import tempfile
import unittest
import shutil
from pathlib import Path

from file_classifier.file_classifier.core import FileManager


class TestFileManager(unittest.TestCase):
    """Tests pour la classe FileManager."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        # Créer un répertoire temporaire pour les tests
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)
        
        # Créer une structure de fichiers pour les tests
        self.create_test_files()
        
        # Initialiser le gestionnaire de fichiers
        self.manager = FileManager()
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        self.test_dir.cleanup()
    
    def create_test_files(self):
        """Crée une structure de fichiers pour les tests."""
        # Créer quelques fichiers de différents types
        (self.test_path / "image1.jpg").write_text("Test image 1")
        (self.test_path / "image2.png").write_text("Test image 2")
        (self.test_path / "document1.pdf").write_text("Test document 1")
        (self.test_path / "document2.docx").write_text("Test document 2")
        (self.test_path / "video.mp4").write_text("Test video")
        (self.test_path / "temp.tmp").write_text("Test temp file")
        
        # Créer un sous-répertoire avec des fichiers
        subdir = self.test_path / "subdir"
        subdir.mkdir()
        (subdir / "subfile1.txt").write_text("Test subfile 1")
        (subdir / "subfile2.jpg").write_text("Test subfile 2")
    
    def test_sort_files_by_type(self):
        """Teste le tri de fichiers par type."""
        # Trier les fichiers par type (sans déplacer)
        result = self.manager.sort_files(self.test_path, criteria="type", dry_run=True)
        
        # Vérifier que les fichiers sont correctement catégorisés
        self.assertIn("images", result)
        self.assertIn("documents", result)
        self.assertIn("videos", result)
        self.assertIn("other", result)
        
        # Vérifier le nombre de fichiers par catégorie
        self.assertEqual(len(result["images"]), 2)  # image1.jpg, image2.png
        self.assertEqual(len(result["documents"]), 2)  # document1.pdf, document2.docx
        self.assertEqual(len(result["videos"]), 1)  # video.mp4
    
    def test_sort_files_by_type_with_move(self):
        """Teste le tri de fichiers par type avec déplacement."""
        # Trier les fichiers par type (avec déplacement)
        self.manager.sort_files(self.test_path, criteria="type", dry_run=False)
        
        # Vérifier que les répertoires ont été créés
        self.assertTrue((self.test_path / "images").exists())
        self.assertTrue((self.test_path / "documents").exists())
        self.assertTrue((self.test_path / "videos").exists())
        
        # Vérifier que les fichiers ont été déplacés
        self.assertTrue((self.test_path / "images" / "image1.jpg").exists())
        self.assertTrue((self.test_path / "images" / "image2.png").exists())
        self.assertTrue((self.test_path / "documents" / "document1.pdf").exists())
        self.assertTrue((self.test_path / "documents" / "document2.docx").exists())
        self.assertTrue((self.test_path / "videos" / "video.mp4").exists())
    
    def test_rename_batch(self):
        """Teste le renommage par lot."""
        # Créer des fichiers avec un motif commun
        for i in range(1, 4):
            (self.test_path / f"test_{i}.txt").write_text(f"Test file {i}")
        
        # Renommer les fichiers (sans renommer)
        result = self.manager.rename_batch(
            self.test_path,
            pattern=r"test_(\d+)\.txt",
            replacement=r"renamed_\1.txt",
            dry_run=True
        )
        
        # Vérifier le résultat
        self.assertEqual(len(result), 3)
        
        # Renommer les fichiers (avec renommage)
        self.manager.rename_batch(
            self.test_path,
            pattern=r"test_(\d+)\.txt",
            replacement=r"renamed_\1.txt",
            dry_run=False
        )
        
        # Vérifier que les fichiers ont été renommés
        self.assertTrue((self.test_path / "renamed_1.txt").exists())
        self.assertTrue((self.test_path / "renamed_2.txt").exists())
        self.assertTrue((self.test_path / "renamed_3.txt").exists())
        self.assertFalse((self.test_path / "test_1.txt").exists())
    
    def test_find_duplicates(self):
        """Teste la détection de doublons."""
        # Créer des fichiers avec le même contenu
        content = "This is a test content"
        (self.test_path / "original.txt").write_text(content)
        (self.test_path / "duplicate1.txt").write_text(content)
        (self.test_path / "duplicate2.txt").write_text(content)
        (self.test_path / "different.txt").write_text("Different content")
        
        # Trouver les doublons
        result = self.manager.find_duplicates([self.test_path])
        
        # Vérifier qu'un groupe de doublons a été trouvé
        self.assertEqual(len(result), 1)
        
        # Vérifier que le groupe contient les trois fichiers avec le même contenu
        duplicate_files = list(result.values())[0]
        self.assertEqual(len(duplicate_files), 3)
        
        # Vérifier que le fichier différent n'est pas dans les doublons
        duplicate_paths = [str(p) for p in duplicate_files]
        self.assertIn(str(self.test_path / "original.txt"), duplicate_paths)
        self.assertIn(str(self.test_path / "duplicate1.txt"), duplicate_paths)
        self.assertIn(str(self.test_path / "duplicate2.txt"), duplicate_paths)
        self.assertNotIn(str(self.test_path / "different.txt"), duplicate_paths)
    
    def test_clean_temp_files(self):
        """Teste le nettoyage des fichiers temporaires."""
        # Créer des fichiers temporaires
        (self.test_path / "file1.tmp").write_text("Temp file 1")
        (self.test_path / "file2.temp").write_text("Temp file 2")
        (self.test_path / "file.bak").write_text("Backup file")
        (self.test_path / "regular.txt").write_text("Regular file")
        
        # Nettoyer les fichiers temporaires (sans supprimer)
        result = self.manager.clean_temp_files(self.test_path, dry_run=True)
        
        # Vérifier le résultat
        self.assertEqual(len(result), 4)  # 4 fichiers temporaires incluant temp.tmp du setUp
        
        # Nettoyer les fichiers temporaires (avec suppression)
        self.manager.clean_temp_files(self.test_path, dry_run=False)
        
        # Vérifier que les fichiers temporaires ont été supprimés
        self.assertFalse((self.test_path / "file1.tmp").exists())
        self.assertFalse((self.test_path / "file2.temp").exists())
        self.assertFalse((self.test_path / "file.bak").exists())
        self.assertTrue((self.test_path / "regular.txt").exists())
    
    def test_generate_report(self):
        """Teste la génération de rapport."""
        # Générer un rapport au format texte
        report_text = self.manager.generate_report(self.test_path, output_format="text")
        
        # Vérifier que le rapport contient des informations de base
        self.assertIn("Total des fichiers:", report_text)
        self.assertIn("Par type:", report_text)
        
        # Générer un rapport au format JSON
        report_json = self.manager.generate_report(self.test_path, output_format="json")
        
        # Vérifier que le rapport est au format JSON
        self.assertTrue(report_json.startswith("{"))
        self.assertTrue(report_json.endswith("}"))


if __name__ == "__main__":
    unittest.main() 