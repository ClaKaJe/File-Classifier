#!/usr/bin/env python3
"""Tests pour le module cli."""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import argparse
import io
import sys

from file_classifier.file_classifier.cli import (
    create_parser,
    handle_sort,
    handle_rename,
    handle_duplicates,
    handle_clean,
    handle_report,
    handle_history,
    handle_undo,
    main
)


class TestCLI(unittest.TestCase):
    """Tests pour l'interface en ligne de commande."""
    
    def setUp(self):
        """Initialisation avant chaque test."""
        # Créer un répertoire temporaire pour les tests
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)
        
        # Créer quelques fichiers de test
        (self.test_path / "test1.txt").write_text("Test file 1")
        (self.test_path / "test2.jpg").write_text("Test file 2")
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        self.test_dir.cleanup()
    
    def test_create_parser(self):
        """Teste la création du parseur d'arguments."""
        parser = create_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)
        
        # Vérifier quelques options de base
        with self.assertRaises(SystemExit):
            args = parser.parse_args(["--version"])
        
        args = parser.parse_args(["sort", "/tmp"])
        self.assertEqual(args.command, "sort")
        self.assertEqual(args.directory, "/tmp")
        self.assertEqual(args.criteria, "type")  # valeur par défaut
        
        args = parser.parse_args(["rename", "/tmp", "pattern", "replacement"])
        self.assertEqual(args.command, "rename")
        self.assertEqual(args.pattern, "pattern")
        self.assertEqual(args.replacement, "replacement")
    
    @patch("file_classifier.file_classifier.cli.FileManager")
    def test_handle_sort(self, mock_manager_class):
        """Teste la fonction handle_sort."""
        # Configurer le mock
        mock_manager = mock_manager_class.return_value
        mock_manager.sort_files.return_value = {
            "images": [self.test_path / "test2.jpg"],
            "other": [self.test_path / "test1.txt"]
        }
        
        # Créer les arguments
        args = argparse.Namespace(
            directory=str(self.test_path),
            criteria="type",
            recursive=False,
            dry_run=True,
            verbose=False
        )
        
        # Capturer la sortie standard
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            result = handle_sort(args)
        
        # Vérifier le résultat
        self.assertEqual(result, 0)  # Succès
        mock_manager.sort_files.assert_called_once_with(
            str(self.test_path),
            criteria="type",
            recursive=False,
            dry_run=True
        )
        
        # Vérifier la sortie
        output = fake_stdout.getvalue()
        self.assertIn("Fichiers triés par type", output)
        self.assertIn("images: 1 fichiers", output)
        self.assertIn("other: 1 fichiers", output)
        self.assertIn("Mode simulation", output)
    
    @patch("file_classifier.file_classifier.cli.FileManager")
    def test_handle_rename(self, mock_manager_class):
        """Teste la fonction handle_rename."""
        # Configurer le mock
        mock_manager = mock_manager_class.return_value
        mock_manager.rename_batch.return_value = {
            self.test_path / "test1.txt": self.test_path / "renamed1.txt"
        }
        
        # Créer les arguments
        args = argparse.Namespace(
            directory=str(self.test_path),
            pattern="test(\\d+)",
            replacement="renamed\\1",
            recursive=False,
            dry_run=True
        )
        
        # Capturer la sortie standard
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            result = handle_rename(args)
        
        # Vérifier le résultat
        self.assertEqual(result, 0)  # Succès
        mock_manager.rename_batch.assert_called_once()
        
        # Vérifier la sortie
        output = fake_stdout.getvalue()
        self.assertIn("Fichiers renommés", output)
        self.assertIn("test1.txt -> renamed1.txt", output)
        self.assertIn("Mode simulation", output)
    
    @patch("file_classifier.file_classifier.cli.FileManager")
    def test_handle_duplicates(self, mock_manager_class):
        """Teste la fonction handle_duplicates."""
        # Configurer le mock
        mock_manager = mock_manager_class.return_value
        mock_manager.find_duplicates.return_value = {
            "hash123": [self.test_path / "file1.txt", self.test_path / "file2.txt"]
        }
        
        # Créer les arguments
        args = argparse.Namespace(
            directories=[str(self.test_path)],
            output=None,
            json=False
        )
        
        # Capturer la sortie standard
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            result = handle_duplicates(args)
        
        # Vérifier le résultat
        self.assertEqual(result, 0)  # Succès
        mock_manager.find_duplicates.assert_called_once_with([str(self.test_path)])
        
        # Vérifier la sortie
        output = fake_stdout.getvalue()
        self.assertIn("Fichiers en double", output)
        self.assertIn("Groupe (hash: hash123", output)
    
    @patch("file_classifier.file_classifier.cli.FileManager")
    def test_handle_clean(self, mock_manager_class):
        """Teste la fonction handle_clean."""
        # Configurer le mock
        mock_manager = mock_manager_class.return_value
        mock_manager.clean_temp_files.return_value = [self.test_path / "temp.tmp"]
        
        # Créer les arguments
        args = argparse.Namespace(
            directory=str(self.test_path),
            temp=True,
            old=None,
            recursive=False,
            dry_run=True,
            verbose=False
        )
        
        # Capturer la sortie standard
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            result = handle_clean(args)
        
        # Vérifier le résultat
        self.assertEqual(result, 0)  # Succès
        mock_manager.clean_temp_files.assert_called_once()
        
        # Vérifier la sortie
        output = fake_stdout.getvalue()
        self.assertIn("Fichiers temporaires: 1 fichiers", output)
        self.assertIn("Mode simulation", output)
    
    @patch("file_classifier.file_classifier.cli.FileManager")
    def test_handle_report(self, mock_manager_class):
        """Teste la fonction handle_report."""
        # Configurer le mock
        mock_manager = mock_manager_class.return_value
        mock_manager.generate_report.return_value = "Rapport de test"
        
        # Créer les arguments
        args = argparse.Namespace(
            directory=str(self.test_path),
            recursive=False,
            output=None,
            json=False,
            human_readable=False
        )
        
        # Capturer la sortie standard
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            result = handle_report(args)
        
        # Vérifier le résultat
        self.assertEqual(result, 0)  # Succès
        mock_manager.generate_report.assert_called_once_with(
            str(self.test_path),
            recursive=False,
            output_format="text",
            human_readable=False
        )
        
        # Vérifier la sortie
        output = fake_stdout.getvalue()
        self.assertEqual(output.strip(), "Rapport de test")
        
        # Tester avec l'option JSON
        mock_manager.generate_report.reset_mock()
        args.json = True
        args.human_readable = False
        
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            result = handle_report(args)
        
        self.assertEqual(result, 0)
        mock_manager.generate_report.assert_called_once_with(
            str(self.test_path),
            recursive=False,
            output_format="json",
            human_readable=False
        )
        
        # Tester avec l'option human_readable
        mock_manager.generate_report.reset_mock()
        args.json = True
        args.human_readable = True
        
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            result = handle_report(args)
        
        self.assertEqual(result, 0)
        mock_manager.generate_report.assert_called_once_with(
            str(self.test_path),
            recursive=False,
            output_format="json",
            human_readable=True
        )
    
    @patch("file_classifier.file_classifier.cli.FileManager")
    def test_handle_history(self, mock_manager_class):
        """Teste la fonction handle_history."""
        # Configurer le mock
        mock_manager = mock_manager_class.return_value
        mock_manager.get_action_history.return_value = [
            {
                "id": 1,
                "type": "move",
                "source": "/path/to/source.txt",
                "destination": "/path/to/dest.txt",
                "timestamp": "2025-05-20 15:45:23"
            }
        ]
        
        # Créer les arguments
        args = argparse.Namespace(
            count=None,
            json=False
        )
        
        # Capturer la sortie standard
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            result = handle_history(args)
        
        # Vérifier le résultat
        self.assertEqual(result, 0)  # Succès
        mock_manager.get_action_history.assert_called_once_with(None)
        
        # Vérifier la sortie
        output = fake_stdout.getvalue()
        self.assertIn("Historique des actions", output)
        self.assertIn("DÉPLACEMENT", output)
        
        # Tester avec l'option JSON
        mock_manager.get_action_history.reset_mock()
        args.json = True
        
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            result = handle_history(args)
        
        self.assertEqual(result, 0)
        mock_manager.get_action_history.assert_called_once_with(None)
        
        # Vérifier que la sortie est au format JSON
        output = fake_stdout.getvalue()
        self.assertTrue(output.strip().startswith("["))
        self.assertTrue(output.strip().endswith("]"))
    
    @patch("file_classifier.file_classifier.cli.FileManager")
    @patch("builtins.input", return_value="o")  # Simuler une réponse "oui" à la confirmation
    def test_handle_undo(self, mock_input, mock_manager_class):
        """Teste la fonction handle_undo."""
        # Configurer le mock
        mock_manager = mock_manager_class.return_value
        mock_manager.undo_last_action.return_value = True
        mock_manager.get_action_history.return_value = [
            {
                "id": 1,
                "type": "move",
                "source": "/path/to/source.txt",
                "destination": "/path/to/dest.txt",
                "timestamp": "2025-05-20 15:45:23"
            }
        ]
        
        # Créer les arguments pour undo simple
        args = argparse.Namespace(
            count=None,
            all=False
        )
        
        # Capturer la sortie standard
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            result = handle_undo(args)
        
        # Vérifier le résultat
        self.assertEqual(result, 0)  # Succès
        mock_manager.undo_last_action.assert_called_once_with(None)
        
        # Vérifier la sortie
        output = fake_stdout.getvalue()
        self.assertIn("Dernière action annulée avec succès", output)
        
        # Tester avec l'option --all
        mock_manager.undo_last_action.reset_mock()
        mock_manager.get_action_history.reset_mock()
        args.all = True
        
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            result = handle_undo(args)
        
        self.assertEqual(result, 0)
        mock_manager.undo_last_action.assert_called_once_with(None)
        mock_manager.get_action_history.assert_called_once()
        
        # Vérifier la sortie
        output = fake_stdout.getvalue()
        self.assertIn("Toutes les actions ont été annulées avec succès", output)
        
        # Tester avec l'option --count
        mock_manager.undo_last_action.reset_mock()
        mock_manager.get_action_history.reset_mock()
        args.all = False
        args.count = 3
        
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            result = handle_undo(args)
        
        self.assertEqual(result, 0)
        mock_manager.undo_last_action.assert_called_once_with(3)
        mock_manager.get_action_history.assert_called_once_with(3)
        
        # Vérifier la sortie
        output = fake_stdout.getvalue()
        self.assertIn("Les 3 dernières actions ont été annulées avec succès", output)
    
    @patch("file_classifier.file_classifier.cli.handle_sort")
    @patch("file_classifier.file_classifier.cli.create_parser")
    def test_main_with_sort(self, mock_create_parser, mock_handle_sort):
        """Teste la fonction main avec la commande sort."""
        # Configurer les mocks
        mock_parser = MagicMock()
        mock_create_parser.return_value = mock_parser
        
        args = argparse.Namespace(
            command="sort",
            verbose=False,
            directory="/tmp"
        )
        mock_parser.parse_args.return_value = args
        
        mock_handle_sort.return_value = 0
        
        # Exécuter main
        result = main()
        
        # Vérifier le résultat
        self.assertEqual(result, 0)
        mock_handle_sort.assert_called_once_with(args)
    
    @patch("file_classifier.file_classifier.cli.setup_logging")
    @patch("file_classifier.file_classifier.cli.create_parser")
    def test_main_without_command(self, mock_create_parser, mock_setup_logging):
        """Teste la fonction main sans commande."""
        # Configurer les mocks
        mock_parser = MagicMock()
        mock_create_parser.return_value = mock_parser
        
        args = argparse.Namespace(
            command=None,
            verbose=False
        )
        mock_parser.parse_args.return_value = args
        
        # Exécuter main
        result = main()
        
        # Vérifier le résultat
        self.assertEqual(result, 0)
        mock_parser.print_help.assert_called_once()


if __name__ == "__main__":
    unittest.main() 