#!/usr/bin/env python3

import os
import wave
import struct
import shutil
from pathlib import Path

# Constants
WAVETABLE_SIZE = 16000  # 0x3E80 bytes per wavetable
HEADER_MARKER = b'\x02\x00\x00\x3c'
FIRST_HEADER_MARKER = b'\x21\x00\x01\x00'
SUBHEADER_MARKER = b'\x04\x00\x00\x3c'
DATA_OFFSET = 0x80  # Fixed offset where waveform data starts
NUM_WAVETABLES = 64  # Fixed number of wavetables
IDENTIFIER_SIZE = 4  # Size of identifier bytes after header
TOTAL_FILE_SIZE = 1024128  # Exact size of the file

# Fixed identifiers for each wavetable position
WAVETABLE_IDENTIFIERS = [
    bytes.fromhex("00000000"),  # wavetable_00
    bytes.fromhex("124576e3"),  # wavetable_01
    bytes.fromhex("ad8d97b2"),  # wavetable_02
    bytes.fromhex("6555d03b"),  # wavetable_03
    bytes.fromhex("f2d0b36f"),  # wavetable_04
    bytes.fromhex("3582c2f8"),  # wavetable_05
    bytes.fromhex("06336fb9"),  # wavetable_06
    bytes.fromhex("635574bd"),  # wavetable_07
    bytes.fromhex("67a28fbd"),  # wavetable_08
    bytes.fromhex("f020f9d1"),  # wavetable_09
    bytes.fromhex("143717b0"),  # wavetable_10
    bytes.fromhex("d2189304"),  # wavetable_11
    bytes.fromhex("7e7b65bd"),  # wavetable_12
    bytes.fromhex("70976321"),  # wavetable_13
    bytes.fromhex("fd12da9c"),  # wavetable_14
    bytes.fromhex("f17762e7"),  # wavetable_15
    bytes.fromhex("5d784c83"),  # wavetable_16
    bytes.fromhex("a4bb7f66"),  # wavetable_17
    bytes.fromhex("a386dbe9"),  # wavetable_18
    bytes.fromhex("e3812174"),  # wavetable_19
    bytes.fromhex("0cc1755f"),  # wavetable_20
    bytes.fromhex("abe9460d"),  # wavetable_21
    bytes.fromhex("19ce5703"),  # wavetable_22
    bytes.fromhex("39bdeab0"),  # wavetable_23
    bytes.fromhex("24ee3e0f"),  # wavetable_24
    bytes.fromhex("0c2c88de"),  # wavetable_25
    bytes.fromhex("69d0d9b6"),  # wavetable_26
    bytes.fromhex("de7a4bd8"),  # wavetable_27
    bytes.fromhex("d2b017ce"),  # wavetable_28
    bytes.fromhex("a1e25751"),  # wavetable_29
    bytes.fromhex("7febb4f4"),  # wavetable_30
    bytes.fromhex("bc4a4f83"),  # wavetable_31
    bytes.fromhex("3c60bb82"),  # wavetable_32
    bytes.fromhex("271fc339"),  # wavetable_33
    bytes.fromhex("9ab42b4d"),  # wavetable_34
    bytes.fromhex("ea8dd836"),  # wavetable_35
    bytes.fromhex("3acf4ce6"),  # wavetable_36
    bytes.fromhex("d3656948"),  # wavetable_37
    bytes.fromhex("251ab246"),  # wavetable_38
    bytes.fromhex("d4ddfcb6"),  # wavetable_39
    bytes.fromhex("617306d7"),  # wavetable_40
    bytes.fromhex("eb92b522"),  # wavetable_41
    bytes.fromhex("f3708db7"),  # wavetable_42
    bytes.fromhex("878266aa"),  # wavetable_43
    bytes.fromhex("fc7be8db"),  # wavetable_44
    bytes.fromhex("7e611ff1"),  # wavetable_45
    bytes.fromhex("49322d75"),  # wavetable_46
    bytes.fromhex("4133f82c"),  # wavetable_47
    bytes.fromhex("7b59e052"),  # wavetable_48
    bytes.fromhex("de3a2887"),  # wavetable_49
    bytes.fromhex("6736d446"),  # wavetable_50
    bytes.fromhex("82ab5d61"),  # wavetable_51
    bytes.fromhex("bebeb658"),  # wavetable_52
    bytes.fromhex("c8601db1"),  # wavetable_53
    bytes.fromhex("b8d31730"),  # wavetable_54
    bytes.fromhex("9e81175d"),  # wavetable_55
    bytes.fromhex("411dea48"),  # wavetable_56
    bytes.fromhex("c1907f80"),  # wavetable_57
    bytes.fromhex("81e323eb"),  # wavetable_58
    bytes.fromhex("0431f6cb"),  # wavetable_59
    bytes.fromhex("40e4c30e"),  # wavetable_60
    bytes.fromhex("960a509e"),  # wavetable_61
    bytes.fromhex("5e4c5779"),  # wavetable_62
    bytes.fromhex("47025f65"),  # wavetable_63
]

# Fixed data for the file footer
FOOTER_DATA = (
    # Header at 0x0fa000
    b'\x02\x00\x00\x3c\x1f\x38\xf2\xe1' +
    # Zeros until 0x0fa040
    b'\x00' * (0x40 - 8) +
    # Data at 0x0fa040
    b'\x21\x00\x00\x00' +
    # Rest is zeros
    b'\x00' * (TOTAL_FILE_SIZE - (NUM_WAVETABLES * WAVETABLE_SIZE) - 0x44)
)

def decompile_wavetable(input_file, output_dir=None):
    """Extract wavetables from .polyend file to WAV files."""
    try:
        # Use waves directory next to input file if no output dir specified
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(input_file), 'waves')
        os.makedirs(output_dir, exist_ok=True)
        
        # Read the polyend file
        with open(input_file, 'rb') as f:
            data = f.read()
        
        # Extract wavetables
        num_wavetables = len(data) // WAVETABLE_SIZE
        extracted_files = []
        
        for i in range(num_wavetables):
            # Extract wavetable data
            start = i * WAVETABLE_SIZE
            end = start + WAVETABLE_SIZE
            wavetable_data = data[start:end]
            
            # Extract waveform data (starts at offset 0x80)
            waveform_data = wavetable_data[DATA_OFFSET:]
            
            # Convert to WAV format
            wav_file = os.path.join(output_dir, f'wavetable_{i:02d}.wav')
            with wave.open(wav_file, 'wb') as wav:
                wav.setnchannels(1)  # mono
                wav.setsampwidth(2)  # 16-bit
                wav.setframerate(44100)  # 44.1kHz
                wav.writeframes(waveform_data)
            
            extracted_files.append(wav_file)
        
        return {
            'success': True,
            'num_wavetables': num_wavetables,
            'output_dir': output_dir,
            'files': extracted_files
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def recompile_wavetable(input_dir, output_file):
    """Create .polyend file from WAV files."""
    try:
        wavetables = []
        processed_files = []
        
        for i in range(NUM_WAVETABLES):
            wav_file = os.path.join(input_dir, f'wavetable_{i:02d}.wav')
            
            if not os.path.exists(wav_file):
                raise Exception(f"Missing wavetable_{i:02d}.wav")
            
            with wave.open(wav_file, 'rb') as wav:
                if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
                    raise Exception(f"Invalid format in {wav_file}")
                waveform_data = wav.readframes(wav.getnframes())
            
            # Create wavetable section
            result = bytearray(WAVETABLE_SIZE)
            
            # Write header
            header = FIRST_HEADER_MARKER if i == 0 else HEADER_MARKER
            result[0:4] = header
            
            # Write identifier
            result[4:8] = WAVETABLE_IDENTIFIERS[i]
            
            # Write subheader
            result[0x40:0x44] = SUBHEADER_MARKER
            result[0x44:0x46] = struct.pack('<H', 4)  # Size
            result[0x46:0x48] = struct.pack('<H', i)  # Index
            
            # Write waveform data
            data_size = WAVETABLE_SIZE - DATA_OFFSET
            waveform_data = waveform_data[:data_size]  # Truncate if too long
            waveform_data = waveform_data.ljust(data_size, b'\x00')  # Pad if too short
            result[DATA_OFFSET:] = waveform_data
            
            wavetables.append(result)
            processed_files.append(wav_file)
        
        # Write all wavetables and footer
        with open(output_file, 'wb') as f:
            for wavetable in wavetables:
                f.write(wavetable)
            f.write(FOOTER_DATA)
        
        return {
            'success': True,
            'output_file': output_file,
            'num_wavetables': len(wavetables),
            'files': processed_files
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def process_wavs(input_dir, output_dir):
    """Convert WAV files to Medusa-compatible format."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        processed_files = []
        
        # Get all WAV files from input directory
        wav_files = sorted(Path(input_dir).glob('*.wav'))[:NUM_WAVETABLES]  # Limit to 64 files
        if not wav_files:
            raise Exception("No WAV files found in input directory")
        
        for i, wav_path in enumerate(wav_files):
            output_wav = os.path.join(output_dir, f'wavetable_{i:02d}.wav')
            
            # Process WAV file
            with wave.open(str(wav_path), 'rb') as wav_in:
                # Read audio data
                frames = wav_in.readframes(wav_in.getnframes())
                
                # Convert to mono if stereo
                if wav_in.getnchannels() == 2:
                    # Manual stereo to mono conversion
                    data = []
                    for j in range(0, len(frames), 4):  # 4 bytes per stereo sample (2 channels * 2 bytes per sample)
                        left = struct.unpack('<h', frames[j:j+2])[0]
                        right = struct.unpack('<h', frames[j+2:j+4])[0]
                        mono = (left + right) // 2
                        data.extend(struct.pack('<h', mono))
                    frames = bytes(data)
                
                # Write processed WAV
                with wave.open(output_wav, 'wb') as wav_out:
                    wav_out.setnchannels(1)
                    wav_out.setsampwidth(2)
                    wav_out.setframerate(44100)
                    wav_out.writeframes(frames)
            
            processed_files.append(output_wav)
        
        return {
            'success': True,
            'output_dir': output_dir,
            'num_files': len(processed_files),
            'files': processed_files
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }