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
- FFmpeg (required for audio file conversion)
- Standard Python libraries (no additional dependencies needed)

### Installation

#### FFmpeg Installation (Required)

FFmpeg is required for audio file conversion. To install FFmpeg on macOS:

Using Homebrew (recommended):
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg
```

Alternative methods:
- Download from [FFmpeg website](https://ffmpeg.org/download.html)
- Using MacPorts: `sudo port install ffmpeg`

#### Command Line Version
1. Clone or download this repository
2. Make the scripts executable:
   ```bash
   chmod +x medusa_wavetable_tool.py medusa_wav_preprocessor.py
   ```

#### Mac Version

1. Clone or download this repository
2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Make the script executable:
   ```bash
   chmod +x medusa_mac.py
   ```

The tool is available as a command-line application:

```bash
# Extract wavetables from a .polyend file (defaults to medusa64Wavetables.polyend)
./medusa_mac.py decompile [input.polyend]

# Create a .polyend file from WAV files
./medusa_mac.py recompile waves_dir output.polyend

# Process custom WAV files for use with Medusa
./medusa_mac.py process input_dir output_dir
```

The tool will:
- Automatically create a 'waves' directory for decompiled files
- Preserve all metadata and file structure
- Process WAV files to the correct format (mono, 44.1kHz, 16-bit)

#### Build from Source
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install PySide6 numpy
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
- Each WAV file contains a single cycle waveform

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

### Testing

The project includes a comprehensive test suite that verifies:
- Wavetable decompilation
- Wavetable recompilation with verification
- WAV file processing
- Error handling

Run the tests:
```bash
python3 test_medusa_tools.py -v
```

All tests must pass before any changes are merged.

### Contributing

Before submitting pull requests:
1. Run the test suite to ensure no regressions
2. Add tests for any new functionality
3. Ensure all tests pass

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

### License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). This means:

- ✔️ You can view and fork this code
- ✔️ You can submit contributions via pull requests
- ❌ You cannot use this code in commercial projects
- ❌ You cannot modify or distribute this code without sharing your changes
- ❌ You cannot use this code in closed-source projects

All rights reserved. For permissions beyond the scope of this license, please contact the author.