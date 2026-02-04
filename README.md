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
  - XMI/UML 2.5 (importable to Enterprise Architect, Visual Paradigm, etc.)
  - JSON (for custom processing) - *planned*
- 🏗️ **SW Module Support**: Map C files to SW modules via YAML configuration for architecture-level diagrams
- 📈 **Module-Aware Diagrams**: Generate diagrams with SW module names as participants
- 🎯 **Parameter Display**: Function parameters shown in sequence diagram calls for better visibility
- 🔄 **Automatic Conditional Detection**: Automatically detects `if`/`else` statements and generates `opt` blocks with actual conditions (Mermaid and XMI)
- 🚀 **Performance**: Intelligent caching for fast repeated analysis with file-by-file progress reporting
- 🎯 **Depth Control**: Configurable call tree depth
- 🔄 **Circular Dependency Detection**: Identifies recursive calls and cycles
- 📊 **Statistics**: Detailed analysis statistics including module distribution
- 📝 **Clean Diagrams**: Return statements omitted by default for cleaner sequence diagrams (configurable)

## What's New

### Version 0.4.0 (2026-02-04)

**New Feature: Automatic Conditional Call Detection**

The tool now automatically detects function calls inside `if`/`else` statements and displays them in `opt` blocks with the actual condition text. This feature is supported in both Mermaid and XMI output formats.

**Mermaid Example**:

**Source Code**:
```c
FUNC(void, RTE_CODE) Demo_Update(VAR(uint32, AUTOMATIC) update_mode)
{
    SW_UpdateState(update_mode);

    if (update_mode == 0x05) {
        COM_SendLINMessage(0x456, (uint8*)0x20003000);
    }
}
```

**Generated Mermaid Diagram**:
```mermaid
sequenceDiagram
    participant Demo_Update
    participant COM_SendLINMessage
    participant SW_UpdateState

    Demo_Update->>SW_UpdateState: call(new_state)
    opt update_mode == 0x05
    Demo_Update->>COM_SendLINMessage: call(msg_id, data)
    end
```

**XMI Example**:
```xml
<uml:fragment name="opt" interactionOperator="opt">
  <uml:operand name="update_mode == 0x05">
    <uml:message name="COM_SendLINMessage" signature="COM_SendLINMessage(msg_id, data)">
      <!-- message events -->
    </uml:message>
  </uml:operand>
</uml:fragment>
```

**Benefits**:
- No manual configuration required - automatic detection
- Shows actual condition text for better understanding
- Supports nested conditionals
- Handles `if`, `else if`, and `else` statements
- Works with both Mermaid and XMI output formats
- XMI uses UML combined fragments (standard UML 2.5 representation)

## Installation

```bash
pip install autosar-calltree
```

For development:

```bash
git clone https://github.com/melodypapa/autosar-calltree.git
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

# Generate XMI format (with opt block support)
calltree --start-function Demo_MainFunction --source-dir demo --format xmi --output demo/demo.xmi

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

# Generate Mermaid diagram with module names and parameters
# include_returns=False (default) omits return statements for cleaner diagrams
generator = MermaidGenerator(
    use_module_names=True,
    include_returns=False
)
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

### Mermaid Sequence Diagram with Opt Blocks

```mermaid
sequenceDiagram
    participant DemoModule
    participant CommunicationModule
    participant HardwareModule
    participant SoftwareModule

    DemoModule->>CommunicationModule: COM_InitCommunication(baud_rate, buffer_size)
    opt mode > 0x00
    DemoModule->>DemoModule: Demo_Update(mode)
    opt mode == 0x05
    DemoModule->>CommunicationModule: COM_SendLINMessage(msg_id, data)
    end
    DemoModule->>SoftwareModule: SW_UpdateState(new_state)
    end
    DemoModule->>HardwareModule: HW_ReadSensor(sensor_id)
    DemoModule->>SoftwareModule: SW_ProcessData(data, length)
```

**Key Features**:
- Conditional calls are automatically wrapped in `opt` blocks
- Shows actual condition text from source code (e.g., `mode > 0x00`, `mode == 0x05`)
- Supports nested conditionals
- Participants appear in the order they are first encountered
- Function parameters are displayed in the call arrows
- Return statements are omitted by default for cleaner visualization
- Module names are used as participants when `--use-module-names` is enabled

### XMI Output with Opt Blocks

The XMI output also supports opt blocks using UML combined fragments:

```xml
<uml:fragment name="opt" interactionOperator="opt">
  <uml:operand name="update_mode == 0x05">
    <uml:message name="COM_SendLINMessage" 
                 signature="COM_SendLINMessage(msg_id, data)"
                 messageSort="synchCall">
      <uml:sendEvent xmi:id="calltree_22"/>
      <uml:receiveEvent xmi:id="calltree_23"/>
    </uml:message>
  </uml:operand>
</uml:fragment>
```

**XMI Features**:
- UML 2.5 compliant XMI documents
- Combined fragments with `opt` interaction operator
- Operand elements display the condition text
- Can be imported into UML tools like Enterprise Architect, Visual Paradigm, MagicDraw
- Proper XML structure with correct namespaces

### Generated Markdown Structure

The tool generates comprehensive Markdown files with:
- Metadata header (timestamp, settings, statistics)
- Mermaid sequence diagram with function parameters and opt blocks
- Function details table with parameter information
- Text-based call tree
- Circular dependency warnings
- Analysis statistics

**Note**: Return statements are omitted from sequence diagrams by default for cleaner visualization. This can be configured programmatically when using the Python API.

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
calltree --start-function Demo_Init --module-config demo/module_mapping.yaml --use-module-names --max-depth 3 --output demo/demo_sequence.md
```

This generates diagrams with:
- **Participants**: SW module names (HardwareModule, SoftwareModule, etc.) in the order they are first encountered
- **Arrows**: Function names with parameters being called between modules
- **Opt Blocks**: Conditional calls wrapped with actual condition text
- **Function Table**: Includes module column showing each function's SW module
- **Clean Visualization**: Return statements omitted by default

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
│   ├── generators/       # Output generators (Mermaid, XMI)
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

The project has **comprehensive test coverage** with 298 tests across all modules:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest -vv tests/

# Run specific test module
pytest tests/test_models.py
pytest tests/test_parsers.py
pytest tests/test_database.py
pytest tests/test_analyzers.py
pytest tests/test_config.py
pytest tests/test_generators.py
pytest tests/test_cli.py
pytest tests/test_integration.py

# Run specific test case
pytest tests/test_models.py::TestFunctionType::test_function_type_enum_values

# Run tests with live stdout output (useful for debugging)
pytest -vv -s tests/

# Run tests and show coverage report
pytest --cov=autosar_calltree --cov-report=html --cov-report=term

# Run tests with coverage and omit tests from coverage report
pytest --cov=autosar_calltree --cov-report=html --cov-report=term --omit=tests/
```

### Test Coverage

The project maintains **89% code coverage** across all modules:

| Module | Coverage | Tests |
|--------|----------|-------|
| Models | 97% | 28 |
| AUTOSAR Parser | 97% | 15 |
| C Parser | 86% | 18 |
| Database | 83% | 20 |
| Analyzers | 95% | 20 |
| Config | 97% | 25 |
| Generators | 89% | 45 |
| CLI (Integration) | 90% | 14 |
| End-to-End | ~90% | 120 |
| **Total** | **89%** | **298** |

### Code Quality

```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/

# Run all quality checks (uses pre-configured scripts)
./scripts/run_quality.sh

# Check for traceability between requirements and tests
python scripts/check_traceability.py
```

### Slash Commands

The project provides convenient slash commands for common development tasks:

```bash
# Run all tests
/test

# Run quality checks
/quality

# Test requirement management
/req

# Merge a pull request
/merge-pr

# Generate GitHub workflow
/gh-workflow

# Parse and update documentation
/parse

# Sync documentation
/sync-docs
```

These commands are documented in `.claude/commands/` and can be used from within Claude Code.

### Requirements Traceability

The project maintains 100% traceability between requirements and tests:

```bash
# Check traceability matrix
python scripts/check_traceability.py

# View traceability documentation
cat docs/TRACEABILITY.md

# View requirements index
cat docs/requirements/README.md

# View test index
cat docs/tests/README.md
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

- Melodypapa <melodypapa@outlook.com>

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
- [x] XMI/UML 2.5 output format with opt block support
- [x] Automatic conditional call detection with opt blocks

## Support

- **Issues**: [GitHub Issues](https://github.com/melodypapa/autosar-calltree/issues)
- **Documentation**: [Read the Docs](https://autosar-calltree.readthedocs.io)
- **Discussions**: [GitHub Discussions](https://github.com/melodypapa/autosar-calltree/discussions)

---

**Made with ❤️ for the embedded systems community**