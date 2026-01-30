/*
 * Traditional C functions with comments for testing
 * Covers SWR_PARSER_C_00005
 */

/* Multi-line comment before function */
void before_multiline_comment(void)
{
    return;
}

/*
 * This is a multi-line comment
 * that spans multiple lines
 * and contains code-like text: void fake_func(void);
 */
void after_multiline_comment(void)
{
    return;
}

// Single-line comment before function
void before_single_line_comment(void)
{
    return;
}

/* Function with embedded comments in body */
void function_with_embedded_comments(void)
{
    /* This is a comment inside the function body */
    uint32 value = 0; // End-of-line comment
    /*
     * Multi-line comment in body
     * Contains: uint8 fake = 0;
     */
    return;
}

/* Function that has /* fake */ comment inside */
void function_with_weird_comments(void)
{
    return;
}
