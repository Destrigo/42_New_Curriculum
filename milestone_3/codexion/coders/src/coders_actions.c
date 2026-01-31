/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   coders_actions.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 19:46:42 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/31 14:21:30 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

void	compile(t_struct_input *data, int id, long timeshot, int sleepms)
{
	long	target_time;

	safe_printf(data, id, timeshot, "is compiling\n");
	pthread_mutex_lock(&data->monitor_mutex);
	data->arr[id - 1]->last_action_time = timestamp();
	pthread_mutex_unlock(&data->monitor_mutex);
	target_time = timestamp() + sleepms;
	while (timestamp() < target_time && flag_check_mutex(data) == 0)
		usleep(1000);
	pthread_mutex_lock(&data->monitor_mutex);
	data->arr[id - 1]->counter_compiled += 1;
	pthread_mutex_unlock(&data->monitor_mutex);
}

void	debug(t_struct_input *data, int id, long timeshot, int sleepms)
{
	long	target_time;

	pthread_mutex_lock(&data->monitor_mutex);
	if (data->arr[id - 1]->counter_compiled
		== data->number_of_compiles_required)
	{
		pthread_mutex_unlock(&data->monitor_mutex);
		return ;
	}
	pthread_mutex_unlock(&data->monitor_mutex);
	safe_printf(data, id, timeshot, "is debugging\n");
	target_time = timestamp() + sleepms;
	while (timestamp() < target_time && flag_check_mutex(data) == 0)
		usleep(1000);
}

void	refactor(t_struct_input *data, int id, long timeshot, int sleepms)
{
	long	target_time;

	pthread_mutex_lock(&data->monitor_mutex);
	if (data->arr[id - 1]->counter_compiled
		== data->number_of_compiles_required)
	{
		pthread_mutex_unlock(&data->monitor_mutex);
		return ;
	}
	pthread_mutex_unlock(&data->monitor_mutex);
	safe_printf(data, id, timeshot, "is refactoring\n");
	target_time = timestamp() + sleepms;
	while (timestamp() < target_time && flag_check_mutex(data) == 0)
		usleep(1000);
}

void	safe_printf(t_struct_input *data, int id, long timeshot, char *str)
{
	pthread_mutex_lock(&data->print_mutex);
	if (flag_check_mutex(data) == 0)
		printf("%ld %d %s", timeshot, id, str);
	pthread_mutex_unlock(&data->print_mutex);
}

int	can_take_dongles(t_struct_coder *coder)
{
	const t_struct_input	*data = coder->data_input;
	const long				left = coder->id - 1;
	const long				right = coder->id % data->number_of_coders;
	int						i;
	t_struct_coder			*candidate;

	i = 0;
	if (data->number_of_coders != 1
		&& (timestamp() - data->usb_last_free_time[left]
			>= data->dongle_cooldown)
		&& (timestamp() - data->usb_last_free_time[right]
			>= data->dongle_cooldown))
	{
		while (i < data->scheduler_queue->size)
		{
			candidate = data->scheduler_queue->entries[i].coder;
			if ((timestamp() - data->usb_last_free_time[candidate->id - 1]
					>= data->dongle_cooldown)
				&& (timestamp() - data->usb_last_free_time[candidate->id
						% data->number_of_coders] >= data->dongle_cooldown))
				return (candidate == coder);
			i++;
		}
	}
	return (0);
}
