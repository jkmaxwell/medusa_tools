#!/usr/bin/env python3

import sys
from medusa_core import decompile_wavetable, recompile_wavetable, process_wavs

DEFAULT_INPUT = "medusa64Wavetables.polyend"

def show_help():
    print("""
Medusa Wavetable Tool

Usage:
    medusa_mac.py decompile [input.polyend]
    medusa_mac.py recompile <input_dir> <output.polyend>
    medusa_mac.py process <input_dir> <output_dir>

Commands:
    decompile  Extract wavetables from .polyend file to WAV files
               (defaults to medusa64Wavetables.polyend if not specified)
    recompile  Create .polyend file from WAV files
    process    Convert WAV files to Medusa-compatible format
    """)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        show_help()
        return
    
    command = sys.argv[1]
    
    if command == 'decompile':
        # Use default input file if none specified
        input_file = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_INPUT
        
        result = decompile_wavetable(input_file)
        if result['success']:
            print(f"\nDecompiling {result['num_wavetables']} wavetables to {result['output_dir']}...")
            for file in result['files']:
                print(f"Extracted wavetable to {file}")
            print(f"\nDecompiled {result['num_wavetables']} wavetables successfully")
        else:
            print(f"Error decompiling wavetable: {result['error']}")
    
    elif command == 'recompile':
        if len(sys.argv) != 4:
            print("Error: recompile requires input directory and output file")
            show_help()
            return
        
        result = recompile_wavetable(sys.argv[2], sys.argv[3])
        if result['success']:
            print(f"\nRecompiling wavetables from {sys.argv[2]} to {result['output_file']}...")
            for file in result['files']:
                print(f"Recompiled wavetable from {file}")
            print(f"\nSuccessfully recompiled {result['num_wavetables']} wavetables to {result['output_file']}")
        else:
            print(f"Error recompiling wavetables: {result['error']}")
    
    elif command == 'process':
        if len(sys.argv) != 4:
            print("Error: process requires input and output directories")
            show_help()
            return
        
        result = process_wavs(sys.argv[2], sys.argv[3])
        if result['success']:
            print(f"\nProcessing WAV files to {result['output_dir']}...")
            for file in result['files']:
                print(f"Processed {file}")
            print(f"\nSuccessfully processed {result['num_files']} WAV files")
            print("You can now use 'recompile' to create a .polyend file")
        else:
            print(f"Error processing WAVs: {result['error']}")
    
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()