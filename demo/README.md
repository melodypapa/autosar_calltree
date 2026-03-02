# AUTOSAR Call Tree Analyzer - Demo Files

This directory contains demonstration files showcasing the capabilities of the AUTOSAR Call Tree Analyzer.

## 📁 File Structure

```
demo/
├── src/                     # C source code
│   ├── communication.c      # Communication module (CAN, LIN, Ethernet)
│   ├── demo.c               # Main demo functions
│   ├── demo.h               # Header file with AUTOSAR macros
│   ├── hardware.c           # Hardware module (sensors, actuators)
│   └── software.c           # Software module (data processing)
├── module_mapping.yaml      # SW module configuration
└── output/                  # Generated output files
    ├── demo.md              # Example output: Demo_Init (module-level)
    ├── demo_main.md         # Example output: Demo_MainFunction (module-level)
    ├── rhapsody_demo_main.xmi   # Example output: Rhapsody XMI 2.1 format
    └── README.md            # This file
```

## 🚀 Quick Start

### 1. Analyze Demo_Init (Initialization Sequence)

Generate a module-level sequence diagram showing the initialization flow:

```bash
calltree --start-function Demo_Init \
         --source-dir demo/src \
         --module-config demo/module_mapping.yaml \
         --use-module-names \
         --output demo/output/demo_init_output.md
```

**Output:** Shows initialization of all subsystems (Hardware, Software, Communication)

### 2. Analyze Demo_MainFunction (Main Loop)

Generate a sequence diagram for the main function loop:

```bash
calltree --start-function Demo_MainFunction \
         --source-dir demo/src \
         --module-config demo/module_mapping.yaml \
         --use-module-names \
         --output demo/output/demo_main_output.md
```

**Output:** Shows sensor reading, data processing, and conditional updates

### 3. Generate Rhapsody XMI

Export a Rhapsody-compatible XMI 2.1 file:

```bash
calltree --start-function Demo_MainFunction \
         --source-dir demo/src \
         --module-config demo/module_mapping.yaml \
         --use-module-names \
         --format rhapsody \
         --output demo/output/rhapsody_demo_main_modules.xmi
```

**Output:** XMI file that can be imported into IBM Rhapsody 8.0+

### 4. List All Available Functions

Discover all functions in the demo code:

```bash
calltree --list-functions --source-dir demo/src
```

### 5. Search for Functions

Find functions matching a pattern:

```bash
calltree --search "Init" --source-dir demo/src
```

## 📊 Features Demonstrated

### Source Code Features

#### demo.c
- **Conditional Calls**: `if (0x05 > 0x00)` - Optional function calls
- **For Loops**: `for (sensor_count = 0; sensor_count < 10; sensor_count++)` - Iterative sensor reading
- **Multi-line Conditions**: `if (sensor_count > 5 && sensor_count < 20)` - Complex boolean logic
- **Nested Conditionals**: if/else inside if statements

#### software.c
- **Nested Loops**: for loop inside for loop
- **While Loops**: `while (i < length)` - Conditional iteration
- **Multiple Return Paths**: Early returns in functions
- **If/Else If/Else Chains**: Multi-way conditional logic

#### hardware.c
- **Conditional Initialization**: Functions called based on parameters
- **Sensor Arrays**: Processing multiple sensors in loops
- **Nested Calibration Loops**: For loop inside for loop
- **Conditional Actuator Control**: Enable/disable based on values

#### communication.c
- **Message Queues**: Processing multiple messages
- **Retry Logic**: for loop with break condition
- **Broadcast Functionality**: Loop through all channels

### Generated Output Features

#### Mermaid Sequence Diagrams
- ✅ Function-level diagrams
- ✅ Module-level diagrams (with `--use-module-names`)
- ✅ opt blocks for conditional calls
- ✅ Loop blocks (for, while)
- ✅ Function parameters in call signatures
- ✅ Call tree text representation

#### Rhapsody XMI 2.1
- ✅ XMI 2.1 compliant (OMG UML namespace)
- ✅ GUID+ ID format (e.g., `GUID+8419bfee-6663-4506-815d-c69379b25334`)
- ✅ MessageOccurrenceSpecification elements
- ✅ Role definitions via ownedAttribute
- ✅ Complex profile structure with EPackage references
- ✅ Import-compatible with IBM Rhapsody 8.0+

## 🔧 Module Mapping

The `module_mapping.yaml` file maps C source files to SW modules:

| Source File | SW Module |
|-------------|-----------|
| demo.c | DemoModule |
| hardware.c | HardwareModule |
| software.c | SoftwareModule |
| communication.c | CommunicationModule |

This enables architecture-level diagrams showing module interactions instead of individual function calls.

## 📝 Example Outputs

### demo.md (Demo_Init)
- **Total Functions**: 20
- **Max Depth**: 3
- **Participants**: DemoModule, CommunicationModule, HardwareModule, SoftwareModule
- **Features**: Conditional initialization, nested module calls

### demo_main.md (Demo_MainFunction)
- **Total Functions**: 17
- **Max Depth**: 3
- **Participants**: DemoModule, CommunicationModule, SoftwareModule, HardwareModule
- **Features**: Sensor loops, conditional updates, data processing

### rhapsody_demo_main.xmi
- **Format**: XMI 2.1
- **Namespace**: OMG UML (http://www.omg.org/spec/UML/20090901)
- **Features**: Full Rhapsody compatibility, role definitions, message occurrences

## 🎯 Use Cases

1. **Documentation Generation**: Generate sequence diagrams for design documentation
2. **Code Review**: Visualize function dependencies and call patterns
3. **Impact Analysis**: Understand change impact before modifications
4. **Onboarding**: Help new developers understand codebase structure
5. **Compliance**: Generate diagrams for safety certification (ISO 26262)
6. **Rhapsody Integration**: Import XMI into IBM Rhapsody for professional modeling

## 💡 Tips

- **Use `--verbose`** to see detailed statistics and processing progress
- **Use `--max-depth`** to limit call tree depth for large codebases
- **Use `--rebuild-cache`** to force database rebuilding after code changes
- **Combine formats**: Use `--format both` to generate both Mermaid and XMI simultaneously

## 📚 Related Documentation

- [Main README](../README.md) - Project overview and installation
- [Rhapsody Export Guide](../docs/rhapsody_export.md) - Detailed Rhapsody usage
- [Rhapsody Troubleshooting](../docs/rhapsody_troubleshooting.md) - Common issues and solutions

## 🤝 Contributing

To add new demo examples:

1. Create new C files in this directory
2. Update `module_mapping.yaml` if needed
3. Generate example outputs
4. Update this README with new use cases

## 📄 License

MIT License - See [LICENSE](../LICENSE) file for details