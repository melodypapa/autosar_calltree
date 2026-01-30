/*
 * AUTOSAR functions with parameters for testing
 * Covers SWR_PARSER_AUTOSAR_00005, SWR_PARSER_AUTOSAR_00006, SWR_PARSER_AUTOSAR_00007, SWR_PARSER_AUTOSAR_00008, SWR_PARSER_AUTOSAR_00009
 */

/* Function with VAR parameter */
FUNC(void, RTE_CODE) ProcessValue(VAR(uint32, AUTOMATIC) value)
{
    /* Process value */
    return;
}

/* Function with multiple VAR parameters */
FUNC(void, RTE_CODE) ProcessValues(VAR(uint8, AUTOMATIC) param1, VAR(uint16, AUTOMATIC) param2, VAR(uint32, AUTOMATIC) param3)
{
    /* Process multiple values */
    return;
}

/* Function with P2VAR parameter (pointer to writable) */
FUNC(void, RTE_CODE) WriteBuffer(P2VAR(uint8, AUTOMATIC, APPL_DATA) buffer)
{
    /* Write to buffer */
    return;
}

/* Function with P2CONST parameter (pointer to read-only) */
FUNC(uint32, RTE_CODE) ReadConfig(P2CONST(ConfigType, AUTOMATIC, APPL_CONST) config)
{
    /* Read from config */
    return 0;
}

/* Function with CONST parameter (const value) */
FUNC(void, RTE_CODE) SetTimeout(CONST(uint32, AUTOMATIC) timeout)
{
    /* Set timeout */
    return;
}

/* Mixed parameters: VAR, P2VAR, P2CONST, CONST */
FUNC(void, RTE_CODE) ComplexParameters(
    VAR(uint32, AUTOMATIC) mode,
    P2VAR(uint8, AUTOMATIC, APPL_DATA) output,
    P2CONST(uint8, AUTOMATIC, APPL_DATA) input,
    CONST(uint16, AUTOMATIC) length
)
{
    /* Complex parameter handling */
    return;
}

/* Traditional C parameters mixed with AUTOSAR (fallback) */
FUNC(void, RTE_CODE) MixedParameters(
    VAR(uint32, AUTOMATIC) autosar_param,
    uint8* traditional_param,
    const ConfigType* const_param
)
{
    /* Mixed style parameters */
    return;
}

/* Empty parameter list (void) */
FUNC(void, RTE_CODE) NoParameters(void)
{
    return;
}
