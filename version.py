"""Version information for Medusa Wavetable Utility."""

# Follow Semantic Versioning 2.0.0 (https://semver.org/)
# MAJOR.MINOR.PATCH format
# Major version for incompatible API changes
# Minor version for new functionality in a backwards compatible manner
# Patch version for backwards compatible bug fixes

__version__ = "1.5.3"
__author__ = "jkmaxwell"
__app_name__ = "Medusa Wavetable Utility"

# Update history
VERSION_HISTORY = {
    "1.5.3": {
        "date": "2026-07-02",
        "changes": [
            "Fixed FFmpeg lookup in the packaged app — Create from Audio Files works again",
            "Alphabetical/random ordering now applies with 64 or fewer input files",
            "Create fills all 64 slots by cycling sources when given fewer than 64 files",
            "Decompile now validates .polyend files instead of extracting garbage",
            "process command converts sample rate and bit depth correctly (8/16/24/32-bit, any rate)",
            "Clear error when recompiling from an incomplete set of WAV files",
            "Web app: fixed temp-file cleanup, sanitized output filenames, debug mode off by default",
            "GUI: background errors no longer leave buttons stuck disabled; update check can't race operations",
            "GUI: Create save dialog no longer defaults to the read-only system root when launched from Finder",
            "Repaired and expanded the test suite",
        ]
    },
    "1.5.2": {
        "date": "2026-06-04",
        "changes": [
            "Fixed GUI crash on launch for all users (missing resources_rc in bundle)",
            "Switched to Developer ID signing and notarization — no Gatekeeper warnings",
            "Fixed UI freezing during long operations (background threading)",
            "Fixed temp directory writing inside signed app bundle",
            "Fixed FFmpeg path detection for Intel and Apple Silicon",
            "Dropped app sandbox entitlements that were breaking file access",
            "Fixed version mismatch in app bundle Info.plist",
        ]
    },
    "1.5.1": {
        "date": "2025-06-12",
        "changes": [
            "Testing",
        ]
    },
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