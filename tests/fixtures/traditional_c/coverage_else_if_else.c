/* Test fixture for covering else if and else handling (lines 730-769) */

void test_else_if(void) {
    if (x > 0) {
        do_something();
    } else if (x < 0) {
        do_other();
    }
}

void test_else_if_multiline(void) {
    if (mode == 0x10) {
        func1();
    } else if ((mode == 0x20) ||
               (mode == 0x30)) {
        func2();
    }
}

void test_else_if_without_paren(void) {
    if (x > 0) {
        func1();
    } else if x < 0 {
        func2();
    }
}

void test_else(void) {
    if (x > 0) {
        do_something();
    } else {
        do_other();
    }
}

void test_else_only(void) {
    // This is syntactically invalid but should handle gracefully
    else {
        do_something();
    }
}