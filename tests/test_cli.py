import sys
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def run_cli(*args):
    return subprocess.run([sys.executable, 'medusa_cli.py', *args],
                          capture_output=True, text=True, cwd=PROJECT_ROOT)

def test_cli_version():
    """Test the --version flag."""
    result = run_cli('--version')
    assert result.returncode == 0
    assert 'medusa_cli.py' in result.stdout

def test_cli_help():
    """Test the --help flag."""
    result = run_cli('--help')
    assert result.returncode == 0
    assert 'Commands' in result.stdout
    assert 'decompile' in result.stdout
    assert 'recompile' in result.stdout
    assert 'create' in result.stdout

def test_decompile_valid_file(valid_polyend_file, tmp_path):
    """Test decompiling a valid .polyend file."""
    # Copy the fixture so the default 'waves' output lands in the temp dir
    input_copy = tmp_path / valid_polyend_file.name
    shutil.copyfile(valid_polyend_file, input_copy)

    result = run_cli('decompile', str(input_copy))
    assert result.returncode == 0
    assert 'Extracted 64 wavetables' in result.stdout

    waves_dir = tmp_path / 'waves'
    assert waves_dir.exists()
    wave_files = list(waves_dir.glob('wavetable_*.wav'))
    assert len(wave_files) == 64

def test_decompile_invalid_file(invalid_polyend_file):
    """Test decompiling an invalid .polyend file."""
    result = run_cli('decompile', str(invalid_polyend_file))
    assert result.returncode == 1
    assert 'Error' in result.stderr

def test_recompile_valid_waves(sample_waves_dir, temp_output_dir):
    """Test recompiling valid WAV files."""
    output_file = temp_output_dir / 'recompiled.polyend'
    result = run_cli('recompile', str(sample_waves_dir), str(output_file))
    assert result.returncode == 0
    assert 'Successfully recompiled 64 wavetables' in result.stdout
    assert output_file.exists()

def test_create_wavetable_bank(sample_waves_dir, temp_output_dir):
    """Test creating a wavetable bank."""
    output_file = temp_output_dir / 'created.polyend'
    result = run_cli('create', str(sample_waves_dir), str(output_file))
    assert result.returncode == 0
    assert 'Successfully created wavetable bank' in result.stdout
    assert output_file.exists()

def test_create_wavetable_bank_random(sample_waves_dir, temp_output_dir):
    """Test creating a wavetable bank with random ordering."""
    output_file = temp_output_dir / 'created_random.polyend'
    result = run_cli('create', str(sample_waves_dir), str(output_file), '--random')
    assert result.returncode == 0
    assert 'Successfully created wavetable bank' in result.stdout
    assert output_file.exists() 