# AUTOSAR Call Tree Analyzer

[![PyPI version](https://badge.fury.io/py/autosar-calltree.svg)](https://badge.fury.io/py/autosar-calltree)
[![Python Support](https://img.shields.io/pypi/pyversions/autosar-calltree.svg)](https://pypi.org/project/autosar-calltree/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python package to analyze C/AUTOSAR codebases and generate function call trees with multiple output formats.

## Features

- ✨ **AUTOSAR Support**: Full parsing of AUTOSAR macros (`FUNC`, `FUNC_P2VAR`, `FUNC_P2CONST`, `VAR`, `P2VAR`, etc.)
- 🔍 **Static Analysis**: Analyzes C source code without compilation
- 📊 **Multiple Output Formats**:
  - Mermaid sequence diagrams (Markdown)
  - XMI/UML 2.5 (importable to Enterprise Architect, MagicDraw, etc.) - *planned*
  - JSON (for custom processing) - *planned*
- 🏗️ **SW Module Support**: Map C files to SW modules via YAML configuration for architecture-level diagrams
- 📈 **Module-Aware Diagrams**: Generate diagrams with SW module names as participants
- 🚀 **Performance**: Intelligent caching for fast repeated analysis with file-by-file progress reporting
- 🎯 **Depth Control**: Configurable call tree depth
- 🔄 **Circular Dependency Detection**: Identifies recursive calls and cycles
- 📊 **Statistics**: Detailed analysis statistics including module distribution

## Installation

```bash
pip install autosar-calltree
```

For development:

```bash
git clone https://github.com/yourusername/autosar-calltree.git
cd autosar-calltree
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```bash
# Analyze a function with default settings (depth=3)
calltree --start-function Demo_Init --source-dir demo

# Use SW module configuration for architecture-level diagrams
calltree --start-function Demo_Init --source-dir demo --module-config demo/module_mapping.yaml --use-module-names --output demo/demo.md

# Specify depth and output
calltree --start-function Demo_Init --max-depth 2 -o output.md

# Verbose mode with detailed statistics and cache progress
calltree --start-function Demo_Init --verbose
```

### Python API

```python
from autosar_calltree.database.function_database import FunctionDatabase
from autosar_calltree.analyzers.call_tree_builder import CallTreeBuilder
from autosar_calltree.generators.mermaid_generator import MermaidGenerator
from autosar_calltree.config.module_config import ModuleConfig
from pathlib import Path

# Load module configuration (optional)
config = ModuleConfig(Path("demo/module_mapping.yaml"))

# Build function database (with caching and module config)
db = FunctionDatabase(source_dir="demo", module_config=config)
db.build_database(use_cache=True)

# Build call tree
builder = CallTreeBuilder(db)
result = builder.build_tree(
    start_function="Demo_Init",
    max_depth=3
)

# Generate Mermaid diagram with module names
generator = MermaidGenerator(use_module_names=True)
generator.generate(result, output_path="call_tree.md")
```

## Command-Line Options

```
calltree [OPTIONS]

Options:
  --start-function TEXT          Starting function name [required]
  --max-depth INTEGER           Maximum call depth (default: 3)
  --source-dir PATH             Source code directory (default: ./demo)
  --format [mermaid|xmi|both]   Output format (default: mermaid)
  --output PATH                 Output file path (default: call_tree.md)
  --module-config PATH          YAML file mapping C files to SW modules
  --use-module-names            Use SW module names as Mermaid participants
  --cache-dir PATH              Cache directory (default: <source-dir>/.cache)
  --no-cache                    Disable cache usage
  --rebuild-cache               Force rebuild of cache
  --no-abbreviate-rte           Do not abbreviate RTE function names
  --verbose, -v                 Enable verbose output
  --list-functions, -l          List all available functions and exit
  --search TEXT                 Search for functions matching pattern
  --help                        Show this message and exit
```

## Output Examples

### Mermaid Sequence Diagram

```mermaid

```

### Generated Markdown Structure

The tool generates comprehensive Markdown files with:
- Metadata header (timestamp, settings, statistics)
- Mermaid sequence diagram
- Function details table
- Text-based call tree
- Circular dependency warnings
- Analysis statistics

## Supported AUTOSAR Patterns

The tool recognizes and parses:

```c
// AUTOSAR function declarations
FUNC(void, RTE_CODE) Function_Name(void);
FUNC(Std_ReturnType, RTE_CODE) Com_Test(VAR(uint32, AUTOMATIC) timerId);
STATIC FUNC(uint8, CODE) Internal_Function(void);

// AUTOSAR pointer returns
FUNC_P2VAR(uint8, AUTOMATIC, APPL_VAR) Get_Buffer(void);
FUNC_P2CONST(ConfigType, AUTOMATIC, APPL_VAR) Get_Config(void);

// AUTOSAR parameters
VAR(uint32, AUTOMATIC) variable
P2VAR(uint8, AUTOMATIC, APPL_DATA) buffer
P2CONST(ConfigType, AUTOMATIC, APPL_DATA) config
CONST(uint16, AUTOMATIC) constant

// Traditional C (fallback)
void traditional_function(uint8 param);
static uint32 helper_function(void);
```

## SW Module Configuration

Map C source files to SW modules using YAML configuration:

```yaml
# module_mapping.yaml
version: "1.0"

# Specific file mappings
file_mappings:
  demo.c: DemoModule

# Pattern-based mappings (glob patterns)
pattern_mappings:
  "hw_*.c": HardwareModule
  "sw_*.c": SoftwareModule
  "com_*.c": CommunicationModule

# Default module for unmapped files (optional)
default_module: "Other"
```

**Benefits**:
- Generate architecture-level diagrams showing module interactions
- Identify cross-module dependencies
- Verify architectural boundaries
- Support high-level design documentation

**Usage**:
```bash
calltree --start-function Demo_Init --module-config module_mapping.yaml --use-module-names --max-depth 3
```

This generates diagrams with:
- **Participants**: SW module names (HardwareModule, SoftwareModule, etc.)
- **Arrows**: Function names being called between modules
- **Function Table**: Includes module column showing each function's SW module

## Use Cases

- **Documentation**: Generate call flow diagrams for documentation
- **Code Review**: Visualize function dependencies
- **Impact Analysis**: Understand change impact before modifications
- **Onboarding**: Help new developers understand codebase structure
- **Compliance**: Generate diagrams for safety certification (ISO 26262)
- **Refactoring**: Identify tightly coupled components
- **Architecture**: Verify architectural boundaries

## Project Structure

```
autosar-calltree/
├── src/autosar_calltree/
│   ├── cli/              # Command-line interface
│   ├── config/           # Configuration management (module mappings)
│   ├── parsers/          # Code parsers (AUTOSAR, C)
│   ├── analyzers/        # Analysis logic (call tree, dependencies)
│   ├── database/         # Data models and caching
│   ├── generators/       # Output generators (Mermaid)
│   └── utils/            # Utilities (empty, for future use)
├── test_demo/            # Demo AUTOSAR C files for testing
│   ├── demo.c
│   ├── hardware.c
│   ├── software.c
│   ├── communication.c
│   └── module_mapping.yaml
├── tests/                # Test suite (empty, for future use)
├── docs/                 # Documentation
│   └── requirements/     # Software requirements
└── examples/             # Example scripts (empty, for future use)
```

## Development

### Running Tests

```bash
pytest tests/
pytest --cov=autosar_calltree --cov-report=html
```

### Code Quality

```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

### Building Documentation

```bash
cd docs
make html
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Authors

- Your Name <your.email@example.com>

## Acknowledgments

- Inspired by the need for better AUTOSAR code analysis tools
- Built for the automotive embedded systems community

## Related Projects

- [PlantUML](https://plantuml.com/) - UML diagram generator
- [Doxygen](https://www.doxygen.nl/) - Documentation generator
- [cflow](https://www.gnu.org/software/cflow/) - C call graph generator

## Roadmap

- [ ] PlantUML output format
- [ ] GraphViz DOT format
- [ ] HTML interactive viewer
- [ ] VS Code extension
- [ ] GitHub Actions integration
- [x] Configuration file support (YAML for module mappings)
- [ ] Multi-threading for large codebases
- [ ] Function complexity metrics
- [ ] Dead code detection
- [ ] XMI/UML 2.5 output format

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/autosar-calltree/issues)
- **Documentation**: [Read the Docs](https://autosar-calltree.readthedocs.io)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/autosar-calltree/discussions)

---

**Made with ❤️ for the embedded systems community**
