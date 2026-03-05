/*
 * Demo Application using AUTOSAR headers
 * Tests the preprocessor integration with #include directives
 */

#include "autosar_types.h"
#include "autosar_com.h"
#include "autosar_mcal.h"

/*============================================================================
 * Application Variables
 *===========================================================================*/
static uint32 g_systemState = 0U;
static boolean g_initialized = FALSE;

/*============================================================================
 * Application Functions
 *===========================================================================*/

/**
 * System initialization function
 */
FUNC(void, RTE_CODE) APP_InitSystem(void)
{
    /* Initialize MCU */
    Mcu_Init();
    Mcu_InitClock();

    /* Initialize hardware layer */
    Dio_Init();
    Dio_InitGPIO();

    /* Initialize communication */
    Com_Init(NULL_PTR);
    Com_InitCAN();

    g_initialized = TRUE;
    g_systemState = 1U;
}

/**
 * Main application function (cyclic)
 */
FUNC(void, RTE_CODE) APP_MainFunction(void)
{
    if (!g_initialized) {
        return;
    }

    /* Process communication */
    Com_MainFunction();

    /* Read ADC channel */
    Adc_ValueType adcValue = Adc_ReadChannel(0);

    /* Set PWM output based on ADC */
    if (adcValue > 512U) {
        Pwm_SetDutyCycle(0, 75U);
    } else {
        Pwm_SetDutyCycle(0, 25U);
    }
}

/**
 * Update system state
 */
FUNC(Std_ReturnType, RTE_CODE) APP_UpdateState(VAR(uint32, AUTOMATIC) newState)
{
    Std_ReturnType status = E_NOT_OK;

    if (newState < 10U) {
        g_systemState = newState;
        status = E_OK;
    }

    return status;
}

/**
 * Send diagnostic message
 */
FUNC(void, RTE_CODE) APP_SendDiagnostic(P2VAR(uint8, AUTOMATIC, APPL_DATA) data, VAR(uint16, AUTOMATIC) length)
{
    PduR_PduInfoType pduInfo;

    pduInfo.id = 0x7DFU;
    pduInfo.sdu = data;
    pduInfo.length = length;

    Com_SendPdu(0, &pduInfo);
}
