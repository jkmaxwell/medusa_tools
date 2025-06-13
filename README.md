# Polyend Medusa Tools

A collection of tools for working with Polyend Medusa synthesizer files. MacOS only.

## 🌐 NEW: Web Version Available!

**No downloads, no quarantine issues, no installation required!**

Try the web version at: `http://localhost:5001` (run `./run_web.sh`)

Perfect for users who want to avoid macOS quarantine restrictions.

## Project Structure

```
medusa_tools/
├── wavetables/           # Wavetable source files and compiled .polyend files
│   ├── source/          # Source wavetable files
│   │   ├── vox/        # Vocal wavetable sources
│   │   └── sq80/       # SQ80 wavetable sources
│   └── dist/           # Compiled .polyend files
├── medusa_cli.py        # Command-line interface
├── medusa_gui.py        # Graphical user interface
├── medusa_core.py       # Core functionality
└── ...                 # Other project files
```

=======

1. **The GUI version is temporarily unavailable. Please use the CLI version described below for all operations.**
2. I haven't been a professional engineer since 2005 when I worked on Apple's AJAX libraries. 90% of this code here was written with the help of AI (ChatGPT, Claude Code, RooCode). I honestly could not write this myself nor fix things without AI. So, please use and evaluate it with that knowledge. AI was my engineering partner, and I was effectively PM on it.

>>>>>>> a37015f339995e54426432ec2504da58cd71a236
>>>>>>>
>>>>>>
>>>>>
>>>>
>>>
>>

## Installation

### 🌐 Web Version (Recommended)

**Zero installation, works everywhere:**

```bash
# Clone or download this repo
git clone https://github.com/jkmaxwell/medusa_tools.git
cd medusa_tools

# Install web dependencies
pip install -r requirements_web.txt

# Start the web server
./run_web.sh
```

Open your browser to `http://localhost:5001` and enjoy!

### GUI Version (macOS App)

1. Download the latest release from the releases page
2. Extract the zip file
3. **Important:** Remove macOS quarantine to avoid permission issues:
   ```bash
   # Run this command after downloading:
   xattr -d com.apple.quarantine "/path/to/Medusa Wavetable Utility.app"
   
   # Or use the included fix script:
   ./fix_quarantine.sh
   ```
4. Double-click `Medusa Wavetable Utility.app` to run
5. If you get a security warning:
   - Right-click (or Control-click) the app and select "Open"
   - Or go to System Preferences > Security & Privacy and click "Open Anyway"

### CLI Version

1. Download the compiled `medusa_cli` executable from the releases page
2. Install FFmpeg (required for audio file conversion)
3. Make the CLI tool executable:
   ```bash
   chmod +x medusa_cli
   ```

### FFmpeg Installation

FFmpeg is required for audio file conversion. To install FFmpeg on macOS:

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

## Using the GUI Version

The GUI version provides a user-friendly interface for all wavetable operations:

1. **Creating Wavetables**

   - Click "Create Wavetable" button
   - Select input directory containing audio files
   - Choose output location and filename
   - Select ordering (alphanumeric or random)
   - Click "Create" to generate the wavetable bank
2. **Decompiling Wavetables**

   - Click "Decompile Wavetable" button
   - Select input .polyend file
   - Choose output directory
   - Click "Decompile" to extract individual WAV files
3. **Recompiling Wavetables**

   - Click "Recompile Wavetable" button
   - Select input directory containing WAV files
   - Choose output location and filename
   - Click "Recompile" to create the wavetable bank

The GUI provides real-time feedback and progress updates for all operations.

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

## Troubleshooting

### Permission Errors (macOS)

If you get "Operation not permitted" errors when using the GUI version:

**Cause:** macOS quarantine system restricts downloaded apps from accessing the file system.

**Solutions:**

1. **Remove quarantine (Recommended):**
   ```bash
   # Replace with your actual app path
   xattr -d com.apple.quarantine "/path/to/Medusa Wavetable Utility.app"
   
   # Or use the included script
   ./fix_quarantine.sh
   ```

2. **Use the built-in workaround:**
   - The app will now prompt you to select both input file AND output directory
   - Choose a directory you have write access to (like Desktop or Documents)

3. **Check quarantine status:**
   ```bash
   # Check if app is quarantined
   xattr -l "/path/to/Medusa Wavetable Utility.app"
   
   # Should show no com.apple.quarantine if fixed
   ```

### FFmpeg Not Found

If you get "FFmpeg not found" errors:

1. Install using Homebrew:
   ```bash
   brew install ffmpeg
   ```

2. Or download from [ffmpeg.org](https://ffmpeg.org/download.html)

### File Format Issues

- Ensure input audio files are in supported formats (WAV, AIFF, MP3, OGG)
- For best results, use high-quality source audio (44.1kHz or higher)
- The tool automatically converts to the required format

## Technical Details

The Polyend Medusa wavetable file format consists of 64 wavetables, each containing a single-cycle waveform. The tool handles all the technical details of file formatting and metadata automatically.

## Testing (For Developers — Users can ignore this)

The project includes a comprehensive test suite using pytest. The test structure is organized as follows:

```
tests/
├── __init__.py
├── conftest.py           # pytest configuration and fixtures
├── test_cli.py          # CLI command tests
├── test_core.py         # Core functionality tests
└── data/                # Test data directory
    ├── valid/          # Valid test files
    └── invalid/        # Invalid test files
```

### Running Tests

1. Install test dependencies:

   ```bash
   pip install -r requirements.txt
   ```
2. Run the test suite:

   ```bash
   pytest tests/
   ```

   For more detailed output:

   ```bash
   pytest -v tests/
   ```

### Test Coverage

The test suite covers:

- Basic CLI functionality (--version, --help)
- Decompiling valid and invalid .polyend files
- Recompiling WAV files
- Creating wavetable banks (both normal and random ordering)
- Core functionality testing

Tests follow best practices:

- Using pytest fixtures for test data and temporary directories
- Proper cleanup after tests
- Testing both success and failure cases
- Testing file existence and content
- Using temporary directories for test outputs

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). This means:

- ✔️ You can view and fork this code
- ✔️ You can submit contributions via pull requests
- ❌ You cannot use this code in commercial projects
- ❌ You cannot modify or distribute this code without sharing your changes
- ❌ You cannot use this code in closed-source projects

All rights reserved. For permissions beyond the scope of this license, please contact the author.
