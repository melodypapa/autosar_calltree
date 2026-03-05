/*
 * Hardware Abstraction Layer Header File
 * AUTOSAR MCAL interface definitions
 */

#ifndef AUTOSAR_MCAL_H
#define AUTOSAR_MCAL_H

#include "autosar_types.h"

/*============================================================================
 * MCU Types
 *===========================================================================*/
typedef uint16 Mcu_ModeType;
typedef uint32 Mcu_ClockType;
typedef uint32 Mcu_ResetType;

#define MCU_MODE_RUN      (0U)
#define MCU_MODE_SLEEP    (1U)
#define MCU_MODE_STANDBY  (2U)

/*============================================================================
 * DIO Types
 *===========================================================================*/
typedef uint8 Dio_PortLevel;
typedef uint16 Dio_ChannelType;
typedef uint32 Dio_PortType;

/*============================================================================
 * ADC Types
 *===========================================================================*/
typedef uint16 Adc_ChannelType;
typedef uint16 Adc_ValueType;
typedef uint32 Adc_GroupType;

/*============================================================================
 * PWM Types
 *===========================================================================*/
typedef uint8 Pwm_ChannelType;
typedef uint16 Pwm_DutyType;
typedef uint32 Pwm_FrequencyType;

/*============================================================================
 * MCU Function Declarations
 *===========================================================================*/
FUNC(void, RTE_CODE) Mcu_Init(void);
FUNC(void, RTE_CODE) Mcu_InitClock(void);
FUNC(Std_ReturnType, RTE_CODE) Mcu_SetMode(Mcu_ModeType mode);
FUNC(void, RTE_CODE) Mcu_SetClockMode(Mcu_ClockType mode);
FUNC(Mcu_ResetType, RTE_CODE) Mcu_GetResetSource(void);

/*============================================================================
 * DIO Function Declarations
 *===========================================================================*/
FUNC(void, RTE_CODE) Dio_Init(void);
FUNC(void, RTE_CODE) Dio_InitGPIO(void);
FUNC(Dio_PortLevel, RTE_CODE) Dio_ReadPort(Dio_PortType portId);
FUNC(void, RTE_CODE) Dio_WritePort(Dio_PortType portId, Dio_PortLevel level);
FUNC(uint8, RTE_CODE) Dio_ReadChannel(Dio_ChannelType channelId);
FUNC(void, RTE_CODE) Dio_WriteChannel(Dio_ChannelType channelId, uint8 level);

/*============================================================================
 * ADC Function Declarations
 *===========================================================================*/
FUNC(void, RTE_CODE) Adc_Init(void);
FUNC(Std_ReturnType, RTE_CODE) Adc_StartConversion(Adc_GroupType group);
FUNC(Adc_ValueType, RTE_CODE) Adc_ReadChannel(Adc_ChannelType channelId);

/*============================================================================
 * PWM Function Declarations
 *===========================================================================*/
FUNC(void, RTE_CODE) Pwm_Init(void);
FUNC(Std_ReturnType, RTE_CODE) Pwm_SetDutyCycle(Pwm_ChannelType channelId, Pwm_DutyType duty);
FUNC(Std_ReturnType, RTE_CODE) Pwm_SetFrequency(Pwm_ChannelType channelId, Pwm_FrequencyType freq);

#endif /* AUTOSAR_MCAL_H */
