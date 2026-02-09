/* Test fixture for loop parsing */

// Simple for loop
void Process_Array(uint8* data, uint32 length)
{
    for (uint32 i = 0; i < length; i++) {
        Process_Element(data[i]);
    }
}

// For loop with multiple statements
void Process_With_Multiple_Calls(uint8* data, uint32 count)
{
    for (uint32 i = 0; i < count; i++) {
        Validate_Element(data[i]);
        Process_Element(data[i]);
        Log_Element(i, data[i]);
    }
}

// While loop
void Process_While(uint8* data, uint32 length)
{
    uint32 i = 0;
    while (i < length) {
        Process_Element(data[i]);
        i++;
    }
}

// Nested loops
void Process_Nested(uint8** matrix, uint32 rows, uint32 cols)
{
    for (uint32 i = 0; i < rows; i++) {
        for (uint32 j = 0; j < cols; j++) {
            Process_Element(matrix[i][j]);
        }
    }
}

// Loop with condition
void Process_With_Condition(uint8* data, uint32 length)
{
    for (uint32 i = 0; i < length && data[i] != 0; i++) {
        if (data[i] > 0x10) {
            Process_Element(data[i]);
        }
    }
}

// Mixed if and loop
void Process_Mixed(uint8* data, uint32 length)
{
    if (length > 0) {
        for (uint32 i = 0; i < length; i++) {
            Process_Element(data[i]);
        }
    }
}