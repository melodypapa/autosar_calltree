# Requirements Consolidation Summary

**Date**: 2026-02-10
**Version**: 2.0

---

## What Was Done

Consolidated requirements from **16 individual files** (158+ requirements) down to **6 package-based files** (141 core requirements).

---

## New Structure

### By Package

| Package | File | Requirements | Source Files |
|---------|------|--------------|--------------|
| `autosar_calltree.database` | `requirements_database.md` | 35 | `models.py`, `function_database.py` |
| `autosar_calltree.parsers` | `requirements_parsers.md` | 40 | `autosar_parser.py`, `c_parser.py`, `c_parser_pycparser.py` |
| `autosar_calltree.analyzers` | `requirements_analyzers.md` | 15 | `call_tree_builder.py` |
| `autosar_calltree.config` | `requirements_config.md` | 8 | `module_config.py` |
| `autosar_calltree.generators` | `requirements_generators.md` | 25 | `mermaid_generator.py`, `xmi_generator.py` |
| `autosar_calltree.cli` | `requirements_cli.md` | 18 | `main.py` |
| **Total** | **6 files** | **141** | **13 source files** |

---

## Files Removed

The following files were removed (16 files → 0 files):

### Old Individual Files (Consolidated)
- `autosar_parser.md` → merged into `requirements_parsers.md`
- `c_parser.md` → merged into `requirements_parsers.md`
- `c_parser_multiline.md` → merged into `requirements_parsers.md`
- `call_tree_builder.md` → became `requirements_analyzers.md`
- `cli.md` → became `requirements_cli.md`
- `function_call.md` → merged into `requirements_database.md`
- `function_database.md` → merged into `requirements_database.md`
- `models.md` → merged into `requirements_database.md`
- `requirements_cache_progress.md` → merged into `requirements_database.md`
- `requirements_mermaid_modules.md` → merged into `requirements_generators.md`
- `requirements_mermaid_opt_blocks.md` → merged into `requirements_generators.md`
- `requirements_module_config.md` → became `requirements_config.md`
- `requirements_parameters.md` → merged into `requirements_generators.md`
- `requirements_xmi.md` → merged into `requirements_generators.md`
- `requirements.md` (master index) → replaced by new `README.md`
- `COMBINED_REQUIREMENTS.md` → replaced by new package-based files

### Kept
- `README.md` (updated with new structure)
- `_template.md` (template for future requirements)

---

## How Similar Requirements Were Combined

### Example 1: FunctionInfo Model (Old → New)

**Old** (7 separate requirements):
- SWR_MODEL_00003: FunctionInfo Core Fields
- SWR_MODEL_00004: FunctionInfo Type Classification
- SWR_MODEL_00005: FunctionInfo Call Relationships
- SWR_MODEL_00006: FunctionInfo Disambiguation
- SWR_MODEL_00009: FunctionInfo Signature Generation
- SWR_MODEL_00010: FunctionInfo RTE Detection

**New** (1 combined requirement):
- **SWR_DB_00003**: FunctionInfo Dataclass
  - Combines all fields and methods into one comprehensive requirement
  - Lists all fields, methods, and their purposes

### Example 2: C Parser Features (Old → New)

**Old** (many granular requirements):
- SWR_PARSER_C_00001: Traditional C Function Pattern
- SWR_PARSER_C_00002: C Keyword Filtering
- SWR_PARSER_C_00003: AUTOSAR Type Filtering
- SWR_PARSER_C_00011: Static Function Detection
- SWR_PARSER_C_00012: Line Number Calculation
- etc.

**New** (grouped by feature):
- **SWR_PARSER_00011**: Traditional C Function Pattern
- **SWR_PARSER_00012**: Keyword and Type Filtering (combines 00002, 00003)
- **SWR_PARSER_00017**: Parameter String Parsing (combines multiple parsing reqs)
- etc.

### Example 3: Cache Requirements (Old → New)

**Old** (4 separate files):
- `function_database.md` (SWR_DB_00001-00024)
- `requirements_cache_progress.md` (SWR_CACHE_00001-00004)

**New** (merged into one section):
- `requirements_database.md` with caching section (SWR_DB_00026-00030)

---

## Benefits of Consolidation

### 1. **Aligned with Package Structure**
- Requirements organized by Python package (`autosar_calltree.*`)
- Each package has **one** requirements file
- Easy to find requirements for specific code

### 2. **Reduced Redundancy**
- Combined similar requirements into comprehensive ones
- Removed overlapping requirements across files
- Eliminated duplicate content

### 3. **Easier Maintenance**
- Fewer files to update
- Changes to package affect only one file
- Clear ownership (one file per package)

### 4. **Better Overview**
- Can see all requirements for a package at once
- Total count per package is visible
- Summary statistics are clearer

### 5. **Improved Readability**
- Logical grouping within each file
- Purpose-driven requirement organization
- Consistent structure across all files

---

## New Requirement ID Scheme

### Package-Based IDs

| Package | Prefix | Example | Count |
|---------|--------|---------|-------|
| Database | `SWR_DB_` | SWR_DB_00001 | 35 |
| Parsers | `SWR_PARSER_` | SWR_PARSER_00001 | 40 |
| Analyzers | `SWR_ANALYZER_` | SWR_ANALYZER_00001 | 15 |
| Config | `SWR_CONFIG_` | SWR_CONFIG_00001 | 8 |
| Generators | `SWR_GEN_` | SWR_GEN_00001 | 25 |
| CLI | `SWR_CLI_` | SWR_CLI_00001 | 18 |

**Note**: Old IDs like `SWR_MODEL_*`, `SWR_PARSER_AUTOSAR_*`, `SWR_PARSER_C_*`, `SWR_MERMAID_*`, etc. have been consolidated into package-based prefixes.

---

## Statistics

### Before Consolidation
- **Files**: 16 individual requirement files
- **Requirements**: 158+ (some duplicates/overlaps)
- **Organization**: By component/feature (scattered)

### After Consolidation
- **Files**: 6 package-based requirement files
- **Requirements**: 141 (unique, combined)
- **Organization**: By Python package (aligned with code)

### Reduction
- **Files**: 62.5% reduction (16 → 6)
- **Requirements**: ~11% reduction (158 → 141)
- **Duplication**: Eliminated all overlapping requirements

---

## Migration Notes

### For Developers

1. **Old requirement IDs** still work in:
   - Test files (test files reference old IDs)
   - Code comments (if they reference requirements)
   - Traceability matrix (will need update)

2. **New requirement IDs**:
   - Use package-based prefixes
   - Sequential numbering within each package
   - Clear mapping to source files

3. **To update traceability**:
   - Map old IDs to new consolidated requirements
   - Update `TRACEABILITY.md`
   - Update test references if needed

---

## File Locations

### New Requirements Files
```
docs/requirements/
├── README.md                          # Index and overview
├── requirements_database.md           # Database package
├── requirements_parsers.md            # Parsers package
├── requirements_analyzers.md          # Analyzers package
├── requirements_config.md             # Config package
├── requirements_generators.md         # Generators package
├── requirements_cli.md                # CLI package
└── _template.md                       # Template for new requirements
```

### Package Mapping
```
src/autosar_calltree/
├── database/
│   ├── models.py              → requirements_database.md
│   └── function_database.py   → requirements_database.md
├── parsers/
│   ├── autosar_parser.py       → requirements_parsers.md
│   ├── c_parser.py              → requirements_parsers.md
│   └── c_parser_pycparser.py    → requirements_parsers.md
├── analyzers/
│   └── call_tree_builder.py     → requirements_analyzers.md
├── config/
│   └── module_config.py         → requirements_config.md
├── generators/
│   ├── mermaid_generator.py     → requirements_generators.md
│   └── xmi_generator.py          → requirements_generators.md
└── cli/
    └── main.py                  → requirements_cli.md
```

---

## Next Steps

1. ✅ Create new package-based requirement files
2. ✅ Remove old individual requirement files
3. ✅ Update README with new structure
4. ⏳ Update TRACEABILITY.md with new IDs
5. ⏳ Update test files to reference new IDs (optional)
6. ⏳ Update code comments with new IDs (optional)

---

## Conclusion

The consolidation has successfully:
- ✅ Reduced file count from 16 to 6
- ✅ Organized requirements by package structure
- ✅ Combined similar/overlapping requirements
- ✅ Improved maintainability and readability
- ✅ Maintained complete requirement coverage

**Result**: A cleaner, more organized requirements structure that aligns with the codebase.
