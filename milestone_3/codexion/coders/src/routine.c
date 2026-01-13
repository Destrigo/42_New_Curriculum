/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   routine.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 19:46:42 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/13 16:03:17 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

static void	dongle_checker(t_struct_coder *coder)
{
	struct timespec	timeout;
	struct timeval	now;

	while (!can_take_dongles(coder) && coder->data_input->flag_stop == 0)
	{
		gettimeofday(&now, NULL);
		timeout.tv_sec = now.tv_sec;
		timeout.tv_nsec = (now.tv_usec + 100000) * 1000;
		if (timeout.tv_nsec >= 1000000000)
		{
			timeout.tv_sec++;
			timeout.tv_nsec -= 1000000000;
		}
		pthread_cond_timedwait(&coder->data_input->monitor_cond,
			&coder->data_input->monitor_mutex, &timeout);
	}
}

static void	helper_one(t_struct_coder *coder, const long left, const long right)
{
	dequeue_coder(coder->data_input, coder);
	pthread_mutex_unlock(&coder->data_input->monitor_mutex);
	usleep(100);
	pthread_mutex_lock(&coder->data_input->usb_array[left]);
	pthread_mutex_lock(&coder->data_input->usb_array[right]);
	safe_printf(coder->data_input,
		coder->id, get_timestamp(coder->data_input), "has taken a dongle\n");
	safe_printf(coder->data_input,
		coder->id, get_timestamp(coder->data_input), "has taken a dongle\n");
	compile(coder->data_input,
		coder->id, get_timestamp(coder->data_input),
		coder->data_input->time_to_compile);
	coder->data_input->usb_last_free_time[left] = timestamp();
	coder->data_input->usb_last_free_time[right] = timestamp();
	pthread_mutex_unlock(&coder->data_input->usb_array[left]);
	pthread_mutex_unlock(&coder->data_input->usb_array[right]);
	pthread_cond_broadcast(&coder->data_input->monitor_cond);
}

static int	helper_two(t_struct_coder *coder, const long left, const long right)
{
	enqueue_coder(coder->data_input, coder);
	dongle_checker(coder);
	if (coder->data_input->flag_stop == 1)
	{
		dequeue_coder(coder->data_input, coder);
		pthread_mutex_unlock(&coder->data_input->monitor_mutex);
		return (-1);
	}
	helper_one(coder, left, right);
	if (++coder->counter_compiled
		== coder->data_input->number_of_compiles_required)
		return (coder->flag_finished = 1, -1);
	if (coder->data_input->flag_stop == 1)
		return (-1);
	debug(coder->data_input, coder->id,
		get_timestamp(coder->data_input), coder->data_input->time_to_debug);
	if (coder->data_input->flag_stop == 1)
		return (-1);
	refactor(coder->data_input, coder->id,
		get_timestamp(coder->data_input),
		coder->data_input->time_to_refactor);
	return (0);
}

void	*routine(void *arg)
{
	const t_struct_coder	*data = (t_struct_coder *)arg;
	const long				left = data->id - 1;
	const long				right = (data->id
			% data->data_input->number_of_coders);
	t_struct_coder			*coder;

	coder = (t_struct_coder *)arg;
	while (1)
	{
		if (coder->data_input->flag_stop == 1)
			break ;
		pthread_mutex_lock(&coder->data_input->monitor_mutex);
		if (coder->data_input->flag_stop == 1)
		{
			pthread_mutex_unlock(&coder->data_input->monitor_mutex);
			break ;
		}
		if (helper_two(coder, left, right) == -1)
			break ;
	}
	return (NULL);
}
