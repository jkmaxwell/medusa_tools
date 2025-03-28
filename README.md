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

#### Command Line Version
1. Clone or download this repository
2. Make the scripts executable:
   ```bash
   chmod +x medusa_wavetable_tool.py medusa_wav_preprocessor.py
   ```

#### Native Mac App
The tool is available as a native macOS menu bar app that provides a clean, native interface:

1. Download the latest release
2. Move Medusa.app to your Applications folder
3. Launch the app - it will appear in your menu bar as 🎹
4. Use the menu bar icon to:
   - Decompile .polyend files
   - Recompile wavetables
   - Process custom WAV files

#### Build from Source
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install rumps pyinstaller
   ```
3. Build the app:
   ```bash
   pyinstaller medusa.spec
   ```
4. Move to Applications:
   ```bash
   mv "dist/Medusa.app" /Applications/
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

#### Processing Custom Wavetables

The `medusa_wav_preprocessor.py` script helps prepare custom WAV files for use with Medusa:

1. Converts files to the required format (44.1kHz, 16-bit mono)
2. Extracts single-cycle waveforms at zero crossings
3. Normalizes audio levels
4. Limits to maximum 64 wavetables
5. Creates necessary metadata files

```bash
# Process a folder of WAV files
./medusa_wav_preprocessor.py input_waves/ processed_waves/

# Then recompile into Medusa format
./medusa_wavetable_tool.py recompile processed_waves/ --output custom_wavetables.polyend
```

Requirements:
- Python 3.6 or higher
- scipy
- soundfile
- numpy

Install dependencies:
```bash
pip install scipy soundfile numpy
```

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

### Support the Project

If you find this tool useful, consider supporting its development:

[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/code404)
[![Venmo](https://img.shields.io/badge/Venmo-008CFF?style=for-the-badge&logo=venmo&logoColor=white)](https://venmo.com/octavecat)

### Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

### License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). This means:

- ✔️ You can view and fork this code
- ✔️ You can submit contributions via pull requests
- ❌ You cannot use this code in commercial projects
- ❌ You cannot modify or distribute this code without sharing your changes
- ❌ You cannot use this code in closed-source projects

All rights reserved. For permissions beyond the scope of this license, please contact the author.