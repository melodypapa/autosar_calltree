# IBM Rhapsody Export Guide

## Overview

The AUTOSAR Call Tree Analyzer supports exporting call trees as Rhapsody-compatible XMI 2.1 files that can be imported into IBM Rhapsody 8.0+ for further editing and visualization.

## Requirements

- IBM Rhapsody 8.0 or later
- AUTOSAR Call Tree Analyzer v0.8.0+ (for XMI 2.1 compatibility)

## Generating Rhapsody XMI

### Basic Usage

```bash
# Generate Rhapsody-compatible XMI
calltree --start-function Demo_Init --format rhapsody --source-dir demo

# Output to specific file
calltree --start-function Demo_Init --format rhapsody --output diagrams/rhapsody_demo.xmi

# Generate with nested package structure
calltree --start-function Demo_Init \
         --format rhapsody \
         --output diagrams/rhapsody_demo.xmi \
         --rhapsody-package-path "MyPackage/SubPackage"

# Generate with custom model name
calltree --start-function Demo_Init \
         --format rhapsody \
         --output diagrams/rhapsody_demo.xmi \
         --rhapsody-model-name "MyProjectModel"
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

### With Loop and Conditional Detection

Enable loop and conditional detection for more detailed diagrams:

```bash
calltree --start-function Demo_MainFunction \
         --format rhapsody \
         --source-dir demo \
         --enable-loops \
         --enable-conditionals \
         --output demo/rhapsody_detailed.xmi
```

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

- **XMI 2.1 Format**: OMG XMI 2.1 with UML 2.1 namespace for full Rhapsody compatibility
- **GUID+ ID Format**: All elements use `GUID+<UUID>` format for maximum Rhapsody compatibility
- **MessageOccurrenceSpecification**: Explicit send/receive occurrence fragments for timing info
- **Rhapsody Profiles**: Includes Rhapsody-specific profile references and eAnnotations
- **AUTOSAR Stereotypes**: Supports AUTOSAR-specific stereotypes (e.g., `<<SWC>>`)
- **Nested Package Support**: Optional `--rhapsody-package-path` for hierarchical organization
- **Custom Model Names**: Optional `--rhapsody-model-name` for project-specific naming
- **Tool Metadata**: Includes generation metadata for traceability

## Limitations

### Manual Import Step

Rhapsody XMI files require manual import via **File > Import > OMG XMI**. This is a trade-off for cross-platform compatibility (the feature works on Windows, Linux, and macOS).

### Rhapsody License Required

To import and edit XMI files, you need a valid IBM Rhapsody license. The generated XMI files cannot be viewed without Rhapsody or another UML tool.

### Version Compatibility

- **Minimum**: Rhapsody 8.0 (XMI 2.1 support)
- **Tested**: Rhapsody 10.0.1
- **XMI Format**: XMI 2.1 with UML 2.1 namespace (full Rhapsody compatibility)
- **Breaking Change**: v0.8.0 changed from XMI 4.0 to XMI 2.1 - files generated with v0.8.0+ are not compatible with older versions

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
- Generate Mermaid for docs and Rhapsody XMI for editing (run separately)
- Use `--enable-loops` and `--enable-conditionals` for detailed behavioral diagrams

### For Analysis

- Use `--verbose` to see detailed statistics
- Check circular dependency warnings
- Review module distribution for architecture insights
- Use `--rhapsody-package-path` to organize diagrams by project structure

### For Automation

- Combine with `--rebuild-cache` for fresh analysis
- Use `--output` with directory structure for organized outputs
- Script generation for multiple start functions
- Use `--rhapsody-model-name` for consistent naming across batch exports

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
