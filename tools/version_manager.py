#!/usr/bin/env python3
"""Version management utilities for Medusa Wavetable Utility."""

import os
import re
import sys
import json
import datetime
import urllib.request
from pathlib import Path
from packaging import version
import traceback
import ast

def get_version_file():
    """Get the path to version.py."""
    root_dir = Path(__file__).parent.parent
    return root_dir / "version.py"

def read_version():
    """Read the current version from version.py."""
    version_file = get_version_file()
    with open(version_file) as f:
        content = f.read()
    match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Version not found in version.py")
    return match.group(1)

def bump_version(version_type="patch"):
    """Bump the version number.
    
    Args:
        version_type: One of "major", "minor", or "patch"
    """
    current = read_version()
    major, minor, patch = map(int, current.split("."))
    
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    else:  # patch
        patch += 1
    
    new_version = f"{major}.{minor}.{patch}"
    return new_version

def update_version_file(new_version, changes):
    """Update version.py with new version and changes."""
    version_file = get_version_file()
    with open(version_file) as f:
        content = f.read()
    
    # Update version number
    content = re.sub(
        r'__version__ = ["\']([^"\']+)["\']',
        f'__version__ = "{new_version}"',
        content
    )
    
    # Add to version history
    history_entry = f'    "{new_version}": {{\n'
    history_entry += f'        "date": "{datetime.date.today()}",\n'
    history_entry += '        "changes": [\n'
    for change in changes:
        history_entry += f'            "{change}",\n'
    history_entry += '        ]\n    }'
    
    # Insert new history entry after VERSION_HISTORY opening
    content = re.sub(
        r'VERSION_HISTORY = {',
        f'VERSION_HISTORY = {{\n{history_entry},',
        content
    )
    
    with open(version_file, 'w') as f:
        f.write(content)

def get_latest_github_release():
    """Fetch the latest release information from GitHub."""
    url = "https://api.github.com/repos/jkmaxwell/medusa_tools/releases/latest"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return {
                'version': data['tag_name'].lstrip('v'),
                'url': data['html_url'],
                'notes': data['body']
            }
    except Exception as e:
        print(f"Warning: Could not fetch latest version: {e}")
        return None

def check_for_updates():
    """Check if a newer version is available on GitHub."""
    current = read_version()
    latest_release = get_latest_github_release()
    
    if not latest_release:
        return None
        
    current_ver = version.parse(current)
    latest_ver = version.parse(latest_release['version'])
    
    if latest_ver > current_ver:
        return {
            'current_version': current,
            'latest_version': latest_release['version'],
            'download_url': latest_release['url'],
            'release_notes': latest_release['notes']
        }
    return None

def generate_release_notes(version):
    """Generate release notes for the specified version."""
    version_file = get_version_file()
    with open(version_file) as f:
        content = f.read()
    
    # Extract version history
    history_match = re.search(r'VERSION_HISTORY\s*=\s*{([^}]*)}', content, re.DOTALL)
    if not history_match:
        raise ValueError("Version history not found")
    
    history_str = history_match.group(1).strip()
    
    # Safely parse the dictionary
    try:
        history = ast.literal_eval(f"{{{history_str}}}")
    except SyntaxError as e:
        raise ValueError(f"Failed to parse version history: {e}")
    
    if version not in history:
        raise ValueError(f"Version {version} not found in history")
    
    release_info = history[version]
    
    notes = f"# Medusa Wavetable Utility v{version}\n\n"
    notes += f"Released: {release_info['date']}\n\n"
    notes += "## Changes\n\n"
    for change in release_info['changes']:
        notes += f"- {change}\n"
    
    return notes

def main():
    """CLI interface for version management."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  version_manager.py bump [major|minor|patch]")
        print("  version_manager.py notes <version>")
        print("  version_manager.py check")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        update_info = check_for_updates()
        if update_info:
            print(f"\nUpdate available!")
            print(f"Current version: {update_info['current_version']}")
            print(f"Latest version:  {update_info['latest_version']}")
            print(f"\nDownload: {update_info['download_url']}")
            print("\nRelease Notes:")
            print(update_info['release_notes'])
        else:
            current = read_version()
            print(f"\nYou're up to date! (Version {current})")
    
    elif command == "bump":
        version_type = sys.argv[2] if len(sys.argv) > 2 else "patch"
        new_version = bump_version(version_type)
        print(f"Bumped version to {new_version}")
        
        print("\nEnter changes (one per line, empty line to finish):")
        changes = []
        while True:
            line = input().strip()
            if not line:
                break
            changes.append(line)
        
        update_version_file(new_version, changes)
        print(f"\nVersion {new_version} has been recorded")
        
    elif command == "notes":
        if len(sys.argv) < 3:
            print("Error: Version required")
            sys.exit(1)
        version = sys.argv[2]
        try:
            notes = generate_release_notes(version)
            print(notes)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    main()