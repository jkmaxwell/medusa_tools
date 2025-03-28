#!/usr/bin/env python3

import unittest
import os
import shutil
import wave
import filecmp
from pathlib import Path
import subprocess
import numpy as np

class TestMedusaTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create test directories"""
        cls.test_dir = Path("test_output")
        cls.test_dir.mkdir(exist_ok=True)
        
        # Subdirectories for different test phases
        cls.decompile_dir = cls.test_dir / "decompiled"
        cls.recompile_dir = cls.test_dir / "recompiled"
        cls.process_dir = cls.test_dir / "processed"
        
        for dir in [cls.decompile_dir, cls.recompile_dir, cls.process_dir]:
            if dir.exists():
                shutil.rmtree(dir)
            dir.mkdir()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test directories"""
        shutil.rmtree(cls.test_dir)
    
    def run_command(self, cmd):
        """Run a command and return its output"""
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result
    
    def test_01_decompile(self):
        """Test wavetable decompilation"""
        cmd = [
            "python3",
            "medusa_wavetable_tool.py",
            "decompile",
            "medusa64Wavetables.polyend",
            "--output",
            str(self.decompile_dir)
        ]
        result = self.run_command(cmd)
        
        # Check command succeeded
        self.assertEqual(result.returncode, 0, f"Decompile failed: {result.stderr}")
        
        # Check all files were created
        for i in range(64):
            wav_file = self.decompile_dir / f"wavetable_{i:02d}.wav"
            id_file = self.decompile_dir / f"wavetable_{i:02d}.id"
            
            self.assertTrue(wav_file.exists(), f"Missing WAV file: {wav_file}")
            self.assertTrue(id_file.exists(), f"Missing ID file: {id_file}")
            
            # Check WAV file format
            with wave.open(str(wav_file), 'rb') as wav:
                self.assertEqual(wav.getnchannels(), 1, "WAV should be mono")
                self.assertEqual(wav.getsampwidth(), 2, "WAV should be 16-bit")
                self.assertEqual(wav.getframerate(), 44100, "WAV should be 44.1kHz")
    
    def test_02_recompile(self):
        """Test wavetable recompilation"""
        output_file = self.recompile_dir / "recompiled.polyend"
        cmd = [
            "python3",
            "medusa_wavetable_tool.py",
            "recompile",
            str(self.decompile_dir),
            "--output",
            str(output_file),
            "--verify-with",
            "medusa64Wavetables.polyend"
        ]
        result = self.run_command(cmd)
        
        # Check command succeeded
        self.assertEqual(result.returncode, 0, f"Recompile failed: {result.stderr}")
        
        # Verify file exists and matches original
        self.assertTrue(output_file.exists(), "Recompiled file not created")
        self.assertTrue(
            filecmp.cmp(str(output_file), "medusa64Wavetables.polyend", shallow=False),
            "Recompiled file differs from original"
        )
    
    def test_03_wav_processor(self):
        """Test WAV file processor"""
        # Create a test WAV file (stereo, different sample rate)
        test_wav = self.process_dir / "test.wav"
        samples = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 48000))
        stereo_samples = np.column_stack((samples, samples))
        with wave.open(str(test_wav), 'wb') as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(48000)
            wav.writeframes(stereo_samples.astype(np.int16).tobytes())
        
        # Process the WAV file
        output_dir = self.process_dir / "output"
        cmd = [
            "python3",
            "medusa_wav_preprocessor.py",
            str(self.process_dir),
            str(output_dir)
        ]
        result = self.run_command(cmd)
        
        # Check command succeeded
        self.assertEqual(result.returncode, 0, f"WAV processing failed: {result.stderr}")
        
        # Check processed file
        processed_wav = output_dir / "wavetable_00.wav"
        self.assertTrue(processed_wav.exists(), "Processed WAV not created")
        
        with wave.open(str(processed_wav), 'rb') as wav:
            self.assertEqual(wav.getnchannels(), 1, "Processed WAV should be mono")
            self.assertEqual(wav.getsampwidth(), 2, "Processed WAV should be 16-bit")
            self.assertEqual(wav.getframerate(), 44100, "Processed WAV should be 44.1kHz")
    
    def test_04_error_handling(self):
        """Test error handling"""
        # Test invalid input file
        cmd = [
            "python3",
            "medusa_wavetable_tool.py",
            "decompile",
            "nonexistent.polyend",
            "--output",
            str(self.decompile_dir)
        ]
        result = self.run_command(cmd)
        self.assertNotEqual(result.returncode, 0, "Should fail with nonexistent file")
        
        # Test invalid output directory
        cmd = [
            "python3",
            "medusa_wavetable_tool.py",
            "decompile",
            "medusa64Wavetables.polyend",
            "--output",
            "/nonexistent/directory"
        ]
        result = self.run_command(cmd)
        self.assertNotEqual(result.returncode, 0, "Should fail with invalid directory")

if __name__ == '__main__':
    unittest.main(verbosity=2)