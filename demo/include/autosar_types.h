/*
 * AUTOSAR Types Header File
 * Defines standard AUTOSAR types and macros
 */

#ifndef AUTOSAR_TYPES_H
#define AUTOSAR_TYPES_H

/*============================================================================
 * Standard Integer Types
 *===========================================================================*/
typedef unsigned char uint8;
typedef unsigned short uint16;
typedef unsigned int uint32;
typedef unsigned long long uint64;

typedef signed char sint8;
typedef signed short sint16;
typedef signed int sint32;
typedef signed long long sint64;

/*============================================================================
 * Boolean Types
 *===========================================================================*/
typedef unsigned char boolean;
#define TRUE  (1U)
#define FALSE (0U)

/*============================================================================
 * Status Return Types
 *===========================================================================*/
typedef uint8 Std_ReturnType;
#define E_OK         (0U)
#define E_NOT_OK     (1U)
#define E_BUSY       (2U)
#define E_TIMEOUT    (3U)

/*============================================================================
 * AUTOSAR Memory Macros (simplified for demo)
 *===========================================================================*/
#define FUNC(return_type, mem_class)       return_type
#define FUNC_P2VAR(return_type, mem, ptr)  return_type*
#define FUNC_P2CONST(return_type, mem, ptr) const return_type*
#define VAR(var_type, mem_class)           var_type
#define P2VAR(var_type, mem, ptr)          var_type*
#define P2CONST(var_type, mem, ptr)        const var_type*
#define CONST(var_type, mem_class)         const var_type

/* Compatibility macros for 2-argument P2VAR usage */
#define P2VAR_2ARGS(var_type, ptr)         var_type*

#define AUTOMATIC
#define STATIC static

/*============================================================================
 * Memory Section Macros
 *===========================================================================*/
#define RTE_CODE
#define APPL_DATA
#define DEMO_VAR
#define CODE

/*============================================================================
 * Compiler Abstraction Macros
 *===========================================================================*/
#define NULL_PTR ((void*)0)
#define INLINE inline

#endif /* AUTOSAR_TYPES_H */
