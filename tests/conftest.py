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
def sample_waves_dir(test_data_dir):
    """Return the path to the sample waves directory."""
    return test_data_dir / 'valid' / 'waves' 