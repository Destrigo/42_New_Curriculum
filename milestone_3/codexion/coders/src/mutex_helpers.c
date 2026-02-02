/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   mutex_helpers.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/31 12:12:01 by mtaranti          #+#    #+#             */
/*   Updated: 2026/02/02 12:09:37 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

int	flag_check_mutex(t_struct_input *data_input)
{
	pthread_mutex_lock (&data_input->flag_mutex);
	if (data_input->flag_stop == 1)
	{
		pthread_mutex_unlock (&data_input->flag_mutex);
		return (1);
	}
	pthread_mutex_unlock (&data_input->flag_mutex);
	return (0);
}

void	flag_change_mutex(t_struct_input *data_input)
{
	pthread_mutex_lock (&data_input->flag_mutex);
	data_input->flag_stop = 1;
	pthread_mutex_unlock (&data_input->flag_mutex);
}

void	mutex_destroyer(t_struct_input *data)
{
	int	i;

	i = -1;
	while (++i < data->number_of_coders)
		pthread_mutex_destroy(&(data->usb_array[i]));
}
