
#include "coders.h"

long timestamp(void)
{
    struct timeval tv;

    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000 + tv.tv_usec / 1000;
}

long now_ms(t_struct *data)
{
    return timestamp() - data->start_time_ms;
}