/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   time_stuff.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 19:46:31 by mtaranti          #+#    #+#             */
/*   Updated: 2026/02/02 11:27:04 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

long	timestamp(void)
{
	struct timeval	tv;

	gettimeofday(&tv, NULL);
	return (tv.tv_sec * 1000 + tv.tv_usec / 1000);
}

long	get_timestamp(t_struct_input *data)
{
	return (timestamp() - data->start_time);
}

long	now_ms(t_struct_coder *coder)
{
	return (timestamp() - coder->last_action_time);
}

void	clean_threads(t_struct_input *data_input, int i)
{
	flag_change_mutex(data_input);
	pthread_cond_broadcast(&data_input->monitor_cond);
	while (i-- >= 0)
		pthread_join(data_input->arr[i]->thread, NULL);
}

void	clean_all_coders(t_struct_input *data_input,
	int i)
{
	flag_change_mutex(data_input);
	pthread_cond_broadcast(&data_input->monitor_cond);
	i = -1;
	while (++i < data_input->number_of_coders)
		pthread_join(data_input->arr[i]->thread, NULL);
}
