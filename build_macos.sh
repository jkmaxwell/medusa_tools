#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="Medusa Wavetable Utility"
APP_PATH="dist/${APP_NAME}.app"
CERT_NAME="Developer ID Application: Justin Maxwell (52BMULT3J4)"
VERSION=$(python3 -c "from version import __version__; print(__version__)")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Building ${APP_NAME}...${NC}"

# Clean previous build
echo "Cleaning previous build..."
if [ -d "build" ]; then
    rm -rf build
fi
if [ -d "dist" ]; then
    rm -rf dist
fi

# Use the project venv's PyInstaller if it isn't on PATH
if command -v pyinstaller >/dev/null 2>&1; then
    PYINSTALLER=pyinstaller
elif [ -x "venv/bin/pyinstaller" ]; then
    PYINSTALLER="venv/bin/pyinstaller"
else
    echo -e "${RED}PyInstaller not found. Install it with: venv/bin/pip install pyinstaller${NC}"
    exit 1
fi

# Build the app with --clean flag to ensure clean build
echo "Building with PyInstaller ($PYINSTALLER)..."
"$PYINSTALLER" --clean medusa.spec

# Check if build was successful
if [ ! -d "$APP_PATH" ]; then
    echo -e "${RED}Build failed! App bundle not found.${NC}"
    exit 1
fi

# Sign the app from inside out — --deep is unreliable for PyInstaller bundles
# with nested frameworks. We must sign inner binaries before outer ones.
echo "Signing binaries (inside out)..."

sign_binary() {
    codesign --force --options runtime --timestamp \
        --entitlements entitlements.plist \
        --sign "$CERT_NAME" "$1" 2>/dev/null || true
}

# 1. Sign every Mach-O file (catches .dylib, .so, executables, Qt frameworks
#    without extensions, and shared libraries) — deepest paths first
while IFS= read -r f; do
    if file "$f" | grep -q "Mach-O"; then
        sign_binary "$f"
    fi
done < <(find "$APP_PATH" -type f | awk '{ print length, $0 }' | sort -rn | cut -d' ' -f2-)

# 2. Sign .framework bundles deepest first
while IFS= read -r fw; do
    sign_binary "$fw"
done < <(find "$APP_PATH" -name "*.framework" -type d | awk '{ print length, $0 }' | sort -rn | cut -d' ' -f2-)

# 3. Sign the app bundle itself (must be last)
echo "Signing app bundle..."
codesign --force --options runtime --timestamp \
    --entitlements entitlements.plist \
    --sign "$CERT_NAME" \
    "$APP_PATH"

# Verify the signature
echo "Verifying signature..."
codesign --verify --verbose "$APP_PATH"

# Create zip file for distribution
echo "Creating zip archive..."
cd dist
ditto -c -k --keepParent "${APP_NAME}.app" "${APP_NAME}_v${VERSION}_macos.zip"
cd ..

echo -e "${GREEN}Build completed successfully!${NC}"
echo -e "The app is available at: ${APP_PATH}"
echo -e "The zip archive is available at: dist/${APP_NAME}_v${VERSION}_macos.zip"

# Notarize with Apple
echo "Submitting for notarization (this may take a few minutes)..."
xcrun notarytool submit "$(pwd)/dist/${APP_NAME}_v${VERSION}_macos.zip" \
    --keychain-profile "AC_PASSWORD" \
    --wait

echo "Stapling notarization ticket..."
xcrun stapler staple "$APP_PATH"

echo "Re-zipping with stapled app..."
cd dist
rm "${APP_NAME}_v${VERSION}_macos.zip"
ditto -c -k --keepParent "${APP_NAME}.app" "${APP_NAME}_v${VERSION}_macos.zip"
cd ..

echo -e "${GREEN}Done! Notarized and stapled.${NC}"
echo -e "Distribute: dist/${APP_NAME}_v${VERSION}_macos.zip" 