/*
 * Traditional C function declarations for testing
 * Covers SWR_PARSER_C_00001, SWR_PARSER_C_00011, SWR_PARSER_C_00015, SWR_PARSER_C_00016, SWR_PARSER_C_00017
 */

/* Simple void function */
void simple_function(void)
{
    return;
}

/* Function with return type */
uint32 get_value(void)
{
    return 0;
}

/* Static function */
static uint8 internal_function(void)
{
    return 0;
}

/* Inline function */
inline void fast_function(void)
{
    return;
}

/* Compiler-specific inline */
__inline__ void compiler_specific_inline(void)
{
    return;
}

/* Function with parameters */
void process_value(uint32 value)
{
    return;
}

/* Function with multiple parameters */
void process_values(uint8 param1, uint16 param2, uint32 param3)
{
    return;
}

/* Function with pointer parameters */
void write_buffer(uint8* buffer)
{
    return;
}

/* Function with const pointer parameter */
uint32 read_config(const ConfigType* config)
{
    return 0;
}

/* Function with const value parameter */
void set_timeout(const uint32 timeout)
{
    return;
}

/* Static function with parameters */
static void static_helper(uint32 value)
{
    return;
}

/* Function with array parameter (pointer in disguise) */
void process_array(int arr[10])
{
    return;
}

/* Function with function pointer parameter */
void register_callback(void (*callback)(uint32), uint32 context)
{
    if (callback) {
        callback(context);
    }
}

/* Function returning pointer */
uint8* get_buffer(void)
{
    static uint8 buffer[100];
    return buffer;
}

/* Function returning const pointer */
const uint32* get_readonly_data(void)
{
    static const uint32 data[50] = {0};
    return data;
}

/* Function with mixed parameters */
void complex_parameters(
    uint32 mode,
    uint8* output,
    const uint8* input,
    const uint16 length
)
{
    return;
}

/* Function with no parameter name (type-only) */
void function_with_unnamed_params(uint32, uint8*)
{
    return;
}

/* Multiple parameters with complex types */
void complex_types(
    uint8** double_pointer,
    const void* const_data,
    volatile uint32* volatile_data
)
{
    return;
}

/* This looks like a function but is a preprocessor directive - should be skipped */
/*
#define FAKE_FUNCTION(x) void fake_function_##x(void)
FAKE_FUNCTION(test)
*/

/* Function with lots of whitespace */
void    whitespace_test    (   uint32   value   )
{
    return;
}

/* Static inline combination */
static inline void static_inline_function(void)
{
    return;
}
