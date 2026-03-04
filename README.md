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
  - Rhapsody XMI 2.1 (importable to IBM Rhapsody 8.0+)
  - JSON (for custom processing) - *planned*
- 🏗️ **SW Module Support**: Map C files to SW modules via YAML configuration for architecture-level diagrams
- 📈 **Module-Aware Diagrams**: Generate diagrams with SW module names as participants
- 🎯 **Parameter Display**: Function parameters shown in sequence diagram calls for better visibility
- 🔄 **Automatic Conditional Detection**: Automatically detects `if`/`else` statements and generates `opt` blocks with actual conditions (Mermaid and Rhapsody XMI)
- 🚀 **Performance**: Intelligent caching for fast repeated analysis with file-by-file progress reporting
- 🎯 **Depth Control**: Configurable call tree depth
- 🔄 **Circular Dependency Detection**: Identifies recursive calls and cycles
- 📊 **Statistics**: Detailed analysis statistics including module distribution
- 📝 **Clean Diagrams**: Return statements omitted by default for cleaner sequence diagrams (configurable)

## What's New

### Version 0.8.3 (2026-03-05)

**🎉 Major Feature: Comprehensive C Comment Removal with String Literal Protection**

This release adds robust C comment removal that protects string literals from being incorrectly parsed as comments.

**New Features**:
- 🛡️ **String Literal Protection**: Comments inside string literals are preserved correctly
- 📝 **Multi-line String Support**: Handles complex multi-line string literals
- ✅ **Production Ready**: Verified on real AUTOSAR codebases with complex string formatting

**Example**:
```c
// String containing what looks like a comment
const char* msg = "Hello // this is not a comment";
const char* multi = "Start /* also not a comment */ End";
```

**Benefits**:
- ✅ Prevents false positive comment detection inside strings
- ✅ Handles both single-line (`//`) and multi-line (`/* */`) comments
- ✅ Preserves string literal content exactly as written
- ✅ Verified on production AUTOSAR codebases

---

### Version 0.8.0 (2026-03-01)

**🎉 Major Feature: Full Rhapsody XMI 2.1 Compatibility**

This release adds complete Rhapsody XMI 2.1 compatibility, matching Rhapsody's native export format for seamless import into IBM Rhapsody 8.0+.

**New Features**:
- 🎯 **Rhapsody XMI 2.1 Export**: Full XMI 2.1 compliant output with OMG UML namespace
- 🔑 **GUID+ ID Format**: Uses `GUID+<UUID>` format for maximum Rhapsody compatibility
- 📊 **MessageOccurrenceSpecification**: Explicit send/receive occurrence fragments
- 🏗️ **Role Definitions**: Proper lifeline role definitions via ownedAttribute
- 🌐 **Element Imports**: Profile metaclass imports for complete model structure
- 🔄 **CoveredBy Attributes**: Lifeline coverage tracking for message occurrences
- 📦 **Complex Profile Structure**: Nested eAnnotations with EPackage references

**CLI Usage**:
```bash
# Generate Rhapsody-compatible XMI
calltree --start-function Demo_MainFunction \
         --source-dir demo/src \
         --format rhapsody \
         --output demo/rhapsody_output.xmi
```

**Implementation**:
- Independent `RhapsodyXmiGenerator` implementation (does not extend XmiGenerator)
- Uses lxml for proper namespace control
- Full structural match with Rhapsody's native XMI export format
- All 8 critical structural differences addressed

**Benefits**:
- ✅ Direct import into IBM Rhapsody 8.0+ without conversion
- ✅ Full Rhapsody XMI 2.1 compatibility (not just UML 2.5)
- ✅ Proper MessageOccurrenceSpecification for timing/sequencing info
- ✅ Role definitions matching Rhapsody's internal structure
- ✅ Complex profile structure with EPackage references

**Demo Files**:
- Enhanced demo code showcasing loops, multi-line conditions, nested conditionals
- Reorganized structure: `demo/src/` for source code
- Updated documentation in `demo/README.md`

**Breaking Changes**:
- Rhapsody XMI output structure completely changed (old format not compatible)
- Source directory changed from `demo/` to `demo/src/`
- All existing Rhapsody XMI files need regeneration

---

### Version 0.6.0 (2026-02-10)

**🎉 Major Feature: Loop Detection and Multi-line If Condition Support**

This release adds parsing of function calls inside `for`/`while` loops and improves multi-line if condition extraction for complex AUTOSAR code.

**New Features**:
- 🔄 **Loop Detection**: Automatically detects function calls inside `for` and `while` loops with condition extraction
- 📝 **Multi-line If Condition Extraction**: Handles complex multi-line if statements with nested parentheses and logical operators
- ✅ **Production Ready**: Verified on real AUTOSAR codebases with complex formatting

**Example Multi-line If**:
```c
// Complex multi-line condition with nested parentheses
if ((((uint32)config_ptr->settings->mode &
         ((uint32)0x1U << SLEEP_MODE)) > 0x0U) &&
    (sensor_status == SENSOR_READY))
{
    InitPeripheral();
    EnableClockControl();
}
```
**Parsed Condition**: `(((uint32)config_ptr->settings->mode & ((uint32)0x1U << SLEEP_MODE)) > 0x0U) && (sensor_status == SENSOR_READY)`

**Example Loop Detection**:
```c
while (retry_counter > 0x0U)
{
    if (InitOscillator() != E_OK)
    {
        ReportError(ERR_INIT_FAILED);
    }
    retry_counter--;
}
```
**Detected**: Loop condition `retry_counter > 0x0U` with nested conditional call `ReportError`

**Benefits**:
- ✅ Handles production AUTOSAR code with complex formatting
- ✅ Accurate condition extraction across line breaks
- ✅ Better visualization of loop-based call patterns
- ✅ Verified on real-world embedded codebases with zero parse errors

---

### Version 0.5.0 (2026-02-04)

**🎉 Major Feature: Automatic Conditional Call Detection with Opt/Alt/Else Blocks**

This release adds intelligent parsing of conditional function calls, automatically detecting `if`/`else` blocks in your C code and representing them as `opt`/`alt`/`else` blocks in both Mermaid and XMI output formats.

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
- ✅ No manual configuration required - automatic detection
- ✅ Shows actual condition text for better understanding
- ✅ Supports nested conditionals
- ✅ Handles `if`, `else if`, and `else` statements
- ✅ Works with both Mermaid and Rhapsody XMI output formats
- ✅ Rhapsody XMI uses UML combined fragments (standard UML 2.5 representation)

**Technical Changes**:
- `FunctionCall` model extended with `is_conditional` and `condition` fields
- `CallTreeNode` extended with `is_optional` and `condition` fields
- `CParser` enhanced with line-by-line conditional context tracking
- `MermaidGenerator` supports `opt`, `alt`, and `else` blocks
- `RhapsodyXmiGenerator` supports UML combined fragments
- 298 tests passing with 89% code coverage

## Changelog

### [Version 0.8.3] - 2026-03-05

#### Added
- **Comprehensive C comment removal**: Robust comment parsing with string literal protection
- **String literal protection**: Comments inside string literals are correctly preserved
- **Multi-line string support**: Handles complex multi-line string literals with embedded comment-like patterns
- **Production verification**: Tested on real AUTOSAR codebases with complex string formatting

#### Improved
- False positive prevention for comment detection inside strings
- Both single-line (`//`) and multi-line (`/* */`) comment handling
- String literal content preservation

#### Technical
- Verified parsing of production AUTOSAR codebase with zero comment-related parse errors
- All existing tests passing

---

### [Version 0.8.0] - 2026-03-01

#### Added
- **Rhapsody XMI 2.1 full compatibility**: Complete structural match with Rhapsody's native XMI export format
- **GUID+ ID format**: Uses `GUID+<UUID>` format for all XMI elements
- **MessageOccurrenceSpecification**: Explicit send/receive occurrence fragments for each message
- **Lifeline role definitions**: Proper ownedAttribute elements for lifeline roles
- **Element imports**: Profile metaclass imports for complete model structure
- **CoveredBy attributes**: Lifeline coverage tracking linking lifelines to message occurrences
- **Complex profile structure**: Nested eAnnotations with EPackage references
- **lxml-based generator**: Uses lxml for proper namespace control and XMI 2.1 compliance
- **Independent RhapsodyXmiGenerator**: Complete rewrite (does not extend XmiGenerator) for full structural control
- **Enhanced demo files**: Showcases loops, multi-line conditions, nested conditionals
- **Reorganized demo structure**: Source code moved to `demo/src/`
- **Comprehensive demo documentation**: Usage guide in `demo/README.md`

#### Breaking Changes
- **Rhapsody XMI output format**: Complete structural change from XMI 4.0 to XMI 2.1
- **Old Rhapsody files incompatible**: All existing Rhapsody XMI files must be regenerated
- **Source directory changed**: Default source directory changed from `./demo` to `./demo/src`
- **Namespace format**: Changed from Eclipse UML2 to OMG UML namespace
- **ID format**: Changed from `rhapsody_<UUID>` to `GUID+<UUID>`

#### Improved
- Direct import into IBM Rhapsody 8.0+ without conversion
- Proper MessageOccurrenceSpecification for timing/sequencing information
- Role definitions matching Rhapsody's internal structure
- Full structural compatibility with Rhapsody's native export format

#### Technical
- All 8 critical structural differences between XMI 4.0 and Rhapsody XMI 2.1 addressed
- lxml used for proper namespace control and XMI generation
- RhapsodyXmiGenerator implemented independently for full structural control
- Demo files enhanced to showcase all parsing features

---

### [Version 0.7.0] - 2026-02-14

#### Added
- **IBM Rhapsody XMI export**: Complete support for IBM Rhapsody 8.0+ XMI format with AUTOSAR profile
- **RhapsodyGenerator**: New generator class (221 lines) with IBM-specific XMI schema
- **Rhapsody documentation**: Comprehensive guides (1,075 lines total)
  - `docs/rhapsody_export.md`: Complete export guide
  - `docs/rhapsody_troubleshooting.md`: Troubleshooting guide
  - `docs/requirements/requirements_rhapsody.md`: Requirements documentation
- **Rhapsody import helper**: Script to assist with XMI imports
- **Rhapsody demo files**: 3 example XMI files (init, modules, update)
- **Rhapsody CLI option**: `--format rhapsody` for Rhapsody XMI output

#### Fixed
- **Invalid PyPI license classifier**: Corrected license classifier in pyproject.toml for proper PyPI publishing
- **Temporary file cleanup**: Automatic cleanup of test output files
- **Type safety**: Code simplification and type safety improvements
- **Code quality issues**: Formatting, imports, and linting corrections

#### Improved
- **Test structure**: Reorganized unit tests to match source code package layout
- **Documentation**: Removed deprecated setup.py references, updated build docs
- **Code quality**: Resolved all ruff linting errors
- **Test hygiene**: Added automatic cleanup for temporary test files

#### Technical
- 17 new requirements (SWR_RHAPSODY_00001 through SWR_RHAPSODY_00017)
- 759 lines of comprehensive Rhapsody-specific tests
- All 397 tests passing (100%)
- Overall test coverage: 89%
- Rhapsody-specific AUTOSAR profile support
- Cross-platform compatibility with Rhapsody 8.0+

#### CLI Usage
```bash
# Generate Rhapsody XMI
calltree --start-function Demo_Init --format rhapsody
```

---

### [Version 0.6.0] - 2026-02-10

#### Added
- **Loop detection**: Automatic detection of `for` and `while` loops with condition text extraction
- **Multi-line if condition extraction**: Handles complex multi-line if statements with nested parentheses
- **FunctionCall model**: Extended with `is_loop` and `loop_condition` fields
- **CallTreeNode model**: Extended with `is_loop` and `loop_condition` fields
- **CParser enhancements**: Multi-line parenthesis tracking for complete condition extraction
- Production AUTOSAR codebase verification (tested on large-scale embedded codebases)
- Requirements documentation for loop detection (SWR_PARSER_C_00021)

#### Improved
- Multi-line if condition extraction now captures complete conditions across line breaks
- Parenthesis depth tracking for complex nested conditions (4+ levels)
- Condition extraction for bitwise operations (`&`, `|`, `<<`, `>>`)
- Production code validation with zero parse errors

#### Technical
- Verified parsing of real-world AUTOSAR codebase with complex formatting
- Functions with loop calls correctly identified and tracked
- Multi-line conditions with 100+ character length properly extracted
- All existing tests passing (298 tests, 89% coverage)

---

### [Version 0.5.0] - 2026-02-04

#### Added
- **Conditional function call tracking**: Automatic detection of `if`/`else` blocks with condition text extraction
- **Mermaid opt/alt/else blocks**: Generate `opt`, `alt`, and `else` blocks for conditional calls
- **XMI combined fragments**: UML 2.5 compliant `opt`/`alt`/`else` fragment generation
- **FunctionCall model**: Extended with `is_conditional` and `condition` fields
- **CallTreeNode model**: Extended with `is_optional` and `condition` fields
- **CParser enhancements**: Line-by-line parsing to track conditional context
- Requirements documentation for conditional call tracking (SWR_MODEL_00026-00028)

#### Fixed
- Linting errors (flake8 W292, W391) for proper file endings
- Type annotations in `c_parser.py:442` for mypy compliance

#### Technical
- 298 tests passing, 89% code coverage
- All CI quality checks passing (ruff, isort, flake8, mypy)
- Python 3.8-3.12 test matrix

---

### [Version 0.4.0] - 2026-02-03

#### Added
- **XMI/UML 2.5 output format**: Complete XMI generation with UML 2.5 compliance (now superseded by Rhapsody XMI 2.1 in v0.8.0)
- **XMIGenerator**: New generator class for XMI document creation (deprecated, use RhapsodyXmiGenerator)
- **UML combined fragments**: Support for `opt`, `alt`, `else` interactions
- **Rhapsody XMI demo output**: `demo/rhapsody_demo_main.xmi` example file

#### Technical
- XMI documents importable into Enterprise Architect, Visual Paradigm, MagicDraw
- Proper XML namespaces and structure (UML 2.5, XMI 2.5)
- Message events with sendEvent and receiveEvent elements

---

### [Version 0.3.3] - 2026-02-02

#### Fixed
- **AUTOSAR macro false positives**: Performance degradation caused by incorrect macro matching
- Parser optimization to reduce false positive detections
- Improved AUTOSAR pattern matching accuracy

---

### [Version 0.3.2] - 2026-02-01

#### Added
- **File size display**: Show file sizes during processing in verbose mode
- Enhanced progress reporting with line counts and file sizes
- Improved user feedback for large file processing

---

### [Version 0.3.1] - 2026-01-31

#### Added
- **Verbose file progress**: File-by-file progress display during database building
- **Line count reporting**: Show number of lines processed per file
- **Enhanced cache loading**: File-by-file progress when loading from cache
- **C parser line-by-line tests**: Comprehensive testing for line-by-line processing

#### Fixed
- Import sorting to pass isort checks
- Minor documentation updates

---

### [Version 0.3.0] - 2026-01-30

#### Added
- **SW Module Configuration System**: YAML-based file-to-module mapping
- **Module-aware diagrams**: Generate diagrams with SW module names as participants
- **Comprehensive test suite**: 298 tests across all modules (89% coverage)
- **Requirements traceability**: Complete traceability matrix between requirements and tests
- **Integration tests**: End-to-end CLI testing
- **PyPI publishing workflow**: Automated PyPI releases with OIDC trusted publishing
- **ModuleConfig class**: Load, validate, and perform module lookups
- **Module assignment**: Functions tagged with SW module information
- **FunctionDatabase integration**: Module assignments preserved in cache
- **CLI `--use-module-names` option**: Enable module-level diagrams
- **CLI `--module-config` option**: Specify module mapping YAML file

#### Technical
- Glob pattern support for file mappings (e.g., `hw_*.c`)
- Default module fallback for unmapped files
- Module lookup caching for performance
- Cache preserves module assignments across runs

---

### Earlier Versions

**Version 0.2.x** - Initial development releases with basic AUTOSAR parsing and Mermaid output

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

## Building Distribution Packages

This project uses `pyproject.toml` for modern Python packaging (PEP 621). To build distribution packages:

```bash
# Install build dependencies
pip install build

# Build source distribution (sdist) and wheel
python -m build

# The built packages will be in the dist/ directory:
# - autosar_calltree-<version>.tar.gz  (source distribution)
# - autosar_calltree-<version>-py3-none-any.whl  (wheel)
```

To install from the built packages:

```bash
pip install dist/autosar_calltree-<version>-py3-none-any.whl
```

**Note**: This project no longer uses `setup.py`. All configuration is managed through `pyproject.toml`.

## Quick Start

### Basic Usage

```bash
# Analyze a function with default settings (depth=3)
calltree --start-function Demo_Init --source-dir demo/src

# Use SW module configuration for architecture-level diagrams
calltree --start-function Demo_Init \
         --source-dir demo/src \
         --module-config demo/module_mapping.yaml \
         --use-module-names \
         --output demo/demo.md

# Specify depth and output
calltree --start-function Demo_Init \
         --max-depth 2 \
         --output demo/output.md

# Generate Rhapsody XMI 2.1
calltree --start-function Demo_MainFunction \
         --source-dir demo/src \
         --format rhapsody \
         --output demo/demo.xmi

# Generate Rhapsody-compatible XMI 2.1
calltree --start-function Demo_Init \
         --source-dir demo/src \
         --format rhapsody \
         --output demo/rhapsody_demo.xmi

# Generate Rhapsody XMI with nested package structure
calltree --start-function Demo_Init \
         --source-dir demo/src \
         --format rhapsody \
         --output demo/rhapsody_nested.xmi \
         --rhapsody-package-path "MyPackage/SubPackage/DeepPackage"

# Generate Rhapsody XMI with custom model name
calltree --start-function Demo_Init \
         --source-dir demo/src \
         --format rhapsody \
         --output demo/rhapsody_custom_model.xmi \
         --rhapsody-model-name "MyProjectModel"

# Generate Rhapsody XMI with both custom model name and nested packages
calltree --start-function Demo_Init \
         --source-dir demo/src \
         --format rhapsody \
         --output demo/rhapsody_full.xmi \
         --rhapsody-model-name "MyProjectModel" \
         --rhapsody-package-path "MyPackage/SubPackage/DeepPackage"

# Enable loop detection
calltree --start-function Demo_MainFunction \
         --source-dir demo/src \
         --enable-loops \
         --output demo/demo_loops.md

# Enable conditional detection
calltree --start-function Demo_MainFunction \
         --source-dir demo/src \
         --enable-conditionals \
         --output demo/demo_conditionals.md

# Enable both loops and conditionals
calltree --start-function Demo_MainFunction \
         --source-dir demo/src \
         --enable-loops \
         --enable-conditionals \
         --output demo/demo_full.md

# Verbose mode with detailed statistics and cache progress
calltree --start-function Demo_Init \
         --source-dir demo/src \
         --verbose
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
db = FunctionDatabase(source_dir="demo/src", module_config=config)
db.build_database(use_cache=True)

# Build call tree with loop and conditional detection
builder = CallTreeBuilder(db)
result = builder.build_tree(
    start_function="Demo_Init",
    max_depth=3,
    enable_loops=True,      # Enable loop detection
    enable_conditionals=True  # Enable conditional detection
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
  --format [mermaid|rhapsody]   Output format (default: mermaid)
  --output PATH                 Output file path (default: call_tree.md)
  --module-config PATH          YAML file mapping C files to SW modules
  --use-module-names/--no-use-module-names
                               Use SW module names as Mermaid participants (default: True)
  --enable-loops                Enable loop detection and representation (default: False)
  --enable-conditionals         Enable if-else conditional detection and representation (default: False)
  --rhapsody-package-path TEXT  Package path for Rhapsody XMI output
                               (e.g., 'Package1/Package2/Package3').
                               Creates nested packages in the XMI structure.
  --rhapsody-model-name TEXT    Custom name for the UML model in Rhapsody XMI output
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

### Rhapsody Package Path

When generating Rhapsody XMI output, you can specify a nested package structure using the `--rhapsody-package-path` option. This allows you to organize your sequence diagrams within a hierarchical package structure that matches your project's organization.

**Usage**:
```bash
# Create nested packages: MyPackage → SubPackage → DeepPackage → Sequence_Diagram
calltree --start-function Demo_Init \
         --source-dir demo/src \
         --format rhapsody \
         --output demo/rhapsody_nested.xmi \
         --rhapsody-package-path "MyPackage/SubPackage/DeepPackage"
```

**Generated XMI Structure**:
```xml
<uml:Model name="CallTree_Demo_Init">
  <packagedElement xmi:type="uml:Package" name="MyPackage">
    <packagedElement xmi:type="uml:Package" name="SubPackage">
      <packagedElement xmi:type="uml:Package" name="DeepPackage">
        <packagedElement xmi:type="uml:Package" name="Sequence_Diagram">
          <packagedElement xmi:type="uml:Interaction" name="seq_Demo_Init">
            <!-- Interaction content -->
          </packagedElement>
        </packagedElement>
      </packagedElement>
    </packagedElement>
  </packagedElement>
</uml:Model>
```

**Package Path Constraints**:
- **Maximum depth**: 30 levels
- **Maximum name length**: 50 characters per package name
- **Valid characters**: Alphanumeric, underscore, and space only
- **Whitespace handling**: Leading/trailing whitespace is automatically stripped
- **Empty segments**: Trailing slashes are handled gracefully

**Examples**:
```bash
# Valid: 3 levels
--rhapsody-package-path "MyPackage/SubPackage/DeepPackage"

# Valid: At maximum depth (30 levels)
--rhapsody-package-path "P1/P2/P3/.../P30"

# Invalid: Exceeds maximum depth (31 levels)
--rhapsody-package-path "P1/P2/.../P31"
# Error: Package path depth exceeds maximum of 30 levels. Got 31 levels.

# Invalid: Contains hyphen
--rhapsody-package-path "My-Package"
# Error: Package name 'My-Package' contains invalid characters: -.

# Invalid: Name too long (51 characters)
--rhapsody-package-path "A" * 51
# Error: Package name 'AAA...' exceeds maximum length of 50 characters.
```

**Benefits**:
- Organize diagrams within project-specific package hierarchies
- Match your Rhapsody project structure
- Better integration with existing Rhapsody models
- Clear separation between different analysis results

**Note**: If not specified, the default behavior creates a flat package structure with a single `Sequence_Diagram` package directly under the Model.

### Rhapsody Model Name

You can also customize the UML model name in the Rhapsody XMI output using the `--rhapsody-model-name` option. By default, the model name is set to `CallTree_{root_function}`, but you can specify any custom name to match your project's naming conventions.

**Usage**:
```bash
# Generate Rhapsody XMI with custom model name
calltree --start-function Demo_Init \
         --source-dir demo/src \
         --format rhapsody \
         --output demo/rhapsody_custom.xmi \
         --rhapsody-model-name "MyProjectModel"
```

**Generated XMI Structure**:
```xml
<uml:Model name="MyProjectModel">
  <packagedElement xmi:type="uml:Package" name="Sequence_Diagram">
    <!-- Interaction content -->
  </packagedElement>
</uml:Model>
```

**Default Behavior**:
```bash
# Without --rhapsody-model-name, uses default naming
calltree --start-function Demo_Init --format rhapsody --output demo/rhapsody.xmi
```

**Generated XMI with Default Name**:
```xml
<uml:Model name="CallTree_Demo_Init">
  <packagedElement xmi:type="uml:Package" name="Sequence_Diagram">
    <!-- Interaction content -->
  </packagedElement>
</uml:Model>
```

**Combined with Package Path**:
```bash
# Use both custom model name and nested package path
calltree --start-function Demo_Init \
         --source-dir demo/src \
         --format rhapsody \
         --output demo/rhapsody_full.xmi \
         --rhapsody-model-name "MyProjectModel" \
         --rhapsody-package-path "MyPackage/SubPackage/DeepPackage"
```

**Benefits**:
- Match your Rhapsody project's model naming conventions
- Better integration with existing Rhapsody models
- Clear identification of different analysis results
- Consistent naming across multiple XMI exports

**Note**: The model name is independent of the package path. You can use a custom model name with or without nested packages.

### Generated Markdown Structure

The tool generates comprehensive Markdown files with:
- Metadata header (timestamp, settings, statistics)
- Mermaid sequence diagram with function parameters and opt/loop blocks
- Function details table with parameter information
- Text-based call tree
- Circular dependency warnings
- Analysis statistics

**Note**: Return statements are omitted from sequence diagrams by default for cleaner visualization. This can be configured programmatically when using the Python API.

### Loop and Conditional Detection

The tool automatically detects `for`, `while`, and `if`/`else` statements in your C code and represents them as `loop` and `opt` blocks in Mermaid diagrams and combined fragments in XMI.

**Note**: Loop and conditional detection are disabled by default to keep diagrams clean. Use `--enable-loops` and `--enable-conditionals` flags to enable them.

#### Mermaid Loop Example

**Source Code**:
```c
for (sensor_count = 0; sensor_count < 10; sensor_count++) {
    HW_ReadSensor(sensor_count);
    SW_ProcessData((uint8*)0x20001000, 0x64);
}
```

**Generated Mermaid Diagram** (with `--enable-loops`):
```mermaid
sequenceDiagram
    participant Demo_MainFunction
    participant HW_ReadSensor
    participant SW_ProcessData

    loop sensor_count < 10
    Demo_MainFunction->>HW_ReadSensor: call(sensor_id)
    Demo_MainFunction->>SW_ProcessData: call(data, length)
    end
```

#### Mermaid Conditional Example

**Source Code**:
```c
if (update_mode == 0x05) {
    COM_SendLINMessage(0x456, (uint8*)0x20003000);
}
```

**Generated Mermaid Diagram** (with `--enable-conditionals`):
```mermaid
sequenceDiagram
    participant Demo_Update
    participant COM_SendLINMessage

    opt update_mode == 0x05
    Demo_Update->>COM_SendLINMessage: call(msg_id, data)
    end
```

#### XMI Combined Fragments

Both loops and conditionals are represented as UML combined fragments in XMI output:

```xml
<!-- Loop fragment -->
<uml:fragment name="loop" interactionOperator="loop">
  <uml:operand name="sensor_count < 10">
    <uml:message name="HW_ReadSensor" />
    <uml:message name="SW_ProcessData" />
  </uml:operand>
</uml:fragment>

<!-- Conditional fragment -->
<uml:fragment name="opt" interactionOperator="opt">
  <uml:operand name="update_mode == 0x05">
    <uml:message name="COM_SendLINMessage" />
  </uml:operand>
</uml:fragment>
```

**Features**:
- ✅ Automatic detection of `for`, `while`, and `if`/`else` statements
- ✅ Actual condition text extracted from source code
- ✅ Nested conditionals and loops supported
- ✅ Works with both Mermaid and XMI output formats
- ✅ Disabled by default for cleaner diagrams

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
│   ├── generators/       # Output generators (Mermaid, XMI, Rhapsody)
│   └── utils/            # Utilities (empty, for future use)
├── demo/                 # Demo AUTOSAR C files and examples
│   ├── src/              # C source code
│   │   ├── communication.c
│   │   ├── demo.c
│   │   ├── demo.h
│   │   ├── hardware.c
│   │   └── software.c
│   ├── module_mapping.yaml  # Module configuration
│   ├── demo.md           # Example Mermaid output
│   ├── demo_main.md      # Example Mermaid output
│   ├── rhapsody_demo_main.xmi  # Example Rhapsody XMI 2.1 output
│   └── README.md         # Demo usage guide
├── tests/                # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test data
├── docs/                 # Documentation
│   ├── requirements/     # Software requirements
│   ├── rhapsody_export.md     # Rhapsody export guide
│   └── rhapsody_troubleshooting.md  # Rhapsody troubleshooting
└── scripts/              # Utility scripts
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
- [x] Rhapsody XMI 2.1 export with full structural compatibility (v0.8.0)
- [x] Automatic conditional call detection with opt/alt/else blocks
- [x] Loop detection (for/while) with condition extraction
- [x] C comment removal with string literal protection (v0.8.3)

## Support

- **Issues**: [GitHub Issues](https://github.com/melodypapa/autosar-calltree/issues)
- **Documentation**: [Read the Docs](https://autosar-calltree.readthedocs.io)
- **Discussions**: [GitHub Discussions](https://github.com/melodypapa/autosar-calltree/discussions)

---

**Made with ❤️ for the embedded systems community**