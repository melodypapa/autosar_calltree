/* Test file to cover remaining lines in c_parser.py */

// Test for line 326-328: multiline function with non-type return type line
// This triggers the else: break branch when prev_line doesn't match ^[\w\s\*]+$
struct ComplexType
{
    int field;
};

// This multiline function has a struct type on previous line
// which doesn't match ^[\w\s\*]+$ pattern, triggering line 326-328
struct ComplexType
multiline_with_struct(int param)
{
    return param;
}

// Test for line 440: return_type is a C keyword (static is a C keyword)
static void static_return_function(void)
{
    return;
}

// Test for line 458: function_name is a control structure (typedef is a C keyword)
void typedef_function(void)
{
    return;
}

// Test for lines 730-766: else if with multiline condition
void test_else_if_multiline_condition(void)
{
    int x = 0;
    int y = 0;

    if (x > 0)
    {
        Func1();
    }
    else if (x < 0 &&
             y > 0 &&
             z > 0)
    {
        Func2();
    }
}

// Test for line 788: for loop without semicolon (fallback)
void test_for_no_semicolon(void)
{
    for (int i = 0; i < 10)
    {
        Func1();
    }
}

// Test for lines 805-806: while loop fallback without closing paren
void test_while_no_closing_paren(void)
{
    while (count > 0 &&
           index < limit
    {
        Func1();
    }
}

// Test for line 826: RTE call update existing with conditional
void test_rte_update_conditional(void)
{
    Rte_Call_StartOperation();  // First call - non-conditional

    if (mode == 0x05)
    {
        Rte_Call_StartOperation();  // Same call - should update with conditional flag
    }
}

// Test for lines 846-848: nested blocks with brace depth tracking
void test_nested_blocks_depth(void)
{
    if (x > 0)
    {
        if (y > 0)
        {
            {
                Func1();
            }
        }
    }
}

// Test for line 875: function call with AUTOSAR type name (should be skipped)
void test_autosar_type_as_call(void)
{
    uint8(value);  // uint8 is AUTOSAR type, should be skipped
    Func1();
}

// Test for lines 879-881: RTE call update loop condition
void test_rte_update_loop(void)
{
    Rte_Call_Process();  // First call - non-loop

    for (int i = 0; i < 10; i++)
    {
        Rte_Call_Process();  // Same call - should update with loop flag
    }
}

// Test for combined conditional and loop on RTE calls
void test_rte_conditional_loop(void)
{
    for (int i = 0; i < 10; i++)
    {
        if (x > 0)
        {
            Rte_Call_Operation();  // Should have both conditional and loop flags
        }
    }
}