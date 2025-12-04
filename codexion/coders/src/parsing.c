/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   parsing.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 19:46:28 by mtaranti          #+#    #+#             */
/*   Updated: 2025/12/04 21:33:57 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

t_struct_input *parse_input(int arg, char **argv)
{
	t_struct_input *data;

	data = malloc(sizeof(t_struct_input));
	if (!data)
		return (NULL);
	if (parse_datastruct(data, argv) == -1)
		return (free(data), NULL);
	if (parse_coders(data) == -1)
		return (free(data->usb_array), free(data), NULL);
	return (data);
}

int parse_datastruct(t_struct_input *data, char **argv)
{
	int i;

	i = -1;
	data->number_of_coders = atoi(argv[1]);
	while (++i < data->number_of_coders)
		pthread_mutex_init(&(data->usb_array[i]), NULL);
	data->time_to_burnout = atoi(argv[2]);
	data->flag_stop = 0;
	data->time_to_compile = atoi(argv[3]);
	data->time_to_debug = atoi(argv[4]);
	data->time_to_refactor = atoi(argv[5]);
	data->number_of_compiles_required = atoi(argv[6]);
	data->dongle_cooldown = atoi(argv[7]);
	data->scheduler = is_fifo_or_edf(argv[8]);
	pthread_mutex_init(&data->print_mutex, NULL);
	return (0);
}

int parse_coders(t_struct_input *data)
{
    long i;

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
        data->arr[i]->last_action_time = 0;
        data->arr[i]->counter_compiled = 0;
        data->arr[i]->flag_burnout = 0;
        data->arr[i]->flag_finished = 0;
        data->arr[i]->thread = (pthread_t){0};
    }
    return (0);
}

