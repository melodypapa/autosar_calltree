/*
 * Complex AUTOSAR macros for testing edge cases
 * Covers SWR_PARSER_AUTOSAR_00004, SWR_PARSER_AUTOSAR_00010, SWR_PARSER_AUTOSAR_00013, SWR_PARSER_AUTOSAR_00014
 */

/* Function with nested parentheses in parameters */
FUNC(void, RTE_CODE) FunctionWithCallback(
    VAR(void, AUTOMATIC) (*callback)(VAR(uint32, AUTOMATIC)),
    VAR(uint32, AUTOMATIC) context
)
{
    /* Function with function pointer parameter */
    if (callback) {
        callback(context);
    }
    return;
}

/* Multiple parameters with nested macros */
FUNC(void, RTE_CODE) ComplexNestedParams(
    VAR(uint32, AUTOMATIC) param1,
    P2VAR(uint8, AUTOMATIC, APPL_DATA) buffer1,
    VAR(uint32, AUTOMATIC) (*transform)(VAR(uint8, AUTOMATIC)),
    P2CONST(uint8, AUTOMATIC, APPL_CONST) buffer2
)
{
    /* Complex nested parameter handling */
    return;
}

/* Whitespace variations - extra spaces */
FUNC(  void  ,  RTE_CODE  )  WhitespaceTest1  (  void  )
{
    return;
}

FUNC(void, RTE_CODE) WhitespaceTest2(  VAR  (  uint32  ,  AUTOMATIC  )  value  )
{
    return;
}

/* Pointer return with complex memory classes */
FUNC_P2VAR(uint8, AUTOMATIC, APPL_VAR) GetApplicationBuffer(void)
{
    static uint8 app_buffer[256];
    return app_buffer;
}

FUNC_P2CONST(uint32, RTE_CONST, CONFIG_VAR) GetReadOnlyConfig(void)
{
    static const uint32 config[10] = {0};
    return config;
}

/* Multiple functions with same name pattern (different static/non-static) */
STATIC FUNC(void, RTE_CODE) LocalHelper(VAR(uint32, AUTOMATIC) value)
{
    return;
}

FUNC(void, RTE_CODE) LocalHelper(VAR(uint32, AUTOMATIC) value)
{
    return;
}

/* Function with complex return types */
FUNC_P2VAR(uint32, AUTOMATIC, APPL_DATA) GetPointerArray(void)
{
    static uint32 array[100];
    return array;
}

FUNC_P2CONST(struct Config_s, AUTOMATIC, APPL_CONST) GetStructConfig(void)
{
    static const struct Config_s config = {0};
    return &config;
}
