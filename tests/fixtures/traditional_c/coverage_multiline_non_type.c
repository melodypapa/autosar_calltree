// Test for line 326-328: multiline function with non-type return type line
// This triggers the else: break branch when prev_line doesn't match ^[\w\s\*]+$
// Using a line with special characters that don't match the pattern
const char* // Comment on same line
multiline_with_comment(int param)
{
    return param;
}