/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/07 21:02:18 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/31 13:00:30 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

int	main(int arg, char **argv)
{
	t_struct_input	*data_input;
	int				i;

	i = 0;
	if (input_validation(arg, argv) != 0)
		return (write(2, "Invalid input\n", 14), 1);
	data_input = parse_input(argv);
	if (!data_input)
		return (write(2, "Error allocating memory", 23), 1);
	execute_multithread(data_input);
	while (i < data_input->number_of_coders)
	{
		pthread_mutex_destroy(&(data_input->usb_array[i]));
		i++;
	}
	pthread_mutex_destroy(&data_input->print_mutex);
	pthread_mutex_destroy(&data_input->monitor_mutex);
	pthread_cond_destroy(&data_input->monitor_cond);
	free_all_one(data_input);
	free_all_two(data_input);
	return (0);
}

void	execute_multithread(t_struct_input *data_input)
{
	pthread_t	monitor;
	int			i;

	i = -1;
	while (++i < data_input->number_of_coders)
	{
		if (pthread_create(&(data_input->arr[i]->thread),
				NULL, &routine, data_input->arr[i]) != 0)
			return ;
	}
	if (pthread_create(&monitor, NULL, &monitor_routine, data_input) != 0)
		return ;
	pthread_join(monitor, NULL);
	flag_change_mutex(data_input);
	pthread_cond_broadcast(&data_input->monitor_cond);
	usleep(30000);
	pthread_cond_broadcast(&data_input->monitor_cond);
	i = -1;
	while (++i < data_input->number_of_coders)
		pthread_join(data_input->arr[i]->thread, NULL);
}

static void	helper_five(t_struct_input *data, int i, int flag)
{
	if (flag_check_mutex(data) == 0)
	{
		flag_change_mutex(data);
		pthread_mutex_lock(&data->print_mutex);
		if (flag != 1)
			printf("%ld %d burned out\n", get_timestamp(data), i + 1);
		pthread_mutex_unlock(&data->print_mutex);
		pthread_cond_broadcast(&data->monitor_cond);
	}
}

void	*monitor_routine(void *arg)
{
	const t_struct_input	*data = (t_struct_input *)arg;
	int						i;
	int						counter;
	long					time;

	while (1)
	{
		counter = 0;
		i = -1;
		time = timestamp();
		if (flag_check_mutex((t_struct_input *)data) == 1)
			return (NULL);
		pthread_mutex_lock((pthread_mutex_t *)&data->monitor_mutex);
		while (++i < data->number_of_coders)
		{
			if (data->arr[i]->flag_finished == 1)
				counter++;
			time = timestamp() - data->arr[i]->last_action_time;
			if (time >= data->time_to_burnout)
				return (helper_five((t_struct_input *)data, i, 0), NULL);
		}
		pthread_mutex_unlock((pthread_mutex_t *)&data->monitor_mutex);
		if (counter == data->number_of_coders)
			return (helper_five((t_struct_input *)data, i, 1), NULL);
		usleep(1);
	}
	return (NULL);
}
