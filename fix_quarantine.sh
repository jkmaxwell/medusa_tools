#!/bin/bash

echo "Medusa Wavetable Utility - Quarantine Fix"
echo "========================================"
echo ""

# Find the app in common locations
APP_PATHS=(
    "$HOME/Downloads/Medusa Wavetable Utility.app"
    "$HOME/Downloads/Medusa Wavetable Utility 2.app" 
    "/Applications/Medusa Wavetable Utility.app"
    "$HOME/Applications/Medusa Wavetable Utility.app"
)

FOUND_APP=""
for path in "${APP_PATHS[@]}"; do
    if [ -d "$path" ]; then
        FOUND_APP="$path"
        break
    fi
done

if [ -z "$FOUND_APP" ]; then
    echo "Could not find Medusa Wavetable Utility.app automatically."
    echo "Please drag and drop the app onto this script, or run:"
    echo "xattr -d com.apple.quarantine '/path/to/Medusa Wavetable Utility.app'"
    exit 1
fi

echo "Found app at: $FOUND_APP"
echo ""

# Check if quarantined
if xattr -p com.apple.quarantine "$FOUND_APP" >/dev/null 2>&1; then
    echo "App is quarantined. Removing quarantine..."
    xattr -d com.apple.quarantine "$FOUND_APP"
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully removed quarantine!"
        echo "The app should now work properly."
    else
        echo "❌ Failed to remove quarantine. You may need to run with sudo:"
        echo "sudo xattr -d com.apple.quarantine '${FOUND_APP}'"
    fi
else
    echo "✅ App is not quarantined. No action needed."
fi

echo ""
echo "You can now run the Medusa Wavetable Utility normally." 