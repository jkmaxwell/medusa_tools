#!/usr/bin/env python3

import unittest
import subprocess
import os
from unittest.mock import patch, MagicMock
from dependency_checker import check_ffmpeg

class TestDependencyChecker(unittest.TestCase):
    def setUp(self):
        self.version_output = 'ffmpeg version 4.2.3\nother info...'
        self.mock_result = MagicMock()
        self.mock_result.stdout = self.version_output
        self.mock_result.returncode = 0

    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_ffmpeg_in_path(self, mock_exists, mock_run, mock_which):
        # Mock ffmpeg being in PATH
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.return_value = True
        mock_run.return_value = self.mock_result
        
        result = check_ffmpeg()
        self.assertTrue(result['installed'])
        self.assertEqual(result['path'], '/usr/bin/ffmpeg')
        self.assertEqual(result['version'], self.version_output)
        self.assertIsNone(result['error'])
    
    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_ffmpeg_in_homebrew(self, mock_exists, mock_run, mock_which):
        # Mock ffmpeg being in Homebrew location but not in PATH
        mock_which.return_value = None
        mock_exists.side_effect = lambda p: p == '/usr/local/bin/ffmpeg'
        mock_run.return_value = self.mock_result
        
        result = check_ffmpeg()
        self.assertTrue(result['installed'])
        self.assertEqual(result['path'], '/usr/local/bin/ffmpeg')
        self.assertEqual(result['version'], self.version_output)
        self.assertIsNone(result['error'])
    
    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_ffmpeg_custom_path(self, mock_exists, mock_run, mock_which):
        # Mock ffmpeg being in custom location
        custom_path = '/custom/path/ffmpeg'
        mock_which.return_value = None
        mock_exists.side_effect = lambda p: p == custom_path
        mock_run.return_value = self.mock_result
        
        result = check_ffmpeg(custom_path=custom_path)
        self.assertTrue(result['installed'])
        self.assertEqual(result['path'], custom_path)
        self.assertEqual(result['version'], self.version_output)
        self.assertIsNone(result['error'])
    
    @patch('shutil.which')
    @patch('os.path.exists')
    def test_ffmpeg_not_found(self, mock_exists, mock_which):
        # Mock ffmpeg not being found anywhere
        mock_which.return_value = None
        mock_exists.return_value = False
        
        result = check_ffmpeg()
        self.assertFalse(result['installed'])
        self.assertIsNone(result['version'])
        self.assertIn('not installed or not in system PATH', result['error'])
        self.assertIn('brew install ffmpeg', result['install_instructions'])
    
    @patch('shutil.which')
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_ffmpeg_permission_error(self, mock_exists, mock_run, mock_which):
        # Mock ffmpeg being found but having permission issues
        mock_which.return_value = '/usr/bin/ffmpeg'
        mock_exists.return_value = True
        mock_run.side_effect = PermissionError()
        
        result = check_ffmpeg()
        self.assertFalse(result['installed'])
        self.assertIn('not working correctly', result['error'])
        self.assertIsNotNone(result['install_instructions'])

if __name__ == '__main__':
    unittest.main()