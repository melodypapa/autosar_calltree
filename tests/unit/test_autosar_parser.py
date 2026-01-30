"""Tests for AUTOSAR parser module (SWUT_PARSER_AUTOSAR_*)"""

from pathlib import Path

from autosar_calltree.database.models import FunctionType
from autosar_calltree.parsers.autosar_parser import AutosarParser


class TestAutosarParserPatterns:
    """Test AUTOSAR parser pattern recognition."""

    # SWUT_PARSER_AUTOSAR_00001: FUNC Macro Pattern Recognition
    def test_SWUT_PARSER_AUTOSAR_00001_func_macro_pattern(self):
        """Test that FUNC macro pattern is correctly recognized and parsed."""
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
        assert result.memory_class == "AUTOMATIC"
        assert len(result.parameters) == 1
        assert result.parameters[0].name == "sensor_id"
        assert result.parameters[0].param_type == "uint32"

        # Test STATIC FUNC
        line = "STATIC FUNC(uint8, CODE) Internal_Function(void)"
        result = parser.parse_function_declaration(line, Path("test.c"), 10)
        assert result is not None
        assert result.name == "Internal_Function"
        assert result.is_static is True
        assert result.memory_class == "CODE"

    # SWUT_PARSER_AUTOSAR_00002: FUNC_P2VAR Macro Pattern Recognition
    def test_SWUT_PARSER_AUTOSAR_00002_func_p2var_macro_pattern(self):
        """Test that FUNC_P2VAR macro pattern is correctly recognized and parsed."""
        parser = AutosarParser()

        # Test basic FUNC_P2VAR pattern
        line = "FUNC_P2VAR(uint8, AUTOMATIC, Demo_VAR) GetBuffer(void)"
        result = parser.parse_function_declaration(line, Path("test.c"), 1)
        assert result is not None
        assert result.name == "GetBuffer"
        assert result.return_type == "uint8*"  # Pointer asterisk added
        assert result.memory_class == "Demo_VAR"
        assert result.macro_type == "FUNC_P2VAR"
        assert result.function_type == FunctionType.AUTOSAR_FUNC_P2VAR

        # Test FUNC_P2VAR with parameters
        line = "FUNC_P2VAR(uint32, RTE_VAR, APPL_DATA) GetData(VAR(uint8, AUTOMATIC) index)"
        result = parser.parse_function_declaration(line, Path("test.c"), 5)
        assert result is not None
        assert result.name == "GetData"
        assert result.return_type == "uint32*"
        assert len(result.parameters) == 1

    # SWUT_PARSER_AUTOSAR_00003: FUNC_P2CONST Macro Pattern Recognition
    def test_SWUT_PARSER_AUTOSAR_00003_func_p2const_macro_pattern(self):
        """Test that FUNC_P2CONST macro pattern is correctly recognized and parsed."""
        parser = AutosarParser()

        # Test basic FUNC_P2CONST pattern
        line = "FUNC_P2CONST(ConfigType, AUTOMATIC, APPL_VAR) GetConfig(void)"
        result = parser.parse_function_declaration(line, Path("test.c"), 1)
        assert result is not None
        assert result.name == "GetConfig"
        assert result.return_type == "const ConfigType*"  # const + pointer asterisk
        assert result.memory_class == "APPL_VAR"
        assert result.macro_type == "FUNC_P2CONST"
        assert result.function_type == FunctionType.AUTOSAR_FUNC_P2CONST

        # Test FUNC_P2CONST with parameters
        line = "FUNC_P2CONST(uint8, RTE_CONST, CONFIG_VAR) GetReadOnlyData(VAR(uint32, AUTOMATIC) offset)"
        result = parser.parse_function_declaration(line, Path("test.c"), 5)
        assert result is not None
        assert result.name == "GetReadOnlyData"
        assert result.return_type == "const uint8*"


class TestAutosarParserParameters:
    """Test AUTOSAR parser parameter parsing."""

    # SWUT_PARSER_AUTOSAR_00004: Parameter String Extraction
    def test_SWUT_PARSER_AUTOSAR_00004_parameter_string_extraction(self):
        """Test that parameter strings are correctly extracted from function declarations."""
        parser = AutosarParser()

        # Test simple parameter list
        line = "FUNC(void, RTE_CODE) TestFunc(VAR(uint32, AUTOMATIC) value)"
        start = line.find("TestFunc") + len("TestFunc")
        param_string = parser._extract_param_string(line, start)
        assert param_string == "VAR(uint32, AUTOMATIC) value"

        # Test multiple parameters
        line = "FUNC(void, RTE_CODE) TestFunc(VAR(uint8, AUTOMATIC) a, VAR(uint16, AUTOMATIC) b)"
        start = line.find("TestFunc") + len("TestFunc")
        param_string = parser._extract_param_string(line, start)
        assert "VAR(uint8, AUTOMATIC) a" in param_string
        assert "VAR(uint16, AUTOMATIC) b" in param_string

        # Test empty parameter list
        line = "FUNC(void, RTE_CODE) TestFunc(void)"
        start = line.find("TestFunc") + len("TestFunc")
        param_string = parser._extract_param_string(line, start)
        assert param_string == "void"

        # Test nested parentheses (function pointer parameter)
        line = "FUNC(void, RTE_CODE) TestFunc(VAR(void, AUTOMATIC) (*callback)(VAR(uint32, AUTOMATIC)))"
        start = line.find("TestFunc") + len("TestFunc")
        param_string = parser._extract_param_string(line, start)
        assert "(VAR(uint32, AUTOMATIC))" in param_string

    # SWUT_PARSER_AUTOSAR_00005: VAR Parameter Pattern Recognition
    def test_SWUT_PARSER_AUTOSAR_00005_var_parameter_pattern(self):
        """Test that VAR macro parameters are correctly parsed."""
        parser = AutosarParser()

        # Test basic VAR parameter
        param_str = "VAR(uint32, AUTOMATIC) config_mode"
        params = parser.parse_parameters(param_str)
        assert len(params) == 1
        assert params[0].name == "config_mode"
        assert params[0].param_type == "uint32"
        assert params[0].is_pointer is False
        assert params[0].is_const is False
        assert params[0].memory_class == "AUTOMATIC"

        # Test VAR with different memory class
        param_str = "VAR(uint8, APPL_DATA) value"
        params = parser.parse_parameters(param_str)
        assert len(params) == 1
        assert params[0].memory_class == "APPL_DATA"

        # Test multiple VAR parameters
        param_str = "VAR(uint8, AUTOMATIC) param1, VAR(uint16, AUTOMATIC) param2, VAR(uint32, AUTOMATIC) param3"
        params = parser.parse_parameters(param_str)
        assert len(params) == 3
        assert params[0].name == "param1"
        assert params[1].name == "param2"
        assert params[2].name == "param3"

    # SWUT_PARSER_AUTOSAR_00006: P2VAR Parameter Pattern Recognition
    def test_SWUT_PARSER_AUTOSAR_00006_p2var_parameter_pattern(self):
        """Test that P2VAR macro parameters are correctly parsed."""
        parser = AutosarParser()

        # Test basic P2VAR parameter
        param_str = "P2VAR(uint8, AUTOMATIC, APPL_DATA) buffer"
        params = parser.parse_parameters(param_str)
        assert len(params) == 1
        assert params[0].name == "buffer"
        assert params[0].param_type == "uint8"
        assert params[0].is_pointer is True
        assert params[0].is_const is False
        assert params[0].memory_class == "APPL_DATA"

        # Test P2VAR with different memory classes
        param_str = "P2VAR(ConfigType, RTE_VAR, APPL_DATA) config"
        params = parser.parse_parameters(param_str)
        assert len(params) == 1
        assert params[0].memory_class == "APPL_DATA"

    # SWUT_PARSER_AUTOSAR_00007: P2CONST Parameter Pattern Recognition
    def test_SWUT_PARSER_AUTOSAR_00007_p2const_parameter_pattern(self):
        """Test that P2CONST macro parameters are correctly parsed."""
        parser = AutosarParser()

        # Test basic P2CONST parameter
        param_str = "P2CONST(uint8, AUTOMATIC, APPL_CONST) data"
        params = parser.parse_parameters(param_str)
        assert len(params) == 1
        assert params[0].name == "data"
        assert params[0].param_type == "uint8"
        assert params[0].is_pointer is True
        assert params[0].is_const is True
        assert params[0].memory_class == "APPL_CONST"

        # Test P2CONST with different memory classes
        param_str = "P2CONST(ConfigType, RTE_CONST, APPL_DATA) config"
        params = parser.parse_parameters(param_str)
        assert len(params) == 1
        assert params[0].memory_class == "APPL_DATA"

    # SWUT_PARSER_AUTOSAR_00008: CONST Parameter Pattern Recognition
    def test_SWUT_PARSER_AUTOSAR_00008_const_parameter_pattern(self):
        """Test that CONST macro parameters are correctly parsed."""
        parser = AutosarParser()

        # Test basic CONST parameter
        param_str = "CONST(uint32, AUTOMATIC) timeout"
        params = parser.parse_parameters(param_str)
        assert len(params) == 1
        assert params[0].name == "timeout"
        assert params[0].param_type == "uint32"
        assert params[0].is_pointer is False
        assert params[0].is_const is True
        assert params[0].memory_class == "AUTOMATIC"

        # Test CONST with different memory class
        param_str = "CONST(uint16, RTE_CONST) max_retries"
        params = parser.parse_parameters(param_str)
        assert len(params) == 1
        assert params[0].memory_class == "RTE_CONST"

    # SWUT_PARSER_AUTOSAR_00009: Traditional C Parameter Fallback
    def test_SWUT_PARSER_AUTOSAR_00009_traditional_c_parameter_fallback(self):
        """Test that traditional C parameters are parsed as fallback."""
        parser = AutosarParser()

        # Test pointer parameter
        param_str = "uint8* buffer"
        params = parser.parse_parameters(param_str)
        assert len(params) == 1
        assert params[0].name == "buffer"
        assert params[0].param_type == "uint8"
        assert params[0].is_pointer is True
        assert params[0].is_const is False

        # Test const pointer parameter
        param_str = "const ConfigType* config"
        params = parser.parse_parameters(param_str)
        assert len(params) == 1
        assert params[0].name == "config"
        assert params[0].param_type == "ConfigType"
        assert params[0].is_pointer is True
        assert params[0].is_const is True

        # Test type-only parameter (no name)
        param_str = "uint32"
        params = parser.parse_parameters(param_str)
        assert len(params) == 1
        assert params[0].name == ""
        assert params[0].param_type == "uint32"

    # SWUT_PARSER_AUTOSAR_00010: Parameter List Splitting
    def test_SWUT_PARSER_AUTOSAR_00010_parameter_list_splitting(self):
        """Test that parameter lists are split correctly respecting nested parentheses."""
        parser = AutosarParser()

        # Test simple splitting
        param_str = "VAR(uint32, AUTOMATIC) a, VAR(uint8, AUTOMATIC) b"
        parts = parser._split_parameters(param_str)
        assert len(parts) == 2
        assert parts[0].strip() == "VAR(uint32, AUTOMATIC) a"
        assert parts[1].strip() == "VAR(uint8, AUTOMATIC) b"

        # Test splitting with nested parentheses in VAR macro
        param_str = (
            "VAR(uint32, AUTOMATIC) value, P2VAR(uint8, AUTOMATIC, APPL_DATA) buffer"
        )
        parts = parser._split_parameters(param_str)
        assert len(parts) == 2

        # Test splitting with function pointer
        param_str = "VAR(void, AUTOMATIC) (*callback)(VAR(uint32, AUTOMATIC)), VAR(uint32, AUTOMATIC) context"
        parts = parser._split_parameters(param_str)
        assert len(parts) == 2


class TestAutosarParserEdgeCases:
    """Test AUTOSAR parser edge cases."""

    # SWUT_PARSER_AUTOSAR_00011: Function Declaration Parsing
    def test_SWUT_PARSER_AUTOSAR_00011_function_declaration_parsing(self):
        """Test complete function declaration parsing."""
        parser = AutosarParser()

        # Test FUNC declaration
        line = "FUNC(void, RTE_CODE) Demo_Init(void)"
        result = parser.parse_function_declaration(line, Path("demo.c"), 8)
        assert result is not None
        assert result.name == "Demo_Init"
        assert result.return_type == "void"
        assert result.function_type == FunctionType.AUTOSAR_FUNC
        assert result.file_path == Path("demo.c")
        assert result.line_number == 8
        assert result.macro_type == "FUNC"
        assert result.memory_class == "RTE_CODE"

        # Test FUNC_P2VAR declaration
        line = "FUNC_P2VAR(uint8, AUTOMATIC, APPL_VAR) GetBuffer(void)"
        result = parser.parse_function_declaration(line, Path("demo.c"), 15)
        assert result is not None
        assert result.name == "GetBuffer"
        assert result.return_type == "uint8*"
        assert result.function_type == FunctionType.AUTOSAR_FUNC_P2VAR
        assert result.macro_type == "FUNC_P2VAR"

        # Test FUNC_P2CONST declaration
        line = "FUNC_P2CONST(ConfigType, AUTOMATIC, APPL_CONST) GetConfig(void)"
        result = parser.parse_function_declaration(line, Path("demo.c"), 20)
        assert result is not None
        assert result.name == "GetConfig"
        assert result.return_type == "const ConfigType*"
        assert result.function_type == FunctionType.AUTOSAR_FUNC_P2CONST
        assert result.macro_type == "FUNC_P2CONST"

        # Test non-matching line returns None
        line = "void traditional_c_function(void)"
        result = parser.parse_function_declaration(line, Path("demo.c"), 25)
        assert result is None

    # SWUT_PARSER_AUTOSAR_00012: AUTOSAR Function Detection
    def test_SWUT_PARSER_AUTOSAR_00012_autosar_function_detection(self):
        """Test is_autosar_function method."""
        parser = AutosarParser()

        # Test FUNC detection
        assert (
            parser.is_autosar_function("FUNC(void, RTE_CODE) Demo_Init(void)") is True
        )

        # Test FUNC_P2VAR detection
        assert (
            parser.is_autosar_function(
                "FUNC_P2VAR(uint8, AUTOMATIC, APPL_VAR) GetBuffer(void)"
            )
            is True
        )

        # Test FUNC_P2CONST detection
        assert (
            parser.is_autosar_function(
                "FUNC_P2CONST(ConfigType, AUTOMATIC, APPL_CONST) GetConfig(void)"
            )
            is True
        )

        # Test non-AUTOSAR function
        assert parser.is_autosar_function("void traditional_c_function(void)") is False

        # Test empty string
        assert parser.is_autosar_function("") is False

    # SWUT_PARSER_AUTOSAR_00013: Empty Parameter List Handling
    def test_SWUT_PARSER_AUTOSAR_00013_empty_parameter_list_handling(self):
        """Test that void and empty parameter lists are handled correctly."""
        parser = AutosarParser()

        # Test void parameter list
        params = parser.parse_parameters("void")
        assert len(params) == 0

        # Test empty parameter list
        params = parser.parse_parameters("")
        assert len(params) == 0

        # Test whitespace-only parameter list
        params = parser.parse_parameters("   ")
        assert len(params) == 0

    # SWUT_PARSER_AUTOSAR_00014: Whitespace Tolerance
    def test_SWUT_PARSER_AUTOSAR_00014_whitespace_tolerance(self):
        """Test that parser handles variable whitespace correctly."""
        parser = AutosarParser()

        # Test extra spaces in FUNC macro
        line = "FUNC(  void  ,  RTE_CODE  )  Demo_Init  (  void  )"
        result = parser.parse_function_declaration(line, Path("test.c"), 1)
        assert result is not None
        assert result.name == "Demo_Init"
        assert result.return_type == "void"
        assert result.memory_class == "RTE_CODE"

        # Test extra spaces in parameters
        line = (
            "FUNC(void, RTE_CODE) TestFunc(  VAR  (  uint32  ,  AUTOMATIC  )  value  )"
        )
        result = parser.parse_function_declaration(line, Path("test.c"), 2)
        assert result is not None
        assert len(result.parameters) == 1
        assert result.parameters[0].name == "value"

    # SWUT_PARSER_AUTOSAR_00015: FunctionInfo Object Creation
    def test_SWUT_PARSER_AUTOSAR_00015_functioninfo_object_creation(self):
        """Test that FunctionInfo objects are created with all fields populated."""
        parser = AutosarParser()

        # Test FUNC FunctionInfo creation
        line = "FUNC(void, RTE_CODE) Demo_Init(VAR(uint32, AUTOMATIC) mode)"
        result = parser.parse_function_declaration(line, Path("demo.c"), 8)
        assert result.name == "Demo_Init"
        assert result.return_type == "void"
        assert result.file_path == Path("demo.c")
        assert result.line_number == 8
        assert result.is_static is False
        assert result.function_type == FunctionType.AUTOSAR_FUNC
        assert result.memory_class == "RTE_CODE"
        assert result.macro_type == "FUNC"
        assert len(result.parameters) == 1
        assert result.parameters[0].name == "mode"

        # Test STATIC FUNC FunctionInfo creation
        line = "STATIC FUNC(uint8, CODE) InternalFunction(void)"
        result = parser.parse_function_declaration(line, Path("demo.c"), 12)
        assert result.name == "InternalFunction"
        assert result.return_type == "uint8"
        assert result.is_static is True
        assert result.function_type == FunctionType.AUTOSAR_FUNC
        assert result.memory_class == "CODE"

        # Test FUNC_P2VAR FunctionInfo creation
        line = "FUNC_P2VAR(uint32, AUTOMATIC, APPL_DATA) GetBuffer(void)"
        result = parser.parse_function_declaration(line, Path("demo.c"), 15)
        assert result.name == "GetBuffer"
        assert result.return_type == "uint32*"
        assert result.function_type == FunctionType.AUTOSAR_FUNC_P2VAR
        assert result.macro_type == "FUNC_P2VAR"

        # Test FUNC_P2CONST FunctionInfo creation
        line = "FUNC_P2CONST(uint8, RTE_CONST, CONFIG_VAR) GetConfig(void)"
        result = parser.parse_function_declaration(line, Path("demo.c"), 18)
        assert result.name == "GetConfig"
        assert result.return_type == "const uint8*"
        assert result.function_type == FunctionType.AUTOSAR_FUNC_P2CONST
        assert result.macro_type == "FUNC_P2CONST"


class TestAutosarParserWithFixtures:
    """Test AUTOSAR parser with fixture files."""

    def test_parse_basic_functions_fixture(self):
        """Test parsing basic_functions.c fixture."""
        parser = AutosarParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "autosar_code"
            / "basic_functions.c"
        )
        content = fixture_path.read_text()

        functions = []
        for line_num, line in enumerate(content.split("\n"), 1):
            if parser.is_autosar_function(line):
                func = parser.parse_function_declaration(line, fixture_path, line_num)
                if func:
                    functions.append(func)

        # Should find 6 AUTOSAR functions
        assert len(functions) >= 6

        # Check for specific functions
        func_names = [f.name for f in functions]
        assert "SimpleVoidFunction" in func_names
        assert "GetValue" in func_names
        assert "StaticInternalFunction" in func_names
        assert "GetBuffer" in func_names

    def test_parse_with_parameters_fixture(self):
        """Test parsing with_parameters.c fixture."""
        parser = AutosarParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "autosar_code"
            / "with_parameters.c"
        )
        content = fixture_path.read_text()

        functions = []
        for line_num, line in enumerate(content.split("\n"), 1):
            if parser.is_autosar_function(line):
                func = parser.parse_function_declaration(line, fixture_path, line_num)
                if func:
                    functions.append(func)

        # Should find multiple functions with parameters
        assert len(functions) >= 8

        # Check function with VAR parameters
        process_value = next((f for f in functions if f.name == "ProcessValue"), None)
        assert process_value is not None
        assert len(process_value.parameters) == 1
        assert process_value.parameters[0].memory_class == "AUTOMATIC"

        # Check function with P2VAR parameter
        write_buffer = next((f for f in functions if f.name == "WriteBuffer"), None)
        assert write_buffer is not None
        assert len(write_buffer.parameters) == 1
        assert write_buffer.parameters[0].is_pointer is True
        assert write_buffer.parameters[0].is_const is False

    def test_parse_complex_macros_fixture(self):
        """Test parsing complex_macros.c fixture."""
        parser = AutosarParser()
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "autosar_code"
            / "complex_macros.c"
        )
        content = fixture_path.read_text()

        functions = []
        for line_num, line in enumerate(content.split("\n"), 1):
            if parser.is_autosar_function(line):
                func = parser.parse_function_declaration(line, fixture_path, line_num)
                if func:
                    functions.append(func)

        # Should find multiple functions including complex ones
        assert len(functions) >= 5
