/*
 * Basic AUTOSAR function declarations for testing
 * Covers SWR_PARSER_AUTOSAR_00001, SWR_PARSER_AUTOSAR_00002, SWR_PARSER_AUTOSAR_00003
 */

/* Simple void function with no parameters */
FUNC(void, RTE_CODE) SimpleVoidFunction(void)
{
    return;
}

/* Function with return type */
FUNC(uint32, AUTOMATIC) GetValue(void)
{
    uint32 result = 0;
    return result;
}

/* Static function */
STATIC FUNC(uint8, CODE) StaticInternalFunction(void)
{
    uint8 value = 0;
    return value;
}

/* FUNC_P2VAR - returns pointer to writable memory */
FUNC_P2VAR(uint8, AUTOMATIC, APPL_VAR) GetBuffer(void)
{
    static uint8 buffer[100];
    return buffer;
}

/* FUNC_P2CONST - returns pointer to read-only memory */
FUNC_P2CONST(ConfigType, AUTOMATIC, APPL_CONST) GetConfig(void)
{
    static const ConfigType config = {0};
    return &config;
}

/* Static FUNC_P2VAR */
STATIC FUNC_P2VAR(uint32, RTE_VAR, DEMO_VAR) GetStaticBuffer(void)
{
    static uint32 buffer[50];
    return buffer;
}
