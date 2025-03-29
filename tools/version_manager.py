#!/usr/bin/env python3
"""Version management utilities for Medusa Wavetable Utility."""

import os
import re
import sys
import datetime
from pathlib import Path

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

def generate_release_notes(version):
    """Generate release notes for the specified version."""
    version_file = get_version_file()
    with open(version_file) as f:
        content = f.read()
    
    # Extract version history
    history_match = re.search(r'VERSION_HISTORY = {(.*?)}', content, re.DOTALL)
    if not history_match:
        raise ValueError("Version history not found")
    
    history = eval(f"{{{history_match.group(1)}}}")
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
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "bump":
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
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()