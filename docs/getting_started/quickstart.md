# Quick Start

This guide will help you get started with AUTOSAR Call Tree Analyzer in just a few minutes.

## Basic Usage

### 1. List All Functions

First, let's see what functions are in your codebase:

```bash
calltree -l -i /path/to/your/source
```

This will scan all C files in the directory and list all functions found.

**Example output:**

```
Database Statistics:
┌──────────────────┬─────┐
│ Files Scanned    │ 15  │
│ Functions Found  │ 127 │
│ Unique Names     │ 124 │
│ Static Functions │ 3   │
│ Parse Errors     │ 0   │
└──────────────────┴─────┘

Available Functions:

   1. CanIf_Init
   2. CanIf_Transmit
   3. CanIf_MainFunction
   ...
```

### 2. Generate a Call Tree

Now let's generate a call tree for a specific function:

```bash
calltree -s CanIf_Transmit -i /path/to/your/source -o call_tree.md
```

This creates a Mermaid sequence diagram showing the function call tree.

**Example output (call_tree.md):**

```markdown
# Call Tree: CanIf_Transmit

## Sequence Diagram

\`\`\`mermaid
sequenceDiagram
    participant CanIf_Transmit
    participant CanIf_TransmitInternal

    CanIf_Transmit->>CanIf_TransmitInternal: call(TxPduId, PduInfoPtr)
\`\`\`

## Function Details

| Function | File | Line | Return Type | Parameters |
|----------|------|------|-------------|------------|
| `CanIf_Transmit` | CanIf.c | 356 | `Std_ReturnType` | `PduIdType TxPduId`<br>`const PduInfoType *PduInfoPtr` |
```

### 3. Control Depth

By default, the call tree goes 3 levels deep. You can control this:

```bash
# Only 1 level deep
calltree -s main -i /path/to/source -d 1 -o call_tree.md

# Go 5 levels deep
calltree -s main -i /path/to/source -d 5 -o call_tree.md
```

### 4. Search for Functions

Search for functions matching a pattern:

```bash
calltree --search Can -i /path/to/source
```

**Example output:**

```
Search Results for 'Can':

  CanIf_Init (CanIf.c:246)
  CanIf_Transmit (CanIf.c:356)
  CanNm_MainFunction (CanNm.c:1139)
  Can_Write (Can.c:102)

Found 4 matches
```

## Advanced Features

### Enable Loop Detection

Detect and visualize loops in the call tree:

```bash
calltree -s main -i /path/to/source --enable-loops -o call_tree.md
```

### Enable Conditional Branches

Show if-else branches in the diagram:

```bash
calltree -s main -i /path/to/source --enable-conditionals -o call_tree.md
```

### Use Module Names

If you have a module configuration file:

```bash
calltree -s main -i /path/to/source --module-config module_mapping.yaml -o call_tree.md
```

### Generate Rhapsody XMI

For IBM Rhapsody integration:

```bash
calltree -s main -i /path/to/source -f rhapsody -o output.xmi
```

## Working with AUTOSAR Projects

AUTOSAR Call Tree Analyzer is designed to work with AUTOSAR codebases:

### Auto-detection of Include Directories

The tool automatically detects include directories in common AUTOSAR project structures:

- `<source_dir>/include`
- `<source_dir>/../include`
- `<source_dir>/../../include`
- `<source_dir>/../../infras/include` (AUTOSAR pattern)

### AUTOSAR Macro Support

The clang parser handles AUTOSAR-specific macros:

- `FUNC()` declarations
- `P2VAR()`, `P2CONST()` type definitions
- `RTE_CALL()` invocations
- Standard AUTOSAR types

### Example: Analyzing AUTOSAR Communication Stack

```bash
# Analyze the entire communication stack
calltree -l -i /path/to/autosar/infras/communication

# Generate call tree for CanIf module
calltree -s CanIf_MainFunction -i /path/to/autosar/infras/communication/CanIf -d 3
```

## Using Cache

For large codebases, use caching to speed up analysis:

```bash
# First run builds the cache
calltree -l -i /path/to/large/codebase

# Subsequent runs use the cache
calltree -s main -i /path/to/large/codebase  # Fast!

# Force rebuild cache
calltree -l -i /path/to/large/codebase --rebuild-cache

# Disable cache
calltree -l -i /path/to/large/codebase --no-cache
```

## Common Patterns

### Analyze a Single File

```bash
calltree -l -i /path/to/single/file.c
```

### Analyze Multiple Directories

```bash
# Just specify the parent directory
calltree -l -i /path/to/project/src
```

### Find Entry Points

```bash
# List all functions and grep for main or init functions
calltree -l -i /path/to/source | grep -E "(main|init)"
```

## Next Steps

- {doc}`/getting_started/configuration` - Learn about configuration options
- {doc}`/user_guide/basic_usage` - Detailed usage examples
- {doc}`/tutorials/analyzing_autosar` - AUTOSAR-specific tutorials
