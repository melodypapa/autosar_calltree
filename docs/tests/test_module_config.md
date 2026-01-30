# Module Configuration Test Cases

## Overview
This document describes the test cases for the Module Configuration module (module_config.py).

## Requirements Summary

| ID | Title | Priority |
|----|-------|----------|
| SWR_CONFIG_00001 | YAML Configuration File Support | High |
| SWR_CONFIG_00002 | Module Configuration Validation | High |
| SWR_CONFIG_00003 | Specific File Mappings | High |
| SWR_CONFIG_00004 | Pattern Mappings with Glob | High |
| SWR_CONFIG_00005 | Default Module Assignment | Medium |
| SWR_CONFIG_00006 | Lookup Caching | Medium |
| SWR_CONFIG_00007 | Module Lookup by File Path | High |
| SWR_CONFIG_00008 | Configuration Validation | Medium |
| SWR_CONFIG_00009 | Configuration Statistics | Low |
| SWR_CONFIG_00010 | Empty Configuration Handling | Medium |

## Test Cases

### SWUT_CONFIG_00001: Configuration File Loading

**Requirement:** SWR_CONFIG_00001
**Priority:** High
**Status:** Implemented

**Description:**
Verify that the ModuleConfig class can successfully load a valid YAML configuration file.

**Test Function:** `test_SWUT_CONFIG_00001_load_valid_config()`

**Test Setup:**
```python
config_path = Path("fixtures/valid_module_config.yaml")
config_content = """
version: "1.0"
file_mappings:
  demo.c: DemoModule
  main.c: Application
pattern_mappings:
  "hw_*.c": HardwareModule
default_module: "Other"
"""
```

**Test Execution:**
```python
config = ModuleConfig(config_path)
assert config.specific_mappings == {"demo.c": "DemoModule", "main.c": "Application"}
assert len(config.pattern_mappings) == 1
assert config.default_module == "Other"
```

**Expected Result:**
Configuration loads successfully with all mappings populated.

**Edge Cases Covered:**
- Valid YAML with all sections
- Mix of file_mappings and pattern_mappings
- Optional default_module

---

### SWUT_CONFIG_00002: Missing Configuration File

**Requirement:** SWR_CONFIG_00001
**Priority:** High
**Status:** Implemented

**Description:**
Verify that FileNotFoundError is raised when configuration file doesn't exist.

**Test Function:** `test_SWUT_CONFIG_00002_missing_config_file()`

**Test Setup:**
```python
config_path = Path("/nonexistent/path/config.yaml")
```

**Test Execution:**
```python
with pytest.raises(FileNotFoundError, match="Configuration file not found"):
    config = ModuleConfig(config_path)
```

**Expected Result:**
FileNotFoundError raised with clear message.

---

### SWUT_CONFIG_00003: Invalid YAML Format

**Requirement:** SWR_CONFIG_00002
**Priority:** High
**Status:** Implemented

**Description:**
Verify that ValueError is raised for malformed YAML.

**Test Function:** `test_SWUT_CONFIG_00003_invalid_yaml()`

**Test Setup:**
```python
config_content = """
file_mappings:
  demo.c: DemoModule
    invalid_indentation: value
"""
```

**Test Execution:**
```python
with pytest.raises((ValueError, yaml.YAMLError)):
    config = ModuleConfig(config_path)
```

**Expected Result:**
ValueError raised for malformed YAML.

---

### SWUT_CONFIG_00004: Non-Dictionary Root

**Requirement:** SWR_CONFIG_00002
**Priority:** High
**Status:** Implemented

**Description:**
Verify that ValueError is raised when root element is not a dictionary.

**Test Function:** `test_SWUT_CONFIG_00004_invalid_root_type()`

**Test Setup:**
```python
config_content = "- item1\n- item2\n"  # List instead of dict
```

**Test Execution:**
```python
with pytest.raises(ValueError, match="expected dictionary at root level"):
    config = ModuleConfig(config_path)
```

**Expected Result:**
ValueError raised with clear message.

---

### SWUT_CONFIG_00005: Invalid File Mappings Type

**Requirement:** SWR_CONFIG_00002
**Priority:** High
**Status:** Implemented

**Description:**
Verify that ValueError is raised when file_mappings is not a dictionary.

**Test Function:** `test_SWUT_CONFIG_00005_invalid_file_mappings_type()`

**Test Setup:**
```python
config_content = """
file_mappings:
  - demo.c
  - main.c
"""
```

**Test Execution:**
```python
with pytest.raises(ValueError, match="'file_mappings' must be a dictionary"):
    config = ModuleConfig(config_path)
```

**Expected Result:**
ValueError raised.

---

### SWUT_CONFIG_00006: Empty Module Names in File Mappings

**Requirement:** SWR_CONFIG_00002
**Priority:** High
**Status:** Implemented

**Description:**
Verify that ValueError is raised when module names are empty strings.

**Test Function:** `test_SWUT_CONFIG_00006_empty_module_name_file_mappings()`

**Test Setup:**
```python
config_content = """
file_mappings:
  demo.c: ""
  main.c: "   "
"""
```

**Test Execution:**
```python
with pytest.raises(ValueError, match="Module name cannot be empty"):
    config = ModuleConfig(config_path)
```

**Expected Result:**
ValueError raised indicating empty module name.

---

### SWUT_CONFIG_00007: Non-String File Mapping Values

**Requirement:** SWR_CONFIG_00002
**Priority:** High
**Status:** Implemented

**Description:**
Verify that ValueError is raised for non-string mapping values.

**Test Function:** `test_SWUT_CONFIG_00007_non_string_file_mappings()`

**Test Setup:**
```python
config_content = """
file_mappings:
  demo.c: 123
  main.c:
    nested: value
"""
```

**Test Execution:**
```python
with pytest.raises(ValueError, match="File mappings must be strings"):
    config = ModuleConfig(config_path)
```

**Expected Result:**
ValueError raised.

---

### SWUT_CONFIG_00008: Pattern Mappings Compilation

**Requirement:** SWR_CONFIG_00004
**Priority:** High
**Status:** Implemented

**Description:**
Verify that glob patterns are correctly compiled to regex patterns.

**Test Function:** `test_SWUT_CONFIG_00008_pattern_compilation()`

**Test Setup:**
```python
config_content = """
pattern_mappings:
  "hw_*.c": HardwareModule
  "sw_*.c": SoftwareModule
  "com_*.c": CommunicationModule
"""
```

**Test Execution:**
```python
config = ModuleConfig(config_path)
assert len(config.pattern_mappings) == 3
# Each pattern should be a tuple of (compiled_regex, module_name)
for pattern, module in config.pattern_mappings:
    assert hasattr(pattern, "match")  # Regex object
    assert isinstance(module, str)
```

**Expected Result:**
All patterns compiled to regex objects.

---

### SWUT_CONFIG_00009: Invalid Pattern Mappings Type

**Requirement:** SWR_CONFIG_00002
**Priority:** High
**Status:** Implemented

**Description:**
Verify that ValueError is raised when pattern_mappings is not a dictionary.

**Test Function:** `test_SWUT_CONFIG_00009_invalid_pattern_mappings_type()`

**Test Setup:**
```python
config_content = """
pattern_mappings:
  - "hw_*.c"
  - "sw_*.c"
"""
```

**Test Execution:**
```python
with pytest.raises(ValueError, match="'pattern_mappings' must be a dictionary"):
    config = ModuleConfig(config_path)
```

**Expected Result:**
ValueError raised.

---

### SWUT_CONFIG_00010: Empty Module Names in Pattern Mappings

**Requirement:** SWR_CONFIG_00002
**Priority:** High
**Status:** Implemented

**Description:**
Verify that ValueError is raised when pattern module names are empty.

**Test Function:** `test_SWUT_CONFIG_00010_empty_module_name_pattern_mappings()`

**Test Setup:**
```python
config_content = """
pattern_mappings:
  "hw_*.c": ""
"""
```

**Test Execution:**
```python
with pytest.raises(ValueError, match="Module name cannot be empty"):
    config = ModuleConfig(config_path)
```

**Expected Result:**
ValueError raised.

---

### SWUT_CONFIG_00011: Default Module Assignment

**Requirement:** SWR_CONFIG_00005
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that default_module is correctly loaded when specified.

**Test Function:** `test_SWUT_CONFIG_00011_default_module()`

**Test Setup:**
```python
config_content = """
default_module: "Other"
"""
```

**Test Execution:**
```python
config = ModuleConfig(config_path)
assert config.default_module == "Other"
```

**Expected Result:**
Default module correctly stored.

---

### SWUT_CONFIG_00012: Invalid Default Module Type

**Requirement:** SWR_CONFIG_00002
**Priority:** High
**Status:** Implemented

**Description:**
Verify that ValueError is raised when default_module is not a string.

**Test Function:** `test_SWUT_CONFIG_00012_invalid_default_module_type()`

**Test Setup:**
```python
config_content = """
default_module: 123
"""
```

**Test Execution:**
```python
with pytest.raises(ValueError, match="'default_module' must be a non-empty string"):
    config = ModuleConfig(config_path)
```

**Expected Result:**
ValueError raised.

---

### SWUT_CONFIG_00013: Empty Default Module

**Requirement:** SWR_CONFIG_00002
**Priority:** High
**Status:** Implemented

**Description:**
Verify that ValueError is raised when default_module is whitespace only.

**Test Function:** `test_SWUT_CONFIG_00013_empty_default_module()`

**Test Setup:**
```python
config_content = """
default_module: "   "
"""
```

**Test Execution:**
```python
with pytest.raises(ValueError, match="'default_module' must be a non-empty string"):
    config = ModuleConfig(config_path)
```

**Expected Result:**
ValueError raised.

---

### SWUT_CONFIG_00014: Specific File Mapping Lookup

**Requirement:** SWR_CONFIG_00007
**Priority:** High
**Status:** Implemented

**Description:**
Verify that get_module_for_file returns correct module for exact filename match.

**Test Function:** `test_SWUT_CONFIG_00014_specific_file_lookup()`

**Test Setup:**
```python
config_content = """
file_mappings:
  demo.c: DemoModule
  main.c: Application
"""
config = ModuleConfig(config_path)
file_path = Path("/some/path/to/demo.c")
```

**Test Execution:**
```python
module = config.get_module_for_file(file_path)
assert module == "DemoModule"
```

**Expected Result:**
Returns "DemoModule" for demo.c file.

**Edge Cases Covered:**
- Path with directories (should only use filename)
- Exact match
- Case sensitivity

---

### SWUT_CONFIG_00015: Pattern Mapping Lookup

**Requirement:** SWR_CONFIG_00004, SWR_CONFIG_00007
**Priority:** High
**Status:** Implemented

**Description:**
Verify that get_module_for_file matches glob patterns correctly.

**Test Function:** `test_SWUT_CONFIG_00015_pattern_lookup()`

**Test Setup:**
```python
config_content = """
pattern_mappings:
  "hw_*.c": HardwareModule
  "sw_*.c": SoftwareModule
"""
config = ModuleConfig(config_path)
```

**Test Execution:**
```python
assert config.get_module_for_file(Path("hw_driver.c")) == "HardwareModule"
assert config.get_module_for_file(Path("hw_init.c")) == "HardwareModule"
assert config.get_module_for_file(Path("sw_component.c")) == "SoftwareModule"
assert config.get_module_for_file(Path("sw_handler.c")) == "SoftwareModule"
```

**Expected Result:**
Pattern matching works with wildcards.

---

### SWUT_CONFIG_00016: Specific Mapping Takes Precedence Over Pattern

**Requirement:** SWR_CONFIG_00003
**Priority:** High
**Status:** Implemented

**Description:**
Verify that specific file mappings take precedence over pattern mappings.

**Test Function:** `test_SWUT_CONFIG_00016_specific_overrides_pattern()`

**Test Setup:**
```python
config_content = """
file_mappings:
  hw_driver.c: SpecialModule
pattern_mappings:
  "hw_*.c": HardwareModule
"""
config = ModuleConfig(config_path)
```

**Test Execution:**
```python
# hw_driver.c matches both specific and pattern
module = config.get_module_for_file(Path("hw_driver.c"))
assert module == "SpecialModule"  # Specific wins
# hw_init.c only matches pattern
module = config.get_module_for_file(Path("hw_init.c"))
assert module == "HardwareModule"
```

**Expected Result:**
Specific mappings take precedence.

---

### SWUT_CONFIG_00017: Default Module Fallback

**Requirement:** SWR_CONFIG_00005, SWR_CONFIG_00007
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that default module is returned when no specific or pattern matches.

**Test Function:** `test_SWUT_CONFIG_00017_default_module_fallback()`

**Test Setup:**
```python
config_content = """
file_mappings:
  demo.c: DemoModule
default_module: "Other"
"""
config = ModuleConfig(config_path)
```

**Test Execution:**
```python
assert config.get_module_for_file(Path("demo.c")) == "DemoModule"
assert config.get_module_for_file(Path("unmapped.c")) == "Other"
assert config.get_module_for_file(Path("unknown.h")) == "Other"
```

**Expected Result:**
Default module used for unmapped files.

---

### SWUT_CONFIG_00018: No Match Returns None

**Requirement:** SWR_CONFIG_00007
**Priority:** High
**Status:** Implemented

**Description:**
Verify that get_module_for_file returns None when no match and no default.

**Test Function:** `test_SWUT_CONFIG_00018_no_match_returns_none()`

**Test Setup:**
```python
config_content = """
file_mappings:
  demo.c: DemoModule
"""
config = ModuleConfig(config_path)
```

**Test Execution:**
```python
assert config.get_module_for_file(Path("unmapped.c")) is None
assert config.get_module_for_file(Path("unknown.h")) is None
```

**Expected Result:**
None returned for unmapped files without default.

---

### SWUT_CONFIG_00019: Lookup Caching

**Requirement:** SWR_CONFIG_00006
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that lookup results are cached for performance.

**Test Function:** `test_SWUT_CONFIG_00019_lookup_caching()`

**Test Setup:**
```python
config_content = """
file_mappings:
  demo.c: DemoModule
"""
config = ModuleConfig(config_path)
file_path = Path("demo.c")
```

**Test Execution:**
```python
# First lookup
module1 = config.get_module_for_file(file_path)
assert "demo.c" in config._lookup_cache

# Second lookup should use cache
module2 = config.get_module_for_file(file_path)
assert module1 == module2
assert config._lookup_cache["demo.c"] == "DemoModule"
```

**Expected Result:**
Subsequent lookups use cached value.

---

### SWUT_CONFIG_00020: Cache Stores None Results

**Requirement:** SWR_CONFIG_00006
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that cache stores None for unmapped files.

**Test Function:** `test_SWUT_CONFIG_00020_cache_stores_none()`

**Test Setup:**
```python
config = ModuleConfig()  # Empty config
file_path = Path("unmapped.c")
```

**Test Execution:**
```python
# First lookup
module1 = config.get_module_for_file(file_path)
assert module1 is None
assert "unmapped.c" in config._lookup_cache
assert config._lookup_cache["unmapped.c"] is None

# Second lookup also returns None (from cache)
module2 = config.get_module_for_file(file_path)
assert module2 is None
```

**Expected Result:**
Cache stores None for no-match results.

---

### SWUT_CONFIG_00021: Configuration Validation Success

**Requirement:** SWR_CONFIG_00008
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that validate_config returns empty list for valid configuration.

**Test Function:** `test_SWUT_CONFIG_00021_validate_success()`

**Test Setup:**
```python
config_content = """
file_mappings:
  demo.c: DemoModule
pattern_mappings:
  "hw_*.c": HardwareModule
"""
config = ModuleConfig(config_path)
```

**Test Execution:**
```python
errors = config.validate_config()
assert errors == []
```

**Expected Result:**
Empty error list for valid config.

---

### SWUT_CONFIG_00022: Configuration Validation Failure

**Requirement:** SWR_CONFIG_00008
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that validate_config detects empty configuration.

**Test Function:** `test_SWUT_CONFIG_00022_validate_empty_config()`

**Test Setup:**
```python
config_content = "{}"
config = ModuleConfig(config_path)
```

**Test Execution:**
```python
errors = config.validate_config()
assert len(errors) > 0
assert "must contain either" in errors[0]
```

**Expected Result:**
Error list contains validation messages.

---

### SWUT_CONFIG_00023: Configuration Statistics

**Requirement:** SWR_CONFIG_00009
**Priority:** Low
**Status:** Implemented

**Description:**
Verify that get_statistics returns correct counts.

**Test Function:** `test_SWUT_CONFIG_00023_statistics()`

**Test Setup:**
```python
config_content = """
file_mappings:
  demo.c: DemoModule
  main.c: Application
pattern_mappings:
  "hw_*.c": HardwareModule
  "sw_*.c": SoftwareModule
default_module: "Other"
"""
config = ModuleConfig(config_path)
```

**Test Execution:**
```python
stats = config.get_statistics()
assert stats["specific_file_mappings"] == 2
assert stats["pattern_mappings"] == 2
assert stats["has_default_module"] == 1
```

**Expected Result:**
Statistics reflect configuration content.

---

### SWUT_CONFIG_00024: Empty Configuration Initialization

**Requirement:** SWR_CONFIG_00010
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that ModuleConfig can be initialized without a config file.

**Test Function:** `test_SWUT_CONFIG_00024_empty_initialization()`

**Test Setup:**
```python
config = ModuleConfig()  # No config_path
```

**Test Execution:**
```python
assert config.specific_mappings == {}
assert config.pattern_mappings == []
assert config.default_module is None
assert config.get_module_for_file(Path("any.c")) is None
```

**Expected Result:**
Empty config with all lookups returning None.

---

### SWUT_CONFIG_00025: Multiple Pattern Match Order

**Requirement:** SWR_CONFIG_00004
**Priority:** Medium
**Status:** Implemented

**Description:**
Verify that first matching pattern in configuration is used.

**Test Function:** `test_SWUT_CONFIG_00025_pattern_match_order()`

**Test Setup:**
```python
config_content = """
pattern_mappings:
  "hw_*.c": HardwareModule
  "hw_init.c": InitModule
  "*_init.c": GenericInitModule
"""
config = ModuleConfig(config_path)
```

**Test Execution:**
```python
# hw_init.c matches all three patterns, should get first match
module = config.get_module_for_file(Path("hw_init.c"))
assert module == "HardwareModule"  # First pattern wins
```

**Expected Result:**
First matching pattern is selected.

---

## Coverage Summary

| Requirement ID | Test ID | Status | Coverage |
|----------------|---------|--------|----------|
| SWR_CONFIG_00001 | SWUT_CONFIG_00001-00002 | ✅ Pass | Full |
| SWR_CONFIG_00002 | SWUT_CONFIG_00003-00013 | ✅ Pass | Full |
| SWR_CONFIG_00003 | SWUT_CONFIG_00014, 00016 | ✅ Pass | Full |
| SWR_CONFIG_00004 | SWUT_CONFIG_00008-00009, 00015, 00025 | ✅ Pass | Full |
| SWR_CONFIG_00005 | SWUT_CONFIG_00011, 00017 | ✅ Pass | Full |
| SWR_CONFIG_00006 | SWUT_CONFIG_00019-00020 | ✅ Pass | Full |
| SWR_CONFIG_00007 | SWUT_CONFIG_00014-00018, 00020 | ✅ Pass | Full |
| SWR_CONFIG_00008 | SWUT_CONFIG_00021-00022 | ✅ Pass | Full |
| SWR_CONFIG_00009 | SWUT_CONFIG_00023 | ✅ Pass | Full |
| SWR_CONFIG_00010 | SWUT_CONFIG_00024 | ✅ Pass | Full |

**Total Tests:** 25
**Requirements:** 10
**Coverage Target:** ≥90%
