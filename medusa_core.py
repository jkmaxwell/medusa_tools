#!/usr/bin/env python3

import os
import wave
import struct
import shutil
import json
import numpy as np
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

def extract_identifiers(polyend_file):
    """Extract identifiers from a .polyend file."""
    identifiers = []
    with open(polyend_file, 'rb') as f:
        data = f.read()
        for i in range(NUM_WAVETABLES):
            start = i * WAVETABLE_SIZE + 4  # ID starts at offset 4
            identifiers.append(data[start:start + IDENTIFIER_SIZE].hex())
    return identifiers

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
        
        # Save original file for reference
        with open(os.path.join(output_dir, 'original.polyend'), 'wb') as f:
            f.write(data)
        
        # Extract identifiers and save to metadata file
        identifiers = extract_identifiers(input_file)
        metadata = {'identifiers': identifiers}
        with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
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
        # Check if we have the original file for reference
        original_file = os.path.join(input_dir, 'original.polyend')
        if os.path.exists(original_file):
            with open(original_file, 'rb') as f:
                original_data = f.read()
        else:
            original_data = None
        
        # Load identifiers from metadata file
        metadata_file = os.path.join(input_dir, 'metadata.json')
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                identifiers = [bytes.fromhex(id_hex) for id_hex in metadata['identifiers']]
        else:
            identifiers = [b'\x00' * IDENTIFIER_SIZE] * NUM_WAVETABLES
        
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
            result[4:8] = identifiers[i]
            
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
        
        # Write all wavetables
        with open(output_file, 'wb') as f:
            for wavetable in wavetables:
                f.write(wavetable)
            
            # If we have the original file, copy any remaining data
            if original_data and len(original_data) > NUM_WAVETABLES * WAVETABLE_SIZE:
                remaining_data = original_data[NUM_WAVETABLES * WAVETABLE_SIZE:]
                f.write(remaining_data)
            else:
                # Otherwise pad to exact file size
                padding_size = TOTAL_FILE_SIZE - (NUM_WAVETABLES * WAVETABLE_SIZE)
                if padding_size > 0:
                    f.write(b'\x00' * padding_size)
        
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
        
        # First check if we have original.polyend for identifiers
        original_file = os.path.join(input_dir, 'original.polyend')
        if os.path.exists(original_file):
            # Copy original file to output directory
            shutil.copy2(original_file, os.path.join(output_dir, 'original.polyend'))
            
            # Extract identifiers and save to metadata file
            identifiers = extract_identifiers(original_file)
            metadata = {'identifiers': identifiers}
            with open(os.path.join(output_dir, 'metadata.json'), 'w') as f:
                json.dump(metadata, f, indent=2)
        
        for i, wav_path in enumerate(wav_files):
            output_wav = os.path.join(output_dir, f'wavetable_{i:02d}.wav')
            
            # Process WAV file
            with wave.open(str(wav_path), 'rb') as wav_in:
                # Read audio data
                frames = wav_in.readframes(wav_in.getnframes())
                
                # Convert to mono if stereo
                if wav_in.getnchannels() == 2:
                    data = np.frombuffer(frames, dtype=np.int16)
                    data = data.reshape(-1, 2)
                    data = np.mean(data, axis=1, dtype=np.int16)
                    frames = data.tobytes()
                
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