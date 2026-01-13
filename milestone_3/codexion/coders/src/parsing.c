/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parsing.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 19:46:28 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/13 18:23:38 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

t_struct_input	*parse_input(char **argv)
{
	t_struct_input	*data;

	data = malloc(sizeof(t_struct_input));
	if (!data)
		return (NULL);
	if (parse_datastruct(data, argv) == -1)
		return (free(data), NULL);
	if (parse_coders(data) == -1)
		return (free(data->usb_array), free(data), NULL);
	return (data);
}

static void	helper_three(t_struct_input *data, char **argv)
{
	data->time_to_burnout = atoi(argv[2]);
	data->flag_stop = 0;
	data->time_to_compile = atoi(argv[3]);
	data->time_to_debug = atoi(argv[4]);
	data->time_to_refactor = atoi(argv[5]);
	data->number_of_compiles_required = atoi(argv[6]);
	data->dongle_cooldown = atoi(argv[7]);
	data->scheduler = is_fifo_or_edf(argv[8]);
}

static int	helper_lostcount(t_struct_input *data)
{
	pthread_mutex_init(&data->print_mutex, NULL);
	pthread_mutex_init(&data->monitor_mutex, NULL);
	pthread_cond_init(&data->monitor_cond, NULL);
	data->scheduler_queue = malloc(sizeof(t_priority_queue));
	if (!data->scheduler_queue)
		return (-1);
	data->scheduler_queue->capacity = data->number_of_coders;
	data->scheduler_queue->size = 0;
	data->scheduler_queue->entries = malloc(sizeof(t_queue_entry)
			* data->number_of_coders);
	if (!data->scheduler_queue->entries)
		return (free(data->scheduler_queue), -1);
	return (0);
}

int	parse_datastruct(t_struct_input *data, char **argv)
{
	int	i;

	i = -1;
	data->number_of_coders = atoi(argv[1]);
	data->start_time = timestamp();
	data->usb_array = malloc(sizeof(pthread_mutex_t) * data->number_of_coders);
	if (!data->usb_array)
		return (-1);
	while (++i < data->number_of_coders)
		pthread_mutex_init(&(data->usb_array[i]), NULL);
	data->usb_last_free_time = malloc(sizeof(long) * data->number_of_coders);
	if (!data->usb_last_free_time)
		return (-1);
	i = data->number_of_coders;
	while (--i >= 0)
		data->usb_last_free_time[i] = data->start_time - data->dongle_cooldown;
	helper_three(data, argv);
	if (helper_lostcount(data) == -1)
		return (free(data->usb_array), free(data->usb_last_free_time), -1);
	return (0);
}

int	parse_coders(t_struct_input *data)
{
	long	i;

	i = -1;
	data->arr = malloc(sizeof(t_struct_coder *) * data->number_of_coders);
	if (!data->arr)
		return (-1);
	while (++i < data->number_of_coders)
	{
		data->arr[i] = malloc(sizeof(t_struct_coder));
		if (!data->arr[i])
		{
			while (--i >= 0)
				free(data->arr[i]);
			return (free(data->arr), -1);
		}
		data->arr[i]->data_input = data;
		data->arr[i]->id = i + 1;
		data->arr[i]->last_action_time = data->start_time;
		data->arr[i]->counter_compiled = 0;
		data->arr[i]->flag_burnout = 0;
		data->arr[i]->flag_finished = 0;
		data->arr[i]->thread = (pthread_t){0};
	}
	return (0);
}
