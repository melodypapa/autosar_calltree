/*
 * Demo header file for AUTOSAR function declarations
 */

#ifndef DEMO_H
#define DEMO_H

/* AUTOSAR macro definitions (simplified) */
#define FUNC(return_type, mem_class) return_type
#define VAR(var_type, mem_class) var_type
#define P2VAR(var_type, mem_class, ptr_class) var_type*
#define P2CONST(var_type, mem_class, ptr_class) const var_type*
#define CONST(var_type, mem_class) const var_type

/* Standard types */
typedef unsigned char uint8;
typedef unsigned short uint16;
typedef unsigned int uint32;

/* Memory classes */
#define RTE_CODE
#define AUTOMATIC
#define APPL_DATA
#define DEMO_VAR

/* Function declarations */
FUNC(void, RTE_CODE) Demo_Init(void);
FUNC(void, RTE_CODE) Demo_InitHardware(void);
FUNC(void, RTE_CODE) Demo_InitSoftware(void);
FUNC(void, RTE_CODE) Demo_InitVariables(void);
FUNC(void, RTE_CODE) Demo_InitClock(void);
FUNC(void, RTE_CODE) Demo_InitGPIO(void);
FUNC(void, RTE_CODE) Demo_InitState(void);
FUNC(void, RTE_CODE) Demo_InitConfig(void);
FUNC(void, RTE_CODE) Demo_MainFunction(void);
FUNC(void, RTE_CODE) Demo_Process(void);
FUNC(void, RTE_CODE) Demo_Update(void);

#endif /* DEMO_H */
