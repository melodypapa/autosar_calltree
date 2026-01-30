# Database Models Requirements

## Overview
The models module defines the core data structures used throughout the AUTOSAR Call Tree Analyzer. It provides enums, dataclasses, and type aliases for representing function information, call trees, analysis results, and statistics. These models are the foundation for parsing, analyzing, and generating output from C/AUTOSAR source code.

## Requirements

### SWR_MODEL_00001: FunctionType Enum

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The system shall provide a FunctionType enum to classify different function declaration types found in AUTOSAR and traditional C code.

**Rationale:**
Different function types require different parsing strategies. AUTOSAR macros (FUNC, FUNC_P2VAR, FUNC_P2CONST) have complex syntax that traditional C parsers cannot handle. The classification enables the progressive enhancement parsing strategy and allows generators to format functions appropriately.

**Acceptance Criteria:**
- [ ] Enum has value AUTOSAR_FUNC for FUNC(rettype, memclass) name() macros
- [ ] Enum has value AUTOSAR_FUNC_P2VAR for FUNC_P2VAR(type, ...) macros returning pointers
- [ ] Enum has value AUTOSAR_FUNC_P2CONST for FUNC_P2CONST(type, ...) macros returning const pointers
- [ ] Enum has value TRADITIONAL_C for standard C function declarations
- [ ] Enum has value RTE_CALL for RTE functions (Rte_Read_*, Rte_Write_*, etc.)
- [ ] Enum has value UNKNOWN for functions that cannot be classified

**Related Requirements:** None

---

### SWR_MODEL_00002: Parameter Dataclass - Core Fields

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The system shall provide a Parameter dataclass to represent function parameter information with type details and AUTOSAR-specific attributes.

**Rationale:**
AUTOSAR parameters include memory classes (AUTOMATIC, APPL_DATA, etc.) and const/pointer qualifiers that are essential for accurate function signatures. Traditional C parameters only need type and name information. The unified dataclass supports both parsing strategies.

**Acceptance Criteria:**
- [ ] Has field `name: str` for parameter name
- [ ] Has field `param_type: str` for actual type (uint32, uint8*, etc.)
- [ ] Has field `is_pointer: bool` defaulting to False
- [ ] Has field `is_const: bool` defaulting to False
- [ ] Has field `memory_class: Optional[str]` defaulting to None for AUTOSAR memory class

**Related Requirements:** None

---

### SWR_MODEL_00003: Parameter Dataclass - String Representation

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The Parameter dataclass shall provide a `__str__` method that formats the parameter as a string suitable for function signatures.

**Rationale:**
Function signatures in generated diagrams must display parameters in standard C format with const, pointer, and memory class information. This enables accurate documentation and code generation.

**Acceptance Criteria:**
- [ ] Formats const prefix if is_const is True
- [ ] Formats asterisk suffix if is_pointer is True
- [ ] Formats memory class in brackets if present (e.g., "[AUTOMATIC]")
- [ ] Returns format "{const}{type}{ptr} {name} [{memclass}]" or "{const}{type}{ptr} {name}"

**Related Requirements:** None

---

### SWR_MODEL_00004: FunctionInfo Dataclass - Core Identity Fields

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The system shall provide a FunctionInfo dataclass with core identity fields to uniquely identify functions in the codebase.

**Rationale:**
Function information must be uniquely identifiable and trackable for call tree construction. The combination of name, file path, and line number provides a unique identifier, even for static functions with the same name in different files.

**Acceptance Criteria:**
- [ ] Has field `name: str` for function name
- [ ] Has field `return_type: str` for return type
- [ ] Has field `file_path: Path` for source file location
- [ ] Has field `line_number: int` for declaration line number
- [ ] Has field `is_static: bool` for static linkage indicator

**Related Requirements:** SWR_MODEL_00008, SWR_MODEL_00009

---

### SWR_MODEL_00005: FunctionInfo Dataclass - Type Classification

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The FunctionInfo dataclass shall include function type classification and AUTOSAR-specific metadata.

**Rationale:**
Function type classification enables different parsing and display strategies. AUTOSAR metadata (memory class, macro type) preserves source code structure for accurate documentation and code generation.

**Acceptance Criteria:**
- [ ] Has field `function_type: FunctionType` for classification
- [ ] Has field `memory_class: Optional[str]` defaulting to None for AUTOSAR memory class (RTE_CODE, etc.)
- [ ] Has field `macro_type: Optional[str]` defaulting to None for macro name ("FUNC", "FUNC_P2VAR", etc.)

**Related Requirements:** SWR_MODEL_00001

---

### SWR_MODEL_00006: FunctionInfo Dataclass - Call Relationships

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The FunctionInfo dataclass shall track bidirectional call relationships between functions.

**Rationale:**
Call trees require both forward relationships (what this function calls) and backward relationships (what calls this function) for analysis and visualization. The list/set structure allows multiple callers and multiple callees.

**Acceptance Criteria:**
- [ ] Has field `parameters: List[Parameter]` defaulting to empty list
- [ ] Has field `calls: List[str]` defaulting to empty list for function names called within
- [ ] Has field `called_by: Set[str]` defaulting to empty set for function names that call this

**Related Requirements:** SWR_MODEL_00002

---

### SWR_MODEL_00007: FunctionInfo Dataclass - Disambiguation and Module Assignment

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The FunctionInfo dataclass shall support disambiguation of static functions and SW module assignment for architecture-level diagrams.

**Rationale:**
Static functions can have the same name in different files. The qualified name (file::function) uniquely identifies them. SW module assignment enables architecture-level diagrams showing module interactions instead of individual function calls.

**Acceptance Criteria:**
- [ ] Has field `qualified_name: Optional[str]` defaulting to None for file::function format
- [ ] Has field `sw_module: Optional[str]` defaulting to None for SW module name from config

**Related Requirements:** SWR_CONFIG_00001

---

### SWR_MODEL_00008: FunctionInfo Dataclass - Hash Implementation

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The FunctionInfo dataclass shall implement `__hash__` method to enable use in sets and as dictionary keys.

**Rationale:**
Call tree analysis requires tracking unique functions and detecting cycles. Sets of FunctionInfo objects are used for deduplication and cycle detection. Hashing must be based on identity fields (name, file_path, line_number).

**Acceptance Criteria:**
- [ ] Returns hash of tuple (name, file_path, line_number)
- [ ] Produces consistent hash values for equal objects
- [ ] Enables use in sets and as dictionary keys

**Related Requirements:** SWR_MODEL_00009

---

### SWR_MODEL_00009: FunctionInfo Dataclass - Equality Implementation

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The FunctionInfo dataclass shall implement `__eq__` method for equality comparison based on identity fields.

**Rationale:**
Function comparison is needed for set operations, cycle detection, and duplicate removal. Equality should be based on identity (name, file_path, line_number), not all fields, to treat different definitions of the same function as distinct.

**Acceptance Criteria:**
- [ ] Returns False if comparing with non-FunctionInfo object
- [ ] Returns True only when name, file_path, and line_number are equal
- [ ] Does not compare other fields (parameters, calls, etc.)

**Related Requirements:** SWR_MODEL_00008

---

### SWR_MODEL_00010: FunctionInfo Dataclass - Signature Generation

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The FunctionInfo dataclass shall provide `get_signature` method that generates a formatted function signature string.

**Rationale:**
Generated diagrams and documentation must display function signatures in standard C format. The signature includes return type, function name, and parameter list with proper formatting.

**Acceptance Criteria:**
- [ ] Returns string in format "{return_type} {name}({param1}, {param2}, ...)"
- [ ] Formats parameters using Parameter.__str__ method
- [ ] Joins parameters with comma and space
- [ ] Handles empty parameter list (returns "name()")

**Related Requirements:** SWR_MODEL_00003

---

### SWR_MODEL_00011: FunctionInfo Dataclass - RTE Function Detection

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The FunctionInfo dataclass shall provide `is_rte_function` method to detect RTE functions.

**Rationale:**
RTE functions (Rte_Call_*, Rte_Read_*, etc.) are often excluded from call trees or displayed differently. Detection is based on both naming convention (Rte_ prefix) and function type classification.

**Acceptance Criteria:**
- [ ] Returns True if function name starts with "Rte_"
- [ ] Returns True if function_type is FunctionType.RTE_CALL
- [ ] Returns False otherwise

**Related Requirements:** SWR_MODEL_00001

---

### SWR_MODEL_00012: CallTreeNode Dataclass - Core Structure

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The system shall provide a CallTreeNode dataclass to represent nodes in the function call tree with hierarchical relationships.

**Rationale:**
Call trees are hierarchical structures where each function may call multiple child functions. The tree structure enables depth-first traversal, recursive call detection, and depth limit enforcement.

**Acceptance Criteria:**
- [ ] Has field `function_info: FunctionInfo` for function details
- [ ] Has field `depth: int` for depth in call tree
- [ ] Has field `children: List[CallTreeNode]` defaulting to empty list
- [ ] Has field `parent: Optional[CallTreeNode]` defaulting to None

**Related Requirements:** SWR_MODEL_00004

---

### SWR_MODEL_00013: CallTreeNode Dataclass - State Flags

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The CallTreeNode dataclass shall include state flags to track recursive calls, truncation, and call frequency.

**Rationale:**
Recursive calls must be marked to prevent infinite traversal. Truncation flags indicate when depth limits prevent full tree exploration. Call counts enable generation of statistics and frequency-based visualization.

**Acceptance Criteria:**
- [ ] Has field `is_recursive: bool` defaulting to False if function already in call stack
- [ ] Has field `is_truncated: bool` defaulting to False if depth limit reached
- [ ] Has field `call_count: int` defaulting to 1 for number of times function is called

**Related Requirements:** None

---

### SWR_MODEL_00014: CallTreeNode Dataclass - Tree Manipulation

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The CallTreeNode dataclass shall provide `add_child` method to build the tree structure.

**Rationale:**
Tree construction requires adding child nodes with proper parent reference. The method encapsulates the parent-child relationship maintenance.

**Acceptance Criteria:**
- [ ] Accepts child parameter of type CallTreeNode
- [ ] Sets child.parent to self
- [ ] Appends child to self.children list

**Related Requirements:** None

---

### SWR_MODEL_00015: CallTreeNode Dataclass - Function Collection

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The CallTreeNode dataclass shall provide `get_all_functions` method to collect all unique functions in the subtree.

**Rationale:**
Statistics generation and duplicate detection require collecting all functions in the call tree. The recursive traversal aggregates functions from the entire subtree.

**Acceptance Criteria:**
- [ ] Returns Set[FunctionInfo] of unique functions
- [ ] Includes current node's function_info
- [ ] Recursively collects from all children
- [ ] Deduplicates automatically using set

**Related Requirements:** SWR_MODEL_00004

---

### SWR_MODEL_00016: CallTreeNode Dataclass - Depth Calculation

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The CallTreeNode dataclass shall provide `get_max_depth` method to calculate maximum depth of the subtree.

**Rationale:**
Statistics generation requires knowing the maximum depth reached during analysis. The recursive traversal finds the deepest leaf node in the subtree.

**Acceptance Criteria:**
- [ ] Returns int representing maximum depth
- [ ] Returns self.depth if no children exist
- [ ] Returns maximum depth among all children if children exist
- [ ] Traverses recursively through entire subtree

**Related Requirements:** None

---

### SWR_MODEL_00017: CircularDependency Dataclass - Core Structure

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The system shall provide a CircularDependency dataclass to represent circular call chains detected during analysis.

**Rationale:**
Circular dependencies (e.g., A calls B calls C calls A) must be detected and reported to prevent infinite traversal and inform users about potential design issues.

**Acceptance Criteria:**
- [ ] Has field `cycle: List[str]` for sequence of function names forming the cycle
- [ ] Has field `depth: int` for depth at which cycle was detected

**Related Requirements:** None

---

### SWR_MODEL_00018: CircularDependency Dataclass - String Representation

**Priority:** Low
**Status:** Implemented
**Maturity:** accept

**Description:**
The CircularDependency dataclass shall provide `__str__` method for human-readable cycle display.

**Rationale:**
Generated diagrams and error messages must display cycles in readable format. The arrow notation clearly shows the call sequence.

**Acceptance Criteria:**
- [ ] Returns string with function names joined by " -> "
- [ ] Example: "FuncA -> FuncB -> FuncC -> FuncA"

**Related Requirements:** None

---

### SWR_MODEL_00019: AnalysisStatistics Dataclass - Counters

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The system shall provide an AnalysisStatistics dataclass to track metrics collected during call tree analysis.

**Rationale:**
Analysis statistics provide users with insights about the codebase complexity, depth of call chains, and distribution of function types. These metrics are displayed in generated output and used for validation.

**Acceptance Criteria:**
- [ ] Has field `total_functions: int` defaulting to 0
- [ ] Has field `unique_functions: int` defaulting to 0
- [ ] Has field `max_depth_reached: int` defaulting to 0
- [ ] Has field `total_function_calls: int` defaulting to 0
- [ ] Has field `static_functions: int` defaulting to 0
- [ ] Has field `rte_functions: int` defaulting to 0
- [ ] Has field `autosar_functions: int` defaulting to 0
- [ ] Has field `circular_dependencies_found: int` defaulting to 0

**Related Requirements:** None

---

### SWR_MODEL_00020: AnalysisStatistics Dataclass - Dictionary Conversion

**Priority:** Low
**Status:** Implemented
**Maturity:** accept

**Description:**
The AnalysisStatistics dataclass shall provide `to_dict` method to convert statistics to dictionary format.

**Rationale:**
Dictionary format enables JSON serialization for machine-readable output, logging, and testing. The flat structure is easy to consume by external tools.

**Acceptance Criteria:**
- [ ] Returns Dict[str, int] with all statistics fields
- [ ] Keys match field names (e.g., "total_functions", "unique_functions")
- [ ] Values are integer field values

**Related Requirements:** None

---

### SWR_MODEL_00021: AnalysisResult Dataclass - Result Container

**Priority:** High
**Status:** Implemented
**Maturity:** accept

**Description:**
The system shall provide an AnalysisResult dataclass to encapsulate the complete results of call tree analysis.

**Rationale:**
Analysis results must include the call tree, statistics, circular dependencies, and any errors encountered. This single data structure is passed to generators for output production.

**Acceptance Criteria:**
- [ ] Has field `root_function: str` for starting function name
- [ ] Has field `call_tree: Optional[CallTreeNode]` for root of tree (None if analysis failed)
- [ ] Has field `statistics: AnalysisStatistics` for analysis metrics
- [ ] Has field `circular_dependencies: List[CircularDependency]` defaulting to empty list
- [ ] Has field `errors: List[str]` defaulting to empty list

**Related Requirements:** SWR_MODEL_00012, SWR_MODEL_00017, SWR_MODEL_00019

---

### SWR_MODEL_00022: AnalysisResult Dataclass - Metadata

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The AnalysisResult dataclass shall include metadata fields for analysis context and reproducibility.

**Rationale:**
Analysis results must track when analysis was performed, what source directory was analyzed, and what depth limit was used. This metadata enables result validation and reproducibility.

**Acceptance Criteria:**
- [ ] Has field `timestamp: datetime` defaulting to current time
- [ ] Has field `source_directory: Optional[Path]` defaulting to None
- [ ] Has field `max_depth_limit: int` defaulting to 3

**Related Requirements:** None

---

### SWR_MODEL_00023: AnalysisResult Dataclass - Function Collection

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The AnalysisResult dataclass shall provide `get_all_functions` method to collect all unique functions from the call tree.

**Rationale:**
Generators and validators need access to all functions in the tree for output generation and quality checks. The method delegates to the call tree's implementation.

**Acceptance Criteria:**
- [ ] Returns Set[FunctionInfo] from call_tree.get_all_functions()
- [ ] Raises error if call_tree is None

**Related Requirements:** SWR_MODEL_00015

---

### SWR_MODEL_00024: AnalysisResult Dataclass - Circular Dependency Check

**Priority:** Low
**Status:** Implemented
**Maturity:** accept

**Description:**
The AnalysisResult dataclass shall provide `has_circular_dependencies` method to check if circular dependencies were found.

**Rationale:**
Generators and validators need to know if circular dependencies exist to display warnings or adjust output format. The boolean check is more convenient than checking list length.

**Acceptance Criteria:**
- [ ] Returns True if circular_dependencies list has length > 0
- [ ] Returns False if circular_dependencies list is empty

**Related Requirements:** None

---

### SWR_MODEL_00025: FunctionDict Type Alias

**Priority:** Medium
**Status:** Implemented
**Maturity:** accept

**Description:**
The system shall provide a FunctionDict type alias for mapping function names to lists of FunctionInfo objects.

**Rationale:**
Multiple definitions of the same function (e.g., declarations in headers included in multiple files, plus the actual implementation) are common in C/AUTOSAR codebases. The type alias provides clear semantics for this mapping throughout the codebase.

**Acceptance Criteria:**
- [ ] Type alias is Dict[str, List[FunctionInfo]]
- [ ] Key is function name (e.g., "COM_InitCommunication")
- [ ] Value is list of all FunctionInfo objects with that name
- [ ] Used for function lookup with smart selection strategy

**Related Requirements:** SWR_MODEL_00004

---

## Traceability

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_MODEL_00001 | SWUT_MODEL_00001 | test_SWUT_MODEL_00001_function_type_enum_values | ⏳ Pending |
| SWR_MODEL_00002 | SWUT_MODEL_00002 | test_SWUT_MODEL_00002_parameter_core_fields | ⏳ Pending |
| SWR_MODEL_00003 | SWUT_MODEL_00003 | test_SWUT_MODEL_00003_parameter_str_representation | ⏳ Pending |
| SWR_MODEL_00004 | SWUT_MODEL_00004 | test_SWUT_MODEL_00004_function_info_identity_fields | ⏳ Pending |
| SWR_MODEL_00005 | SWUT_MODEL_00005 | test_SWUT_MODEL_00005_function_info_type_classification | ⏳ Pending |
| SWR_MODEL_00006 | SWUT_MODEL_00006 | test_SWUT_MODEL_00006_function_info_call_relationships | ⏳ Pending |
| SWR_MODEL_00007 | SWUT_MODEL_00007 | test_SWUT_MODEL_00007_function_info_disambiguation_module | ⏳ Pending |
| SWR_MODEL_00008 | SWUT_MODEL_00008 | test_SWUT_MODEL_00008_function_info_hash | ⏳ Pending |
| SWR_MODEL_00009 | SWUT_MODEL_00009 | test_SWUT_MODEL_00009_function_info_equality | ⏳ Pending |
| SWR_MODEL_00010 | SWUT_MODEL_00010 | test_SWUT_MODEL_00010_function_info_signature | ⏳ Pending |
| SWR_MODEL_00011 | SWUT_MODEL_00011 | test_SWUT_MODEL_00011_function_info_rte_detection | ⏳ Pending |
| SWR_MODEL_00012 | SWUT_MODEL_00012 | test_SWUT_MODEL_00012_call_tree_node_structure | ⏳ Pending |
| SWR_MODEL_00013 | SWUT_MODEL_00013 | test_SWUT_MODEL_00013_call_tree_node_state_flags | ⏳ Pending |
| SWR_MODEL_00014 | SWUT_MODEL_00014 | test_SWUT_MODEL_00014_call_tree_node_add_child | ⏳ Pending |
| SWR_MODEL_00015 | SWUT_MODEL_00015 | test_SWUT_MODEL_00015_call_tree_node_get_all_functions | ⏳ Pending |
| SWR_MODEL_00016 | SWUT_MODEL_00016 | test_SWUT_MODEL_00016_call_tree_node_get_max_depth | ⏳ Pending |
| SWR_MODEL_00017 | SWUT_MODEL_00017 | test_SWUT_MODEL_00017_circular_dependency_structure | ⏳ Pending |
| SWR_MODEL_00018 | SWUT_MODEL_00018 | test_SWUT_MODEL_00018_circular_dependency_str | ⏳ Pending |
| SWR_MODEL_00019 | SWUT_MODEL_00019 | test_SWUT_MODEL_00019_analysis_statistics_counters | ⏳ Pending |
| SWR_MODEL_00020 | SWUT_MODEL_00020 | test_SWUT_MODEL_00020_analysis_statistics_to_dict | ⏳ Pending |
| SWR_MODEL_00021 | SWUT_MODEL_00021 | test_SWUT_MODEL_00021_analysis_result_container | ⏳ Pending |
| SWR_MODEL_00022 | SWUT_MODEL_00022 | test_SWUT_MODEL_00022_analysis_result_metadata | ⏳ Pending |
| SWR_MODEL_00023 | SWUT_MODEL_00023 | test_SWUT_MODEL_00023_analysis_result_get_all_functions | ⏳ Pending |
| SWR_MODEL_00024 | SWUT_MODEL_00024 | test_SWUT_MODEL_00024_analysis_result_has_circular_deps | ⏳ Pending |
| SWR_MODEL_00025 | SWUT_MODEL_00025 | test_SWUT_MODEL_00025_function_dict_type_alias | ⏳ Pending |

## Revision History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2026-01-30 | 1.0 | Claude | Initial version - 25 requirements covering all models module components |
