#!/usr/bin/env python3
"""Command line interface for Medusa Wavetable Utility."""

import sys
import argparse
from medusa_core import decompile_wavetable, recompile_wavetable, process_wavs, create_wavetable_bank
from version import __version__, __app_name__

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=f"{__app_name__} - Command line interface for working with Polyend Medusa wavetables"
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Decompile command
    decompile_parser = subparsers.add_parser(
        'decompile',
        help='Extract wavetables from a .polyend file'
    )
    decompile_parser.add_argument(
        'input_file',
        help='Input .polyend file'
    )
    
    # Recompile command
    recompile_parser = subparsers.add_parser(
        'recompile',
        help='Create .polyend file from processed WAV files'
    )
    recompile_parser.add_argument(
        'input_dir',
        help='Directory containing WAV files'
    )
    recompile_parser.add_argument(
        'output_file',
        help='Output .polyend file'
    )
    
    # Create command
    create_parser = subparsers.add_parser(
        'create',
        help='Create wavetable bank from audio files'
    )
    create_parser.add_argument(
        'input_dir',
        help='Directory containing audio files'
    )
    create_parser.add_argument(
        'output_file',
        help='Output .polyend file'
    )
    create_parser.add_argument(
        '--random',
        action='store_true',
        help='Use random file selection (default: alphabetical)'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'decompile':
            result = decompile_wavetable(args.input_file)
            if result['success']:
                print(f"Extracted {result['num_wavetables']} wavetables to {result['output_dir']}")
            else:
                print(f"Error: {result['error']}", file=sys.stderr)
                return 1
                
        elif args.command == 'recompile':
            result = recompile_wavetable(args.input_dir, args.output_file)
            if result['success']:
                print(f"Successfully recompiled {result['num_wavetables']} wavetables to {result['output_file']}")
            else:
                print(f"Error: {result['error']}", file=sys.stderr)
                return 1
                
        elif args.command == 'create':
            result = create_wavetable_bank(
                args.input_dir,
                args.output_file,
                random_order=args.random
            )
            if result['success']:
                print(f"Successfully created wavetable bank:")
                print(f"- Output file: {result['output_file']}")
                print(f"- Number of wavetables: {result['num_wavetables']}")
                print(f"- Source files: {len(result['source_files'])}")
            else:
                print(f"Error: {result['error']}", file=sys.stderr)
                return 1
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())