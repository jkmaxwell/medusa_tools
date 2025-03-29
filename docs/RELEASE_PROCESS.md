# Release Process

This document outlines the release process for Medusa Wavetable Utility.

## Version Numbering

We follow [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

## Branching Strategy

- `main` - Main development branch, always stable
- `develop` - Integration branch for new features
- `feature/*` - Feature branches
- `release/*` - Release preparation branches
- `hotfix/*` - Urgent fixes for production issues

## Release Process

1. **Feature Development**
   ```bash
   # Create feature branch
   git checkout develop
   git checkout -b feature/new-feature
   
   # Work on feature
   git commit -m "Add new feature"
   
   # When ready, merge to develop
   git checkout develop
   git merge feature/new-feature
   ```

2. **Release Preparation**
   ```bash
   # Create release branch
   git checkout -b release/v1.1.0
   
   # Bump version
   python tools/version_manager.py bump minor
   
   # Update version in GUI
   # Test thoroughly
   # Update documentation
   
   # Commit version bump
   git add version.py
   git commit -m "Bump version to 1.1.0"
   ```

3. **Release Creation**
   ```bash
   # Merge to main
   git checkout main
   git merge release/v1.1.0
   
   # Tag release
   git tag -a v1.1.0 -m "Version 1.1.0"
   
   # Generate release notes
   python tools/version_manager.py notes 1.1.0 > RELEASE_NOTES.md
   
   # Build release artifacts
   pyinstaller --noconfirm medusa.spec
   
   # Create release zip
   cd dist && zip -r "Medusa_Wavetable_Utility_v{version}.zip" "Medusa Wavetable Utility.app" && cd ..
   
   # Create release on GitHub
   # Upload artifacts (zip file) and release notes
   ```

4. **Post-Release**
   ```bash
   # Merge back to develop
   git checkout develop
   git merge release/v1.1.0
   
   # Delete release branch
   git branch -d release/v1.1.0
   
   # Push everything
   git push origin main develop --tags
   ```

## Hotfix Process

1. **Create Hotfix**
   ```bash
   git checkout -b hotfix/v1.1.1 main
   
   # Fix the issue
   # Bump patch version
   python tools/version_manager.py bump patch
   
   git add .
   git commit -m "Fix critical issue"
   ```

2. **Merge Hotfix**
   ```bash
   # Merge to main
   git checkout main
   git merge hotfix/v1.1.1
   
   # Tag hotfix
   git tag -a v1.1.1 -m "Version 1.1.1"
   
   # Merge to develop
   git checkout develop
   git merge hotfix/v1.1.1
   
   # Delete hotfix branch
   git branch -d hotfix/v1.1.1
   ```

## Version Management Tools

The `tools/version_manager.py` script provides utilities for version management:

```bash
# Bump version
python tools/version_manager.py bump [major|minor|patch]

# Generate release notes
python tools/version_manager.py notes <version>
```

## Release Checklist

- [ ] All tests pass
- [ ] Version bumped
- [ ] Documentation updated
- [ ] Release notes generated
- [ ] Artifacts built and tested
- [ ] GitHub release created
- [ ] Version tagged
- [ ] Changes merged to all relevant branches

## Maintaining Multiple Versions

- Major versions are maintained in separate branches: `1.x`, `2.x`, etc.
- Security fixes are backported to supported versions
- Only the latest minor version of each major version receives updates
- End-of-life versions are clearly marked in documentation

## Release Schedule

- Minor releases: Every 2-3 months
- Patch releases: As needed for bug fixes
- Major releases: When significant changes warrant it

## Support Policy

- Latest version: Full support
- Previous major version: Security updates only
- Older versions: No support