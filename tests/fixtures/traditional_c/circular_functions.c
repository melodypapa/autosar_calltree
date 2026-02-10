/* Test fixture for circular dependency detection */

// Function A calls Function B
void Circular_A(void)
{
    Circular_B();
}

// Function B calls Function A (creates circular dependency)
void Circular_B(void)
{
    Circular_A();
}

// Function C calls Function A (to reach the cycle)
void Start_Circular(void)
{
    Circular_A();
}

// Separate cycle with 3 functions
void Cycle_X(void)
{
    Cycle_Y();
}

void Cycle_Y(void)
{
    Cycle_Z();
}

void Cycle_Z(void)
{
    Cycle_X();
}