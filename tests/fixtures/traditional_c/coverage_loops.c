/* Test fixture for covering loop detection (lines 781-792) */

void test_for_loop(void) {
    for (i = 0; i < 10; i++) {
        Process_Element();
    }
}

void test_for_without_semicolon(void) {
    for (i = 0 i < 10 i++) {
        Process_Element();
    }
}

void test_for_without_paren(void) {
    for {
        Process_Element();
    }
}

void test_while_loop(void) {
    while (count > 0) {
        Process_Element();
        count--;
    }
}

void test_while_without_paren(void) {
    while count > 0 {
        Process_Element();
        count--;
    }
}