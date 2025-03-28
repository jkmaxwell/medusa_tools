#!/usr/bin/env python3

import sys
import os
import wave
import struct
import numpy as np
from pathlib import Path

# Constants from CLI version
WAVETABLE_SIZE = 16000  # 0x3E80 bytes per wavetable
HEADER_MARKER = b'\x02\x00\x00\x3c'
FIRST_HEADER_MARKER = b'\x21\x00\x01\x00'
SUBHEADER_MARKER = b'\x04\x00\x00\x3c'
DATA_OFFSET = 0x80  # Fixed offset where waveform data starts
NUM_WAVETABLES = 64  # Fixed number of wavetables
IDENTIFIER_SIZE = 4  # Size of identifier bytes after header
TOTAL_FILE_SIZE = 1024128  # Exact size of the file

def decompile_wavetable(input_file):
    try:
        # Create waves directory next to the input file
        input_dir = os.path.dirname(input_file)
        output_dir = os.path.join(input_dir, 'waves')
        os.makedirs(output_dir, exist_ok=True)
        
        # Read the polyend file
        with open(input_file, 'rb') as f:
            data = f.read()
        
        # Save original file for reference
        with open(os.path.join(output_dir, 'original.polyend'), 'wb') as f:
            f.write(data)
        
        # Extract wavetables
        num_wavetables = len(data) // WAVETABLE_SIZE
        
        print(f"\nDecompiling {num_wavetables} wavetables to {output_dir}...")
        
        for i in range(num_wavetables):
            # Extract wavetable data
            start = i * WAVETABLE_SIZE
            end = start + WAVETABLE_SIZE
            wavetable_data = data[start:end]
            
            # Save identifier
            id_file = os.path.join(output_dir, f'wavetable_{i:02d}.id')
            with open(id_file, 'wb') as f:
                f.write(wavetable_data[4:8])  # ID is at offset 4
            
            # Extract waveform data (starts at offset 0x80)
            waveform_data = wavetable_data[DATA_OFFSET:]
            
            # Convert to WAV format
            wav_file = os.path.join(output_dir, f'wavetable_{i:02d}.wav')
            with wave.open(wav_file, 'wb') as wav:
                wav.setnchannels(1)  # mono
                wav.setsampwidth(2)  # 16-bit
                wav.setframerate(44100)  # 44.1kHz
                wav.writeframes(waveform_data)
            
            print(f"Extracted wavetable {i} to {wav_file}")
        
        print(f"\nDecompiled {num_wavetables} wavetables successfully")
        
    except Exception as e:
        print(f"Error decompiling wavetable: {str(e)}")
        return False
    return True

def recompile_wavetable(input_dir, output_file):
    try:
        wavetables = []
        
        print(f"\nRecompiling wavetables from {input_dir} to {output_file}...")
        
        # Check if we have the original file for reference
        original_file = os.path.join(input_dir, 'original.polyend')
        if os.path.exists(original_file):
            with open(original_file, 'rb') as f:
                original_data = f.read()
        else:
            original_data = None
        
        for i in range(NUM_WAVETABLES):
            wav_file = os.path.join(input_dir, f'wavetable_{i:02d}.wav')
            id_file = os.path.join(input_dir, f'wavetable_{i:02d}.id')
            
            if not os.path.exists(wav_file):
                raise Exception(f"Missing wavetable_{i:02d}.wav")
            
            # Read identifier if it exists
            if os.path.exists(id_file):
                with open(id_file, 'rb') as f:
                    identifier = f.read()
            else:
                identifier = b'\x00' * IDENTIFIER_SIZE
            
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
            result[4:8] = identifier
            
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
            print(f"Recompiled wavetable {i} from {wav_file}")
        
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
        
        print(f"\nSuccessfully recompiled {len(wavetables)} wavetables to {output_file}")
        
    except Exception as e:
        print(f"Error recompiling wavetables: {str(e)}")
        return False
    return True

def process_wavs(input_dir, output_dir):
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Get all WAV files from input directory
        wav_files = sorted(Path(input_dir).glob('*.wav'))[:NUM_WAVETABLES]  # Limit to 64 files
        if not wav_files:
            raise Exception("No WAV files found in input directory")
        
        print(f"\nProcessing {len(wav_files)} WAV files to {output_dir}...")
        
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
            
            print(f"Processed {wav_path.name} to {os.path.basename(output_wav)}")
        
        print(f"\nSuccessfully processed {len(wav_files)} WAV files")
        print("You can now use 'recompile' to create a .polyend file")
        
    except Exception as e:
        print(f"Error processing WAVs: {str(e)}")
        return False
    return True

def show_help():
    print("""
Medusa Wavetable Tool

Usage:
    medusa_mac.py decompile <input.polyend>
    medusa_mac.py recompile <input_dir> <output.polyend>
    medusa_mac.py process <input_dir> <output_dir>

Commands:
    decompile  Extract wavetables from .polyend file to WAV files
    recompile  Create .polyend file from WAV files
    process    Convert WAV files to Medusa-compatible format
    """)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        show_help()
        return
    
    command = sys.argv[1]
    
    if command == 'decompile':
        if len(sys.argv) != 3:
            print("Error: decompile requires input file")
            show_help()
            return
        decompile_wavetable(sys.argv[2])
    
    elif command == 'recompile':
        if len(sys.argv) != 4:
            print("Error: recompile requires input directory and output file")
            show_help()
            return
        recompile_wavetable(sys.argv[2], sys.argv[3])
    
    elif command == 'process':
        if len(sys.argv) != 4:
            print("Error: process requires input and output directories")
            show_help()
            return
        process_wavs(sys.argv[2], sys.argv[3])
    
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()