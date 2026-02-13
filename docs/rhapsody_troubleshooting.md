# Rhapsody Export Troubleshooting

## Common Issues and Solutions

### Issue: Import Fails with "Invalid XMI Format"

**Symptoms**:
- Rhapsody shows error dialog when opening XMI file
- Error message mentions "XMI format" or "schema validation"

**Causes**:
1. Rhapsody version < 8.0 (lacks UML 2.1 support)
2. Corrupted XMI file (incomplete write)
3. Non-standard XML characters in function names

**Solutions**:
```bash
# 1. Check Rhapsody version
# In Rhapsody: Help > About, verify version >= 8.0

# 2. Re-generate XMI with cache rebuild
calltree --start-function Demo_Init \
         --format rhapsody \
         --rebuild-cache \
         --source-dir demo

# 3. Verify XMI file size (should be > 0 bytes)
ls -l output.xmi

# 4. Check for non-ASCII characters in source
calltree --start-function Demo_Init \
         --list-functions \
         --source-dir demo
```

---

### Issue: Empty Diagram After Import

**Symptoms**:
- Rhapsody imports successfully
- Sequence diagram shows no lifelines or messages
- Only empty interaction element present

**Causes**:
1. Start function not found in database
2. Max depth too shallow (no children)
3. Parse errors prevented function discovery

**Solutions**:
```bash
# 1. Verify start function exists
calltree --source-dir demo --list-functions | grep Demo_Init

# 2. Increase depth
calltree --start-function Demo_Init \
         --format rhapsody \
         --max-depth 5 \
         --source-dir demo

# 3. Check for parse errors
calltree --start-function Demo_Init \
         --format rhapsody \
         --verbose \
         --source-dir demo 2>&1 | grep -i error

# 4. Verify database has functions
calltree --start-function Demo_Init \
         --verbose \
         --source-dir demo | grep "Functions Found"
```

---

### Issue: Loop/Opt Blocks Not Showing

**Symptoms**:
- Diagram shows messages but no combined fragments
- Loop/opt blocks from source code not visible
- All messages appear as sequential calls

**Causes**:
1. Loop/opt detection failed during parsing
2. C parser didn't recognize loop syntax
3. Complex multi-line conditions not parsed

**Solutions**:
```bash
# 1. Rebuild cache to re-parse source
calltree --start-function Demo_Update \
         --format rhapsody \
         --rebuild-cache \
         --source-dir demo

# 2. Check source code formatting
# Ensure loops follow standard C syntax:
#   for (i = 0; i < 10; i++) { ... }
#   while (condition) { ... }
#   if (condition) { ... }

# 3. Verify with verbose output
calltree --start-function Demo_Update \
         --format rhapsody \
         --verbose \
         --source-dir demo

# 4. Check for loop detection in statistics
calltree --start-function Demo_Update \
         --verbose \
         --source-dir demo | grep -i loop
```

---

### Issue: Module Names Not Showing

**Symptoms**:
- Lifelines show function names instead of module names
- `--use-module-names` flag appears to be ignored

**Causes**:
1. `--module-config` not specified or invalid
2. Source files not mapped in module config
3. Module config has syntax errors

**Solutions**:
```bash
# 1. Verify module config exists
cat demo/module_mapping.yaml

# 2. Check module config syntax
python -c "
import yaml
from pathlib import Path
config = yaml.safe_load(Path('demo/module_mapping.yaml').read_text())
print('Config valid:', config is not None)
print('Mappings:', len(config.get('file_mappings', {})))
"

# 3. Re-generate with explicit config
calltree --start-function Demo_Init \
         --format rhapsody \
         --module-config demo/module_mapping.yaml \
         --use-module-names \
         --source-dir demo

# 4. Check module statistics
calltree --start-function Demo_Init \
         --verbose \
         --module-config demo/module_mapping.yaml \
         --source-dir demo | grep -A 20 "Module Distribution"
```

---

### Issue: Duplicate Lifelines

**Symptoms**:
- Same function appears multiple times as lifeline
- Diagram shows redundant participants

**Causes**:
1. Multiple function definitions in different files
2. Smart function lookup selecting wrong definition
3. Static functions with same name in different files

**Solutions**:
```bash
# 1. List all function definitions
calltree --source-dir demo --list-functions | grep -c "FunctionName"

# 2. Search for specific function locations
calltree --source-dir demo --search "FunctionName"

# 3. Use qualified names if needed
# The tool automatically selects best match
# For manual control, edit source to have single definition

# 4. Verify with verbose output
calltree --start-function FunctionName \
         --verbose \
         --source-dir demo | grep "Selected"
```

---

### Issue: XMI File Too Large

**Symptoms**:
- XMI file size > 10MB
- Slow import into Rhapsody
- Out of memory errors

**Causes**:
1. Max depth too high (exponential growth)
2. Large codebase with many functions
3. Circular dependencies causing infinite loops

**Solutions**:
```bash
# 1. Reduce depth
calltree --start-function Demo_Init \
         --format rhapsody \
         --max-depth 2 \
         --source-dir demo

# 2. Check for circular dependencies
calltree --start-function Demo_Init \
         --format rhapsody \
         --verbose \
         --source-dir demo | grep -A 10 "circular"

# 3. Analyze smaller sub-trees
# Break into smaller start functions
for func in Func1 Func2 Func3; do
    calltree --start-function "$func" \
             --format rhapsody \
             --max-depth 2 \
             --output "diagrams/${func}.xmi"
done

# 4. Check statistics before export
calltree --start-function Demo_Init \
         --verbose \
         --source-dir demo | grep "Total functions"
```

---

### Issue: Characters Not Displaying Correctly

**Symptoms**:
- Special characters in function names show as escaped XML
- Non-ASCII characters appear as `&#xNNNN;`
- Underscores or other symbols are missing

**Causes**:
1. XML encoding issues
2. Special AUTOSAR macros with non-standard characters
3. Source file encoding not UTF-8

**Solutions**:
```bash
# 1. Verify source file encoding
file -I demo/*.c

# 2. Check XMI file encoding
file -I output.xmi

# 3. Re-generate if needed
calltree --start-function Demo_Init \
         --format rhapsody \
         --rebuild-cache \
         --source-dir demo

# 4. Verify XML declaration
head -1 output.xmi
# Should show: <?xml version="1.0" encoding="utf-8"?>
```

---

## Debug Mode

For systematic troubleshooting, use debug mode:

```bash
# Enable verbose output with all details
calltree --start-function Demo_Init \
         --format rhapsody \
         --verbose \
         --rebuild-cache \
         --source-dir demo \
         2>&1 | tee debug.log

# Check log file for issues
grep -i "error\|warning\|failed" debug.log
```

## Log File Analysis

### Key Indicators

**Success Indicators**:
```
Generated Rhapsody XMI: diagrams/output.xmi
Analysis complete!
```

**Warning Indicators**:
```
Warning: Circular dependencies detected!
Warning: --use-module-names requires --module-config
```

**Error Indicators**:
```
Error: Cannot generate XMI: call tree is None
Error: start_function not found
Error: Invalid module config
```

## Getting Help

If issues persist:

1. **Check Documentation**:
   - [Rhapsody Export Guide](rhapsody_export.md)
   - [Main README](../README.md)
   - [Requirements](requirements/requirements_rhapsody.md)

2. **Verify Environment**:
   ```bash
   # Check Python version
   python --version  # Should be 3.9+

   # Check tool version
   calltree --version

   # Check Rhapsody version
   # In Rhapsody: Help > About
   ```

3. **Create Minimal Reproducer**:
   ```bash
   # Create smallest possible example
   mkdir /tmp/test_case
   cd /tmp/test_case
   # Copy minimal source files
   # Run with verbose output
   calltree --start-function TestFunc --verbose --source-dir . > debug.log 2>&1
   ```

4. **Report Issue**:
   - Include: XMI file, debug.log, source code sample
   - Platform: macOS/Linux/Windows, Python version, Rhapsody version
   - GitHub: https://github.com/your-org/autosar-calltree/issues

## Known Limitations

### By Design

1. **Manual Import Required**: XMI files must be manually imported via Rhapsody's File > Import menu
   - **Reason**: Cross-platform compatibility (works on Windows, Linux, macOS)
   - **Alternative**: Use COM API automation on Windows (future enhancement)

2. **Rhapsody License Required**: Need valid Rhapsody installation
   - **Reason**: XMI import requires Rhapsody or compatible UML tool
   - **Alternative**: Use Mermaid format for free visualization

3. **Stereotypes as Comments**: AUTOSAR stereotypes added as XML comments
   - **Reason**: Rhapsody profile compatibility
   - **Impact**: May not display in all Rhapsody views

### Platform-Specific

**Windows**:
- Path separator: Use forward slashes or double backslashes
- Permissions: May need administrator for Program Files

**Linux/macOS**:
- Case sensitivity: File paths are case-sensitive
- Permissions: May need chmod for output directories

## Performance Tips

### For Faster Generation

```bash
# Use cache (default)
calltree --start-function Demo_Init --format rhapsody --source-dir demo

# Skip cache for fresh analysis only when needed
calltree --start-function Demo_Init --format rhapsody --rebuild-cache --source-dir demo
```

### For Smaller XMI Files

```bash
# Limit depth
calltree --start-function Demo_Init --format rhapsody --max-depth 2 --source-dir demo

# Use module-level view (fewer lifelines)
calltree --start-function Demo_Init --format rhapsody --use-module-names --source-dir demo
```

### For Better Import Performance

```bash
# Split large diagrams
for func in $(calltree --list-functions --source-dir demo | head -20); do
    calltree --start-function "$func" --format rhapsody --max-depth 3 --output "diagrams/${func}.xmi"
done
```
