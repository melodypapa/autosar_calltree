# Function Database Requirements

## Overview
This document specifies requirements for the FunctionDatabase module, which manages the database of all functions found in the codebase.

## Requirements

### SWR_DB_00001: Database Initialization
**Priority:** High
**Description:** The FunctionDatabase class must initialize with source directory, cache directory, and optional module configuration.

**Rationale:** Provides flexible configuration for different project structures.

**Verification:** Database can be instantiated with custom paths and module config.

---

### SWR_DB_00002: Cache Directory Creation
**Priority:** Medium
**Description:** The database must automatically create the cache directory if it doesn't exist.

**Rationale:** Eliminates manual setup steps for users.

**Verification:** Database creates `.cache` directory on initialization.

---

### SWR_DB_00003: Three-Index Database Structure
**Priority:** High
**Description:** The database must maintain three indexing structures:
1. `functions`: function_name -> List[FunctionInfo]
2. `qualified_functions`: "file::function" -> FunctionInfo
3. `functions_by_file`: file_path -> List[FunctionInfo]

**Rationale:** Different lookup patterns require different indexes for optimal performance.

**Verification:** All three indexes are populated correctly during database building.

---

### SWR_DB_00004: Source File Discovery
**Priority:** High
**Description:** The database must recursively discover all `.c` files in the source directory.

**Rationale:** Ensures complete coverage of the codebase.

**Verification:** All C files in subdirectories are found and processed.

---

### SWR_DB_00005: File Parsing Integration
**Priority:** High
**Description:** The database must use C parser (with AUTOSAR fallback) to parse each source file.

**Rationale:** Leverages progressive enhancement strategy for maximum compatibility.

**Verification:** Both AUTOSAR and traditional C functions are parsed correctly.

---

### SWR_DB_00006: Module Configuration Integration
**Priority:** High
**Description:** When module configuration is provided, the database must assign SW modules to functions during addition.

**Rationale:** Enables architecture-level analysis with module names.

**Verification:** Functions get `sw_module` field set based on file mappings.

---

### SWR_DB_00007: Module Statistics Tracking
**Priority:** Medium
**Description:** The database must track function counts per module.

**Rationale:** Provides insights into module complexity and distribution.

**Verification:** `module_stats` dictionary contains correct counts per module.

---

### SWR_DB_00008: Qualified Function Key Generation
**Priority:** High
**Description:** The database must generate qualified keys in the format "file_stem::function_name" for static function resolution.

**Rationale:** Enables disambiguation of static functions with same name in different files.

**Verification:** Static functions can be resolved via qualified lookup.

---

### SWR_DB_00009: Smart Function Lookup - Level 1 (Implementation Preference)
**Priority:** High
**Description:** When multiple definitions exist, prefer functions with actual implementations (have function calls).

**Rationale:** Declarations don't have bodies; implementations are needed for call tree analysis.

**Verification:** Functions with calls are selected over empty declarations.

---

### SWR_DB_00010: Smart Function Lookup - Level 2 (File Name Heuristics)
**Priority:** High
**Description:** Prefer functions from files matching the function name pattern (e.g., `COM_InitCommunication` in `communication.c`).

**Rationale:** AUTOSAR naming conventions typically align with file names.

**Verification:** Cross-module calls select correct implementation based on filename matching.

---

### SWR_DB_00011: Smart Function Lookup - Level 3 (Cross-Module Awareness)
**Priority:** High
**Description:** For cross-module calls, avoid selecting functions from the calling file to prevent choosing local declarations.

**Rationale:** Ensures module-level diagrams show actual cross-module interactions.

**Verification:** When `Demo_Init` (demo.c) calls `COM_InitCommunication`, selects implementation from communication.c, not declaration from demo.c.

---

### SWR_DB_00012: Smart Function Lookup - Level 4 (Module Preference)
**Priority:** Medium
**Description:** Prefer functions with assigned SW modules over those without.

**Rationale:** Functions with modules are typically more important for architecture analysis.

**Verification:** Functions with `sw_module` set are preferred over unassigned ones.

---

### SWR_DB_00013: Cache Metadata Validation
**Priority:** High
**Description:** Cache loading must validate metadata including source directory and file count.

**Rationale:** Prevents using stale cache from different projects.

**Verification:** Cache is rejected if source directory doesn't match.

---

### SWR_DB_00014: Cache Save with Metadata
**Priority:** High
**Description:** Cache saving must store metadata, all three indexes, and statistics in pickle format.

**Rationale:** Enables fast reload with complete state restoration.

**Verification:** Cache file contains all database structures with metadata.

---

### SWR_DB_00015: File-by-File Cache Loading Progress
**Priority:** Medium
**Description:** When loading cache with verbose mode, display progress for each file loaded.

**Rationale:** Provides user feedback during cache loading.

**Verification:** Verbose mode shows "[N/M] filename: X functions" for each file.

---

### SWR_DB_00016: Cache Error Handling
**Priority:** High
**Description:** Cache loading must handle errors gracefully and fall back to rebuilding database.

**Rationale:** Prevents crashes from corrupted cache files.

**Verification:** Corrupted cache triggers rebuild without user intervention.

---

### SWR_DB_00017: Function Lookup by Name
**Priority:** High
**Description:** Provide method to lookup functions by name, returning list of candidates.

**Rationale:** Primary lookup interface for analyzer.

**Verification:** Returns all definitions for function name.

---

### SWR_DB_00018: Qualified Function Lookup
**Priority:** Medium
**Description:** Provide method to lookup functions by qualified name (file::function).

**Rationale:** Enables precise static function resolution.

**Verification:** Returns exact function for qualified key.

---

### SWR_DB_00019: Function Search by Pattern
**Priority:** Medium
**Description:** Provide method to search for functions by substring pattern (case-insensitive).

**Rationale:** Enables CLI search functionality.

**Verification:** Returns all functions with matching names.

---

### SWR_DB_00020: Database Statistics
**Priority:** Medium
**Description:** Provide method to get database statistics including files scanned, functions found, static count, parse errors, and module stats.

**Rationale:** Enables CLI reporting and analysis insights.

**Verification:** Statistics dictionary contains all required fields.

---

### SWR_DB_00021: Parse Error Collection
**Priority:** Medium
**Description:** The database must collect and track parse errors without stopping the scan.

**Rationale:** One bad file shouldn't prevent analysis of the rest.

**Verification:** Parse errors are logged and accessible via statistics.

---

### SWR_DB_00022: Cache Clearing
**Priority:** Low
**Description:** Provide method to delete cache file.

**Rationale:** Enables manual cache invalidation.

**Verification:** Cache file is removed after calling clear_cache().

---

### SWR_DB_00023: Get All Function Names
**Priority:** Medium
**Description:** Provide method to get sorted list of all unique function names.

**Rationale:** Enables CLI list functionality.

**Verification:** Returns sorted list of function names.

---

### SWR_DB_00024: Get Functions by File
**Priority:** Medium
**Description:** Provide method to get all functions defined in a specific file.

**Rationale:** Useful for file-level analysis and reporting.

**Verification:** Returns correct functions for given file path.

---

### SWR_DB_00025: File Size Display in Processing
**Priority:** Medium
**Description:** When processing source files, display file size in human-readable format (bytes, KB, or MB).

**Rationale:** Helps users understand which files are being processed and identify large files that may impact performance.

**Functional Requirements:**
- File size shall be displayed during database building: `Processing: [N/M] filename.c (Size: X.XXK)`
- Files smaller than 1KB shall display raw bytes (e.g., `512`)
- Files 1KB to 1MB shall display size with 2 decimal places in KB (e.g., `5.25K`)
- Files 1MB and larger shall display size with 2 decimal places in MB (e.g., `2.50M`)
- Size formatting shall use a helper function `_format_file_size(size_bytes: int) -> str`

**Verification:** Processing messages show correctly formatted file sizes.

**Implementation Notes:**
- Helper function `_format_file_size()` in `function_database.py`
- Uses `file_path.stat().st_size` to get file size in bytes
- Formatting thresholds: >= 1MB for MB, >= 1KB for KB, otherwise bytes

**Example Output:**
```
Processing: [1/4] small.c (Size: 512)
Processing: [2/4] medium.c (Size: 5.25K)
Processing: [3/4] large.c (Size: 2.50M)
```

---

## Summary
- **Total Requirements:** 25
- **High Priority:** 13
- **Medium Priority:** 11
- **Low Priority:** 1
