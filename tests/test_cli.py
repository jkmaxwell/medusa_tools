import pytest
import subprocess
from pathlib import Path

def test_cli_version():
    """Test the --version flag."""
    result = subprocess.run(['python', 'medusa_cli.py', '--version'], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert 'medusa_cli.py' in result.stdout

def test_cli_help():
    """Test the --help flag."""
    result = subprocess.run(['python', 'medusa_cli.py', '--help'], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert 'Commands' in result.stdout
    assert 'decompile' in result.stdout
    assert 'recompile' in result.stdout
    assert 'create' in result.stdout

def test_decompile_valid_file(valid_polyend_file, temp_output_dir):
    """Test decompiling a valid .polyend file."""
    result = subprocess.run(['python', 'medusa_cli.py', 'decompile', 
                           str(valid_polyend_file)],
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert 'Extracted 64 wavetables' in result.stdout
    
    # Verify the output directory contains the expected files
    waves_dir = valid_polyend_file.parent / 'waves'
    assert waves_dir.exists()
    wave_files = list(waves_dir.glob('wavetable_*.wav'))
    assert len(wave_files) == 64

def test_decompile_invalid_file(invalid_polyend_file):
    """Test decompiling an invalid .polyend file."""
    result = subprocess.run(['python', 'medusa_cli.py', 'decompile', 
                           str(invalid_polyend_file)],
                          capture_output=True, text=True)
    assert result.returncode == 1
    assert 'Error' in result.stderr

def test_recompile_valid_waves(sample_waves_dir, temp_output_dir):
    """Test recompiling valid WAV files."""
    output_file = temp_output_dir / 'recompiled.polyend'
    result = subprocess.run(['python', 'medusa_cli.py', 'recompile',
                           str(sample_waves_dir), str(output_file)],
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert 'Successfully recompiled 64 wavetables' in result.stdout
    assert output_file.exists()

def test_create_wavetable_bank(sample_waves_dir, temp_output_dir):
    """Test creating a wavetable bank."""
    output_file = temp_output_dir / 'created.polyend'
    result = subprocess.run(['python', 'medusa_cli.py', 'create',
                           str(sample_waves_dir), str(output_file)],
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert 'Successfully created wavetable bank' in result.stdout
    assert output_file.exists()

def test_create_wavetable_bank_random(sample_waves_dir, temp_output_dir):
    """Test creating a wavetable bank with random ordering."""
    output_file = temp_output_dir / 'created_random.polyend'
    result = subprocess.run(['python', 'medusa_cli.py', 'create',
                           str(sample_waves_dir), str(output_file), '--random'],
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert 'Successfully created wavetable bank' in result.stdout
    assert output_file.exists() 