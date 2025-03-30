# Polyend Medusa Tools

A collection of tools for working with Polyend Medusa synthesizer files.

## Important Notice

**The GUI version is temporarily unavailable. Please use the CLI version described below for all operations.**

## Installation

1. Download the compiled `medusa_cli` executable from the releases page
2. Install FFmpeg (required for audio file conversion)
3. Make the CLI tool executable:
   ```bash
   chmod +x medusa_cli
   ```

### FFmpeg Installation

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

The tool will automatically detect FFmpeg in common installation locations:
- Homebrew: /usr/local/bin/ffmpeg
- MacPorts: /opt/local/bin/ffmpeg
- System: /usr/bin/ffmpeg

Please click watch this intro:

[![CLI Intro](https://cdn.loom.com/sessions/thumbnails/3f718f692a5c465cb3c0d09050ec9560-162fb22de36196ca.jpg)](https://www.loom.com/share/3f718f692a5c465cb3c0d09050ec9560)

## Quick Start

The most common use case is creating a new wavetable bank from audio files:

```bash
# Create a wavetable bank with alphanumeric ordering (recommended for most users)
./medusa_cli create input_directory output.polyend

# Create a wavetable bank with random ordering
./medusa_cli create input_directory output.polyend --random
```

Other available commands:
```bash
# Extract wavetables from an existing .polyend file
./medusa_cli decompile input.polyend

# Recompile processed WAV files into a .polyend file
./medusa_cli recompile processed_waves/ output.polyend

# Show version information
./medusa_cli --version
```

## Detailed Usage Guide

### Creating Wavetable Banks

The `create` command is the primary way to generate wavetable banks from your audio files. You have two ordering options:

1. Alphanumeric ordering (default):
   ```bash
   ./medusa_cli create input_directory output.polyend
   ```
   - Files are processed in alphanumeric order
   - Predictable and organized results
   - Recommended for most users
   - Great for organized sound design

2. Random ordering:
   ```bash
   ./medusa_cli create input_directory output.polyend --random
   ```
   - Files are randomly ordered in the wavetable bank
   - Creates unique combinations
   - Good for experimental sound design
   - Different result each time

The tool will automatically:
- Convert files to the required format (44.1kHz, 16-bit mono)
- Extract single-cycle waveforms at zero crossings
- Normalize audio levels
- Limit to maximum 64 wavetables
- Create necessary metadata

### Decompiling Wavetables

Extract all wavetables from a `.polyend` file to individual WAV files:

```bash
./medusa_cli decompile input.polyend
```

This creates a directory containing:
- 64 WAV files (wavetable_00.wav through wavetable_63.wav)
- Each WAV file contains a single cycle waveform

### Editing Wavetables

The extracted WAV files are standard 44.1kHz 16-bit mono files that can be edited in any audio editor. Each wavetable is a single cycle waveform.

### Recompiling Wavetables

After editing the WAV files, recompile them back into a Medusa wavetable file:

```bash
./medusa_cli recompile waves --output recompiled.polyend
```

To verify the recompiled file matches the original structure:

```bash
./medusa_cli recompile waves --output recompiled.polyend --verify-with original.polyend
```

## Technical Details

The Polyend Medusa wavetable file format consists of 64 wavetables, each containing a single-cycle waveform. The tool handles all the technical details of file formatting and metadata automatically.

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). This means:

- ✔️ You can view and fork this code
- ✔️ You can submit contributions via pull requests
- ❌ You cannot use this code in commercial projects
- ❌ You cannot modify or distribute this code without sharing your changes
- ❌ You cannot use this code in closed-source projects

All rights reserved. For permissions beyond the scope of this license, please contact the author.
