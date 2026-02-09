# Requirements Traceability Matrix

This document traces the mapping between requirements (SWR_*) and tests (SWUT_*).

## Overview

| Module | Requirements | Tests | Status |
|--------|-------------|-------|--------|
| Models | SWR_MODEL_00001-00028 (28) | SWUT_MODEL_00001-00028 (28) | ✅ Complete (100% coverage) |
| AUTOSAR Parser | SWR_PARSER_AUTOSAR_00001-00015 (15) | SWUT_PARSER_AUTOSAR_00001-00015 (15) | ✅ Complete (97% coverage) |
| C Parser | SWR_PARSER_C_00001-00023 (23) | SWUT_PARSER_C_00001-00026 (26) | ✅ Complete (86% coverage) |
| Database | SWR_DB_00001-00025 (25) | SWUT_DB_00001-00021 (21) | ✅ Complete (80% coverage) |
| Analyzers | SWR_ANALYZER_00001-00020 (20) | SWUT_ANALYZER_00001-00020 (20) | ✅ Complete (94% coverage) |
| Config | SWR_CONFIG_00001-00010 (10) | SWUT_CONFIG_00001-00025 (25) | ✅ Complete (97% coverage) |
| Generators | SWR_GENERATOR_00001-00048 (48) | SWUT_GENERATOR_00001-00048 (48) | ✅ Complete (89% coverage) |
| CLI | SWR_CLI_00001-00014 (14) | SWUT_CLI_00001-00014 (14) | ✅ Complete (integration tests) |
| E2E | SWR_E2E_00001-00018 (18) | SWUT_E2E_00001-00018 (18) | ✅ Complete (integration tests) |
| XMI | SWR_XMI_00001-00003 (3) | SWUT_XMI_00001-00003 (3) | ✅ Complete (70% coverage) |

---

## Models Module

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_MODEL_00001 | SWUT_MODEL_00001 | test_SWUT_MODEL_00001_function_type_enum_values | ✅ Pass |
| SWR_MODEL_00002 | SWUT_MODEL_00002 | test_SWUT_MODEL_00002_parameter_core_fields | ✅ Pass |
| SWR_MODEL_00003 | SWUT_MODEL_00003 | test_SWUT_MODEL_00003_parameter_string_representation | ✅ Pass |
| SWR_MODEL_00004 | SWUT_MODEL_00004 | test_SWUT_MODEL_00004_function_info_core_fields | ✅ Pass |
| SWR_MODEL_00005 | SWUT_MODEL_00005 | test_SWUT_MODEL_00005_function_info_type_classification | ✅ Pass |
| SWR_MODEL_00006 | SWUT_MODEL_00006 | test_SWUT_MODEL_00006_function_info_call_relationships | ✅ Pass |
| SWR_MODEL_00007 | SWUT_MODEL_00007 | test_SWUT_MODEL_00007_function_info_disambiguation | ✅ Pass |
| SWR_MODEL_00008 | SWUT_MODEL_00008 | test_SWUT_MODEL_00008_function_info_hash | ✅ Pass |
| SWR_MODEL_00009 | SWUT_MODEL_00009 | test_SWUT_MODEL_00009_function_info_equality | ✅ Pass |
| SWR_MODEL_00010 | SWUT_MODEL_00010 | test_SWUT_MODEL_00010_function_info_signature_generation | ✅ Pass |
| SWR_MODEL_00011 | SWUT_MODEL_00011 | test_SWUT_MODEL_00011_function_info_rte_detection | ✅ Pass |
| SWR_MODEL_00012 | SWUT_MODEL_00012 | test_SWUT_MODEL_00012_call_tree_node_core_structure | ✅ Pass |
| SWR_MODEL_00013 | SWUT_MODEL_00013 | test_SWUT_MODEL_00013_call_tree_node_state_flags | ✅ Pass |
| SWR_MODEL_00014 | SWUT_MODEL_00014 | test_SWUT_MODEL_00014_call_tree_node_tree_manipulation | ✅ Pass |
| SWR_MODEL_00015 | SWUT_MODEL_00015 | test_SWUT_MODEL_00015_call_tree_node_function_collection | ✅ Pass |
| SWR_MODEL_00016 | SWUT_MODEL_00016 | test_SWUT_MODEL_00016_call_tree_node_depth_calculation | ✅ Pass |
| SWR_MODEL_00017 | SWUT_MODEL_00017 | test_SWUT_MODEL_00017_circular_dependency_structure | ✅ Pass |
| SWR_MODEL_00018 | SWUT_MODEL_00018 | test_SWUT_MODEL_00018_circular_dependency_string_representation | ✅ Pass |
| SWR_MODEL_00019 | SWUT_MODEL_00019 | test_SWUT_MODEL_00019_analysis_statistics_counters | ✅ Pass |
| SWR_MODEL_00020 | SWUT_MODEL_00020 | test_SWUT_MODEL_00020_analysis_statistics_dict_conversion | ✅ Pass |
| SWR_MODEL_00021 | SWUT_MODEL_00021 | test_SWUT_MODEL_00021_analysis_result_container | ✅ Pass |
| SWR_MODEL_00022 | SWUT_MODEL_00022 | test_SWUT_MODEL_00022_analysis_result_metadata | ✅ Pass |
| SWR_MODEL_00023 | SWUT_MODEL_00023 | test_SWUT_MODEL_00023_analysis_result_function_collection | ✅ Pass |
| SWR_MODEL_00024 | SWUT_MODEL_00024 | test_SWUT_MODEL_00024_analysis_result_circular_check | ✅ Pass |
| SWR_MODEL_00025 | SWUT_MODEL_00025 | test_SWUT_MODEL_00025_function_dict_type_alias | ✅ Pass |
| SWR_MODEL_00026 | SWUT_MODEL_00026 | test_SWUT_MODEL_00026_function_call_conditional_tracking | ✅ Pass |
| SWR_MODEL_00027 | SWUT_MODEL_00027 | test_SWUT_MODEL_00027_function_call_string_representation | ✅ Pass |
| SWR_MODEL_00028 | SWUT_MODEL_00028 | test_SWUT_MODEL_00028_call_tree_node_optional_tracking | ✅ Pass |

---

## C Parser Multi-line Support Module

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_PARSER_C_00021 | SWUT_PARSER_C_00021 | test_SWUT_PARSER_C_00021_multiline_function_prototype | ✅ Pass |
| SWR_PARSER_C_00022 | SWUT_PARSER_C_00022 | test_SWUT_PARSER_C_00022_multiline_if_condition | ✅ Pass |

---

## C Parser Loop Support Module

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_PARSER_C_00023 | SWUT_PARSER_C_00023 | test_loop_detection_for | ✅ Pass |
| SWR_PARSER_C_00023 | SWUT_PARSER_C_00024 | test_loop_detection_while | ✅ Pass |
| SWR_PARSER_C_00023 | SWUT_PARSER_C_00025 | test_loop_multiple_calls | ✅ Pass |
| SWR_PARSER_C_00023 | SWUT_PARSER_C_00026 | test_loop_with_condition | ✅ Pass |

---

## Mermaid Opt Blocks Module

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_MERMAID_00004 | SWUT_GENERATOR_00032 | test_SWUT_GENERATOR_00032_opt_block_generation | ✅ Pass |
| SWR_MERMAID_00004 | SWUT_GENERATOR_00033 | test_SWUT_GENERATOR_00033_multiple_optional_calls | ✅ Pass |
| SWR_MERMAID_00004 | SWUT_GENERATOR_00034 | test_SWUT_GENERATOR_00034_mixed_optional_and_regular | ✅ Pass |
| SWR_MERMAID_00004 | SWUT_GENERATOR_00035 | test_SWUT_GENERATOR_00035_nested_optional | ✅ Pass |
| SWR_MERMAID_00004 | SWUT_GENERATOR_00036 | test_SWUT_GENERATOR_00036_recursive_not_opt | ✅ Pass |
| SWR_MERMAID_00004 | SWUT_GENERATOR_00037 | test_SWUT_GENERATOR_00037_optional_with_returns | ✅ Pass |
| SWR_MERMAID_00004 | SWUT_GENERATOR_00038 | test_SWUT_GENERATOR_00038_optional_function_mode | ✅ Pass |

---

## Mermaid Loop Blocks Module

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_MERMAID_00005 | SWUT_GENERATOR_00039 | test_SWUT_GENERATOR_00039_loop_block_generation | ✅ Pass |
| SWR_MERMAID_00005 | SWUT_GENERATOR_00040 | test_SWUT_GENERATOR_00040_multiple_loop_calls | ✅ Pass |
| SWR_MERMAID_00005 | SWUT_GENERATOR_00041 | test_SWUT_GENERATOR_00041_mixed_loop_and_optional | ✅ Pass |

---

## XMI Generator Module

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_XMI_00001 | SWUT_XMI_00001 | test_SWUT_XMI_00001_xmi_namespace_compliance | ✅ Pass |
| SWR_XMI_00002 | SWUT_XMI_00002 | test_SWUT_XMI_00002_sequence_diagram_representation | ✅ Pass |
| SWR_XMI_00003 | SWUT_XMI_00003 | test_SWUT_XMI_00003_opt_block_support | ✅ Pass |

---

## Generator Module (Existing Tests)

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_GENERATOR_00001 | SWUT_GENERATOR_00001 | test_SWUT_GENERATOR_00001_initialization | ✅ Pass |
| SWR_GENERATOR_00002 | SWUT_GENERATOR_00002 | test_SWUT_GENERATOR_00002_mermaid_header | ✅ Pass |
| SWR_GENERATOR_00003 | SWUT_GENERATOR_00003 | test_SWUT_GENERATOR_00003_collect_participants_functions | ✅ Pass |
| SWR_GENERATOR_00004 | SWUT_GENERATOR_00004 | test_SWUT_GENERATOR_00004_collect_participants_modules | ✅ Pass |
| SWR_GENERATOR_00005 | SWUT_GENERATOR_00005 | test_SWUT_GENERATOR_00005_module_fallback_to_filename | ✅ Pass |
| SWR_GENERATOR_00006 | SWUT_GENERATOR_00006 | test_SWUT_GENERATOR_00006_rte_abbreviation | ✅ Pass |
| SWR_GENERATOR_00007 | SWUT_GENERATOR_00007 | test_SWUT_GENERATOR_00007_rte_abbreviation_disabled | ✅ Pass |
| SWR_GENERATOR_00008 | SWUT_GENERATOR_00008 | test_SWUT_GENERATOR_00008_short_rte_not_abbreviated | ✅ Pass |
| SWR_GENERATOR_00009 | SWUT_GENERATOR_00009 | test_SWUT_GENERATOR_00009_sequence_calls_function_mode | ✅ Pass |
| SWR_GENERATOR_00010 | SWUT_GENERATOR_00010 | test_SWUT_GENERATOR_00010_sequence_calls_module_mode | ✅ Pass |
| SWR_GENERATOR_00011 | SWUT_GENERATOR_00011 | test_SWUT_GENERATOR_00011_parameters_on_arrows | ✅ Pass |
| SWR_GENERATOR_00012 | SWUT_GENERATOR_00012 | test_SWUT_GENERATOR_00012_multiple_parameters | ✅ Pass |
| SWR_GENERATOR_00013 | SWUT_GENERATOR_00013 | test_SWUT_GENERATOR_00013_recursive_call_handling | ✅ Pass |
| SWR_GENERATOR_00014 | SWUT_GENERATOR_00014 | test_SWUT_GENERATOR_00014_return_statements | ✅ Pass |
| SWR_GENERATOR_00015 | SWUT_GENERATOR_00015 | test_SWUT_GENERATOR_00015_returns_disabled_default | ✅ Pass |
| SWR_GENERATOR_00016 | SWUT_GENERATOR_00016 | test_SWUT_GENERATOR_00016_function_table_format | ✅ Pass |
| SWR_GENERATOR_00017 | SWUT_GENERATOR_00017 | test_SWUT_GENERATOR_00017_function_table_module_column | ✅ Pass |
| SWR_GENERATOR_00018 | SWUT_GENERATOR_00018 | test_SWUT_GENERATOR_00018_function_table_na_for_unmapped | ✅ Pass |
| SWR_GENERATOR_00019 | SWUT_GENERATOR_00019 | test_SWUT_GENERATOR_00019_parameter_formatting_table | ✅ Pass |
| SWR_GENERATOR_00020 | SWUT_GENERATOR_00020 | test_SWUT_GENERATOR_00020_void_parameters | ✅ Pass |
| SWR_GENERATOR_00021 | SWUT_GENERATOR_00021 | test_SWUT_GENERATOR_00021_parameter_formatting_diagram | ✅ Pass |
| SWR_GENERATOR_00022 | SWUT_GENERATOR_00022 | test_SWUT_GENERATOR_00022_text_tree_generation | ✅ Pass |
| SWR_GENERATOR_00023 | SWUT_GENERATOR_00023 | test_SWUT_GENERATOR_00023_circular_dependencies_section | ✅ Pass |
| SWR_GENERATOR_00024 | SWUT_GENERATOR_00024 | test_SWUT_GENERATOR_00024_metadata_generation | ✅ Pass |
| SWR_GENERATOR_00025 | SWUT_GENERATOR_00025 | test_SWUT_GENERATOR_00025_file_output_generation | ✅ Pass |
| SWR_GENERATOR_00026 | SWUT_GENERATOR_00026 | test_SWUT_GENERATOR_00026_string_output_generation | ✅ Pass |
| SWR_GENERATOR_00027 | SWUT_GENERATOR_00027 | test_SWUT_GENERATOR_00027_empty_call_tree_error | ✅ Pass |
| SWR_GENERATOR_00028 | SWUT_GENERATOR_00028 | test_SWUT_GENERATOR_00028_optional_sections | ✅ Pass |
| SWR_GENERATOR_00029 | SWUT_GENERATOR_00029 | test_SWUT_GENERATOR_00029_unique_functions_in_table | ✅ Pass |
| SWR_GENERATOR_00030 | SWUT_GENERATOR_00030 | test_SWUT_GENERATOR_00030_sorted_function_table | ✅ Pass |
| SWR_GENERATOR_00031 | SWUT_GENERATOR_00031 | test_SWUT_GENERATOR_00031_parent_directory_creation | ✅ Pass |

---

## Summary

- **Total Requirements**: 173 requirements across 10 modules
- **Total Tests**: 307 tests
- **Overall Coverage**: 86%
- **Passing Tests**: 307/307 (100%)

## Recent Updates

- **2026-02-09**: Added loop detection requirements (SWR_PARSER_C_00023) with 4 tests
- **2026-02-09**: Added loop block generation requirements (SWR_MERMAID_00005) with 3 tests
- **2026-02-04**: Added FunctionCall model requirements (SWR_MODEL_00026-00028)
- **2026-02-04**: Added Mermaid opt blocks requirements (SWR_MERMAID_00004)
- **2026-02-04**: Added XMI generator requirements (SWR_XMI_00001-00003) with opt block support
- **2026-02-04**: Added 7 new tests for opt block generation (SWUT_GENERATOR_00032-00038)
- **2026-02-04**: Added 3 new tests for XMI generation (SWUT_XMI_00001-00003)

## Recent Updates

- **2026-02-09**: Added multi-line support requirements (SWR_PARSER_C_00021-00022)
- **2026-02-09**: Added 2 new tests for multi-line parsing (SWUT_PARSER_C_00021-00022)
- **2026-02-04**: Added FunctionCall model requirements (SWR_MODEL_00026-00028)
- **2026-02-04**: Added Mermaid opt blocks requirements (SWR_MERMAID_00004)
- **2026-02-04**: Added XMI generator requirements (SWR_XMI_00001-00003) with opt block support
- **2026-02-04**: Added 7 new tests for opt block generation (SWUT_GENERATOR_00032-00038)
- **2026-02-04**: Added 3 new tests for XMI generation (SWUT_XMI_00001-00003)