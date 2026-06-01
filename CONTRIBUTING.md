# Contributing to AI Signal

Thank you for your interest in contributing to AI Signal! This document provides
guidelines and information to help you get started.

## Getting Started

### Prerequisites

- Python 3.11 or later
- Git

### Development Setup

```bash
# Clone the repository
git clone https://github.com/vhdesai/ai-signal.git
cd ai-signal

# Run the setup script (creates venv, installs deps)
pwsh ./scripts/setup.ps1       # Windows
./scripts/setup.sh             # Linux / macOS

# Activate the virtual environment
.venv\Scripts\activate         # Windows
source .venv/bin/activate      # Linux / macOS
```

### Running the Pipeline

```bash
# Full pipeline
pwsh ./scripts/run-pipeline.ps1    # Windows
./scripts/run-pipeline.sh          # Linux / macOS

# Individual stage
pwsh ./scripts/run-pipeline.ps1 build-site
```

## How to Contribute

### Reporting Issues

- Use the [GitHub issue tracker](https://github.com/vhdesai/ai-signal/issues)
- Include steps to reproduce, expected vs actual behavior
- Attach relevant logs or screenshots

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test locally by running the pipeline end-to-end
5. Commit with a clear message: `git commit -m "Add feature X"`
6. Push to your fork: `git push origin feature/my-feature`
7. Open a Pull Request against `main`

### Pull Request Guidelines

- Keep PRs focused on a single change
- Update documentation if your change affects the user-facing behavior
- Ensure the pipeline runs successfully (`run-all`) before submitting
- Add a CHANGELOG entry under `[Unreleased]` for notable changes

## Project Structure

```
source/news_trends/     # Pipeline Python package
source/config/          # YAML configuration files
scripts/                # Setup, run, and sync scripts
site/                   # Generated static HTML (do not edit manually)
articles/               # Generated article notes
indexes/                # SQLite DB + ChromaDB
```

## Code Style

- Follow PEP 8 for Python code
- Use type hints where practical
- Keep functions focused and well-documented
- Prefer explicit over implicit

## Areas for Contribution

- **New entity/topic configurations** — Add companies or themes to track
- **Digest parser improvements** — Handle new digest formats in `split.py`
- **Site theme enhancements** — Improve the generated HTML/CSS in `site.py`
- **URL repair heuristics** — Improve relevance scoring in `urls.py`
- **Documentation** — Improve guides, add examples, fix typos

## Questions?

Open a [discussion](https://github.com/vhdesai/ai-signal/discussions) or file an issue.
