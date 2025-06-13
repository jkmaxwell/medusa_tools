import pytest
from medusa_core import decompile_wavetable, recompile_wavetable, create_wavetable_bank
from pathlib import Path

def test_decompile_wavetable_valid(valid_polyend_file, temp_output_dir):
    """Test decompile_wavetable function with valid input."""
    result = decompile_wavetable(str(valid_polyend_file), str(temp_output_dir))
    assert result['success'] is True
    assert result['num_wavetables'] == 64
    assert len(result['files']) == 64
    
    # Verify all files exist and have correct format
    for wav_file in result['files']:
        assert Path(wav_file).exists()
        assert Path(wav_file).suffix == '.wav'

def test_decompile_wavetable_invalid(invalid_polyend_file, temp_output_dir):
    """Test decompile_wavetable function with invalid input."""
    result = decompile_wavetable(str(invalid_polyend_file), str(temp_output_dir))
    assert result['success'] is False
    assert 'error' in result

def test_recompile_wavetable_valid(sample_waves_dir, temp_output_dir):
    """Test recompile_wavetable function with valid input."""
    output_file = temp_output_dir / 'recompiled.polyend'
    result = recompile_wavetable(str(sample_waves_dir), str(output_file))
    assert result['success'] is True
    assert result['num_wavetables'] == 64
    assert output_file.exists()
    assert output_file.stat().st_size > 0

def test_create_wavetable_bank_valid(sample_waves_dir, temp_output_dir):
    """Test create_wavetable_bank function with valid input."""
    output_file = temp_output_dir / 'created.polyend'
    result = create_wavetable_bank(str(sample_waves_dir), str(output_file))
    assert result['success'] is True
    assert result['num_wavetables'] == 64
    assert output_file.exists()
    assert output_file.stat().st_size > 0

def test_create_wavetable_bank_random(sample_waves_dir, temp_output_dir):
    """Test create_wavetable_bank function with random ordering."""
    output_file = temp_output_dir / 'created_random.polyend'
    result = create_wavetable_bank(str(sample_waves_dir), str(output_file), random_order=True)
    assert result['success'] is True
    assert result['num_wavetables'] == 64
    assert output_file.exists()
    assert output_file.stat().st_size > 0 