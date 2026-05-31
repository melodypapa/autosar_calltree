# Configuration

AUTOSAR Call Tree Analyzer can be configured through command-line options and configuration files.

## Command-Line Options

### Basic Options

```bash
calltree [OPTIONS]
```

#### Source and Output

- `-i, --source-dir DIRECTORY` - Source directory containing C files (default: ./demo)
- `-o, --output PATH` - Output file path (default: call_tree.md)
- `-f, --format [mermaid|rhapsody]` - Output format (default: mermaid)

#### Function Selection

- `-s, --start-function TEXT` - Name of the function to start call tree from
- `-d, --max-depth INTEGER` - Maximum depth to traverse (default: 3)
- `-l, --list-functions` - List all available functions and exit
- `--search TEXT` - Search for functions matching pattern and exit

#### Cache Options

- `--cache-dir DIRECTORY` - Cache directory (default: <source-dir>/.cache)
- `--no-cache` - Disable cache usage
- `--rebuild-cache` - Force rebuild of cache

#### Output Options

- `-v, --verbose` - Enable verbose output
- `--no-abbreviate-rte` - Do not abbreviate RTE function names in diagrams

#### Module Configuration

- `--module-config PATH` - Path to YAML file mapping C files to SW modules
- `--use-module-names / --no-use-module-names` - Use SW module names as Mermaid participants (default: True)

#### Advanced Features

- `--enable-loops` - Enable loop detection and representation in diagrams
- `--enable-conditionals` - Enable if-else conditional detection in diagrams

#### Rhapsody-Specific

- `--rhapsody-package-path TEXT` - Package path for Rhapsody XMI output
- `--rhapsody-model-name TEXT` - Rhapsody model name in generated XMI

## Module Configuration File

Create a YAML file to map C files to software modules:

### Example: `module_mapping.yaml`

```yaml
# Module mapping configuration
default_module: "Application"

# Map file patterns to module names
file_mappings:
  "app.c": "Application"
  "com_stack.c": "Communication"
  "hardware.c": "Hardware Abstraction"
  "mcal_*.c": "MCAL"

# Map directories to module names
pattern_mappings:
  "communication/": "Communication"
  "drivers/": "Drivers"
  "mcal/": "MCAL"
```

### Using Module Configuration

```bash
calltree -s main -i /path/to/source --module-config module_mapping.yaml -o call_tree.md
```

## Include Directories

### Auto-Detection

The tool automatically detects include directories in these locations:

1. `<source_dir>/include`
2. `<source_dir>/../include`
3. `<source_dir>/../../include`
4. `<source_dir>/../../infras/include` (AUTOSAR pattern)

### Manual Include Paths

If your project has a different structure, you may need to set environment variables or ensure headers are accessible.

## Environment Variables

### LLVM_CONFIG_PATH

Path to llvm-config for libclang:

```bash
export LLVM_CONFIG_PATH=/usr/bin/llvm-config
```

### PYTHONPATH

Add custom Python modules:

```bash
export PYTHONPATH=/path/to/custom/modules:$PYTHONPATH
```

## Output Formats

### Mermaid (Default)

Generates Markdown files with embedded Mermaid sequence diagrams:

```bash
calltree -s main -i /path/to/source -o call_tree.md
```

### Rhapsody XMI

Generates IBM Rhapsody XMI files:

```bash
calltree -s main -i /path/to/source -f rhapsody -o output.xmi
```

## Cache Management

### Cache Location

By default, cache is stored in `<source_dir>/.cache/function_db.pkl`

### Cache Benefits

- Faster subsequent analysis
- Avoids re-parsing unchanged files
- Stores function database for quick lookups

### Cache Invalidation

The cache is automatically invalidated when:
- Source files are modified
- `--rebuild-cache` is used
- Parser version changes

### Disabling Cache

For one-time analysis or when cache is not needed:

```bash
calltree -s main -i /path/to/source --no-cache
```

## Performance Tuning

### Large Codebases

For large codebases (1000+ files):

1. **Use caching** - Always use cache for repeated analysis
2. **Limit depth** - Use `-d 2` or `-d 3` to limit traversal depth
3. **Specific functions** - Analyze specific functions rather than the entire codebase

### Example: Large Project

```bash
# Build cache first
calltree -l -i /path/to/large/project

# Analyze specific functions
calltree -s main_function -i /path/to/large/project -d 2
```

## Integration with Build Systems

### Makefile

```makefile
.PHONY: calltree

calltree:
	calltree -l -i src -o docs/call_tree.md
```

### CMake

```cmake
find_program(CALLTREE_EXE calltree)

if(CALLTREE_EXE)
    add_custom_target(calltree
        COMMAND ${CALLTREE_EXE} -l -i ${CMAKE_SOURCE_DIR}/src
        WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
        COMMENT "Generating call tree documentation"
    )
endif()
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Generate Call Tree
  run: |
    pip install autosar-calltree
    calltree -l -i src -o call_tree.md
    calltree -s main -i src -o docs/call_tree.md
```

## Troubleshooting

### Missing Headers

If you get "file not found" errors for headers:

1. Check include directory structure
2. Ensure headers are in one of the auto-detected locations
3. Verify header files exist and are readable

### Parse Errors

If you get parse errors:

1. Check C code syntax
2. Ensure all required headers are available
3. Use `-v` for verbose output to see details

### Slow Performance

If analysis is slow:

1. Enable caching (default)
2. Reduce traversal depth
3. Analyze specific subdirectories
4. Check for circular dependencies

## Next Steps

- {doc}`/user_guide/basic_usage` - Learn more usage patterns
- {doc}`/user_guide/output_formats` - Understand output format options
- {doc}`/tutorials/analyzing_autosar` - AUTOSAR-specific examples
