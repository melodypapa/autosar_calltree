# Software Requirements Specification

## Introduction

This document is the master index for all software requirements of the AUTOSAR Call Tree Analyzer project.

## Maturity Levels

Requirements are marked with maturity levels:
- **draft**: Newly created, under review, not yet implemented
- **accept**: Implemented in codebase
- **invalid**: Deprecated, superseded, or no longer applicable

## Requirements by Component

### Model Requirements

**Document**: [Model Requirements](models.md)

**ID Range**: SWR_MODEL_00001 - SWR_MODEL_00025

Core data models and structures used throughout the application.

**Key Areas**:
- FunctionType enum for function classification
- Parameter dataclass for function parameters
- FunctionInfo dataclass for function metadata
- CallTreeNode dataclass for call tree structure
- CircularDependency dataclass for cycle tracking
- AnalysisStatistics and AnalysisResult dataclasses

### FunctionCall Model Requirements

**Document**: [FunctionCall Requirements](function_call.md)

**ID Range**: SWR_MODEL_00026 - SWR_MODEL_00028

Function call tracking with conditional status.

**Key Areas**:
- FunctionCall dataclass with conditional flag
- Condition text extraction from if/else statements
- Optional call tracking in CallTreeNode

### Parser Requirements

**Document**: [Parser Requirements](parsers.md) (not yet created)

**ID Range**: SWR_PARSER_00001 - SWR_PARSER_00032

C and AUTOSAR code parsing functionality.

### Writer Requirements

**Document**: [Writer Requirements](writers.md) (not yet created)

**ID Range**: SWR_WRITER_00001 - SWR_WRITER_00008

Output generation and formatting.

### CLI Requirements

**Document**: [CLI Requirements](cli.md) (not yet created)

**ID Range**: SWR_CLI_00001 - SWR_CLI_00014

Command-line interface and user interaction.

### Configuration Requirements

**Document**: [Configuration Requirements](requirements_module_config.md)

**ID Range**: SWR_CONFIG_00001 - SWR_CONFIG_00003

YAML-based module configuration and file-to-module mapping.

**Key Areas**:
- YAML configuration file support
- Configuration validation
- Integration with database building

### Mermaid Generator Requirements

**Document**: [Mermaid Module Requirements](requirements_mermaid_modules.md)

**ID Range**: SWR_MERMAID_00001 - SWR_MERMAID_00003

Module-aware Mermaid diagram generation.

**Key Areas**:
- Module-based participants
- Function names on arrows
- Module column in function tables
- Fallback behavior for unmapped files

### Mermaid Opt Blocks Requirements

**Document**: [Mermaid Opt Blocks Requirements](requirements_mermaid_opt_blocks.md)

**ID Range**: SWR_MERMAID_00004

Automatic conditional call detection and opt block generation.

**Key Areas**:
- Automatic if/else detection
- Condition text extraction
- Opt block generation with actual conditions
- Nested conditional support

### XMI Generator Requirements

**Document**: [XMI Generator Requirements](requirements_xmi.md)

**ID Range**: SWR_XMI_00001 - SWR_XMI_00003

XMI 2.5 compliant UML sequence diagram generation.

**Key Areas**:
- XMI 2.5 compliance and namespaces
- Sequence diagram representation with lifelines and messages
- Opt block support using UML combined fragments
- Module-aware participant support

### Parameter Display Requirements

**Document**: [Parameter Display Requirements](requirements_parameters.md)

**ID Range**: SWR_PARAMS_00001 - SWR_PARAMS_00003

Function parameter extraction and display in sequence diagrams.

**Key Areas**:
- Parameter extraction from AUTOSAR and C function declarations
- Parameter display in sequence diagram arrows
- Optional return statements (omitted by default)
- Participant order preservation (first encounter order)

### Cache Requirements

**Document**: [Cache Progress Requirements](requirements_cache_progress.md)

**ID Range**: SWR_CACHE_00001 - SWR_CACHE_00004

Cache loading and progress reporting.

**Key Areas**:
- File-by-file cache loading progress
- Cache status indication
- Error handling and fallback
- Performance considerations

### Package Requirements

**Document**: [Package Requirements](package.md) (not yet created)

**ID Range**: SWR_PACKAGE_00001 - SWR_PACKAGE_00003

Python packaging and distribution.

## Quick Reference

| Component | Document | ID Range | Status |
|-----------|----------|----------|--------|
| Model | models.md | SWR_MODEL_00001-00025 | ✅ Complete |
| FunctionCall | function_call.md | SWR_MODEL_00026-00028 | ✅ Complete |
| Parser | parsers.md | SWR_PARSER_00001-00032 | Not Created |
| Writer | writers.md | SWR_WRITER_00001-00008 | Not Created |
| CLI | cli.md | SWR_CLI_00001-00014 | Not Created |
| Configuration | requirements_module_config.md | SWR_CONFIG_00001-00003 | ✅ Complete |
| Mermaid | requirements_mermaid_modules.md | SWR_MERMAID_00001-00003 | ✅ Complete |
| Opt Blocks | requirements_mermaid_opt_blocks.md | SWR_MERMAID_00004 | ✅ Complete |
| XMI | requirements_xmi.md | SWR_XMI_00001-00003 | ✅ Complete |
| Parameter Display | requirements_parameters.md | SWR_PARAMS_00001-00003 | ✅ Complete |
| Cache | requirements_cache_progress.md | SWR_CACHE_00001-00004 | ✅ Complete |
| Package | package.md | SWR_PACKAGE_00001-00003 | Not Created |

## Version History

- **2026-02-04**: Added FunctionCall model requirements, Mermaid opt blocks requirements, and XMI generator requirements
- **2026-01-29**: Added Configuration, Mermaid, Cache, and Parameter Display requirements
- Initial version created

## Document Structure

Each component requirements document follows this structure:

1. **Requirement ID**: Unique identifier (e.g., SWR_CONFIG_00001)
2. **Title**: Brief descriptive title
3. **Maturity**: draft/accept/invalid
4. **Description**: Detailed functional requirement
5. **Rationale**: Justification for the requirement (when applicable)
6. **Functional Requirements**: Detailed breakdown
7. **Error Handling**: Error conditions and handling
8. **Implementation Notes**: Technical implementation details
9. **Examples**: Usage examples (when applicable)
10. **Traceability**: Mapping to test cases