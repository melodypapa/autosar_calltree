# Config Package Requirements

**Package**: `autosar_calltree.config`
**Source Files**: `module_config.py`
**Requirements**: SWR_CONFIG_00001 - SWR_CONFIG_00008 (8 requirements)

---

## Overview

The config package provides module configuration functionality for mapping C source files to SW modules, enabling architecture-level diagrams that show module interactions instead of individual function calls.

**Core Class**: `ModuleConfig`

---

## YAML Configuration (SWR_CONFIG_00001 - SWR_CONFIG_00004)

### SWR_CONFIG_00001 - YAML Configuration File Support
**Purpose**: Load module mappings from YAML file

**File Format**:
```yaml
version: "1.0"

file_mappings:
  demo.c: DemoModule

pattern_mappings:
  "hw_*.c": HardwareModule
  "communication.c": CommunicationModule

default_module: "Other"
```

**Implementation**: `ModuleConfig.__init__(config_path)`

---

### SWR_CONFIG_00002 - File Mappings
**Purpose**: Exact filename to module mappings

**Format**: `filename.c: ModuleName`

**Example**: `demo.c: DemoModule`

**Priority**: Highest (checked before patterns)

---

### SWR_CONFIG_00003 - Pattern Mappings
**Purpose**: Glob pattern to module mappings

**Format**: `"pattern*.c": ModuleName`

**Examples**:
- `"hw_*.c": HardwareModule`
- `"sw_*.c": SoftwareModule`
- `"*_.c": TestModule`

**Implementation**: `fnmatch` module for pattern matching

---

### SWR_CONFIG_00004 - Default Module
**Purpose**: Default module for unmapped files

**Field**: `default_module`

**Default Value**: `"Other"` or user-specified

**Priority**: Lowest (used if no match found)

---

## Configuration Loading (SWR_CONFIG_00005 - SWR_CONFIG_00006)

### SWR_CONFIG_00005 - Configuration Loading and Validation
**Purpose**: Load and validate YAML configuration

**Validation**:
- YAML syntax valid
- Required fields present
- File mappings valid
- Pattern mappings valid

**Error Handling**: Raise exception on invalid config

**Implementation**: `ModuleConfig.__init__()`

---

### SWR_CONFIG_00006 - Configuration Version
**Purpose**: Track configuration version

**Field**: `version` in YAML

**Use**: Future compatibility checks

**Current Version**: "1.0"

---

## Module Lookup (SWR_CONFIG_00007 - SWR_CONFIG_00008)

### SWR_CONFIG_00007 - Module Lookup
**Purpose**: Get module name for a source file

**Method**: `get_module_for_file(file_path)`

**Priority Order**:
1. Exact file mapping
2. Pattern mapping (first match wins)
3. Default module

**Returns**: Module name (str) or None

---

### SWR_CONFIG_00008 - Lookup Caching
**Purpose**: Cache lookup results for performance

**Implementation**: Dictionary cache

**Behavior**:
- Cache lookups by file path
- Return cached result if available
- No cache invalidation (config doesn't change)

---

## Summary

**Total Requirements**: 8
**Implementation Status**: ✅ All Implemented

**Package Structure**:
```
autosar_calltree.config/
└── module_config.py    # SWR_CONFIG_00001 - SWR_CONFIG_00008
```

**Key Features**:
- YAML-based configuration
- Exact filename and pattern mappings
- Default module fallback
- Result caching for performance
