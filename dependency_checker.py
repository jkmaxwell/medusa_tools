#!/usr/bin/env python3

import os
import subprocess
import shutil
from typing import Dict, Union

# Installation instructions template
INSTALL_INSTRUCTIONS = """
FFmpeg is required but not found on your system. To install FFmpeg:

Using Homebrew (recommended):
1. Open Terminal
2. Install Homebrew if not installed:
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
3. Install FFmpeg:
   brew install ffmpeg

Alternative methods:
• Download from FFmpeg website: https://ffmpeg.org/download.html
• Use MacPorts: sudo port install ffmpeg

After installing, restart this application.
"""

def check_ffmpeg(custom_path: str = None) -> Dict[str, Union[bool, str]]:
    """
    Check if ffmpeg is installed and accessible.
    
    Args:
        custom_path: Optional path to ffmpeg executable
    
    Returns:
        Dict containing:
            - installed (bool): Whether ffmpeg is installed
            - version (str): ffmpeg version if installed
            - error (str): Error message if not installed
            - install_instructions (str): Installation instructions if not installed
            - path: Path to ffmpeg if found
    """
    # Common installation paths on macOS
    common_paths = [
        '/usr/local/bin/ffmpeg',  # Homebrew default
        '/opt/local/bin/ffmpeg',  # MacPorts default
        '/usr/bin/ffmpeg',        # System default
    ]
    
    # Try custom path first if provided
    if custom_path:
        common_paths.insert(0, custom_path)
    
    # Check if ffmpeg is in PATH
    path_ffmpeg = shutil.which('ffmpeg')
    if path_ffmpeg:
        common_paths.insert(0, path_ffmpeg)
    
    # Try each possible location
    for ffmpeg_path in common_paths:
        if os.path.exists(ffmpeg_path):
            try:
                # Get version info
                result = subprocess.run([ffmpeg_path, '-version'],
                                     capture_output=True,
                                     text=True,
                                     check=True)
                return {
                    'installed': True,
                    'version': result.stdout.strip(),  # Keep full version output
                    'error': None,
                    'install_instructions': None,
                    'path': ffmpeg_path
                }
            except (subprocess.CalledProcessError, PermissionError) as e:
                if isinstance(e, PermissionError):
                    error = f'FFmpeg found at {ffmpeg_path} but not working correctly. Try: chmod +x {ffmpeg_path}'
                else:
                    error = 'FFmpeg is found but not working correctly. Try reinstalling.'
                continue
    
    # Determine appropriate error message for when no working ffmpeg is found
    if path_ffmpeg:
        error = 'FFmpeg is found but not working correctly. Try reinstalling.'
    elif custom_path:
        error = f'FFmpeg not found at specified path: {custom_path}'
    else:
        error = 'FFmpeg is not installed or not in system PATH'
    
    # Return error state with appropriate message
    return {
        'installed': False,
        'version': None,
        'error': error,
        'install_instructions': INSTALL_INSTRUCTIONS,
        'path': None
    }