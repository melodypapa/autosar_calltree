# PDF Parser

Parse AUTOSAR PDF files and extract model hierarchies with various output options.

## Actions

When the user runs `/parse`, help the user parse AUTOSAR PDF files:

### 1. Identify Input
- Check if `$ARGUMENTS` contains file paths or use current directory
- Validate that input files/directories exist
- List PDF files found

### 2. Run Parser
Use the `autosar-extract` CLI with appropriate options:
```bash
# Basic parsing (output to stdout)
autosar-extract input.pdf

# Save to file
autosar-extract input.pdf -o output.md

# Parse multiple PDFs
autosar-extract file1.pdf file2.pdf -o output.md

# Parse directory of PDFs
autosar-extract /path/to/pdfs/

# Write individual class files
autosar-extract input.pdf --write-class-files

# Verbose mode for debugging
autosar-extract input.pdf -v
```

### 3. Handle Output
- Display the markdown output if not saved to file
- Show output file location if saved
- Report number of packages/classes extracted
- Display any warnings or errors

### 4. Logging Levels
- **INFO** (default): Standard progress messages
- **DEBUG** (`-v` flag): Detailed debug information
- **WARNING**: Non-critical issues
- **ERROR**: Critical failures

## Usage Examples

```
/parse
/parse input.pdf
/parse input.pdf -o output.md
/parse /path/to/pdfs/ --write-class-files
/parse -v (verbose mode)
```

## Options

Based on `$ARGUMENTS`:
- `-o <file>`: Output to file
- `--write-class-files`: Write each class to separate file
- `-v, --verbose`: Enable debug logging
- `<directory>`: Parse all PDFs in directory

## Error Handling

- Skip non-PDF files with warning
- Report empty directories
- Handle parse errors gracefully
- Show detailed error messages in verbose mode
