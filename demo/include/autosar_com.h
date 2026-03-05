/*
 * Communication Module Header File
 * AUTOSAR COM module interface definitions
 */

#ifndef AUTOSAR_COM_H
#define AUTOSAR_COM_H

#include "autosar_types.h"

/*============================================================================
 * Communication Types
 *===========================================================================*/
typedef uint32 Com_MessageIdType;
typedef uint32 Com_ChannelType;
typedef uint8 Com_IPduType;

/*============================================================================
 * Signal Group Types
 *===========================================================================*/
typedef struct {
    uint8* data;
    uint32 length;
} Com_SignalGroupType;

/*============================================================================
 * PDU Router Types
 *===========================================================================*/
typedef struct {
    Com_MessageIdType id;
    uint8* sdu;
    uint16 length;
} PduR_PduInfoType;

/*============================================================================
 * Communication Function Declarations
 *===========================================================================*/

/* Initialization functions */
FUNC(Std_ReturnType, RTE_CODE) Com_Init(const void* config);
FUNC(void, RTE_CODE) Com_InitCAN(void);
FUNC(void, RTE_CODE) Com_InitLIN(void);
FUNC(void, RTE_CODE) Com_InitEthernet(void);

/* Signal transmission functions */
FUNC(Std_ReturnType, RTE_CODE) Com_SendSignal(Com_MessageIdType signalId);
FUNC(Std_ReturnType, RTE_CODE) Com_ReceiveSignal(Com_MessageIdType signalId, void* data);

/* PDU functions */
FUNC(Std_ReturnType, RTE_CODE) Com_SendPdu(Com_ChannelType channel, const PduR_PduInfoType* pduInfo);
FUNC(Std_ReturnType, RTE_CODE) Com_ReceivePdu(Com_ChannelType channel, PduR_PduInfoType* pduInfo);

/* Communication control */
FUNC(void, RTE_CODE) Com_EnableTX(Com_ChannelType channel);
FUNC(void, RTE_CODE) Com_DisableTX(Com_ChannelType channel);
FUNC(void, RTE_CODE) Com_EnableRX(Com_ChannelType channel);
FUNC(void, RTE_CODE) Com_DisableRX(Com_ChannelType channel);

/* Main function (called cyclically) */
FUNC(void, RTE_CODE) Com_MainFunction(void);

#endif /* AUTOSAR_COM_H */
