/*
 * Demo AUTOSAR C file for testing calltree
 * Demonstrates: conditional calls, loop calls, complex conditions
 * Module: DemoModule (main application entry point)
 */

#include "demo.h"

/* AUTOSAR-style function declarations */
FUNC(void, RTE_CODE) Demo_Init(void)
{
    /* Initialize subsystems - demonstrates cross-module calls */
    /* Calls to HardwareModule */
    HW_InitHardware(0x1000, 0x2000);

    /* Calls to SoftwareModule */
    SW_InitSoftware(0x01, 0xFF);

    /* Calls to CommunicationModule */
    COM_InitCommunication(115200, 0x100);

    /* Local function call */
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
    /* Main function loop - demonstrates cross-module coordination */
    uint32 sensor_count = 0;

    /* Cross-module calls */
    HW_ReadSensor(0x01);           /* HardwareModule */
    SW_ProcessData((uint8*)0x20001000, 0x64);  /* SoftwareModule */
    COM_SendCANMessage(0x123, (uint8*)0x20002000);  /* CommunicationModule */

    /* Optional call based on mode */
    if (0x05 > 0x00) {
        Demo_Update(0x05);  /* DemoModule (local) */
    }

    /* Loop through sensors - demonstrates repeated cross-module calls */
    for (sensor_count = 0; sensor_count < 10; sensor_count++) {
        HW_ReadSensor(sensor_count);           /* HardwareModule */
        SW_ProcessData((uint8*)0x20001000, 0x64);  /* SoftwareModule */
    }

    /* Multi-line condition */
    if (sensor_count > 5 &&
        sensor_count < 20) {
        Demo_Update(0x05);  /* DemoModule (local) */
    }

    return;
}

FUNC(void, RTE_CODE) Demo_Update(VAR(uint32, AUTOMATIC) update_mode)
{
    /* Update state with mode - demonstrates coordination across modules */
    SW_UpdateState(update_mode);  /* SoftwareModule */

    /* Optional LIN message based on update mode */
    if (update_mode == 0x05) {
        COM_SendLINMessage(0x456, (uint8*)0x20003000);  /* CommunicationModule */
    }

    /* Nested conditional */
    if (update_mode == 0x05) {
        if (sensor_count > 5) {
            COM_SendCANMessage(0x123, (uint8*)0x20002000);  /* CommunicationModule */
        } else {
            COM_EnableTX(0x01);  /* CommunicationModule */
        }
    }

    return;
}

FUNC(void, RTE_CODE) Demo_ProcessLoop(VAR(uint32, AUTOMATIC) iterations)
{
    /* Demonstrate while loop with cross-module calls */
    uint32 i = 0;
    while (i < iterations) {
        HW_ReadSensor(i);           /* HardwareModule */
        SW_ProcessData((uint8*)0x20001000, 0x64);  /* SoftwareModule */
        i++;
    }

    return;
}
