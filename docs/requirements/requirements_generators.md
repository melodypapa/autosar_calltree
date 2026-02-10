# Generators Package Requirements

**Package**: `autosar_calltree.generators`
**Source Files**: `mermaid_generator.py`, `xmi_generator.py`
**Requirements**: SWR_GEN_00001 - SWR_GEN_00025 (25 requirements)

---

## Overview

The generators package provides output generation functionality, creating Mermaid sequence diagrams and XMI/UML 2.5 documents from call tree analysis results.

**Core Classes**:
- `MermaidGenerator` - Mermaid sequence diagram generation
- `XMIGenerator` - XMI/UML 2.5 document generation

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

## XMI Generator (SWR_GEN_00016 - SWR_GEN_00025)

### SWR_GEN_00016 - XMI 2.5 Document Generation
**Purpose**: Generate XMI/UML 2.5 sequence diagrams

**Method**: `generate(analysis_result, output_path)`

**Output**: XML file with XMI 2.5 format

**Implementation**: `XMIGenerator`

---

### SWR_GEN_00017 - XMI Namespaces and Schema
**Purpose**: Use correct XMI and UML namespaces

**Namespaces**:
- `xmlns:uml="http://www.eclipse.org/uml2/5.0.0/UML"`
- `xmlns:xmi="http://www.omg.org/spec/XMI/20131001"`
- `xmlns:xmi="http://www.omg.org/spec/XMI/20110701"`

**XMI Version**: 4.0 (or 2.5 compatible)

---

### SWR_GEN_00018 - UML Lifeline Generation
**Purpose**: Generate UML lifelines for participants

**Elements**:
- `uml:Lifeline` with unique ID
- `name`: Participant name (function or module)
- `represents`: Property reference

---

### SWR_GEN_00019 - UML Message Generation
**Purpose**: Generate UML messages for calls

**Elements**:
- `uml:Message` with unique ID
- `name`: Function name with parameters
- `messageSort`: "synchCall" for calls
- `sendEvent`: Source lifeline event
- `receiveEvent`: Target lifeline event

---

### SWR_GEN_00020 - XMI Opt Block Support
**Purpose**: Generate UML combined fragments for conditional calls

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

## Summary

**Total Requirements**: 25
**Implementation Status**: ✅ All Implemented

**Package Structure**:
```
autosar_calltree.generators/
├── mermaid_generator.py    # SWR_GEN_00001 - SWR_GEN_00015 (Mermaid)
└── xmi_generator.py        # SWR_GEN_00016 - SWR_GEN_00025 (XMI)
```

**Key Features**:
- Mermaid sequence diagrams with opt/alt/loop blocks
- Module-level or function-level diagrams
- XMI/UML 2.5 compliant output
- Function tables and metadata
- Text tree representations
