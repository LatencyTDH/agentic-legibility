# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-04-07

### Added
- Initial release
- Repository scanner (`scripts/scan_repo.py`) detecting 100+ signals across 7 categories
- Scoring rubric (`references/scoring-rubric.md`) with full/partial/zero credit definitions
- Agent skill (`SKILL.md`) with formatted scorecard output
- Categories: Bootstrap, Entry Points, Documentation, Architecture, Testing, Code Quality, Security
- Grade scale A+ through F- with agent capability descriptions
- Two-pass scoring: mechanical scanner baseline + LLM qualitative assessment per category
- Support for: JavaScript/TypeScript, Python, Rust, Go, Ruby, Java, and more
- Detection of 15+ linter/formatter configs, 8+ CI systems, 12+ package managers
