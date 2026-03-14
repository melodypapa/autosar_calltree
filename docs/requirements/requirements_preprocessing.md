# Preprocessing Package Requirements

**Package**: `autosar_calltree.preprocessing`
**Source Files**: `cpp_preprocessor.py`
**Requirements**: SWR_PREPROCESS_00001 - SWR_PREPROCESS_00008 (8 requirements)

---

## Overview

The preprocessing package provides functionality for running the C preprocessor (cpp) on source files before parsing, with metrics collection and error tracking for improved visibility into parse success rates.

**Core Classes**:
- `CPPPreprocessor` - Runs cpp on source files with statistics collection
- `PreprocessResult` - Result of preprocessing a single file
- `PreprocessStatistics` - Aggregate statistics for preprocessing stage

---

## Two-Stage Pipeline (SWR_PREPROCESS_00001 - SWR_PREPROCESS_00003)

### SWR_PREPROCESS_00001 - Two-Stage Preprocessing Pipeline
**Purpose**: Separate preprocessing and parsing into distinct stages

**Pipeline**:
```
Stage 1: Source Files → CPP Preprocessor → Temp Folder
Stage 2: Preprocessed Files → pycparser → Functions
```

**Benefits**:
- Visibility into each stage's success/failure
- Separate metrics for preprocessing vs parsing
- Can debug each stage independently
- Can re-parse without re-preprocessing

**Implementation**: `CPPPreprocessor` class in `cpp_preprocessor.py`

**Integration**: `FunctionDatabase._build_with_two_stage_pipeline()`

---

### SWR_PREPROCESS_00002 - Preprocessing Metrics Collection
**Purpose**: Collect and report statistics for preprocessing stage

**Metrics**:
- Total files processed
- Successful preprocessing count
- Failed preprocessing count
- Per-file results with error details

**Data Structures**:
- `PreprocessResult`: Per-file result (source_file, output_file, success, error_message, error_type)
- `PreprocessStatistics`: Aggregate stats (total, successful, failed, skipped, results list)

**Implementation**: `PreprocessStatistics` dataclass with `success_rate` property

---

### SWR_PREPROCESS_00003 - Error Visibility and Tracking
**Purpose**: Provide visibility into preprocessing failures

**Error Types**:
- `cpp_not_found`: CPP executable not found on system
- `cpp_error`: CPP returned non-zero exit code
- `timeout`: Preprocessing exceeded time limit

**Reporting**:
- Per-file error messages during processing
- Summary of all failed files at end
- Error type classification for debugging

**Implementation**: `PreprocessResult.error_type` and `PreprocessResult.error_message` fields

---

## CPP Path Resolution (SWR_PREPROCESS_00004 - SWR_PREPROCESS_00005)

### SWR_PREPROCESS_00004 - CPP Path Resolution
**Purpose**: Find the CPP executable on various platforms

**Resolution Order**:
1. Command from `--cpp-config` YAML file
2. Platform-specific default paths
3. System PATH lookup via `shutil.which()`

**Default Paths by Platform**:
- **Windows**: `./cpp/cpp.exe`, `./tools/cpp.exe`, `%MINGW_HOME%/bin/cpp.exe`
- **Linux**: `/usr/bin/cpp`, `/usr/local/bin/cpp`
- **macOS**: `/usr/bin/cpp`, `/usr/local/bin/cpp`

**Fallback**: Try `gcc -E` if cpp not found

**Implementation**: `CPPPreprocessor._get_cpp_path()`

---

### SWR_PREPROCESS_00005 - Windows CPP Support
**Purpose**: Support Windows systems with MinGW/MSYS2

**Setup**:
1. Create `./cpp/` folder in project root
2. Copy `cpp.exe` from MinGW/MSYS2 into that folder
3. Tool automatically finds and uses it

**Environment Variables**:
- `MINGW_HOME`: Checked for `%MINGW_HOME%/bin/cpp.exe`

**Implementation**: Platform-specific paths in `DEFAULT_CPP_PATHS`

---

## File Processing (SWR_PREPROCESS_00006 - SWR_PREPROCESS_00008)

### SWR_PREPROCESS_00006 - Batch Preprocessing with Progress
**Purpose**: Preprocess multiple files with progress display

**Method**: `preprocess_all(source_files, verbose=True)`

**Progress Format**:
```
=== Preprocessing Stage ===
[1/25] demo/main.c         Running cpp...
[2/25] demo/complex.c      FAILED (cpp_error)
    Error: unknown type name 'CustomType'
[3/25] demo/api.c          Running cpp...
```

**Returns**: `PreprocessStatistics` with all results

---

### SWR_PREPROCESS_00007 - Temporary File Management
**Purpose**: Manage preprocessed files in temp directory

**Features**:
- Create temp directory for preprocessed `.i` files
- Default: System temp directory with `autosar_prep_` prefix
- Custom: `--temp-dir` option for specific location
- Cleanup: Remove temp files after parsing (default)
- Keep: `--keep-temp` option to preserve files for debugging

**Output File Naming**: `{source_stem}.i` (e.g., `demo.c` → `demo.i`)

**Implementation**: `CPPPreprocessor._get_temp_dir()` and `cleanup()`

---

### SWR_PREPROCESS_00008 - Preprocessor Configuration Integration
**Purpose**: Integrate with `PreprocessorConfig` for CPP options

**Configuration Options**:
- `command`: CPP executable path or name
- `include_dirs`: List of `-I` directories
- `extra_flags`: Additional flags (`-D`, `-std`, etc.)
- `enabled`: Enable/disable CPP preprocessing

**CLI Integration**:
- `--cpp-config PATH`: Load configuration from YAML
- `--keep-temp`: Keep preprocessed files
- `--temp-dir PATH`: Custom temp directory
- `--preprocess-only`: Run only Stage 1 for debugging

**Implementation**: `CPPPreprocessor._build_command()` uses config for flags

---

## Summary

**Total Requirements**: 8
**Implementation Status**: ✅ All Implemented

**Package Structure**:
```
autosar_calltree.preprocessing/
└── cpp_preprocessor.py    # SWR_PREPROCESS_00001 - SWR_PREPROCESS_00008
```

**Key Features**:
- Two-stage preprocessing and parsing pipeline
- Comprehensive metrics collection
- Full error visibility
- Cross-platform CPP support (Windows, Linux, macOS)
- Progress display during processing
- Temporary file management with cleanup options
- Integration with PreprocessorConfig and CLI