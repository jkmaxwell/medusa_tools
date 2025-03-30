# macOS Packaging Guide

## FFmpeg Integration

The application requires ffmpeg for audio processing. For macOS app bundles, ffmpeg is packaged in the following way:

1. FFmpeg binary is included in the app bundle's Resources directory
2. The spec file configuration in `medusa.spec`:
```python
'datas': [
    ('medusa_core.py', '.'),
    ('version.py', '.'),
    ('styles', 'styles'),
    ('tools/version_manager.py', 'tools'),
    ('/opt/homebrew/bin/ffmpeg', '.')  # Copies ffmpeg to Resources directory
],
```

3. The application code in `medusa_core.py` locates ffmpeg in the Resources directory when running from the app bundle:
```python
if getattr(sys, 'frozen', False):
    app_path = os.path.dirname(os.path.dirname(sys.executable))  # Go up to Contents
    ffmpeg_path = os.path.join(app_path, 'Resources', 'ffmpeg')
    if not os.path.exists(ffmpeg_path):
        raise Exception(f"ffmpeg not found at {ffmpeg_path}")
    # Make ffmpeg executable
    os.chmod(ffmpeg_path, 0o755)
else:
    ffmpeg_path = 'ffmpeg'
```

This ensures that:
- FFmpeg is properly bundled with the application
- The binary is made executable at runtime
- The application can find ffmpeg in both development and bundled environments

## App Bundle Structure

The final app bundle structure follows macOS conventions:
```
Medusa Wavetable Utility.app/
└── Contents/
    ├── MacOS/          # Main executable and binaries
    ├── Resources/      # Resource files
    │   ├── ffmpeg     # FFmpeg binary
    │   ├── styles/    # Application styles
    │   └── tools/     # Application tools
    └── Info.plist     # Bundle metadata