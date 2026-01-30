#!/usr/bin/env python3
"""
Generate 1000 demo AUTOSAR C files for testing function database performance.
"""

import random
from pathlib import Path
from typing import List

# AUTOSAR patterns
FUNCTION_TYPES = [
    "void", "uint8", "uint16", "uint32", "int8", "int16", "int32", "Std_ReturnType"
]

FUNCTION_CLASSES = [
    "RTE_CODE", "CODE", "APPL_CODE", "OS_CODE"
]

VARIANTS = [
    "AUTOMATIC", "STATIC"
]

RETURN_POINTER_TYPES = [
    ("FUNC_P2VAR", "VAR"),
    ("FUNC_P2CONST", "CONST"),
]

# Module prefixes for realistic naming
MODULE_PREFIXES = [
    "ECU", "Sensor", "Actuator", "Communication", "Driver", "Manager",
    "Handler", "Controller", "Processor", "Analyzer", "Monitor", "Validator",
    "Converter", "Calculator", "Estimator", "Filter", "Detector", "Logger"
]

FUNCTION_VERBS = [
    "Init", "Deinit", "Start", "Stop", "Read", "Write", "Send", "Receive",
    "Process", "Calculate", "Update", "Validate", "Check", "Monitor", "Control",
    "Handle", "Execute", "Perform", "Run", "Enable", "Disable", "Reset",
    "Configure", "Get", "Set", "Clear", "Toggle", "Trigger", "Notify"
]

FUNCTION_NOUNS = [
    "Data", "Signal", "Message", "Status", "State", "Value", "Parameter",
    "Configuration", "Error", "Warning", "Request", "Response", "Buffer",
    "Register", "Memory", "Hardware", "Software", "Communication", "Interface",
    "Sensor", "Actuator", "Driver", "Manager", "Handler", "Controller"
]

PARAMETER_TYPES = [
    "uint8", "uint16", "uint32", "int8", "int16", "int32",
    "float32", "float64", "boolean", "Std_ReturnType"
]

random.seed(42)


def generate_function_name() -> str:
    """Generate a realistic AUTOSAR function name."""
    prefix = random.choice(MODULE_PREFIXES)
    verb = random.choice(FUNCTION_VERBS)
    noun = random.choice(FUNCTION_NOUNS)
    return f"{prefix}_{verb}{noun}"


def generate_parameters(num_params: int = None) -> List[str]:
    """Generate AUTOSAR-style function parameters."""
    if num_params is None:
        num_params = random.randint(0, 4)

    params = []
    for i in range(num_params):
        param_type = random.choice(PARAMETER_TYPES)

        # Choose parameter qualifier
        qualifier_roll = random.random()
        if qualifier_roll < 0.6:
            qualifier = f"VAR({param_type}, AUTOMATIC)"
        elif qualifier_roll < 0.8:
            qualifier = f"P2VAR({param_type}, AUTOMATIC, APPL_DATA)"
        elif qualifier_roll < 0.9:
            qualifier = f"P2CONST({param_type}, AUTOMATIC, APPL_DATA)"
        else:
            qualifier = f"CONST({param_type}, AUTOMATIC)"

        param_name = f"param{i}"
        params.append(f"{qualifier} {param_name}")

    return params


def generate_function_declaration(func_name: str, is_static: bool = False) -> tuple[str, str]:
    """Generate a function declaration and its definition."""
    return_type = random.choice(FUNCTION_TYPES)
    func_class = random.choice(FUNCTION_CLASSES)

    # Sometimes use pointer return types
    use_pointer_return = random.random() < 0.1
    if use_pointer_return:
        pointer_macro, var_macro = random.choice(RETURN_POINTER_TYPES)
        return_type_str = f"{pointer_macro}({return_type}, AUTOMATIC, APPL_VAR)"
    else:
        return_type_str = return_type

    params = generate_parameters()
    if params:
        params_str = ", ".join(params)
    else:
        params_str = "void"

    static_prefix = "STATIC " if is_static else ""
    declaration = f"{static_prefix}FUNC({return_type_str}, {func_class}) {func_name}({params_str});"

    return declaration, return_type, params_str


def generate_file_content(file_index: int, num_functions: int = 5) -> str:
    """Generate content for a single C file."""
    module_name = f"Module{file_index:04d}"
    functions = []

    # Generate function declarations
    for i in range(num_functions):
        func_name = generate_function_name()
        is_static = i > 0  # First function is public, rest are static
        decl, return_type, params_str = generate_function_declaration(func_name, is_static)
        functions.append((decl, return_type, params_str, func_name))

    # Build file content
    content = f"/*\n * {module_name} - AUTOSAR Demo File {file_index}\n */\n\n"
    content += f'#include "{module_name}.h"\n\n'

    # Add function definitions
    for i, (decl, return_type, params_str, func_name) in enumerate(functions):
        content += f"/* Function definition */\n"
        content += decl.replace(";", "\n") + " {\n"

        # Add function calls to other functions (create call chains)
        if i < len(functions) - 1:
            # Call to next function
            next_func = functions[i + 1][3]
            num_args = len(params_str.split(",")) if params_str != "void" else 0

            if num_args == 0:
                content += f"    {next_func}();\n"
            else:
                args = ", ".join([f"0x{i*16:02X}" for i in range(num_args)])
                content += f"    {next_func}({args});\n"

        # Add some inline logic comments
        content += "    /* Local processing */\n"

        if return_type != "void":
            content += f"    return ({return_type})0;\n"

        content += "}\n\n"

    return content


def generate_header_content(file_index: int, functions: List[str]) -> str:
    """Generate content for a header file."""
    module_name = f"Module{file_index:04d}"
    content = f"/*\n * {module_name} - Header File\n */\n\n"
    content += f"#ifndef {module_name.upper()}_H\n"
    content += f"#define {module_name.upper()}_H\n\n"
    content += "#include \"Std_Types.h\"\n\n"

    # Add public function declarations (only first function from each file)
    content += "/* Public API */\n"
    content += functions[0] + "\n\n"

    content += f"#endif /* {module_name.upper()}_H */\n"
    return content


def main():
    """Generate 1000 demo files."""
    output_dir = Path("demo/large_scale")
    output_dir.mkdir(exist_ok=True)

    num_files = 1000

    print(f"Generating {num_files} AUTOSAR C files in {output_dir}/...")

    for i in range(num_files):
        # Generate C file
        c_content = generate_file_content(i, num_functions=random.randint(3, 8))
        c_filename = output_dir / f"module_{i:04d}.c"

        with open(c_filename, "w") as f:
            f.write(c_content)

        # Generate corresponding header file (only for some files)
        if i % 2 == 0:  # Every other file gets a header
            # Extract the first function declaration
            func_decls = []
            for line in c_content.split("\n"):
                if "FUNC(" in line and not line.strip().startswith("/*"):
                    if ";" in line:
                        func_decls.append(line.strip())
                        break

            if func_decls:
                h_content = generate_header_content(i, func_decls)
                h_filename = output_dir / f"module_{i:04d}.h"
                with open(h_filename, "w") as f:
                    f.write(h_content)

        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{num_files} files...")

    print(f"\n✓ Successfully generated {num_files} demo files!")
    print(f"  Location: {output_dir.absolute()}")
    print(f"\nTest the database builder with:")
    print(f"  calltree --list-functions --source-dir demo/large_scale")


if __name__ == "__main__":
    main()
