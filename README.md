# Polyend Medusa Tools

A collection of tools for working with Polyend Medusa synthesizer files.

## Wavetable Tool

The `medusa_wavetable_tool.py` script allows you to extract, modify, and recompile wavetables from Polyend Medusa wavetable files (`.polyend` extension).

### Features

- Extract all wavetables to individual WAV files
- Recompile modified WAV files back into Medusa format
- List detailed information about wavetables
- Verify file integrity after modifications
- Preserves all metadata and file structure

### Requirements

- Python 3.6 or higher
- Standard Python libraries (no additional dependencies needed)

### Installation

1. Clone or download this repository
2. Make the script executable:
   ```bash
   chmod +x medusa_wavetable_tool.py
   ```

### Usage

#### Decompiling Wavetables

Extract all wavetables from a `.polyend` file to individual WAV files:

```bash
./medusa_wavetable_tool.py decompile medusa64Wavetables.polyend --output waves
```

This creates a directory named `waves` containing:
- 64 WAV files (wavetable_00.wav through wavetable_63.wav)
- Metadata files (.id) for each wavetable
- A copy of the original file for reference

#### Editing Wavetables

The extracted WAV files are standard 44.1kHz 16-bit mono files that can be edited in any audio editor. Each wavetable is a single cycle waveform.

#### Recompiling Wavetables

After editing the WAV files, recompile them back into a Medusa wavetable file:

```bash
./medusa_wavetable_tool.py recompile waves --output recompiled.polyend
```

To verify the recompiled file matches the original structure:

```bash
./medusa_wavetable_tool.py recompile waves --output recompiled.polyend --verify-with original.polyend
```

#### Listing Wavetable Information

View detailed information about the wavetables in a file:

```bash
./medusa_wavetable_tool.py list medusa64Wavetables.polyend
```

### Technical Details

#### File Format

The Polyend Medusa wavetable file format consists of:
- 64 wavetables, each 16,000 bytes (0x3E80)
- Total file size: 1,024,128 bytes
- Each wavetable contains:
  - Header (4 bytes)
  - Identifier (4 bytes)
  - Subheader at offset 0x40 (8 bytes)
  - Waveform data at offset 0x80

#### Wavetable Structure

Each wavetable section has this structure:
```
Offset  Size    Description
0x0000  4       Header marker (first wavetable: 21 00 01 00, others: 02 00 00 3c)
0x0004  4       Identifier bytes (unique per wavetable)
0x0040  4       Subheader marker (04 00 00 3c)
0x0044  2       Size value (04 00)
0x0046  2       Index value (00-3F)
0x0080  15872   Waveform data (raw 16-bit samples)
```

### Tips

1. Always make a backup of your original wavetable files before modifying them.
2. When editing wavetables, maintain the single-cycle nature of the waveforms.
3. The tool preserves all metadata and file structure, ensuring compatibility with the Medusa.

### Troubleshooting

If you encounter issues:

1. Verify the input file is a valid Medusa wavetable file
2. Check that edited WAV files remain mono 16-bit
3. Ensure all 64 wavetables are present when recompiling
4. Use the --verify-with option to check file integrity

### Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

### License

MIT License - feel free to use and modify as needed.