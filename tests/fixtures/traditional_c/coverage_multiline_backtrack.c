/* Test fixture for covering multiline backtrack logic (lines 326-328) */

/* This file has a multiline function where we need to backtrack
   to find the return type on previous lines */

const uint32_t
MyFunction
(uint8 param1, uint16 param2)
{
    return param1 + param2;
}

/* Another example with static */
static void
InternalProcess
(void)
{
    return;
}

/* Another example with pointer return type */
uint8*
GetBuffer
(uint32 size)
{
    return NULL;
}