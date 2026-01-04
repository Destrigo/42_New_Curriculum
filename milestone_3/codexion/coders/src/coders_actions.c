/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   coders_actions.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 19:46:42 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/04 19:38:32 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

void compile(t_struct_input *data, int id, long timeshot, int sleepms)
{
    safe_printf(data, id, timeshot, "is compiling\n");
    usleep(sleepms * 1000);
    data->arr[id]->last_action_time = now_ms(data->arr[id]); //update time to die
}

void debug(t_struct_input *data, int id, long timeshot, int sleepms)
{
    safe_printf(data, id, timeshot, "is debugging\n");
    usleep(sleepms * 1000);
}

void refactor(t_struct_input *data, int id, long timeshot, int sleepms)
{
    safe_printf(data, id, timeshot, "is refactoring\n");
    usleep(sleepms * 1000);
}

void safe_printf(t_struct_input *data, int id, long timeshot, char *str)
{
    pthread_mutex_lock(&data->print_mutex);
	if (data->flag_stop == 0)
        printf("%ld %d %s", timeshot, id, str);
    pthread_mutex_unlock(&data->print_mutex);
}
