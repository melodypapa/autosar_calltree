/* Test file to trigger fallback code paths in if/else if handling */

// Test for line 728: if statement fallback without brace
void test_if_fallback_no_brace(void)
{
    if (x > 0)
        Func1();
}

// Test for line 766: else if fallback without closing paren
void test_else_if_no_paren(void)
{
    if (x > 0)
    {
        Func1();
    }
    else if (x < 0 && y > 0
    {
        Func2();
    }
}

// Test for line 805-806: while loop fallback without closing paren
void test_while_no_paren(void)
{
    while (count > 0 &&
           index < limit
    {
        Func1();
    }
}