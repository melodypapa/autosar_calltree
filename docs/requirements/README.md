# Requirements Documentation

This directory contains all software requirements for the AUTOSAR Call Tree Analyzer project, organized by Python package structure.

---

## Overview

| Package                       | File                                                     | Requirements | Status               |
| ----------------------------- | -------------------------------------------------------- | ------------ | -------------------- |
| `autosar_calltree.database`   | [requirements_database.md](requirements_database.md)     | 35           | ✅ Complete           |
| `autosar_calltree.parsers`    | [requirements_parsers.md](requirements_parsers.md)       | 40           | ✅ Complete           |
| `autosar_calltree.analyzers`  | [requirements_analyzers.md](requirements_analyzers.md)   | 15           | ✅ Complete           |
| `autosar_calltree.config`     | [requirements_config.md](requirements_config.md)         | 8            | ✅ Complete           |
| `autosar_calltree.generators` | [requirements_generators.md](requirements_generators.md) | 35           | ✅ Complete           |
| `autosar_calltree.cli`        | [requirements_cli.md](requirements_cli.md)               | 25           | ✅ Complete           |
| `autosar_calltree.preprocessing` | [requirements_preprocessing.md](requirements_preprocessing.md) | 8    | ✅ Complete           |
| **Total**                     | **7 files**                                              | **166**      | **✅ 100% Traceable** |

---

## Quick Reference

### By Package

**Database** (`requirements_database.md`)
- Data models (FunctionType, Parameter, FunctionInfo, etc.)
- Function database (indexing, lookup, caching)
- pycparser integration
- Smart function selection

**Parsers** (`requirements_parsers.md`)
- AUTOSAR macro parser
- Regex-based C parser
- pycparser-based C parser
- Hybrid parsing strategy

**Analyzers** (`requirements_analyzers.md`)
- Call tree builder
- DFS traversal
- Cycle detection
- Statistics collection

**Config** (`requirements_config.md`)
- Module configuration (YAML)
- File and pattern mappings
- Module lookup

**Generators** (`requirements_generators.md`)
- Mermaid sequence diagrams
- XMI/UML 2.5 documents
- Opt/alt/loop blocks
- Function tables
- Rhapsody XMI 2.1 support

**CLI** (`requirements_cli.md`)
- Command-line interface (Click)
- Output options
- Caching control
- Rich console output
- Preprocessor options

**Preprocessing** (`requirements_preprocessing.md`)
- Two-stage preprocessing pipeline
- CPP path resolution (Windows, Linux, macOS)
- Metrics collection and error tracking
- Temporary file management

---

## Requirement ID Scheme

**Format**: `SWR_<PACKAGE>_<NUMBER>`

**Package Codes**:
- `DB`: Database (models + function_database)
- `PARSER`: Parsers (autosar + c + c_pycparser)
- `ANALYZER`: Analyzers (call_tree_builder)
- `CONFIG`: Config (module_config)
- `GEN`: Generators (mermaid + xmi)
- `MERMAID`: Mermaid-specific requirements
- `RH`: Rhapsody-specific requirements
- `CLI`: CLI (main)
- `PREPROCESS`: Preprocessing (cpp_preprocessor)
- `MODEL`: Data models
- `CACHE`: Caching subsystem

**Numbering**: Sequential from 00001

**Test IDs**: `SWUT_<PACKAGE>_<NUMBER>` for test traceability

---

## Document Structure

Each requirements document follows this structure:

1. **Overview** - Package purpose and structure
2. **Requirements** - Numbered requirements (SWR_XXXX_NNNNN)
3. **Summary** - Total count and implementation status

Each requirement includes:
- **Purpose**: What the requirement achieves
- **Implementation**: How it's implemented (file/class/method)
- **Details**: Specific behaviors, parameters, formats

---

## Change History

| Date       | Version | Changes                                                                        |
| ---------- | ------- | ------------------------------------------------------------------------------ |
| 2026-03-14 | 2.2     | Updated CLI requirements (25), Generators requirements (35), added test IDs    |
| 2026-03-14 | 2.1     | Added preprocessing package requirements (SWR_PREPROCESS_00001-00008)          |
| 2026-02-10 | 2.0     | **Major reorganization**: Consolidated from 16 files to 6 package-based files. |
| 2026-02-10 | 1.3     | Added COMBINED_REQUIREMENTS.md with package organization                       |
| 2026-02-10 | 1.2     | Added pycparser integration requirements                                       |
| 2026-02-04 | 1.1     | Added conditional call tracking requirements                                   |
| 2026-01-30 | 1.0     | Initial requirements index                                                     |