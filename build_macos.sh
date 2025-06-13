#!/bin/bash

# Exit on error
set -e

# Configuration
APP_NAME="Medusa Wavetable Utility"
APP_PATH="dist/${APP_NAME}.app"
CERT_NAME="PolyendMedusaToolSelfSignCert"  # This should match the name of your certificate in Keychain Access
VERSION=$(python -c "from version import __version__; print(__version__)")

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

# Build the app with --clean flag to ensure clean build
echo "Building with PyInstaller..."
pyinstaller --clean medusa.spec

# Check if build was successful
if [ ! -d "$APP_PATH" ]; then
    echo -e "${RED}Build failed! App bundle not found.${NC}"
    exit 1
fi

# Sign the app with existing certificate
echo "Signing the app..."
codesign --force --deep --sign "$CERT_NAME" "$APP_PATH"

# Verify the signature
echo "Verifying signature..."
codesign --verify --verbose "$APP_PATH"

# Create zip file
echo "Creating zip archive..."
cd dist
zip -r "${APP_NAME}_v${VERSION}_macos.zip" "${APP_NAME}.app"
cd ..

echo -e "${GREEN}Build completed successfully!${NC}"
echo -e "The app is available at: ${APP_PATH}"
echo -e "The zip archive is available at: dist/${APP_NAME}_v${VERSION}_macos.zip"
echo -e "${YELLOW}Note: This is a development build signed with a self-signed certificate.${NC}"
echo -e "${YELLOW}Users will need to right-click and select 'Open' the first time they run the app.${NC}" 