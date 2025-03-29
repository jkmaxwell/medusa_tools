#!/usr/bin/env python3

import subprocess
import shutil
from typing import Dict, Union

def check_ffmpeg() -> Dict[str, Union[bool, str]]:
    """
    Check if ffmpeg is installed and accessible.
    
    Returns:
        Dict containing:
            - installed (bool): Whether ffmpeg is installed
            - version (str): ffmpeg version if installed
            - error (str): Error message if not installed
            - install_instructions (str): Installation instructions if not installed
    """
    # First check if ffmpeg is in PATH
    if shutil.which('ffmpeg'):
        try:
            # Get version info
            result = subprocess.run(['ffmpeg', '-version'], 
                                 capture_output=True, 
                                 text=True, 
                                 check=True)
            return {
                'installed': True,
                'version': result.stdout.split('\n')[0],
                'error': None,
                'install_instructions': None
            }
        except subprocess.CalledProcessError:
            pass
    
    # ffmpeg not found or not working, provide installation instructions
    return {
        'installed': False,
        'version': None,
        'error': 'FFmpeg is not installed or not accessible',
        'install_instructions': """
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
    }