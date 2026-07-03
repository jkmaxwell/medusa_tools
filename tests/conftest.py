import os
import pytest
import shutil
from pathlib import Path

@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return Path(__file__).parent / 'data'

@pytest.fixture
def valid_polyend_file(test_data_dir):
    """Return the path to a valid .polyend file."""
    return test_data_dir / 'valid' / 'vox_wavetables.polyend'

@pytest.fixture
def invalid_polyend_file(test_data_dir):
    """Return the path to an invalid .polyend file."""
    return test_data_dir / 'invalid' / 'incomplete.polyend'

@pytest.fixture
def temp_output_dir(tmp_path):
    """Create and return a temporary directory for test outputs."""
    output_dir = tmp_path / 'test_output'
    output_dir.mkdir()
    yield output_dir
    # Cleanup after test
    shutil.rmtree(output_dir)

@pytest.fixture
def sample_waves_dir(valid_polyend_file, tmp_path):
    """Generate the 64 wavetable WAVs by decompiling the valid fixture file."""
    from medusa_core import decompile_wavetable
    waves_dir = tmp_path / 'sample_waves'
    result = decompile_wavetable(str(valid_polyend_file), str(waves_dir))
    assert result['success'], f"fixture decompile failed: {result.get('error')}"
    return waves_dir