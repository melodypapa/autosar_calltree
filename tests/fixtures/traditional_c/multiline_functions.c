/* Test fixture for multi-line function prototype parsing */

// Return type on separate line
Std_ReturnType
COM_SendMessage(uint32 messageId,
                uint8* data,
                uint16 length)
{
    return COM_SendCANMessage(messageId, data, length);
}

// Function name on separate line
static uint8
Internal_GetValue(
    uint32 index)
{
    return 0x00;
}

// Parameters spanning multiple lines
void
Complex_Function_With_Many_Parameters(
    uint8 param1,
    uint16 param2,
    uint32 param3,
    uint8* ptr1,
    const uint8* ptr2,
    uint32 length,
    uint32 flags)
{
    if (param1 > 0) {
        Internal_GetValue(param2);
    }
}

// Multi-line with complex condition
void
Function_With_Multiline_Condition(uint32 mode,
                                  uint32 length)
{
    if (mode == 0x05 &&
        length > 10) {
        COM_SendMessage(mode, (uint8*)&length, sizeof(length));
    }

    if (mode == 0x10 ||
        mode == 0x20) {
        Internal_GetValue(mode);
    }

    if ((mode & 0xFF) == 0x05 &&
        (length > 10 && length < 100)) {
        Complex_Function_With_Many_Parameters(
            mode,
            length,
            0,
            NULL,
            NULL,
            0,
            0);
    }
}