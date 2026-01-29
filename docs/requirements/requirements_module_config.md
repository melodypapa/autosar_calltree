# Module Configuration Requirements

## SWR_CONFIG_00001: YAML Configuration File Support

**Title**: Load SW module mappings from YAML configuration file

**Maturity**: accept

**Description**:
The tool shall support loading SW (Software) module mappings from a YAML configuration file. The configuration file shall map C source files to SW module names using both specific file mappings and glob pattern mappings.

**Rationale**:
AUTOSAR codebases are typically organized into SW modules (Hardware, Software, Communication, etc.). Mapping C files to SW modules allows the tool to generate call diagrams organized by module rather than by individual function, providing higher-level architectural visibility.

**Functional Requirements**:

1. **Configuration File Format**:
   - The configuration file shall be in YAML format
   - The file shall support a `file_mappings` section for exact filename matches
   - The file shall support a `pattern_mappings` section for glob pattern matches
   - The file shall optionally support a `default_module` for unmapped files

2. **Specific File Mappings**:
   - The tool shall support mapping specific filenames to module names
   - Example: `demo.c: DemoModule`
   - Specific file mappings shall take precedence over pattern mappings

3. **Pattern Mappings**:
   - The tool shall support glob patterns for file matching
   - Example: `hw_*.c: HardwareModule`
   - Patterns shall use standard glob syntax (fnmatch)
   - Patterns shall be case-sensitive

4. **Default Module**:
   - The tool shall support an optional default module name
   - If specified, unmapped files shall be assigned to the default module
   - If not specified, unmapped files shall have no module assignment

5. **Configuration Loading**:
   - The tool shall provide a `--module-config` CLI option
   - The option shall accept a path to the YAML configuration file
   - The tool shall validate the configuration file format
   - The tool shall report clear error messages for invalid configurations

6. **Module Assignment**:
   - The tool shall assign SW module names to all functions during database building
   - Module assignment shall be stored in the `sw_module` field of `FunctionInfo`
   - Module assignment shall be included in cache data

7. **Statistics**:
   - The tool shall track module statistics (number of functions per module)
   - Module statistics shall be displayed in verbose mode
   - Module statistics shall be included in database statistics

**Error Handling**:

- If the configuration file does not exist, the tool shall exit with error code 1
- If the configuration file is malformed YAML, the tool shall exit with error code 1
- If the configuration file has invalid format, the tool shall provide specific error messages
- If module names are empty strings, the tool shall report a validation error

**Implementation Notes**:

- Configuration loading is implemented in `src/autosar_calltree/config/module_config.py`
- The `ModuleConfig` class handles loading, validation, and lookup
- Glob patterns are compiled to regex for performance
- Lookup results are cached for efficiency

**Example Configuration**:

```yaml
version: "1.0"

file_mappings:
  demo.c: DemoModule

pattern_mappings:
  "hw_*.c": HardwareModule
  "sw_*.c": SoftwareModule

default_module: "Other"
```

**Usage Example**:

```bash
calltree --start-function Demo_Init \
         --module-config test_demo/module_mapping.yaml \
         --use-module-names \
         -o output.md
```

## SWR_CONFIG_00002: Module Configuration Validation

**Title**: Validate module configuration file format

**Maturity**: accept

**Description**:
The tool shall validate the module configuration file format and content before using it to map files to modules.

**Functional Requirements**:

1. **YAML Validation**:
   - The tool shall verify the configuration file is valid YAML
   - Malformed YAML files shall be rejected with clear error messages

2. **Structure Validation**:
   - The tool shall verify the root element is a dictionary
   - The tool shall verify `file_mappings` is a dictionary (if present)
   - The tool shall verify `pattern_mappings` is a dictionary (if present)
   - The tool shall verify `default_module` is a string (if present)

3. **Content Validation**:
   - The tool shall verify all filenames are non-empty strings
   - The tool shall verify all module names are non-empty strings
   - The tool shall verify all patterns are valid glob patterns

4. **Validation Error Reporting**:
   - All validation errors shall be reported to the user
   - Error messages shall clearly indicate the problem location
   - Multiple validation errors may be reported in a single run

**Error Handling**:

- Invalid configuration shall result in exit code 1
- Validation errors shall not cause the tool to crash

## SWR_CONFIG_00003: Module Configuration Integration

**Title**: Integrate module configuration with database building

**Maturity**: accept

**Description**:
The tool shall integrate module configuration loading with the database building process to assign SW modules to all parsed functions.

**Functional Requirements**:

1. **Module Assignment**:
   - Functions shall be assigned to modules during parsing
   - Module assignment shall use the configuration file mappings
   - Assignment shall occur before functions are added to the database

2. **Cache Integration**:
   - Module assignments shall be included in cached data
   - Cache files shall include module information for all functions
   - Loading from cache shall preserve module assignments

3. **Statistics Tracking**:
   - The tool shall count functions per module
   - Statistics shall be available via `get_statistics()`
   - Statistics shall be displayed in verbose mode

**Implementation Notes**:

- Module assignment is performed in `FunctionDatabase._add_function()`
- Module statistics are tracked in `FunctionDatabase.module_stats`
- Statistics are included in the return value of `get_statistics()`
