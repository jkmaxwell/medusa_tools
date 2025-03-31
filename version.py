"""Version information for Medusa Wavetable Utility."""

# Follow Semantic Versioning 2.0.0 (https://semver.org/)
# MAJOR.MINOR.PATCH format
# Major version for incompatible API changes
# Minor version for new functionality in a backwards compatible manner
# Patch version for backwards compatible bug fixes

__version__ = "1.5.0"
__author__ = "jkmaxwell"
__app_name__ = "Medusa Wavetable Utility"

# Update history
VERSION_HISTORY = {
    "1.5.0": {
        "date": "2025-03-29",
        "changes": [
            "Gave up on GUI for now. It's above my pay grade. Just CLI for now.",
        ]
    },
    "1.4.0": {
        "date": "2025-03-29",
        "changes": [
            "Finally got FFMPEG and the temp directory working! Oh my god!",
            "Added version manager",
        ]
    },
    "1.1.0": {
        "date": "2025-03-28",
        "changes": [
            "Made it look like a keygen",
            "Added a link to me",
        ]
    },
    "1.0.0": {
        "date": "2024-03-28",
        "changes": [
            "Initial release",
            "Wavetable bank creation from audio files",
            "Support for random/alphabetical file selection",
            "Extract and modify existing wavetable banks",
        ]
    }
}