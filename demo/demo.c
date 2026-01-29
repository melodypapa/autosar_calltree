/*
 * Demo AUTOSAR C file for testing calltree
 */

#include "demo.h"

/* AUTOSAR-style function declarations */
FUNC(void, RTE_CODE) Demo_Init(void)
{
    /* Initialize subsystems */
    HW_InitHardware(0x1000, 0x2000);
    SW_InitSoftware(0x01, 0xFF);
    COM_InitCommunication(115200, 0x100);
    Demo_InitVariables(0x00);

    return;
}

FUNC(void, RTE_CODE) Demo_InitVariables(VAR(uint32, AUTOMATIC) config_mode)
{
    /* Variable initialization with config mode */
    return;
}

FUNC(void, RTE_CODE) Demo_MainFunction(void)
{
    /* Main function loop */
    HW_ReadSensor(0x01);
    SW_ProcessData((uint8*)0x20001000, 0x64);
    COM_SendCANMessage(0x123, (uint8*)0x20002000);
    Demo_Update(0x05);

    return;
}

FUNC(void, RTE_CODE) Demo_Update(VAR(uint32, AUTOMATIC) update_mode)
{
    /* Update state with mode */
    SW_UpdateState(update_mode);

    return;
}
