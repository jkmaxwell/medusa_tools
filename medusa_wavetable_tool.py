#!/usr/bin/env python3
import os
import struct
import argparse
import wave
from pathlib import Path
import re

WAVETABLE_SIZE = 16000  # 0x3E80 bytes per wavetable
HEADER_MARKER = b'\x02\x00\x00\x3c'
FIRST_HEADER_MARKER = b'\x21\x00\x01\x00'
SUBHEADER_MARKER = b'\x04\x00\x00\x3c'
DATA_OFFSET = 0x80  # Fixed offset where waveform data starts
NUM_WAVETABLES = 64  # Fixed number of wavetables
IDENTIFIER_SIZE = 4  # Size of identifier bytes after header
TOTAL_FILE_SIZE = 1024128  # Exact size of the file

# WAV format constants
SAMPLE_RATE = 44100
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit samples

class Wavetable:
    def __init__(self, index, position, size, is_first, identifier=None):
        self.index = index
        self.position = position
        self.size = size
        self.is_first = is_first
        self.identifier = identifier or b'\x00' * IDENTIFIER_SIZE

def read_wavetables(filepath, verbose=False):
    """Read all wavetables from the file and return their positions."""
    wavetables = []
    filesize = os.path.getsize(filepath)
    
    if verbose:
        print(f"File size: {filesize} bytes")
        print(f"Expected size: {TOTAL_FILE_SIZE} bytes")
    
    with open(filepath, 'rb') as f:
        # First wavetable is special
        header = f.read(4)
        if header == FIRST_HEADER_MARKER:
            identifier = f.read(IDENTIFIER_SIZE)
            if verbose:
                print(f"Found first wavetable at position 0 with identifier {identifier.hex()}")
            wavetables.append(Wavetable(0, 0, WAVETABLE_SIZE, True, identifier))
        else:
            if verbose:
                print(f"Warning: First wavetable header not found, got {header.hex()}")
        
        # Read remaining wavetables
        for i in range(1, NUM_WAVETABLES):
            position = i * WAVETABLE_SIZE
            f.seek(position)
            header = f.read(4)
            
            if header == HEADER_MARKER:
                identifier = f.read(IDENTIFIER_SIZE)
                if verbose:
                    print(f"Found wavetable at position 0x{position:06x} with identifier {identifier.hex()}")
                wavetables.append(Wavetable(i, position, WAVETABLE_SIZE, False, identifier))
            elif verbose:
                print(f"Warning: Expected wavetable at 0x{position:06x}, got {header.hex()}")
    
    if verbose:
        print(f"Total wavetables found: {len(wavetables)}")
    return wavetables

def extract_raw_waveform_data(data):
    """Extract the actual waveform data from a wavetable section."""
    return data[DATA_OFFSET:]

def convert_to_wav(raw_data, output_file):
    """Convert raw wavetable data to WAV format."""
    with wave.open(output_file, 'wb') as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(SAMPLE_WIDTH)
        wav_file.setframerate(SAMPLE_RATE)
        
        # Process the raw data as 16-bit samples
        samples = []
        for i in range(0, len(raw_data), 2):
            if i + 1 < len(raw_data):
                sample = struct.unpack('<h', raw_data[i:i+2])[0]
                samples.append(struct.pack('<h', sample))
        
        wav_file.writeframes(b''.join(samples))

def extract_wavetable(filepath, index, output_dir, as_wav=True):
    """Extract a single wavetable to a file."""
    wavetables = read_wavetables(filepath)
    matching_tables = [wt for wt in wavetables if wt.index == index]
    
    if not matching_tables:
        print(f"Error: Wavetable index {index} not found")
        return False
    
    wavetable = matching_tables[0]
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read the wavetable data
    with open(filepath, 'rb') as f:
        f.seek(wavetable.position)
        data = f.read(wavetable.size)
    
    # Save the identifier along with the WAV data
    identifier_file = output_dir / f"wavetable_{index:02d}.id"
    with open(identifier_file, 'wb') as f:
        f.write(wavetable.identifier)
    
    # Extract the raw waveform data
    waveform_data = extract_raw_waveform_data(data)
    
    if as_wav:
        output_file = output_dir / f"wavetable_{index:02d}.wav"
        convert_to_wav(waveform_data, str(output_file))
    else:
        output_file = output_dir / f"wavetable_{index:02d}.bin"
        with open(output_file, 'wb') as f:
            f.write(data)
    
    print(f"Extracted wavetable {index} to {output_file}")
    return True

def decompile_wavetables(filepath, output_dir):
    """Extract all wavetables to separate WAV files."""
    wavetables = read_wavetables(filepath)
    print(f"\nDecompiling {len(wavetables)} wavetables to {output_dir}...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Also save the original file for exact size reference
    with open(filepath, 'rb') as f:
        original_data = f.read()
        with open(output_dir / 'original.polyend', 'wb') as out:
            out.write(original_data)
    
    for wt in wavetables:
        extract_wavetable(filepath, wt.index, output_dir, True)
    
    print(f"\nDecompiled {len(wavetables)} wavetables successfully")

def read_wav_file(wav_path):
    """Read a WAV file and return the raw sample data."""
    with wave.open(str(wav_path), 'rb') as wav_file:
        if wav_file.getnchannels() != CHANNELS:
            raise ValueError(f"WAV file must be mono, got {wav_file.getnchannels()} channels")
        if wav_file.getsampwidth() != SAMPLE_WIDTH:
            raise ValueError(f"WAV file must be 16-bit, got {wav_file.getsampwidth()*8} bits")
        
        return wav_file.readframes(wav_file.getnframes())

def create_wavetable_data(index, wav_data, identifier, is_first=False):
    """Create a complete wavetable section including headers."""
    result = bytearray(WAVETABLE_SIZE)
    
    # Write appropriate header
    if is_first:
        result[0:4] = FIRST_HEADER_MARKER
    else:
        result[0:4] = HEADER_MARKER
    
    # Write identifier
    result[4:8] = identifier
    
    # Write subheader
    result[0x40:0x44] = SUBHEADER_MARKER
    result[0x44:0x46] = struct.pack('<H', 4)  # Size as 16-bit value
    result[0x46:0x48] = struct.pack('<H', index)  # Index as 16-bit value
    
    # Write waveform data
    data_size = WAVETABLE_SIZE - DATA_OFFSET
    wav_data = wav_data[:data_size]  # Truncate if too long
    wav_data = wav_data.ljust(data_size, b'\x00')  # Pad if too short
    result[DATA_OFFSET:] = wav_data
    
    return result

def recompile_wavetables(input_dir, output_file):
    """Recompile WAV files back into a Polyend wavetable file."""
    input_dir = Path(input_dir)
    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a directory")
        return False
    
    # Check if we have the original file for reference
    original_file = input_dir / 'original.polyend'
    if original_file.exists():
        with open(original_file, 'rb') as f:
            original_data = f.read()
    else:
        original_data = None
    
    # Find and sort all WAV files
    wav_pattern = re.compile(r'wavetable_(\d+)\.wav$')
    wav_files = []
    for file in input_dir.glob('*.wav'):
        match = wav_pattern.match(file.name)
        if match:
            index = int(match.group(1))
            if index < NUM_WAVETABLES:  # Only include valid wavetables
                id_file = file.parent / f"wavetable_{index:02d}.id"
                if id_file.exists():
                    with open(id_file, 'rb') as f:
                        identifier = f.read()
                else:
                    identifier = b'\x00' * IDENTIFIER_SIZE
                wav_files.append((index, file, identifier))
    
    if not wav_files:
        print("Error: No wavetable WAV files found")
        return False
    
    if len(wav_files) != NUM_WAVETABLES:
        print(f"Error: Expected {NUM_WAVETABLES} wavetables, found {len(wav_files)}")
        return False
    
    # Sort by index
    wav_files.sort()
    print(f"\nRecompiling {len(wav_files)} wavetables to {output_file}...")
    
    # Create the output file
    with open(output_file, 'wb') as f:
        # Write all wavetables
        for i, (index, wav_path, identifier) in enumerate(wav_files):
            try:
                wav_data = read_wav_file(wav_path)
                wavetable_data = create_wavetable_data(index, wav_data, identifier, i == 0)
                f.write(wavetable_data)
                print(f"Recompiled wavetable {index} from {wav_path.name}")
            except Exception as e:
                print(f"Error processing {wav_path}: {e}")
                return False
        
        # If we have the original file, copy any remaining data
        if original_data and len(original_data) > NUM_WAVETABLES * WAVETABLE_SIZE:
            remaining_data = original_data[NUM_WAVETABLES * WAVETABLE_SIZE:]
            f.write(remaining_data)
    
    print(f"\nSuccessfully recompiled {len(wav_files)} wavetables to {output_file}")
    return True

def verify_wavetables(original_file, recompiled_file):
    """Verify that the recompiled file matches the original."""
    with open(original_file, 'rb') as f1, open(recompiled_file, 'rb') as f2:
        original_data = f1.read()
        recompiled_data = f2.read()
        
        if len(original_data) != len(recompiled_data):
            print(f"Error: File sizes don't match")
            print(f"Original: {len(original_data)} bytes")
            print(f"Recompiled: {len(recompiled_data)} bytes")
            print(f"Difference: {len(original_data) - len(recompiled_data)} bytes")
            return False
        
        if original_data == recompiled_data:
            print("Verification successful: Files are identical")
            return True
        else:
            # Find first difference
            for i in range(min(len(original_data), len(recompiled_data))):
                if original_data[i] != recompiled_data[i]:
                    print(f"First difference at offset 0x{i:06x}")
                    print(f"Original: {original_data[i:i+16].hex()}")
                    print(f"Recompiled: {recompiled_data[i:i+16].hex()}")
                    break
            print("Error: Files don't match")
            return False

def list_wavetables(filepath):
    """List all wavetables in the file."""
    wavetables = read_wavetables(filepath, verbose=True)
    print(f"\nFound {len(wavetables)} wavetables in {filepath}:")
    for wt in wavetables:
        print(f"Wavetable {wt.index:2d}: Position 0x{wt.position:06x} ID {wt.identifier.hex()}")

def main():
    parser = argparse.ArgumentParser(description='Polyend Medusa Wavetable Tool')
    parser.add_argument('action', choices=['list', 'decompile', 'recompile', 'verify'],
                      help='Action to perform')
    parser.add_argument('input',
                      help='Input wavetable file or directory of WAV files')
    parser.add_argument('--output',
                      help='Output directory for decompile or output file for recompile')
    parser.add_argument('--verify-with',
                      help='Original file to verify against after recompiling')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_wavetables(args.input)
    
    elif args.action == 'decompile':
        if not args.output:
            args.output = 'waves'
        decompile_wavetables(args.input, args.output)
    
    elif args.action == 'recompile':
        if not args.output:
            args.output = 'recompiled.polyend'
        if recompile_wavetables(args.input, args.output) and args.verify_with:
            verify_wavetables(args.verify_with, args.output)
    
    elif args.action == 'verify':
        if not args.output:
            print("Error: --output required for verify")
            return
        verify_wavetables(args.input, args.output)

if __name__ == '__main__':
    main()