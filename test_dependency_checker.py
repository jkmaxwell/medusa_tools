#!/usr/bin/env python3

import unittest
import subprocess
from unittest.mock import patch
from dependency_checker import check_ffmpeg

class TestDependencyChecker(unittest.TestCase):
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_ffmpeg_installed(self, mock_run, mock_which):
        # Mock ffmpeg being installed and working
        mock_which.return_value = '/usr/local/bin/ffmpeg'
        mock_run.return_value.stdout = 'ffmpeg version 4.2.3\nother info...'
        mock_run.return_value.returncode = 0
        
        result = check_ffmpeg()
        self.assertTrue(result['installed'])
        self.assertIsNotNone(result['version'])
        self.assertIsNone(result['error'])
        self.assertIsNone(result['install_instructions'])
    
    @patch('shutil.which')
    def test_ffmpeg_not_installed(self, mock_which):
        # Mock ffmpeg not being installed
        mock_which.return_value = None
        
        result = check_ffmpeg()
        self.assertFalse(result['installed'])
        self.assertIsNone(result['version'])
        self.assertIsNotNone(result['error'])
        self.assertIsNotNone(result['install_instructions'])
        self.assertIn('brew install ffmpeg', result['install_instructions'])
    
    @patch('shutil.which')
    @patch('subprocess.run')
    def test_ffmpeg_installed_but_broken(self, mock_run, mock_which):
        # Mock ffmpeg being installed but failing to run
        mock_which.return_value = '/usr/local/bin/ffmpeg'
        mock_run.side_effect = subprocess.CalledProcessError(1, 'ffmpeg')
        
        result = check_ffmpeg()
        self.assertFalse(result['installed'])
        self.assertIsNone(result['version'])
        self.assertIsNotNone(result['error'])
        self.assertIsNotNone(result['install_instructions'])

if __name__ == '__main__':
    unittest.main()