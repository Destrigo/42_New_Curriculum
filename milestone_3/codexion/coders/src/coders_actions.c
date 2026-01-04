/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   coders_actions.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 19:46:42 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/04 21:52:10 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

void compile(t_struct_input *data, int id, long timeshot, int sleepms)
{
    int elapsed;
    int chunk;

    safe_printf(data, id, timeshot, "is compiling\n");
    
    elapsed = 0;
    while (elapsed < sleepms && data->flag_stop == 0)
    {
        chunk = (sleepms - elapsed > 10) ? 10 : (sleepms - elapsed);
        usleep(chunk * 1000);
        elapsed += chunk;
    }
    data->arr[id - 1]->last_action_time = timestamp();
}

void debug(t_struct_input *data, int id, long timeshot, int sleepms)
{
    int elapsed;
    int chunk;
    
    safe_printf(data, id, timeshot, "is debugging\n");
    
    elapsed = 0;
    while (elapsed < sleepms && data->flag_stop == 0)
    {
        chunk = (sleepms - elapsed > 10) ? 10 : (sleepms - elapsed);
        usleep(chunk * 1000);
        elapsed += chunk;
    }
}

void refactor(t_struct_input *data, int id, long timeshot, int sleepms)
{
    int elapsed;
    int chunk;
    
    safe_printf(data, id, timeshot, "is refactoring\n");
    
    elapsed = 0;
    while (elapsed < sleepms && data->flag_stop == 0)
    {
        chunk = (sleepms - elapsed > 10) ? 10 : (sleepms - elapsed);
        usleep(chunk * 1000);
        elapsed += chunk;
    }
}

void safe_printf(t_struct_input *data, int id, long timeshot, char *str)
{
    pthread_mutex_lock(&data->print_mutex);
	if (data->flag_stop == 0)
        printf("%ld %d %s", timeshot, id, str);
    pthread_mutex_unlock(&data->print_mutex);
}
