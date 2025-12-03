#include "coders.h"

void compile(int id, int timeshot, int sleepms)
{
    printf("%i %i is compiling\n", timeshot, id);
    usleep(sleepms);
}

void debug(int id, int timeshot, int sleepms)
{
    printf("%i %i is debugging\n", timeshot, id);
    usleep(sleepms);
}

void refactor(int id, int timeshot, int sleepms)
{
    printf("%i %i is refactoring\n", timeshot, id);
    usleep(sleepms);
}