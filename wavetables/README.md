# Wavetables Directory

This directory contains both source wavetable files and compiled .polyend files for the Polyend Medusa synthesizer.

## Directory Structure

- `source/`: Contains the source wavetable files used to generate the compiled .polyend files
  - `vox/`: Source files for vocal wavetables
  - `sq80/`: Source files for SQ80 wavetables
  - Add new source directories as needed

- `dist/`: Contains the compiled .polyend files ready for use with the Medusa synthesizer
  - All .polyend files are generated from the source files
  - These files are included in releases

## Adding New Wavetables

1. Place your source wavetable files in the appropriate subdirectory under `source/`
2. Use the Medusa Tools CLI to compile them into .polyend files:
   ```bash
   ./medusa_cli create wavetables/source/your_source_dir dist/wavetables/your_output.polyend
   ```

## Release Process

The `dist/wavetables/` directory is included in releases, but requires manual compilation. Before each release:

1. Update source files as needed
2. Manually compile all .polyend files using the CLI:
   ```bash
   # Example for compiling all wavetable sets
   ./medusa_cli create wavetables/source/vox dist/wavetables/vox_wavetables.polyend
   ./medusa_cli create wavetables/source/sq80 dist/wavetables/sq80_wavetables.polyend
   ```
3. Test the compiled files
4. Commit both source and compiled files
5. Create the release

Note: The compiled .polyend files are not automatically generated during the release process. They must be manually compiled and committed before creating a release 