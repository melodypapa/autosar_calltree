# Requirements: IBM Rhapsody Export

## Version History

| Version | Date       | Author         | Description           |
|---------|------------|----------------|-----------------------|
| 1.0     | 2026-02-14 | Development    | Initial requirements  |

## Requirements

### SWR_RH_00001: Rhapsody XMI 2.5 Compatibility

**Priority:** High
**Status:** Implemented

The tool SHALL generate XMI 2.5 compliant documents compatible with IBM Rhapsody 8.0+.

**Rationale:**
- Rhapsody uses XMI 2.1/2.5 format for model interchange
- Ensures compatibility with Rhapsody 8.0 through 10.0.1+
- Enables import via Rhapsody's native XMI import functionality

**Verification:**
- Generated XMI files successfully import into Rhapsody 8.0+
- XMI validation against UML 2.5 schema
- Sequence diagrams render correctly in Rhapsody

**Traceability:**
- Implementation: `src/autosar_calltree/generators/rhapsody_generator.py`
- Tests: `tests/unit/generators/test_rhapsody_generator.py::test_rhapsody_xmi_compatibility`

---

### SWR_RH_00002: Rhapsody Profile Support

**Priority:** High
**Status:** Implemented

The tool SHALL include Rhapsody-specific profile imports in generated XMI files.

**Rationale:**
- Rhapsody uses profiles for extending UML metamodel
- Enables AUTOSAR-specific stereotypes and tagged values
- Required for proper Rhapsody model rendering

**Verification:**
- XMI contains profile application elements
- Profile references point to valid Rhapsody namespaces
- AUTOSAR profile is correctly referenced

**Traceability:**
- Implementation: `RhapsodyXmiGenerator._add_rhapsody_profiles()`
- Tests: `tests/unit/generators/test_rhapsody_generator.py::test_rhapsody_profile_import`

---

### SWR_RH_00003: AUTOSAR Stereotype Support

**Priority:** Medium
**Status:** Implemented

The tool SHALL support AUTOSAR stereotypes for functions and modules.

**Rationale:**
- AUTOSAR modeling requires specific stereotypes (SWC, RunnableEntity, etc.)
- Enables better integration with AUTOSAR development workflows
- Supports automotive industry standards

**Verification:**
- Stereotypes are applied to lifelines and messages
- Stereotype syntax follows UML specification
- Common AUTOSAR stereotypes are supported

**Traceability:**
- Implementation: `RhapsodyXmiGenerator._add_autosar_stereotype()`
- Tests: `tests/unit/generators/test_rhapsody_generator.py::test_autosar_stereotype_generation`

---

### SWR_RH_00004: UUID-based Element IDs

**Priority:** High
**Status:** Implemented

The tool SHALL generate UUID-based element IDs for all XMI elements.

**Rationale:**
- Rhapsody prefers UUID-based IDs over sequential numeric IDs
- Ensures better compatibility with Rhapsody's internal architecture
- Prevents ID collisions when merging models

**Verification:**
- All XMI elements have unique IDs
- IDs follow UUID format with "rhapsody_" prefix
- No duplicate IDs in generated documents

**Traceability:**
- Implementation: `RhapsodyXmiGenerator._generate_id()`
- Tests: `tests/unit/generators/test_rhapsody_generator.py::test_uuid_id_generation`

---

### SWR_RH_00005: Rhapsody-specific Metadata

**Priority:** Medium
**Status:** Implemented

The tool SHALL include Rhapsody-specific tool metadata in XMI documents.

**Rationale:**
- Rhapsody uses metadata for tracking tool information
- Enables proper versioning and change tracking
- Supports Rhapsody's model management features

**Verification:**
- Tool information is included in XMI comments
- Creation timestamp is recorded
- Analysis metadata is preserved

**Traceability:**
- Implementation: `RhapsodyXmiGenerator._add_rhapsody_metadata()`
- Tests: `tests/unit/generators/test_rhapsody_generator.py::test_rhapsody_metadata`

---

### SWR_RH_00006: CLI Integration

**Priority:** High
**Status:** Implemented

The tool SHALL provide `--format rhapsody` CLI option for Rhapsody export.

**Rationale:**
- Consistent with existing `--format mermaid` and `--format xmi` options
- Provides user-friendly interface
- Enables integration into existing workflows

**Verification:**
- `--format rhapsody` option is available
- Generates .xmi files with Rhapsody-compatible content
- Works with all other CLI options (e.g., `--use-module-names`)

**Traceability:**
- Implementation: `src/autosar_calltree/cli/main.py`
- Tests: `tests/integration/test_cli.py` (existing CLI tests)

---

### SWR_RH_00007: Module-level Diagrams

**Priority:** Medium
**Status:** Implemented

The tool SHALL support module-level lifelines when using `--use-module-names`.

**Rationale:**
- AUTOSAR architectures are typically modeled at module level
- Enables higher-level architectural diagrams
- Consistent with existing Mermaid/XMI module-level support

**Verification:**
- Module names appear as lifeline names
- Module-level messages are correctly generated
- Works with `--module-config` option

**Traceability:**
- Implementation: Inherited from `XmiGenerator._collect_participants()`
- Tests: `tests/unit/generators/test_rhapsody_generator.py::test_module_level_diagram`

---

### SWR_RH_00008: Conditional Block Support

**Priority:** High
**Status:** Implemented

The tool SHALL support opt/loop/alt combined fragments in Rhapsody XMI.

**Rationale:**
- AUTOSAR code contains conditional logic and loops
- UML combined fragments are required to represent these constructs
- Consistent with existing Mermaid/XMI support

**Verification:**
- opt blocks are generated for optional calls
- loop blocks are generated for iterative calls
- Combined fragments follow UML 2.5 specification

**Traceability:**
- Implementation: Inherited from `XmiGenerator._create_messages()`
- Tests: `tests/unit/generators/test_rhapsody_generator.py::test_conditional_blocks_rhapsody`

---

### SWR_RH_00009: Cross-platform Compatibility

**Priority:** High
**Status:** Implemented

The Rhapsody export feature SHALL work on all supported platforms (Windows, Linux, macOS).

**Rationale:**
- Users work on various platforms
- XMI file export is platform-independent
- No runtime dependencies required

**Verification:**
- Feature works on Windows
- Feature works on Linux
- Feature works on macOS
- No platform-specific code in implementation

**Traceability:**
- Implementation: Uses only standard library (`xml.etree.ElementTree`)
- Tests: Platform-agnostic unit tests

---

### SWR_RH_00010: Error Handling

**Priority:** High
**Status:** Implemented

The tool SHALL provide clear error messages for Rhapsody export failures.

**Rationale:**
- Users need actionable feedback when exports fail
- Debugging requires specific error information
- Consistent with existing error handling patterns

**Verification:**
- Empty call tree raises `ValueError`
- File I/O errors are properly handled
- Error messages are informative

**Traceability:**
- Implementation: `XmiGenerator.generate()` (inherited)
- Tests: `tests/unit/generators/test_rhapsody_generator.py::test_empty_call_tree_raises_error`

---

### SWR_RH_00011: Test Coverage

**Priority:** High
**Status:** Implemented

The Rhapsody generator SHALL have 80%+ test coverage.

**Rationale:**
- Ensures code quality
- Prevents regressions
- Supports CI/CD quality gates

**Verification:**
- Unit tests cover all public methods
- Unit tests cover edge cases
- Coverage report shows 80%+ coverage

**Traceability:**
- Implementation: `tests/unit/generators/test_rhapsody_generator.py`
- Tests: 20+ test cases covering all requirements

---

### SWR_RH_00012: Documentation

**Priority:** Medium
**Status:** Pending

The tool SHALL include user documentation for Rhapsody export feature.

**Rationale:**
- Users need guidance on using the feature
- Examples help users get started
- Troubleshooting documentation prevents support issues

**Verification:**
- README.md includes Rhapsody export section
- Usage examples are provided
- Troubleshooting guide is available

**Traceability:**
- Implementation: `docs/rhapsody_export.md` (TODO)
- Tests: N/A (documentation verification is manual)

---

### SWR_RH_00013: Rhapsody Version Compatibility

**Priority:** High
**Status:** Implemented

The tool SHALL target Rhapsody 8.0+ compatibility.

**Rationale:**
- Rhapsody 8.0+ is widely used in automotive industry
- UML 2.1 support in Rhapsody 8.0+
- Ensures broad compatibility

**Verification:**
- XMI files import into Rhapsody 8.0
- XMI files import into Rhapsody 10.0.1 (latest)
- No UML 2.5-specific features that break Rhapsody 8.0

**Traceability:**
- Implementation: UML 2.5 core profile (backward compatible)
- Tests: Manual import testing (skip if Rhapsody unavailable)

---

### SWR_RH_00014: Code Reuse

**Priority:** Medium
**Status:** Implemented

The Rhapsody generator SHALL extend XmiGenerator to maximize code reuse.

**Rationale:**
- Reduces maintenance burden
- Ensures consistency between XMI generators
- Leverages existing 521-line XMI infrastructure

**Verification:**
- `RhapsodyXmiGenerator` extends `XmiGenerator`
- Only Rhapsody-specific code is in subclass
- Common functionality is inherited

**Traceability:**
- Implementation: `class RhapsodyXmiGenerator(XmiGenerator)`
- Tests: `tests/unit/generators/test_rhapsody_generator.py::test_inherits_from_xmi_generator`

---

### SWR_RH_00015: No Runtime Dependencies

**Priority:** High
**Status:** Implemented

The Rhapsody export SHALL not require additional runtime dependencies.

**Rationale:**
- Keeps installation simple
- Reduces dependency conflicts
- Leverages existing XML infrastructure

**Verification:**
- Uses only Python standard library
- No additional packages in `pyproject.toml`
- Feature works with core installation

**Traceability:**
- Implementation: Uses `xml.etree.ElementTree` (standard library)
- Tests: N/A

---

### SWR_RH_00016: Performance

**Priority:** Low
**Status:** Implemented

The Rhapsody export SHALL complete within reasonable time for typical call trees.

**Rationale:**
- Users expect fast export times
- Large codebases should be handled efficiently
- Consistent with existing Mermaid/XMI performance

**Verification:**
- 100-function call tree exports in < 1 second
- 1000-function call tree exports in < 5 seconds
- Memory usage is reasonable

**Traceability:**
- Implementation: Same performance as `XmiGenerator`
- Tests: Performance benchmarks (optional)

---

### SWR_RH_00017: File Output

**Priority:** High
**Status:** Implemented

The tool SHALL create output directories if they don't exist.

**Rationale:**
- Users shouldn't need to manually create directories
- Consistent with existing Mermaid/XMI behavior
- Improves user experience

**Verification:**
- Nested directories are created automatically
- No errors when output directory doesn't exist
- File permissions are correct

**Traceability:**
- Implementation: `XmiGenerator.generate()` (inherited)
- Tests: `tests/unit/generators/test_rhapsody_generator.py::test_output_directory_creation`

---

### SWR_RH_00018: Message Signatures

**Priority:** Medium
**Status:** Implemented

The tool SHALL include function parameter information in message signatures.

**Rationale:**
- Improves diagram readability
- Provides complete function signature information
- Consistent with existing Mermaid/XMI behavior

**Verification:**
- Parameters appear in message signatures
- Pointer types are indicated
- Complex types are handled correctly

**Traceability:**
- Implementation: `XmiGenerator._format_message_signature()` (inherited)
- Tests: `tests/unit/generators/test_rhapsody_generator.py::test_parameter_handling`

---

### SWR_RH_00019: Recursive Call Handling

**Priority:** Medium
**Status:** Implemented

The tool SHALL handle recursive calls correctly in Rhapsody XMI.

**Rationale:**
- AUTOSAR code contains recursive functions
- Recursive calls need special handling
- Consistent with existing Mermaid/XMI behavior

**Verification:**
- Recursive calls are marked appropriately
- No infinite loops in generation
- Rhapsody imports recursive diagrams correctly

**Traceability:**
- Implementation: `XmiGenerator._create_messages()` (inherited)
- Tests: `tests/unit/generators/test_rhapsody_generator.py::test_recursive_call_handling`

---

### SWR_RH_00020: Integration with Existing Features

**Priority:** High
**Status:** Implemented

The Rhapsody export SHALL integrate seamlessly with existing CLI features.

**Rationale:**
- Users expect consistent behavior across formats
- All CLI options should work with Rhapsody
- No breaking changes to existing workflows

**Verification:**
- Works with `--max-depth`
- Works with `--module-config` and `--use-module-names`
- Works with `--verbose`
- Works with `--format both`

**Traceability:**
- Implementation: CLI integration in `src/autosar_calltree/cli/main.py`
- Tests: Existing integration tests cover all options
