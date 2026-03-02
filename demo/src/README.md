# AUTOSAR Demo Source Files

This directory contains demonstration C source files that showcase the module mapping feature of the AUTOSAR Call Tree Analyzer.

## File Structure

### demo.c (DemoModule)
Main application entry point that coordinates calls across all other modules. This file demonstrates:
- Cross-module function calls
- Conditional and loop-based cross-module coordination
- Module-aware architecture

### hardware.c (HardwareModule)
Contains hardware-related functions:
- Hardware initialization (clock, GPIO, PWM, ADC)
- Sensor reading with conditional logic
- Actuator control
- Interrupt management
- Sensor array processing

### software.c (SoftwareModule)
Contains software/logic-related functions:
- State management and initialization
- Data processing with nested loops
- State updates with validation
- Data validation and batch processing
- Average calculation

### communication.c (CommunicationModule)
Contains communication-related functions:
- Communication initialization (CAN, LIN, Ethernet)
- Message sending with retry logic
- Conditional message transmission
- Message queue processing
- Broadcast messaging

### demo.h
Header file with function declarations shared across all modules.

## Module Mapping

The `../module_mapping.yaml` file defines the module assignments:

```yaml
file_mappings:
  demo.c: DemoModule

pattern_mappings:
  "hardware.c": HardwareModule
  "software.c": SoftwareModule
  "communication.c": CommunicationModule

default_module: "Other"
```

## Usage Examples

### Generate Function-Level Diagram
```bash
calltree --start-function Demo_Init --source-dir demo/src
```
Shows individual function calls.

### Generate Module-Level Diagram
```bash
calltree --start-function Demo_Init \
         --source-dir demo/src \
         --module-config demo/module_mapping.yaml \
         --use-module-names \
         --output demo_module_diagram.md
```
Shows interactions between **DemoModule**, **HardwareModule**, **SoftwareModule**, and **CommunicationModule**.

## Module Interaction Flow

```
Demo_Init (DemoModule)
    ├──> HW_InitHardware (HardwareModule)
    │     ├──> HW_InitClock
    │     └──> HW_InitGPIO
    ├──> SW_InitSoftware (SoftwareModule)
    │     ├──> SW_InitState
    │     └──> SW_InitConfig
    └──> COM_InitCommunication (CommunicationModule)
          ├──> COM_InitCAN
          │     ├──> COM_EnableTX
          │     └──> COM_EnableRX
          ├──> COM_InitLIN
          └──> COM_InitEthernet
```

This demonstrates how the module mapping feature transforms individual function calls into an architecture-level view showing interactions between software components.