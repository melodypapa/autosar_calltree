/* Test fixture for covering nested blocks (lines 802-810, 846-848) */

void test_nested_if(void) {
    if (x > 0) {
        if (y > 0) {
            if (z > 0) {
                do_something();
            }
        }
    }
}

void test_nested_parens(void) {
    if (((a > 0) && (b < 10)) || ((c > 0) && (d < 10))) {
        do_something();
    }
}

void test_nested_loops(void) {
    for (i = 0; i < 10; i++) {
        for (j = 0; j < 10; j++) {
            Process_Element();
        }
    }
}

void test_if_in_loop(void) {
    for (i = 0; i < 10; i++) {
        if (data[i] > 0) {
            Process_Element();
        }
    }
}

void test_loop_in_if(void) {
    if (mode == 0x05) {
        for (i = 0; i < 10; i++) {
            Process_Element();
        }
    }
}