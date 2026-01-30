/*
 * Traditional C functions with function calls for testing
 * Covers SWR_PARSER_C_00008, SWR_PARSER_C_00009
 */

/* Simple function that calls other functions */
void caller_function(void)
{
    helper1();
    helper2();
    helper3();
}

/* Function with control structures that should not be extracted as calls */
void control_structures(uint32 value)
{
    if (value > 10) {
        handle_large_value();
    } else {
        handle_small_value();
    }

    for (uint32 i = 0; i < value; i++) {
        process_iteration(i);
    }

    while (value > 0) {
        value = decrement_value(value);
    }

    switch (value) {
        case 1:
            handle_case_1();
            break;
        case 2:
            handle_case_2();
            break;
        default:
            handle_default();
            break;
    }
}

/* Function with return statement (should not be extracted as call) */
uint32 function_with_return(void)
{
    return get_value();
}

/* Function that casts AUTOSAR types (should not be extracted) */
void function_with_autosar_type_casts(void)
{
    uint8* buffer = (uint8*)0x20000000;
    uint32 value = (uint32)buffer;
    uint16 length = sizeof(uint8);
}

/* Function with nested braces (should extract calls correctly) */
void function_with_nested_scopes(void)
{
    outer_function();

    if (1) {
        inner_function_1();

        if (2) {
            inner_function_2();
        }

        inner_function_3();
    }

    outer_function_2();
}

/* Function with RTE calls */
void function_with_rte_calls(void)
{
    Rte_Call_StartOperation();
    Rte_Write_Parameter_1(100);
    Rte_Read_Result_2(&result);
    Rte_Call_StopOperation();
}

/* Function with duplicate calls (should deduplicate) */
void function_with_duplicate_calls(void)
{
    helper_function();
    helper_function();
    helper_function();
}

/* Function that calls itself (recursive) */
void recursive_function(uint32 depth)
{
    if (depth > 0) {
        recursive_function(depth - 1);
    }
}

/* Function with complex expressions */
void complex_expression_function(void)
{
    uint32 result = calculate(1, 2) + compute(3, 4);
    process(&result);
}

/* Empty function body */
void empty_function(void)
{
}

/* Function with string literals (should not extract parentheses in strings) */
void function_with_strings(void)
{
    printf("This has (parentheses) in it\n");
    log_message("Value: %d", get_value());
}
