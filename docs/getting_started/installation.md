# Installation

## Prerequisites

Before installing AUTOSAR Call Tree Analyzer, ensure you have the following:

- **Python 3.10 or higher** (3.10, 3.11, 3.12, 3.13 supported)
- **libclang** (for C code parsing)
- **pip** (Python package manager)

## Installing libclang

### macOS

```bash
# Using Homebrew
brew install llvm

# Or install via pip
pip install libclang
```

### Linux (Ubuntu/Debian)

```bash
# Install LLVM and Clang
sudo apt-get update
sudo apt-get install llvm clang libclang-dev

# Or install via pip
pip install libclang
```

### Windows

```bash
# Install via pip
pip install libclang
```

## Installing AUTOSAR Call Tree Analyzer

### From PyPI (Recommended)

```bash
pip install autosar-calltree
```

### From Source

```bash
# Clone the repository
git clone https://github.com/melodypapa/autosar_calltree.git
cd autosar_calltree

# Install in development mode
pip install -e ".[dev]"
```

### From GitHub

```bash
pip install git+https://github.com/melodypapa/autosar_calltree.git
```

## Verifying Installation

After installation, verify it works:

```bash
# Check version
calltree --version

# Get help
calltree --help

# Run a simple test
calltree -l -i /path/to/your/c/code
```

## Development Installation

For contributing to the project:

```bash
# Clone the repository
git clone https://github.com/melodypapa/autosar_calltree.git
cd autosar_calltree

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
ruff check src/ tests/
```

## Troubleshooting

### libclang not found

If you get an error about libclang not being found:

1. Ensure libclang is installed (see instructions above)
2. Set the `LLVM_CONFIG_PATH` environment variable:

```bash
# macOS with Homebrew
export LLVM_CONFIG_PATH=/opt/homebrew/opt/llvm/bin/llvm-config

# Linux
export LLVM_CONFIG_PATH=/usr/bin/llvm-config
```

### Permission errors

If you get permission errors during installation:

```bash
# Use --user flag
pip install --user autosar-calltree

# Or use a virtual environment
python -m venv venv
source venv/bin/activate
pip install autosar-calltree
```

### Python version not supported

Ensure you're using Python 3.10 or higher:

```bash
python --version
```

If you have multiple Python versions, use the specific version:

```bash
python3.12 -m pip install autosar-calltree
```

## Next Steps

- {doc}`/getting_started/quickstart` - Get started with basic usage
- {doc}`/getting_started/configuration` - Configure the tool for your project
