# Cache Loading Progress Requirements

## SWR_CACHE_00001: File-by-File Cache Loading Progress

**Title**: Display file-by-file progress when loading from cache

**Maturity**: accept

**Description**:
When loading function database from cache in verbose mode, the tool shall display progress information showing each file being loaded with its function count.

**Rationale**:
For large codebases, cache loading may involve processing thousands of files. Showing progress helps users understand what's happening and provides confidence that the tool is working correctly. File-by-file progress is particularly useful for debugging and performance analysis.

**Functional Requirements**:

1. **Progress Display**:
   - When loading from cache in verbose mode (`-v` flag), the tool shall display:
     - A header line: "Loading N files from cache..."
     - One line per file with format: `[idx/total] filename: X functions`
   - Files shall be displayed in the order they appear in the cache

2. **Verbose Mode Only**:
   - Progress details shall only be shown in verbose mode
   - Non-verbose mode shall load cache silently (current behavior)
   - This prevents overwhelming output for large projects

3. **Progress Information**:
   - Each file line shall show:
     - Current file index (1-based)
     - Total number of files
     - Filename (base name, not full path)
     - Number of functions in that file
   - Example: `[1/15] demo.c: 5 functions`

4. **Loading Summary**:
   - After all files are loaded, the tool shall display the total
   - Summary shall include total files and total functions
   - This matches the format used during database building

**Implementation Notes**:

- Implemented in `FunctionDatabase._load_from_cache()`
- Progress is only shown when `verbose=True`
- Iterates through `self.functions_by_file` to display progress
- Uses `Path(file_path).name` to get base filename

**Example Output**:

```bash
$ calltree --start-function Demo_Init -v

Loading 4 files from cache...
  [1/4] demo.c: 4 functions
  [2/4] hardware.c: 11 functions
  [3/4] software.c: 9 functions
  [4/4] communication.c: 9 functions

Database Statistics:
  Files Scanned: 4
  Functions Found: 33
  ...
```

## SWR_CACHE_00002: Cache Status Indication

**Title**: Distinguish cache loading from database building

**Maturity**: accept

**Description**:
The tool shall clearly indicate whether data is being loaded from cache or built from source, providing users with visibility into the operation being performed.

**Functional Requirements**:

1. **Cache Hit Indication**:
   - When cache is successfully loaded, the tool shall indicate "Loading from cache..."
   - The progress spinner may show "Loading from cache..." vs "Building database..."
   - This provides immediate feedback to the user

2. **Cache Miss Indication**:
   - When cache is not available, the tool shall build from source
   - Progress shall show "Building database from..."
   - File-by-file progress shall be shown during building

3. **Verbose Mode Details**:
   - In verbose mode, additional cache metadata may be displayed:
     - Cache creation timestamp
     - Number of files in cache
     - Source directory path

**Implementation Notes**:

- Current implementation uses a generic "Building function database..." message
- Cache loading happens inside the same progress block
- The verbose file listing naturally indicates cache loading

**Rationale**:
Users need to know whether the tool is using cached data (fast) or rebuilding from source (slow). This helps with:
- Performance debugging
- Understanding why operations take different amounts of time
- Verifying cache is working correctly

## SWR_CACHE_00003: Cache Loading Errors

**Title**: Handle cache loading errors gracefully

**Maturity**: accept

**Description**:
The tool shall handle cache loading errors gracefully and fall back to building from source when appropriate.

**Functional Requirements**:

1. **Error Detection**:
   - The tool shall detect corrupted cache files
   - The tool shall detect incompatible cache formats
   - The tool shall detect missing cache metadata

2. **Error Reporting**:
   - Cache errors shall be reported in verbose mode
   - Error messages shall clearly indicate the problem
   - Errors shall not cause silent failures

3. **Fallback Behavior**:
   - On cache load failure, the tool shall fall back to building from source
   - The user shall be informed of the fallback
   - The tool shall continue processing normally

**Error Handling**:

- Corrupted cache files shall trigger a rebuild
- Invalid cache metadata shall trigger a rebuild
- Source directory mismatches shall trigger a rebuild
- All exceptions during cache loading shall be caught

**Implementation Notes**:

- Implemented in `FunctionDatabase._load_from_cache()`
- Returns `False` on any error, triggering a rebuild
- Errors are logged if `verbose=True`
- Exception handling prevents crashes

## SWR_CACHE_00004: Performance Considerations

**Title**: Maintain cache loading performance

**Maturity**: accept

**Description**:
The progress display feature shall not significantly impact cache loading performance.

**Functional Requirements**:

1. **Minimal Overhead**:
   - Progress display shall add minimal overhead to cache loading
   - File iteration shall be efficient
   - String formatting shall be optimized

2. **Large File Lists**:
   - The tool shall handle projects with thousands of files
   - Progress display shall not become a bottleneck
   - Memory usage shall remain reasonable

3. **Display Throttling** (Optional):
   - For very large projects, consider displaying progress in batches
   - Example: Show every 100th file instead of every file
   - This would be a future enhancement if needed

**Implementation Notes**:

- Current implementation shows every file in verbose mode
- Overhead is minimal (just string formatting and print)
- Python's print is buffered, so performance impact is small
- For projects with 10,000+ files, batch display could be considered

**Future Enhancements**:

- Add a `--progress` flag to control progress detail level
- Support batch display for very large projects
- Consider progress bars instead of file lists
