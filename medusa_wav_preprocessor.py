#!/usr/bin/env python3

import os
import wave
import numpy as np
from scipy import signal
import soundfile as sf
import argparse
import shutil
from pathlib import Path

def ensure_mono(data, channels):
    """Convert stereo to mono by averaging channels if needed."""
    if channels > 1:
        return np.mean(data, axis=1)
    return data

def resample_to_44100(data, original_sr):
    """Resample audio to 44.1kHz if needed."""
    if original_sr != 44100:
        samples = len(data)
        new_samples = int(samples * 44100 / original_sr)
        return signal.resample(data, new_samples)
    return data

def normalize_audio(data):
    """Normalize audio to -1.0 to 1.0 range."""
    return data / np.max(np.abs(data))

def find_zero_crossings(data):
    """Find zero crossing points in the audio."""
    return np.where(np.diff(np.signbit(data)))[0]

def extract_single_cycle(data, sample_rate):
    """Extract a single cycle waveform starting at a zero crossing."""
    # Target length for Medusa wavetables (based on original format)
    target_length = 2048  # Adjust this based on actual Medusa requirements
    
    # Find zero crossings
    zero_crossings = find_zero_crossings(data)
    if len(zero_crossings) < 2:
        # If no clear cycles, just take the first chunk
        return signal.resample(data[:target_length], target_length)
    
    # Find the first complete cycle
    for i in range(len(zero_crossings) - 1):
        cycle_length = zero_crossings[i + 1] - zero_crossings[i]
        if cycle_length > 20:  # Minimum cycle length to avoid noise
            cycle = data[zero_crossings[i]:zero_crossings[i + 1]]
            # Resample to target length
            return signal.resample(cycle, target_length)
    
    # Fallback if no good cycle found
    return signal.resample(data[:target_length], target_length)

def process_wav_file(input_path, output_path):
    """Process a WAV file to meet Medusa requirements."""
    # Read audio file
    data, sample_rate = sf.read(input_path)
    
    # Convert to mono if stereo
    data = ensure_mono(data, len(data.shape))
    
    # Resample to 44.1kHz if needed
    data = resample_to_44100(data, sample_rate)
    
    # Normalize audio
    data = normalize_audio(data)
    
    # Extract single cycle
    data = extract_single_cycle(data, 44100)
    
    # Save as 16-bit WAV
    sf.write(output_path, data, 44100, subtype='PCM_16')

def main():
    parser = argparse.ArgumentParser(description='Process WAV files for Medusa wavetable format')
    parser.add_argument('input_dir', help='Directory containing input WAV files')
    parser.add_argument('output_dir', help='Directory for processed WAV files')
    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Process WAV files
    input_files = sorted(Path(args.input_dir).glob('*.wav'))[:64]  # Limit to 64 files
    
    for i, input_file in enumerate(input_files):
        output_file = Path(args.output_dir) / f'wavetable_{i:02d}.wav'
        print(f'Processing {input_file.name} -> {output_file.name}')
        process_wav_file(input_file, output_file)
        
        # Create .id file (required for recompilation)
        id_file = output_file.with_suffix('.id')
        with open(id_file, 'wb') as f:
            f.write(i.to_bytes(4, 'little'))

    print(f'\nProcessed {len(input_files)} files')
    print('Now you can use medusa_wavetable_tool.py to recompile the processed files:')
    print(f'./medusa_wavetable_tool.py recompile {args.output_dir} --output new_wavetables.polyend')

if __name__ == '__main__':
    main()