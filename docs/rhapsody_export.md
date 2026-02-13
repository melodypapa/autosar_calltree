# IBM Rhapsody Export Guide

## Overview

The AUTOSAR Call Tree Analyzer supports exporting call trees as Rhapsody-compatible XMI 2.5 files that can be imported into IBM Rhapsody 8.0+ for further editing and visualization.

## Requirements

- IBM Rhapsody 8.0 or later
- AUTOSAR Call Tree Analyzer v0.7.0+

## Generating Rhapsody XMI

### Basic Usage

```bash
# Generate Rhapsody-compatible XMI
calltree --start-function Demo_Init --format rhapsody --source-dir demo

# Output to specific file
calltree --start-function Demo_Init --format rhapsody --output diagrams/rhapsody_demo.xmi
```

### Module-Level Diagrams

For architecture-level diagrams showing SW module interactions:

```bash
calltree --start-function Demo_Init \
         --format rhapsody \
         --source-dir demo \
         --module-config demo/module_mapping.yaml \
         --use-module-names \
         --output demo/rhapsody_architecture.xmi
```

### Combining Formats

Generate both Mermaid and Rhapsody formats:

```bash
calltree --start-function Demo_MainFunction \
         --format both \
         --max-depth 4 \
         --output diagrams/demo
```

This creates:
- `diagrams/demo.mermaid.md` - Mermaid sequence diagram
- `diagrams/demo.xmi` - Rhapsody-compatible XMI

## Importing into Rhapsody

### Method 1: XMI Import (Recommended)

1. Open IBM Rhapsody
2. Select **File > Import > OMG XMI**
3. Browse to the generated `.xmi` file
4. Click **Open**
5. Rhapsody imports the sequence diagram

### Method 2: Drag and Drop

1. Open IBM Rhapsody
2. Drag the `.xmi` file from Explorer/Finder into the Rhapsody window
3. Rhapsody detects the XMI format and imports automatically

## What Gets Exported

### Sequence Diagram Elements

- **Lifelines**: Functions or SW modules (depending on `--use-module-names`)
- **Messages**: Function calls with signatures
- **Combined Fragments**:
  - `opt` blocks for conditional calls (`if` statements)
  - `loop` blocks for iterative calls (`for`/`while` loops)
  - `alt` blocks for `if/else` statements

### Rhapsody-Specific Features

- **UUID-based IDs**: All elements use UUID format for better Rhapsody compatibility
- **Rhapsody Profiles**: Includes Rhapsody-specific profile references
- **AUTOSAR Stereotypes**: Supports AUTOSAR-specific stereotypes (e.g., `<<SWC>>`)
- **Tool Metadata**: Includes generation metadata for traceability

## Limitations

### Manual Import Step

Rhapsody XMI files require manual import via **File > Import > OMG XMI**. This is a trade-off for cross-platform compatibility (the feature works on Windows, Linux, and macOS).

### Rhapsody License Required

To import and edit XMI files, you need a valid IBM Rhapsody license. The generated XMI files cannot be viewed without Rhapsody or another UML tool.

### Version Compatibility

- **Minimum**: Rhapsody 8.0 (UML 2.1 support)
- **Tested**: Rhapsody 10.0.1
- **XMI Format**: UML 2.5 XMI (backward compatible with UML 2.1)

## Troubleshooting

### Import Fails

**Problem**: Rhapsody shows error when importing XMI file.

**Solutions**:
1. Verify Rhapsody version is 8.0+
2. Check XMI file is not corrupted (open in text editor)
3. Try re-generating with `--rebuild-cache`
4. Ensure source directory path is correct

### Diagram Empty

**Problem**: Sequence diagram imports but shows no lifelines or messages.

**Solutions**:
1. Check that `--start-function` exists in codebase: `calltree --list-functions`
2. Verify `--max-depth` is sufficient (default: 3)
3. Check for parse errors in verbose mode: `calltree --verbose ...`

### Stereotypes Not Showing

**Problem**: AUTOSAR stereotypes (e.g., `<<SWC>>`) don't appear in Rhapsody.

**Solution**: This is expected behavior. Stereotypes are added as comments in the XMI for compatibility. Rhapsody may not display all stereotypes depending on profile configuration.

### Large Diagrams

**Problem**: Complex call trees create diagrams that are hard to read.

**Solutions**:
1. Reduce depth: `--max-depth 2`
2. Use module-level view: `--use-module-names --module-config config.yaml`
3. Break into smaller functions (analyze multiple start functions)

## Best Practices

### For Documentation

- Use `--use-module-names` for architecture-level views
- Include `--max-depth` to limit complexity
- Generate both formats: `--format both` (Mermaid for docs, Rhapsody for editing)

### For Analysis

- Use `--verbose` to see detailed statistics
- Check circular dependency warnings
- Review module distribution for architecture insights

### For Automation

- Combine with `--rebuild-cache` for fresh analysis
- Use `--output` with directory structure for organized outputs
- Script generation for multiple start functions

## Examples

### Example 1: Simple Call Tree

```bash
calltree --start-function COM_Init \
         --source-dir demo \
         --format rhapsody \
         --output com_init.xmi
```

### Example 2: Architecture View with Modules

```bash
# Create module mapping
cat > modules.yaml << EOF
version: "1.0"
file_mappings:
  com.c: CommunicationModule
  hw.c: HardwareModule
  sw.c: SoftwareModule
EOF

# Generate module-level diagram
calltree --start-function COM_Init \
         --source-dir demo \
         --module-config modules.yaml \
         --use-module-names \
         --format rhapsody \
         --output architecture.xmi
```

### Example 3: Batch Export

```bash
# Export multiple functions
for func in COM_Init COM_Send HW_Read SW_Update; do
    calltree --start-function "$func" \
             --format rhapsody \
             --output "diagrams/${func}.xmi"
done
```

## Related Documentation

- [README.md](../README.md) - Main project documentation
- [requirements_rhapsody.md](requirements/requirements_rhapsody.md) - Requirements specification
- [CLI Usage Examples](../README.md#basic-usage) - Command-line examples

## Support

For issues or questions:
1. Check [troubleshooting](#troubleshooting) section
2. Review [requirements](requirements/requirements_rhapsody.md)
3. Open GitHub issue with XMI file and error message
