/*
 * MCU Driver Implementation (stub)
 */

#include "autosar_mcal.h"

FUNC(void, RTE_CODE) Mcu_Init(void)
{
    /* Initialize MCU */
}

FUNC(void, RTE_CODE) Mcu_InitClock(void)
{
    /* Initialize clock system */
}

FUNC(Std_ReturnType, RTE_CODE) Mcu_SetMode(VAR(Mcu_ModeType, AUTOMATIC) mode)
{
    return E_OK;
}

FUNC(void, RTE_CODE) Mcu_SetClockMode(VAR(Mcu_ClockType, AUTOMATIC) mode)
{
    /* Set clock mode */
}

FUNC(Mcu_ResetType, RTE_CODE) Mcu_GetResetSource(void)
{
    return 0U;
}
