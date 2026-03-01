/*
 * Hardware Module - AUTOSAR Demo
 * Contains hardware-related functions for demonstration
 * Demonstrates: conditional initialization, sensor arrays, actuator control
 */

#include "demo.h"

/* Hardware initialization functions */
FUNC(void, RTE_CODE) HW_InitClock(void)
{
    /* Initialize system clocks */
    return;
}

FUNC(void, RTE_CODE) HW_InitGPIO(void)
{
    /* Initialize GPIO pins */
    return;
}

FUNC(void, RTE_CODE) HW_InitPWM(void)
{
    /* Initialize PWM peripherals */
    return;
}

FUNC(void, RTE_CODE) HW_InitADC(void)
{
    /* Initialize ADC peripherals */
    return;
}

FUNC(void, RTE_CODE) HW_InitHardware(VAR(uint32, AUTOMATIC) clock_freq, VAR(uint32, AUTOMATIC) gpio_mask)
{
    /* Master hardware initialization with conditional logic */
    if (clock_freq > 0) {
        HW_InitClock();
    }

    if (gpio_mask > 0) {
        HW_InitGPIO();
    }

    HW_InitPWM();
    HW_InitADC();

    return;
}

/* Hardware control functions */
FUNC(uint32, AUTOMATIC) HW_ReadSensor(VAR(uint32, AUTOMATIC) sensor_id)
{
    /* Read sensor value */
    uint32 value = 0;

    /* Conditional sensor reading based on ID */
    if (sensor_id < 10) {
        /* Analog sensor */
        HW_EnableInterrupt(sensor_id);
    } else if (sensor_id < 20) {
        /* Digital sensor */
        HW_DisableInterrupt(sensor_id);
    }

    /* Sensor reading logic here */
    value = sensor_id * 2;

    return value;
}

FUNC(void, RTE_CODE) HW_SetActuator(VAR(uint32, AUTOMATIC) actuator_id, VAR(uint32, AUTOMATIC) value)
{
    /* Set actuator value with conditional logic */
    if (value > 0) {
        HW_EnableInterrupt(actuator_id);
    } else {
        HW_DisableInterrupt(actuator_id);
    }

    return;
}

FUNC(void, RTE_CODE) HW_EnableInterrupt(VAR(uint32, AUTOMATIC) irq_id)
{
    /* Enable specific interrupt */
    return;
}

FUNC(void, RTE_CODE) HW_DisableInterrupt(VAR(uint32, AUTOMATIC) irq_id)
{
    /* Disable specific interrupt */
    return;
}

FUNC(void, RTE_CODE) HW_ReadSensorArray(P2VAR(uint32, AUTOMATIC, APPL_DATA) sensor_ids, VAR(uint32, AUTOMATIC) count)
{
    /* Read multiple sensors in a loop */
    uint32 i = 0;

    for (i = 0; i < count; i++) {
        sensor_ids[i] = HW_ReadSensor(sensor_ids[i]);
    }

    return;
}

FUNC(void, RTE_CODE) HW_CalibrateSensors(VAR(uint32, AUTOMATIC) sensor_count)
{
    /* Calibrate sensors with nested loop */
    uint32 i = 0;
    uint32 j = 0;

    for (i = 0; i < sensor_count; i++) {
        for (j = 0; j < 5; j++) {
            HW_ReadSensor(i);
        }
    }

    return;
}
