"""Tests for parsers/autosar_parser.py (SWUT_PARSER_00001-00010)"""

from pathlib import Path

from autosar_calltree.database.models import FunctionType
from autosar_calltree.parsers.autosar_parser import AutosarParser


# SWUT_PARSER_00001: FUNC Macro Pattern Recognition

def test_func_macro_pattern_recognition():
    """SWUT_PARSER_00001

    Test that FUNC macro pattern is correctly recognized and parsed.
    """
    parser = AutosarParser()

    # Test basic FUNC pattern
    line = "FUNC(void, RTE_CODE) Demo_Init(void)"
    result = parser.parse_function_declaration(line, Path("test.c"), 1)
    assert result is not None
    assert result.name == "Demo_Init"
    assert result.return_type == "void"
    assert result.memory_class == "RTE_CODE"
    assert result.macro_type == "FUNC"
    assert result.function_type == FunctionType.AUTOSAR_FUNC
    assert result.is_static is False

    # Test FUNC with return type and parameters
    line = "FUNC(uint32, AUTOMATIC) HW_ReadSensor(VAR(uint32, AUTOMATIC) sensor_id)"
    result = parser.parse_function_declaration(line, Path("test.c"), 5)
    assert result is not None
    assert result.name == "HW_ReadSensor"
    assert result.return_type == "uint32"
    assert len(result.parameters) == 1
    assert result.parameters[0].name == "sensor_id"
    assert result.parameters[0].param_type == "uint32"
    assert result.function_type == FunctionType.AUTOSAR_FUNC


# SWUT_PARSER_00002: FUNC_P2VAR Macro Pattern Recognition

def test_func_p2var_macro_pattern_recognition():
    """SWUT_PARSER_00002

    Test that FUNC_P2VAR macro pattern is correctly recognized and parsed with
    pointer return type.
    """
    parser = AutosarParser()

    # Test FUNC_P2VAR pattern
    line = "FUNC_P2VAR(uint8, AUTOMATIC, APPL_VAR) GetBuffer(void)"
    result = parser.parse_function_declaration(line, Path("test.c"), 1)
    assert result is not None
    assert result.name == "GetBuffer"
    assert result.return_type == "uint8*"  # Pointer asterisk added
    assert result.memory_class == "APPL_VAR"
    assert result.macro_type == "FUNC_P2VAR"
    assert result.function_type == FunctionType.AUTOSAR_FUNC_P2VAR


# SWUT_PARSER_00003: FUNC_P2CONST Macro Pattern Recognition

def test_func_p2const_macro_pattern_recognition():
    """SWUT_PARSER_00003

    Test that FUNC_P2CONST macro pattern is correctly recognized and parsed with
    const pointer return type.
    """
    parser = AutosarParser()

    # Test FUNC_P2CONST pattern
    line = "FUNC_P2CONST(ConfigType, AUTOMATIC, APPL_CONST) GetConfig(void)"
    result = parser.parse_function_declaration(line, Path("test.c"), 1)
    assert result is not None
    assert result.name == "GetConfig"
    assert result.return_type == "const ConfigType*"  # const + pointer asterisk
    assert result.memory_class == "APPL_CONST"
    assert result.macro_type == "FUNC_P2CONST"
    assert result.function_type == FunctionType.AUTOSAR_FUNC_P2CONST


# SWUT_PARSER_00004: STATIC Keyword Detection

def test_static_keyword_detection():
    """SWUT_PARSER_00004

    Test that STATIC keyword is detected in AUTOSAR function macros.
    """
    parser = AutosarParser()

    # Test STATIC FUNC
    line = "STATIC FUNC(void, RTE_CODE) Internal_Function(void)"
    result = parser.parse_function_declaration(line, Path("test.c"), 10)
    assert result is not None
    assert result.name == "Internal_Function"
    assert result.is_static is True
    assert result.macro_type == "FUNC"
    assert result.function_type == FunctionType.AUTOSAR_FUNC

    # Test STATIC FUNC_P2VAR
    line = "STATIC FUNC_P2VAR(uint8, AUTOMATIC, Demo_VAR) GetLastBuffer(void)"
    result = parser.parse_function_declaration(line, Path("test.c"), 15)
    assert result is not None
    assert result.is_static is True
    assert result.name == "GetLastBuffer"
    assert result.macro_type == "FUNC_P2VAR"

    # Test STATIC FUNC_P2CONST
    line = "STATIC FUNC_P2CONST(ConfigType, AUTOMATIC) GetConfig(void)"
    result = parser.parse_function_declaration(line, Path("test.c"), 20)
    assert result.is_static is True
    assert result.macro_type == "FUNC_P2CONST"


# SWUT_PARSER_00005: VAR Parameter Pattern Recognition

def test_var_parameter_pattern_recognition():
    """SWUT_PARSER_00005

    Test that VAR macro parameter pattern is correctly recognized and parsed.
    """
    parser = AutosarParser()

    # Test basic VAR parameter
    line = "FUNC(void, RTE_CODE) TestFunc(VAR(uint32, AUTOMATIC) value)"
    result = parser.parse_function_declaration(line, Path("test.c"), 1)
    assert result is not None
    assert len(result.parameters) == 1
    assert result.parameters[0].name == "value"
    assert result.parameters[0].param_type == "uint32"
    assert result.parameters[0].memory_class == "AUTOMATIC"
    assert result.parameters[0].is_pointer is False
    assert result.parameters[0].is_const is False

    # Test VAR with different type
    line = "FUNC(void, RTE_CODE) TestFunc(VAR(boolean, AUTOMATIC) flag)"
    result = parser.parse_function_declaration(line, Path("test.c"), 5)
    assert result is not None
    assert result.parameters[0].name == "flag"
    assert result.parameters[0].param_type == "boolean"
    assert result.parameters[0].memory_class == "AUTOMATIC"


# SWUT_PARSER_00006: P2VAR Parameter Pattern Recognition

def test_p2var_parameter_pattern_recognition():
    """SWUT_PARSER_00006

    Test that P2VAR macro parameter pattern is correctly recognized and parsed as
    pointer parameter.
    """
    parser = AutosarParser()

    # Test P2VAR parameter
    line = "FUNC(void, RTE_CODE) TestFunc(VAR(P2VAR(uint8, AUTOMATIC, APPL_VAR) buffer) void)"
    result = parser.parse_function_declaration(line, Path("test.c"), 1)
    assert result is not None
    assert len(result.parameters) == 1
    assert result.parameters[0].name == "buffer"
    assert result.parameters[0].is_pointer is True
    assert result.parameters[0].param_type == "uint8"
    assert result.parameters[0].memory_class == "APPL_VAR"


# SWUT_PARSER_00007: P2CONST Parameter Pattern Recognition

def test_p2const_parameter_pattern_recognition():
    """SWUT_PARSER_00007

    Test that P2CONST macro parameter pattern is correctly recognized and parsed as
    const pointer parameter.
    """
    parser = AutosarParser()

    # Test P2CONST parameter
    line = "FUNC(void, RTE_CODE) TestFunc(VAR(P2CONST(ConfigType, AUTOMATIC, APPL_CONST) config) void)"
    result = parser.parse_function_declaration(line, Path("test.c"), 1)
    assert result is not None
    assert len(result.parameters) == 1
    assert result.parameters[0].name == "config"
    assert result.parameters[0].is_pointer is True
    assert result.parameters[0].is_const is True
    assert result.parameters[0].param_type == "ConfigType"
    assert result.parameters[0].memory_class == "APPL_CONST"


# SWUT_PARSER_00008: CONST Parameter Pattern Recognition

def test_const_parameter_pattern_recognition():
    """SWUT_PARSER_00008

    Test that CONST macro parameter pattern is correctly recognized and parsed as a
    const-qualified parameter.
    """
    parser = AutosarParser()

    # Test CONST parameter
    line = "FUNC(void, RTE_CODE) TestFunc(VAR(CONST(uint16, AUTOMATIC) limit) void)"
    result = parser.parse_function_declaration(line, Path("test.c"), 1)
    assert result is not None
    assert len(result.parameters) == 1
    assert result.parameters[0].name == "limit"
    assert result.parameters[0].is_pointer is False
    assert result.parameters[0].is_const is True
    assert result.parameters[0].param_type == "uint16"
    assert result.parameters[0].memory_class == "AUTOMATIC"


# SWUT_PARSER_00009: Parameter String Extraction

def test_parameter_string_extraction():
    """SWUT_PARSER_00003

    Test that parameter strings are correctly extracted from function declarations by
    counting balanced parentheses.
    """
    parser = AutosarParser()

    # Test simple parameter list
    line = "FUNC(void, RTE_CODE) TestFunc(VAR(uint32, AUTOMATIC) value)"
    start = line.find("VAR")
    param_string = parser._extract_param_string(line, start)
    assert param_string == "VAR(uint32, AUTOMATIC) value"

    # Test empty parameter list
    line = "FUNC(void, RTE_CODE) TestFunc(void)"
    start = line.find("TestFunc")
    param_string = parser._extract_param_string(line, start)
    assert param_string == "void"

    # Test nested parentheses
    line = "FUNC(void, RTE_CODE) ComplexFunc(VAR(void (*)(int), AUTOMATIC) callback)"
    start = line.find("VAR")
    param_string = parser._extract_param_string(line, start)
    assert "(void (*)(int)" in param_string


# SWUT_PARSER_00010: Function Declaration Parsing

def test_function_declaration_parsing():
    """SWUT_PARSER_00005

    Test that AUTOSAR function declarations are parsed into FunctionInfo objects with
    all required fields.
    """
    parser = AutosarParser()

    # Test basic declaration
    line = "FUNC(void, RTE_CODE) Demo_Init(void)"
    result = parser.parse_function_declaration(line, Path("demo.c"), 10)
    assert result is not None
    assert result.name == "Demo_Init"
    assert result.return_type == "void"
    assert result.file_path == Path("demo.c")
    assert result.line_number == 10
    assert result.is_static is False
    assert result.function_type == FunctionType.AUTOSAR_FUNC
    assert result.memory_class == "RTE_CODE"
    assert result.macro_type == "FUNC"

    # Test declaration with parameters
    line = "FUNC(uint32, AUTOMATIC) HW_ReadSensor(VAR(uint32, AUTOMATIC) sensor_id)"
    result = parser.parse_function_declaration(line, Path("hw.c"), 20)
    assert result is not None
    assert result.name == "HW_ReadSensor"
    assert len(result.parameters) == 1
    assert result.parameters[0].name == "sensor_id"
    assert result.parameters[0].param_type == "uint32"


# SWUT_PARSER_00010: Return Type Conversion

def test_return_type_conversion():
    """SWUT_PARSER_00006

    Test that AUTOSAR macros are converted to correct C return types.
    """
    parser = AutosarParser()

    # Test FUNC (no modifier)
    line = "FUNC(void, RTE_CODE) TestFunc(void)"
    result = parser.parse_function_declaration(line, Path("test.c"), 1)
    assert result.return_type == "void"

    # Test FUNC_P2VAR (pointer return)
    line = "FUNC_P2VAR(uint8, AUTOMATIC) GetBuffer(void)"
    result = parser.parse_function_declaration(line, Path("test.c"), 1)
    assert result.return_type == "uint8*"

    # Test FUNC_P2CONST (const pointer return)
    line = "FUNC_P2CONST(ConfigType, AUTOMATIC) GetConfig(void)"
    result = parser.parse_function_declaration(line, Path("test.c"), 1)
    assert result.return_type == "const ConfigType*"
