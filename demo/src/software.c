/*
 * Software Module - AUTOSAR Demo
 * Contains software/logic-related functions for demonstration
 * Demonstrates: nested loops, complex conditionals, multiple return paths
 */

#include "demo.h"

/* Software state management */
FUNC(void, RTE_CODE) SW_InitState(void)
{
    /* Initialize software state machine */
    return;
}

FUNC(void, RTE_CODE) SW_InitConfig(void)
{
    /* Initialize software configuration */
    return;
}

FUNC(void, RTE_CODE) SW_InitSoftware(VAR(uint8, AUTOMATIC) state, VAR(uint8, AUTOMATIC) config)
{
    /* Master software initialization */
    SW_InitState();
    SW_InitConfig();

    return;
}

/* Data processing functions */
FUNC(uint32, AUTOMATIC) SW_ProcessData(P2VAR(uint8, AUTOMATIC, APPL_DATA) data, VAR(uint32, AUTOMATIC) length)
{
    /* Process input data */
    uint32 result = 0;
    uint32 i = 0;

    /* Loop through data with nested loop */
    for (i = 0; i < length; i++) {
        if (data[i] > 0) {
            SW_ValidateData(&data[i], 1);
        }
    }

    /* Data processing logic here */
    result = length;

    return result;
}

FUNC(void, RTE_CODE) SW_UpdateState(VAR(uint32, AUTOMATIC) new_state)
{
    /* Update internal state */
    uint32 current_state = SW_GetState();

    /* Conditional update based on current state */
    if (current_state == 0) {
        SW_InitState();
    } else if (current_state == new_state) {
        /* State already matches */
        return;
    } else {
        SW_InitConfig();
    }

    return;
}

FUNC(uint32, AUTOMATIC) SW_GetState(void)
{
    /* Get current state */
    uint32 state = 0;

    return state;
}

/* Calculation functions */
FUNC(uint32, AUTOMATIC) SW_CalculateAverage(P2VAR(uint32, AUTOMATIC, APPL_DATA) values, VAR(uint32, AUTOMATIC) count)
{
    /* Calculate average of values */
    uint32 sum = 0;
    uint32 average = 0;
    uint32 i = 0;

    /* Loop to calculate sum */
    for (i = 0; i < count; i++) {
        sum = sum + values[i];
    }

    /* Conditional division */
    if (count > 0) {
        average = sum / count;
    }

    return average;
}

FUNC(void, RTE_CODE) SW_ValidateData(P2VAR(uint8, AUTOMATIC, APPL_DATA) data, VAR(uint32, AUTOMATIC) length)
{
    /* Validate data integrity */
    uint32 i = 0;

    /* While loop for validation */
    i = 0;
    while (i < length) {
        if (data[i] == 0) {
            /* Invalid data found */
            return;
        }
        i++;
    }

    return;
}

FUNC(void, RTE_CODE) SW_ProcessBatch(P2VAR(uint8, AUTOMATIC, APPL_DATA) data, VAR(uint32, AUTOMATIC) length)
{
    /* Process data in batches */
    uint32 batch_size = 10;
    uint32 offset = 0;

    /* Nested loop for batch processing */
    while (offset < length) {
        for (uint32 i = 0; i < batch_size && (offset + i) < length; i++) {
            SW_ProcessData(&data[offset + i], 1);
        }
        offset = offset + batch_size;
    }

    return;
}
