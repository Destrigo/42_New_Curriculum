/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   threads.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/31 13:52:29 by mtaranti          #+#    #+#             */
/*   Updated: 2026/02/02 12:07:03 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

void	execute_single_thread(t_struct_input *data_input)
{
	pthread_t	monitor;

	if (pthread_create(&(data_input->arr[0]->thread),
			NULL, &routine, data_input->arr[0]) != 0)
		return ;
	if (pthread_create(&monitor, NULL, &monitor_routine, data_input) != 0)
	{
		flag_change_mutex(data_input);
		pthread_cond_broadcast(&data_input->monitor_cond);
		pthread_join(data_input->arr[0]->thread, NULL);
		return ;
	}
	pthread_join(monitor, NULL);
	flag_change_mutex(data_input);
	pthread_cond_broadcast(&data_input->monitor_cond);
	usleep(30000);
	pthread_cond_broadcast(&data_input->monitor_cond);
	pthread_join(data_input->arr[0]->thread, NULL);
}

void	execute_multithread(t_struct_input *data_input)
{
	pthread_t	monitor;
	int			i;
	int			created;

	i = -1;
	created = 0;
	while (++i < data_input->number_of_coders)
	{
		if (pthread_create(&(data_input->arr[i]->thread),
				NULL, &routine, data_input->arr[i]) != 0)
			return (clean_threads(data_input, i));
		created++;
	}
	if (pthread_create(&monitor, NULL, &monitor_routine, data_input) != 0)
		return (clean_all_coders(data_input, i));
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
		pthread_mutex_lock(&data->monitor_mutex);
		pthread_cond_broadcast(&data->monitor_cond);
		pthread_mutex_unlock(&data->monitor_mutex);
	}
}

int	checker(t_struct_input *data)
{
	int		i;
	int		counter;
	long	time;

	counter = 0;
	i = -1;
	pthread_mutex_lock((pthread_mutex_t *)&data->monitor_mutex);
	while (++i < data->number_of_coders)
	{
		if (data->arr[i]->flag_finished == 1)
			counter++;
		time = timestamp() - data->arr[i]->last_action_time;
		if (time >= data->time_to_burnout)
		{
			pthread_mutex_unlock((pthread_mutex_t *)&data->monitor_mutex);
			helper_five((t_struct_input *)data, i, 0);
			return (0);
		}
	}
	pthread_mutex_unlock((pthread_mutex_t *)&data->monitor_mutex);
	if (counter == data->number_of_coders)
		return (helper_five((t_struct_input *)data, i, 1), 0);
	return (1);
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
		if (checker((t_struct_input *)data) == 0)
			break ;
		usleep(1);
	}
	return (NULL);
}
