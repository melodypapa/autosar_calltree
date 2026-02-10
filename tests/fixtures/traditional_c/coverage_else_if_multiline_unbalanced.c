// Test for lines 734-750: else if with multiline condition (unbalanced parens)
void test_else_if_multiline_unbalanced(void)
{
    if (x > 0) {
        Func1();
    } else if (x < 0 && y > 0 && z < 0
        && w > 0
    {
        Func2();
    }
}