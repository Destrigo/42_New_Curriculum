/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   coders_actions.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 19:46:42 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/13 17:52:42 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

void	compile(t_struct_input *data, int id, long timeshot, int sleepms)
{
	long	target_time;

	safe_printf(data, id, timeshot, "is compiling\n");
	data->arr[id - 1]->last_action_time = timestamp();
	target_time = timestamp() + sleepms;
	while (timestamp() < target_time && data->flag_stop == 0)
		usleep(1000);
}

void	debug(t_struct_input *data, int id, long timeshot, int sleepms)
{
	long	target_time;

	safe_printf(data, id, timeshot, "is debugging\n");
	target_time = timestamp() + sleepms;
	while (timestamp() < target_time && data->flag_stop == 0)
		usleep(1000);
}

void	refactor(t_struct_input *data, int id, long timeshot, int sleepms)
{
	long	target_time;

	safe_printf(data, id, timeshot, "is refactoring\n");
	target_time = timestamp() + sleepms;
	while (timestamp() < target_time && data->flag_stop == 0)
		usleep(1000);
}

void	safe_printf(t_struct_input *data, int id, long timeshot, char *str)
{
	pthread_mutex_lock(&data->print_mutex);
	if (data->flag_stop == 0)
		printf("%ld %d %s", timeshot, id, str);
	pthread_mutex_unlock(&data->print_mutex);
}

int	can_take_dongles(t_struct_coder *coder)
{
	t_struct_input	*data;
	long			left;
	long			right;
	long			now;
	int				i;
	t_struct_coder	*candidate;
	long			cand_left;
	long			cand_right;

	data = coder->data_input;
	left = coder->id - 1;
	right = coder->id % data->number_of_coders;
	now = timestamp();
	i = 0;
	if (data->number_of_coders != 1 &&
	    (now - data->usb_last_free_time[left] >= data->dongle_cooldown) &&
		(now - data->usb_last_free_time[right] >= data->dongle_cooldown))
	{	
		while (i < data->scheduler_queue->size)
		{
			candidate = data->scheduler_queue->entries[i].coder;
			cand_left = candidate->id - 1;
			cand_right = candidate->id % data->number_of_coders;
			if (now - data->usb_last_free_time[cand_left] >= data->dongle_cooldown
				&& now - data->usb_last_free_time[cand_right] >= data->dongle_cooldown)
				return (candidate == coder);
			i++;
		}
	}
	return (0);
}
