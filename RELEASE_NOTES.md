# Medusa Wavetable Utility v1.5.3

Released: 2026-07-02

## Changes

- Fixed FFmpeg lookup in the packaged app — Create from Audio Files works again
- Alphabetical/random ordering now applies with 64 or fewer input files
- Create fills all 64 slots by cycling sources when given fewer than 64 files
- Decompile now validates .polyend files instead of extracting garbage
- `process` command converts sample rate and bit depth correctly (8/16/24/32-bit, any rate)
- Clear error when recompiling from an incomplete set of WAV files
- Web app: fixed temp-file cleanup, sanitized output filenames, debug mode off by default
- GUI: background errors no longer leave buttons stuck disabled; update check can't race operations
- GUI: Create save dialog no longer defaults to the read-only system root when launched from Finder
- Repaired and expanded the test suite

## Installation

1. Download `Medusa Wavetable Utility_v1.5.3_macos.zip` from the releases page (GUI, signed and notarized), or the `medusa_cli` executable for command-line use
2. The GUI bundles FFmpeg; for the CLI, ensure FFmpeg is installed on your system
3. Run the app, or run `medusa_cli` from your terminal
