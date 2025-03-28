#!/usr/bin/env python3

import sys
from medusa_core import decompile_wavetable, recompile_wavetable, process_wavs

DEFAULT_INPUT = "medusa64Wavetables.polyend"
DEFAULT_WAVES_DIR = "waves"
DEFAULT_OUTPUT = "recompiled.polyend"

def show_help():
    print("""
Medusa Wavetable Tool

Usage:
    medusa_mac.py decompile [input.polyend]
    medusa_mac.py recompile [input_dir] [output.polyend]
    medusa_mac.py process <input_dir> <output_dir>

Commands:
    decompile  Extract wavetables from .polyend file to WAV files
               (defaults to medusa64Wavetables.polyend if not specified)
    recompile  Create .polyend file from WAV files
               (defaults to ./waves/ input and recompiled.polyend output if not specified)
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
        # Use default input/output if not specified
        input_dir = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_WAVES_DIR
        output_file = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_OUTPUT
        
        result = recompile_wavetable(input_dir, output_file)
        if result['success']:
            print(f"\nRecompiling wavetables from {input_dir} to {result['output_file']}...")
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