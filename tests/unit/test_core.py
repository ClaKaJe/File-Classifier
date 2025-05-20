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
        # Avec notre classification améliorée, le fichier temp.tmp pourrait être classé comme "text" plutôt que "other"
        self.assertTrue("text" in result or "other" in result)
        
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
        
        # Générer un rapport au format JSON avec tailles lisibles
        report_json_hr = self.manager.generate_report(
            self.test_path, 
            output_format="json", 
            human_readable=True
        )
        
        # Vérifier que le rapport contient des tailles lisibles
        self.assertIn("total_size_hr", report_json_hr)
        self.assertIn("size_hr", report_json_hr)
    
    def test_undo_last_action(self):
        """Teste l'annulation de la dernière action."""
        # Créer un fichier à déplacer
        test_file = self.test_path / "file_to_move.txt"
        test_file.write_text("Test file to move")
        
        # Créer un répertoire de destination
        dest_dir = self.test_path / "dest_dir"
        dest_dir.mkdir()
        
        # Déplacer le fichier (pour enregistrer une action)
        dest_file = dest_dir / "file_to_move.txt"
        shutil.move(str(test_file), str(dest_file))
        
        # Enregistrer l'action dans la base de données
        self.manager._record_action("move", test_file, dest_file)
        
        # Vérifier que le fichier a été déplacé
        self.assertFalse(test_file.exists())
        self.assertTrue(dest_file.exists())
        
        # Annuler la dernière action
        result = self.manager.undo_last_action()
        
        # Vérifier que l'annulation a réussi
        self.assertTrue(result)
        
        # Vérifier que le fichier a été restauré
        self.assertTrue(test_file.exists())
        self.assertFalse(dest_file.exists())
    
    def test_undo_multiple_actions(self):
        """Teste l'annulation de plusieurs actions."""
        # Créer des fichiers à déplacer
        files = []
        for i in range(3):
            file_path = self.test_path / f"file_{i}.txt"
            file_path.write_text(f"Test file {i}")
            files.append(file_path)
        
        # Créer un répertoire de destination
        dest_dir = self.test_path / "dest_dir"
        dest_dir.mkdir()
        
        # Déplacer les fichiers et enregistrer les actions
        dest_files = []
        for file_path in files:
            dest_file = dest_dir / file_path.name
            shutil.move(str(file_path), str(dest_file))
            self.manager._record_action("move", file_path, dest_file)
            dest_files.append(dest_file)
        
        # Vérifier que les fichiers ont été déplacés
        for i, file_path in enumerate(files):
            self.assertFalse(file_path.exists())
            self.assertTrue(dest_files[i].exists())
        
        # Annuler les 2 dernières actions (les 2 premiers fichiers dans l'ordre inverse)
        result = self.manager.undo_last_action(count=2)
        
        # Vérifier que l'annulation a réussi
        self.assertTrue(result)
        
        # Vérifier que les 2 premiers fichiers ont été restaurés (dans l'ordre inverse de l'enregistrement)
        # Les fichiers sont traités dans l'ordre inverse de leur enregistrement
        self.assertTrue(files[2].exists())  # Le dernier enregistré est le premier annulé
        self.assertTrue(files[1].exists())  # L'avant-dernier enregistré est le deuxième annulé
        self.assertFalse(files[0].exists())  # Le premier enregistré n'a pas été annulé
        
        self.assertFalse(dest_files[2].exists())
        self.assertFalse(dest_files[1].exists())
        self.assertTrue(dest_files[0].exists())
        
        # Annuler toutes les actions restantes
        result = self.manager.undo_last_action(count=None)
        
        # Vérifier que l'annulation a réussi
        self.assertTrue(result)
        
        # Vérifier que tous les fichiers ont été restaurés
        for i, file_path in enumerate(files):
            self.assertTrue(file_path.exists())
            self.assertFalse(dest_files[i].exists())
    
    def test_get_action_history(self):
        """Teste la récupération de l'historique des actions."""
        # Créer des fichiers et enregistrer des actions
        for i in range(3):
            source = self.test_path / f"source_{i}.txt"
            source.write_text(f"Test file {i}")
            dest = self.test_path / f"dest_{i}.txt"
            self.manager._record_action("rename", source, dest)
        
        # Récupérer l'historique complet
        history = self.manager.get_action_history()
        
        # Vérifier que l'historique contient au moins les 3 actions que nous venons d'ajouter
        self.assertGreaterEqual(len(history), 3)
        
        # Vérifier que nos actions de renommage sont dans l'historique
        rename_actions = [action for action in history if action["type"] == "rename" 
                          and str(self.test_path) in action["source"]]
        self.assertGreaterEqual(len(rename_actions), 3)
        
        # Récupérer un historique limité
        limited_history = self.manager.get_action_history(limit=2)
        
        # Vérifier que l'historique est limité
        self.assertEqual(len(limited_history), 2)


if __name__ == "__main__":
    unittest.main() 