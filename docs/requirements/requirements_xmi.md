# XMI Generator Requirements

## SWR_XMI_00001: XMI 2.5 Compliance

**Title**: Generate XMI 2.5 compliant XML documents

**Maturity**: accept

**Description**:
The XMI generator shall produce XMI 2.5 compliant XML documents that conform to the OMG XMI specification and can be imported into UML modeling tools like Enterprise Architect, Visual Paradigm, MagicDraw, etc.

**Rationale**:
XMI 2.5 is the standard interchange format for UML models. Compliance ensures the generated documents can be used across different UML tools without compatibility issues.

**Functional Requirements**:

1. **XMI Namespace Declarations**:
   - Document shall declare correct XMI namespace: `http://www.omg.org/spec/XMI/20131001`
   - Document shall declare correct UML namespace: `http://www.eclipse.org/uml2/5.0.0/UML`
   - XMI version shall be set to "4.0"

2. **XMI Structure**:
   - Root element shall be `xmi:XMI`
   - Model element shall be `uml:Model`
   - Interaction element shall be `uml:Interaction`

3. **XML Formatting**:
   - Output shall be well-formed XML
   - Output shall be pretty-printed with proper indentation
   - XML declaration shall be included

**Implementation Notes**:

- Implemented in `src/autosar_calltree/generators/xmi_generator.py`
- Uses `xml.etree.ElementTree` for XML generation
- Uses `xml.dom.minidom` for pretty-printing
- Namespace constants defined at class level

**Example Output**:

```xml
<?xml version="1.0" ?>
<xmi:XMI xmi:version="4.0" xmlns:xmi="http://www.omg.org/spec/XMI/20131001" xmlns:uml="http://www.eclipse.org/uml2/5.0.0/UML">
  <uml:Model xmi:id="calltree_1" name="CallTree_Demo_Init" visibility="public">
    <uml:packagedElement xmi:id="calltree_2" name="Sequence_Demo_Init" visibility="public">
      <uml:Interaction xmi:id="calltree_3" name="CallSequence_Demo_Init" visibility="public" isReentrant="false">
        <!-- Lifelines and messages go here -->
      </uml:Interaction>
    </uml:packagedElement>
  </uml:Model>
</xmi:XMI>
```

---

## SWR_XMI_00002: Sequence Diagram Representation

**Title**: Represent UML sequence diagrams with lifelines and messages

**Maturity**: accept

**Description**:
The XMI generator shall create UML sequence diagrams with lifelines representing participants and messages representing function calls.

**Rationale**:
Sequence diagrams are the standard way to visualize call flows. XMI representation allows these diagrams to be imported into UML tools for further editing and visualization.

**Functional Requirements**:

1. **Lifeline Creation**:
   - One lifeline per unique participant (function or module)
   - Lifeline name shall match participant name
   - Lifelines shall include `represents` property
   - Participants shall appear in order of first encounter

2. **Message Creation**:
   - Each function call shall be represented as a UML message
   - Message name shall be the function name
   - Message signature shall include parameters
   - Messages shall have `sendEvent` and `receiveEvent`
   - Message sort shall be "synchCall" for synchronous calls

3. **Module Support**:
   - When `use_module_names` is enabled, lifelines represent SW modules
   - Function names shall appear in message signatures
   - When disabled, lifelines represent individual functions

4. **Recursive Calls**:
   - Recursive calls shall be marked with `messageSort="reply"`

**Implementation Notes**:

- Implemented in `_create_lifelines()` and `_create_messages()` methods
- Participant mapping stored in `self.participant_map`
- Message counter for unique IDs

**Example Output**:

```xml
<uml:lifeline xmi:id="calltree_4" name="DemoModule" visibility="public">
  <uml:represents xmi:id="calltree_5" name="DemoModule"/>
</uml:lifeline>
<uml:lifeline xmi:id="calltree_6" name="HardwareModule" visibility="public">
  <uml:represents xmi:id="calltree_7" name="HardwareModule"/>
</uml:lifeline>
<uml:message xmi:id="calltree_8" name="HW_InitHardware" visibility="public" messageSort="synchCall" signature="HW_InitHardware(clock_freq, gpio_mask)">
  <uml:sendEvent xmi:id="calltree_9"/>
  <uml:receiveEvent xmi:id="calltree_10"/>
</uml:message>
```

---

## SWR_XMI_00003: Opt Block Support (Combined Fragments)

**Title**: Represent conditional calls using UML combined fragments with opt operator

**Maturity**: accept

**Description**:
The XMI generator shall represent conditional function calls (inside `if`/`else` statements) using UML combined fragments with the `opt` operator, displaying the actual condition text.

**Rationale**:
Conditional calls represent optional execution paths. UML combined fragments with `opt` operator are the standard way to represent this in UML sequence diagrams. The condition text provides context about when the call is executed.

**Functional Requirements**:

1. **Combined Fragment Creation**:
   - Conditional calls shall be wrapped in `uml:fragment` elements
   - Fragment `interactionOperator` shall be set to "opt"
   - Fragment shall have `name` attribute set to "opt"

2. **Operand Creation**:
   - Each combined fragment shall have one `uml:operand` element
   - Operand `name` shall display the condition text from the `if` statement
   - If condition text is not available, operand name shall default to "condition"

3. **Message Placement**:
   - Messages inside opt blocks shall be children of the operand element
   - Messages shall retain all standard attributes (name, signature, events)
   - Nested opt blocks shall be represented as nested combined fragments

4. **Condition Text**:
   - Condition text shall be extracted from the `if` statement
   - For `else if`, the condition text shall be displayed
   - For `else`, the operand name shall be "else"

**Implementation Notes**:

- Implemented in `_create_messages()` method
- Checks `child.is_optional` flag to determine opt block wrapping
- Uses `child.condition` field for operand name
- Supports nested opt blocks via recursive `traverse_opt()` function

**Example Output**:

```xml
<uml:fragment xmi:id="calltree_20" name="opt" visibility="public" interactionOperator="opt">
  <uml:operand xmi:id="calltree_21" name="update_mode == 0x05" visibility="public">
    <uml:message xmi:id="calltree_22" name="COM_SendLINMessage" visibility="public" messageSort="synchCall" signature="COM_SendLINMessage(msg_id, data)">
      <uml:sendEvent xmi:id="calltree_23"/>
      <uml:receiveEvent xmi:id="calltree_24"/>
    </uml:message>
  </uml:operand>
</uml:fragment>
```

**Nested Opt Blocks Example**:

```xml
<uml:fragment xmi:id="calltree_30" name="opt" visibility="public" interactionOperator="opt">
  <uml:operand xmi:id="calltree_31" name="mode > 0x00" visibility="public">
    <uml:message xmi:id="calltree_32" name="Demo_Update" visibility="public" messageSort="synchCall" signature="Demo_Update(mode)">
      <uml:sendEvent xmi:id="calltree_33"/>
      <uml:receiveEvent xmi:id="calltree_34"/>
    </uml:message>
    <uml:fragment xmi:id="calltree_35" name="opt" visibility="public" interactionOperator="opt">
      <uml:operand xmi:id="calltree_36" name="mode == 0x05" visibility="public">
        <uml:message xmi:id="calltree_37" name="COM_SendLINMessage" visibility="public" messageSort="synchCall" signature="COM_SendLINMessage(msg_id, data)">
          <uml:sendEvent xmi:id="calltree_38"/>
          <uml:receiveEvent xmi:id="calltree_39"/>
        </uml:message>
      </uml:operand>
    </uml:fragment>
  </uml:operand>
</uml:fragment>
```

**Error Handling**:

- Missing condition text shall default to "condition"
- Malformed opt blocks shall not crash the generator
- Nested opt blocks shall be handled correctly

**Limitations**:

- Only `opt` operator is implemented (not `alt`, `loop`, etc.)
- Only `if`/`else if`/`else` statements are tracked (not `switch`/`case`)
- Guard conditions are displayed as text (not evaluated)

---

## Traceability

| Requirement ID | Test ID | Test Function | Status |
|----------------|---------|---------------|--------|
| SWR_XMI_00001 | SWUT_XMI_00001 | test_SWUT_XMI_00001_xmi_namespace_compliance | ✅ Pass |
| SWR_XMI_00002 | SWUT_XMI_00002 | test_SWUT_XMI_00002_sequence_diagram_representation | ✅ Pass |
| SWR_XMI_00003 | SWUT_XMI_00003 | test_SWUT_XMI_00003_opt_block_support | ✅ Pass |

## Revision History

| Date | Version | Author | Change Description |
|------|---------|--------|-------------------|
| 2026-02-04 | 1.0 | Claude | Initial version - 3 requirements covering XMI generation with opt block support |