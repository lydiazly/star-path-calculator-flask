# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Astronomical twilight display

### Changed

- Changed point labels
- Made temporary adjustment to make `get_tzid_by_tzfpy` compatible with newer tzfpy versions
- Move default output location to `output/`
- Changed package structure and update tests and scripts

## [0.1.0]

### Added

- Conversion from Gregorian/Julian calendar to Chinese calendar
- Chinese calendar conversion tests

### Changed

- Migrated to uv
- Updated tests and scripts

## [Pre-0.1.0]

### Added

- Local Mean Time (LMT)

### Changed

- Refactored to improve performance
- Included atmospheric refraction in position calculation

### Fixed

- Text display in SVG
- Removed the r=0 tick to avoid a redundant path in SVG
