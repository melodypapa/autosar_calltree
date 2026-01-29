/*
 * Demo AUTOSAR C file for testing calltree
 */

#include "demo.h"

/* AUTOSAR-style function declarations */
FUNC(void, RTE_CODE) Demo_Init(void)
{
    /* Initialize subsystems */
    HW_InitHardware();
    SW_InitSoftware();
    COM_InitCommunication();
    Demo_InitVariables();

    return;
}

FUNC(void, RTE_CODE) Demo_InitVariables(void)
{
    /* Variable initialization */
    return;
}

FUNC(void, RTE_CODE) Demo_MainFunction(void)
{
    /* Main function loop */
    HW_ReadSensor(0);
    SW_ProcessData(NULL, 0);
    COM_SendCANMessage(0, NULL);
    Demo_Update();

    return;
}

FUNC(void, RTE_CODE) Demo_Update(void)
{
    /* Update state */
    SW_UpdateState(0);

    return;
}
