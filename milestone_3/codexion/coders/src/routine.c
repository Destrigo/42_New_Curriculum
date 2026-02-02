/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   routine.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 19:46:42 by mtaranti          #+#    #+#             */
/*   Updated: 2026/02/02 11:09:43 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

static void	dongle_checker(t_struct_coder *coder)
{
	struct timespec	timeout;
	struct timeval	now;

	while (!can_take_dongles(coder) && flag_check_mutex(coder->data_input) == 0)
	{
		gettimeofday(&now, NULL);
		timeout.tv_sec = now.tv_sec;
		timeout.tv_nsec = (now.tv_usec) * 1000;
		if (timeout.tv_nsec >= 1000000000)
		{
			timeout.tv_sec++;
			timeout.tv_nsec -= 1000000000;
		}
		pthread_cond_timedwait(&coder->data_input->monitor_cond,
			&coder->data_input->monitor_mutex, &timeout);
	}
}

static int	try_acquire_dongles(t_struct_coder *coder, const long left,
	const long right)
{
	long	now;

	pthread_mutex_lock(&coder->data_input->usb_array[left]);
	pthread_mutex_lock(&coder->data_input->usb_array[right]);
	now = timestamp();
	if ((now - coder->data_input->usb_last_free_time[left]
			< coder->data_input->dongle_cooldown)
		|| (now - coder->data_input->usb_last_free_time[right]
			< coder->data_input->dongle_cooldown))
	{
		pthread_mutex_unlock(&coder->data_input->usb_array[right]);
		pthread_mutex_unlock(&coder->data_input->usb_array[left]);
		return (0);
	}
	return (1);
}

static int	helper_one(t_struct_coder *coder, const long left, const long right)
{
	dequeue_coder(coder->data_input, coder);
	pthread_mutex_unlock(&coder->data_input->monitor_mutex);
	if (!try_acquire_dongles(coder, left, right))
	{
		pthread_mutex_lock(&coder->data_input->monitor_mutex);
		enqueue_coder(coder->data_input, coder);
		return (0);
	}
	safe_printf(coder->data_input,
		coder->id, get_timestamp(coder->data_input), "has taken a dongle\n");
	safe_printf(coder->data_input,
		coder->id, get_timestamp(coder->data_input), "has taken a dongle\n");
	compile(coder->data_input,
		coder->id, get_timestamp(coder->data_input),
		coder->data_input->time_to_compile);
	pthread_mutex_lock(&coder->data_input->monitor_mutex);
	coder->data_input->usb_last_free_time[left] = timestamp();
	coder->data_input->usb_last_free_time[right] = timestamp();
	pthread_mutex_unlock(&coder->data_input->usb_array[left]);
	pthread_mutex_unlock(&coder->data_input->usb_array[right]);
	pthread_cond_broadcast(&coder->data_input->monitor_cond);
	return (1);
}

static int	helper_two(t_struct_coder *coder,
	const long left,
	const long right,
	t_struct_input *data)
{
	enqueue_coder(data, coder);
	while (1)
	{
		dongle_checker(coder);
		if (flag_check_mutex(data) == 1)
		{
			pthread_mutex_unlock(&coder->data_input->monitor_mutex);
			return (dequeue_coder(data, coder), -1);
		}
		if (helper_one(coder, left, right) == 1)
			break ;
	}
	if (++coder->counter_compiled
		== data->number_of_compiles_required)
		coder->flag_finished = 1;
	pthread_cond_broadcast(&data->monitor_cond);
	pthread_mutex_unlock(&coder->data_input->monitor_mutex);
	usleep(10);
	if (flag_check_mutex(data) == 1)
		return (-1);
	debug(data, coder->id, get_timestamp(data), data->time_to_debug);
	if (flag_check_mutex(data) == 1)
		return (-1);
	refactor(data, coder->id, get_timestamp(data), data->time_to_refactor);
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
		if (flag_check_mutex(coder->data_input) == 1)
			break ;
		pthread_mutex_lock(&coder->data_input->monitor_mutex);
		if (helper_two(coder, left, right, coder->data_input) == -1)
			break ;
	}
	return (NULL);
}
