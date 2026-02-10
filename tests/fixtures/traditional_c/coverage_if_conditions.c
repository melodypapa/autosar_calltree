/* Test fixture for covering if condition extraction (lines 718-728) */

void test_simple_if(void) {
    if (x > 0) {
        do_something();
    }
}

void test_if_with_condition(void) {
    if (mode == 0x05) {
        COM_SendMessage();
    }
}

void test_if_without_paren(void) {
    if {
        // This is unusual but should handle gracefully
        do_something();
    }
}

void test_if_with_multiline_condition(void) {
    if ((mode == 0x05) &&
        (length > 10)) {
        COM_SendMessage();
    }
}

void test_if_with_unbalanced_parens(void) {
    if (func(x) > 0 && func(y) {
        do_something();
    }
}