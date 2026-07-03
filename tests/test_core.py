import struct
import wave
import pytest
from medusa_core import (decompile_wavetable, recompile_wavetable,
                         create_wavetable_bank, process_wavs,
                         TOTAL_FILE_SIZE, DATA_OFFSET)
from pathlib import Path

def write_wav(path, value, n_frames=1000, rate=44100, width=2, channels=1):
    """Write a WAV file with every sample set to a constant value."""
    if width == 2:
        frame = struct.pack('<h', value) * channels
    elif width == 3:
        frame = value.to_bytes(3, 'little', signed=True) * channels
    else:
        raise ValueError(width)
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(width)
        wav.setframerate(rate)
        wav.writeframes(frame * n_frames)

def read_first_sample(path):
    with wave.open(str(path), 'rb') as wav:
        return struct.unpack('<h', wav.readframes(1))[0]

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

def test_decompile_rejects_wrong_header(tmp_path):
    """A correctly-sized file without the header marker must be rejected."""
    bogus = tmp_path / 'bogus.polyend'
    bogus.write_bytes(b'\xff' * TOTAL_FILE_SIZE)
    result = decompile_wavetable(str(bogus), str(tmp_path / 'out'))
    assert result['success'] is False
    assert 'header' in result['error'].lower()

def test_create_alphabetical_order(tmp_path):
    """Alphabetical mode must sort inputs even when there are fewer than 64."""
    write_wav(tmp_path / 'b.wav', -1000)
    write_wav(tmp_path / 'a.wav', 1000)
    output_file = tmp_path / 'bank.polyend'
    result = create_wavetable_bank(str(tmp_path), str(output_file))
    assert result['success'] is True

    waves = tmp_path / 'decompiled'
    assert decompile_wavetable(str(output_file), str(waves))['success']
    # slot 0 should hold a.wav (constant +1000), slot 1 b.wav (constant -1000)
    assert abs(read_first_sample(waves / 'wavetable_00.wav') - 1000) <= 1
    assert abs(read_first_sample(waves / 'wavetable_01.wav') + 1000) <= 1

def test_create_cycles_sources_below_64(tmp_path):
    """With fewer than 64 inputs, sources cycle so every slot has sound."""
    write_wav(tmp_path / 'a.wav', 1000)
    write_wav(tmp_path / 'b.wav', -1000)
    output_file = tmp_path / 'bank.polyend'
    result = create_wavetable_bank(str(tmp_path), str(output_file))
    assert result['success'] is True
    assert result['num_wavetables'] == 64
    assert len(result['source_files']) == 2

    waves = tmp_path / 'decompiled'
    assert decompile_wavetable(str(output_file), str(waves))['success']
    wt = {i: (waves / f'wavetable_{i:02d}.wav').read_bytes() for i in (0, 1, 2, 3, 62, 63)}
    assert wt[0] == wt[2] == wt[62]  # a.wav in every even slot
    assert wt[1] == wt[3] == wt[63]  # b.wav in every odd slot
    assert wt[0] != wt[1]

def test_recompile_incomplete_dir_gives_clear_error(tmp_path):
    """Recompiling from too few files should say how many were found."""
    for i in range(3):
        write_wav(tmp_path / f'wavetable_{i:02d}.wav', 100)
    result = recompile_wavetable(str(tmp_path), str(tmp_path / 'out.polyend'))
    assert result['success'] is False
    assert '3 of 64' in result['error']

def test_process_wavs_resamples_to_44100(tmp_path):
    """Non-44.1kHz input must be resampled, not just relabeled."""
    src = tmp_path / 'in'
    src.mkdir()
    write_wav(src / 'half.wav', 500, n_frames=1000, rate=22050)
    result = process_wavs(str(src), str(tmp_path / 'out'))
    assert result['success'] is True
    with wave.open(result['files'][0], 'rb') as wav:
        assert wav.getframerate() == 44100
        assert abs(wav.getnframes() - 2000) <= 2  # duration preserved

def test_process_wavs_converts_24bit(tmp_path):
    """24-bit input must be converted to valid 16-bit output."""
    src = tmp_path / 'in'
    src.mkdir()
    write_wav(src / 'deep.wav', 1000 << 8, width=3)  # 24-bit value == 1000 at 16-bit
    result = process_wavs(str(src), str(tmp_path / 'out'))
    assert result['success'] is True
    with wave.open(result['files'][0], 'rb') as wav:
        assert wav.getsampwidth() == 2
    assert read_first_sample(result['files'][0]) == 1000

def test_process_wavs_stereo_to_mono(tmp_path):
    """Stereo input is averaged down to mono."""
    src = tmp_path / 'in'
    src.mkdir()
    write_wav(src / 'stereo.wav', 800, channels=2)
    result = process_wavs(str(src), str(tmp_path / 'out'))
    assert result['success'] is True
    with wave.open(result['files'][0], 'rb') as wav:
        assert wav.getnchannels() == 1
    assert read_first_sample(result['files'][0]) == 800