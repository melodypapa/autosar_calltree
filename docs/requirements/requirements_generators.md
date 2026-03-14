# Generators Package Requirements

**Package**: `autosar_calltree.generators`
**Source Files**: `mermaid_generator.py`, `rhapsody_generator.py`
**Requirements**: SWR_GEN_00001 - SWR_GEN_00025, SWR_MERMAID_00001 - SWR_MERMAID_00005, SWR_RH_00001 - SWR_RH_00005 (35 requirements)

---

## Overview

The generators package provides output generation functionality, creating Mermaid sequence diagrams and Rhapsody XMI 2.1 documents from call tree analysis results.

**Core Classes**:
- `MermaidGenerator` - Mermaid sequence diagram generation
- `RhapsodyXmiGenerator` - Rhapsody XMI 2.1 document generation (v0.8.0+)

---

## Mermaid Generator (SWR_GEN_00001 - SWR_GEN_00015)

### SWR_GEN_00001 - Mermaid Sequence Diagram Generation
**Purpose**: Generate Mermaid sequence diagrams from call tree

**Method**: `generate(analysis_result, output_path)`

**Output**: Markdown file with Mermaid diagram

**Implementation**: `MermaidGenerator`

---

### SWR_GEN_00002 - Participant Management
**Purpose**: Manage participants in sequence diagram

**Participant Types**:
- Function names (default)
- Module names (with `--use-module-names`)

**Implementation**: Track participants in encounter order

---

### SWR_GEN_00003 - Module-Based Participants
**Purpose**: Use SW modules as participants

**Trigger**: `--use-module-names` flag

**Behavior**:
- Use module name as participant
- Fallback to filename if no module
- Show function names on arrows

**Example**: `DemoModule->CommunicationModule: COM_InitCommunication()`

---

### SWR_GEN_00004 - Function Names on Arrows
**Purpose**: Display function names on call arrows

**Format**: `ParticipantA->ParticipantB: function_name(params)`

**Implementation**: Arrow label generation

---

### SWR_GEN_00005 - Parameter Display
**Purpose**: Display parameters on call arrows

**Format**: `function_name(param1, param2)`

**Options**:
- Show parameter names only (not types)
- Handle empty parameters (no parentheses)
- Configurable via Python API

**Implementation**: Parameter formatting in arrow labels

---

### SWR_GEN_00006 - Opt Block Generation
**Purpose**: Generate Mermaid opt blocks for conditional calls

**Trigger**: `is_conditional=True` in FunctionCall

**Format**:
```mermaid
opt condition text
  Source->Target: function_name()
end
```

**Implementation**: Conditional block generation

---

### SWR_GEN_00007 - Alt Block Generation
**Purpose**: Generate Mermaid alt blocks for if/else chains

**Trigger**: Multiple conditions at same level

**Format**:
```mermaid
alt condition 1
  Source->Target: func1()
else condition 2
  Source->Target: func2()
else
  Source->Target: func3()
end
```

**Implementation**: Alt block generation (future enhancement)

---

### SWR_GEN_00008 - Loop Block Generation
**Purpose**: Generate Mermaid loop blocks for loop calls

**Trigger**: `is_loop=True` in FunctionCall

**Format**:
```mermaid
opt loop condition
  Source->Target: function_name()
end
```

**Note**: Using `opt` with "loop" prefix for Mermaid compatibility

---

### SWR_GEN_00009 - Function Table Generation
**Purpose**: Generate function table in output

**Columns**:
- Function name
- Return type
- File path
- Line number
- SW module (if configured)

**Implementation**: Table generation in Mermaid output

---

### SWR_GEN_00010 - Module Column in Table
**Purpose**: Add module column to function table

**Display**: Show SW module for each function

**Fallback**: Show filename if no module assigned

---

### SWR_GEN_00011 - Metadata Section
**Purpose**: Include metadata in generated document

**Fields**:
- Analysis timestamp
- Source directory
- Start function
- Max depth
- Statistics

---

### SWR_GEN_00012 - Text Tree Generation
**Purpose**: Generate ASCII art tree representation

**Format**: Indented tree with box-drawing characters

**Example**:
```
Demo_Init
├─ HW_InitHardware
├─ SW_InitSoftware
└─ COM_InitCommunication
    ├─ COM_InitCAN
    ├─ COM_InitEthernet
    └─ COM_InitLIN
```

**Implementation**: Text tree with `│`, `└`, `└─` characters

---

### SWR_GEN_00013 - Statistics Display
**Purpose**: Display analysis statistics

**Includes**:
- Total functions
- Unique functions
- Max depth
- Circular dependencies
- RTE functions

---

### SWR_GEN_00014 - Circular Dependencies Section
**Purpose**: Document circular dependencies in output

**Format**: List each cycle with functions involved

---

### SWR_GEN_00015 - Mermaid File Format
**Purpose**: Generate valid Mermaid markdown

**Structure**:
```markdown
# Call Tree for {function_name}

```mermaid
sequenceDiagram
    ...
```

## Metadata
...

## Function Table
...

## Text Tree
...
```

---

## Mermaid-Specific Requirements (SWR_MERMAID_00001 - SWR_MERMAID_00005)

### SWR_MERMAID_00001 - Module-Based Participants
**Purpose**: Support module-based participants in Mermaid diagrams

**Implementation**: `MermaidGenerator._get_participant_name()` method

**Behavior**:
- Return module name when `use_module_names=True` and module is assigned
- Fall back to function name when no module assigned
- Display function names on arrows in module mode

---

### SWR_MERMAID_00002 - Module Column in Function Table
**Purpose**: Include module column in function table when modules are used

**Implementation**: Table generation with conditional module column

**Behavior**: Show SW module name for each function in table

---

### SWR_MERMAID_00003 - Module Fallback Behavior
**Purpose**: Gracefully handle functions without module assignment

**Behavior**: Fall back to file name or function name when no module configured

---

### SWR_MERMAID_00004 - Opt Block Generation
**Purpose**: Generate Mermaid opt blocks for conditional calls

**Implementation**: `_generate_opt_block()` method

**Format**: `opt <condition>` ... `end`

---

### SWR_MERMAID_00005 - Loop Block Generation
**Purpose**: Generate Mermaid loop blocks for loop calls

**Implementation**: `_generate_loop_block()` method

**Format**: `opt loop <condition>` ... `end`

---

## Rhapsody XMI Generator (SWR_GEN_00016 - SWR_GEN_00025)

### SWR_GEN_00016 - Rhapsody XMI 2.1 Document Generation
**Purpose**: Generate Rhapsody-compatible XMI 2.1 sequence diagrams

**Method**: `generate(analysis_result, output_path)`

**Output**: XML file with XMI 2.1 format (OMG UML 2.1 namespace)

**Implementation**: `RhapsodyXmiGenerator` (uses lxml for namespace control)

**Note**: v0.8.0 migrated from generic XMI/UML 2.5 to Rhapsody-specific XMI 2.1 format for full IBM Rhapsody 8.0+ compatibility.

---

### SWR_GEN_00017 - XMI Namespaces and Schema
**Purpose**: Use correct XMI and UML namespaces for Rhapsody compatibility

**Namespaces**:
- `xmlns:uml="http://www.omg.org/spec/UML/20090901"` (OMG UML 2.1)
- `xmlns:xmi="http://schema.omg.org/spec/XMI/2.1"` (XMI 2.1)
- `xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"`
- `xmlns:ecore="http://www.eclipse.org/emf/2002/Ecore"`

**XMI Version**: 2.1 (Rhapsody native format)

**ID Format**: `GUID+<UUID>` for all elements

---

### SWR_GEN_00018 - UML Lifeline Generation
**Purpose**: Generate UML lifelines for participants

**Elements**:
- `uml:Lifeline` with GUID+ UUID
- `name`: Participant name (function or module)
- `represents`: Property reference via ownedAttribute

---

### SWR_GEN_00019 - UML Message Generation
**Purpose**: Generate UML messages for calls

**Elements**:
- `uml:Message` with GUID+ UUID
- `name`: Function name with parameters
- `messageSort`: "synchCall" for calls
- `MessageOccurrenceSpecification`: Explicit send/receive events

---

### SWR_GEN_00020 - Rhapsody Opt/Loop Block Support
**Purpose**: Generate UML combined fragments for conditional/loop calls

**Element**: `uml:CombinedFragment`

**Attributes**:
- `interactionOperator="opt"`
- `operand` with condition name

---

### SWR_GEN_00021 - Module Support in XMI
**Purpose**: Use modules as lifelines when configured

**Trigger**: `use_module_names=True`

**Behavior**:
- Lifelines represent modules
- Messages show function names

---

### SWR_GEN_00022 - Recursive Call Handling
**Purpose**: Mark recursive calls in XMI

**Attribute**: `messageSort="reply"` for recursive calls

---

### SWR_GEN_00023 - XMI Metadata
**Purpose**: Include metadata in XMI document

**Elements**:
- Timestamp
- Source directory
- Tool information
- Package documentation

---

### SWR_GEN_00024 - XML Formatting
**Purpose**: Generate properly formatted XML

**Requirements**:
- Valid XML 1.0
- Proper indentation
- Escaped special characters
- UTF-8 encoding

---

### SWR_GEN_00025 - XMI File Extension
**Purpose**: Use correct file extension

**Extension**: `.xmi`

**MIME Type**: `application/XMI`

---

## Rhapsody-Specific Requirements (SWR_RH_00001 - SWR_RH_00005)

### SWR_RH_00001 - Rhapsody XMI 2.1 Compatibility
**Purpose**: Ensure XMI output is compatible with IBM Rhapsody 8.0+

**Implementation**: XMI 2.1 schema with OMG UML 2.1 namespace

**Features**:
- Uses `http://www.omg.org/spec/UML/20090901` namespace
- XMI version 2.1
- Proper GUID+ UUID format for all elements

---

### SWR_RH_00002 - Rhapsody Profile Support
**Purpose**: Support Rhapsody-specific profile elements

**Implementation**: Profile-related XMI elements in generated documents

**Features**:
- Nested package support via `--rhapsody-package-path`
- Proper package hierarchy in XMI structure

---

### SWR_RH_00003 - AUTOSAR Stereotype Support
**Purpose**: Support AUTOSAR-specific stereotypes in Rhapsody

**Implementation**: Stereotype elements for AUTOSAR components

**Future Enhancement**: Full AUTOSAR profile support

---

### SWR_RH_00004 - UUID-based Element IDs (GUID+ Format)
**Purpose**: Generate Rhapsody-compatible element IDs

**Format**: `GUID+<UUID>` (e.g., `GUID+_12345678-1234-5678-1234-567812345678`)

**Implementation**: `_generate_guid()` method in `RhapsodyXmiGenerator`

---

### SWR_RH_00005 - Rhapsody-specific Metadata
**Purpose**: Include Rhapsody-specific metadata in XMI

**Elements**:
- Model name (customizable via `--rhapsody-model-name`)
- Package path (customizable via `--rhapsody-package-path`)
- Timestamp and tool information

---

## Summary

**Total Requirements**: 35
- SWR_GEN_00001 - SWR_GEN_00025: 25 requirements
- SWR_MERMAID_00001 - SWR_MERMAID_00005: 5 requirements
- SWR_RH_00001 - SWR_RH_00005: 5 requirements

**Implementation Status**: ✅ All Implemented

**Package Structure**:
```
autosar_calltree.generators/
├── mermaid_generator.py     # SWR_GEN_00001 - SWR_GEN_00015, SWR_MERMAID_00001 - SWR_MERMAID_00005
└── rhapsody_generator.py    # SWR_GEN_00016 - SWR_GEN_00025, SWR_RH_00001 - SWR_RH_00005
```

**Key Features**:
- Mermaid sequence diagrams with opt/alt/loop blocks
- Module-level or function-level diagrams
- Rhapsody XMI 2.1 compliant output (OMG UML 2.1 namespace)
- GUID+ UUID format for all elements
- MessageOccurrenceSpecification for timing info
- Nested package support via --rhapsody-package-path
- Custom model name support via --rhapsody-model-name
- Function tables and metadata
- Text tree representations
