/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/07 21:02:18 by mtaranti          #+#    #+#             */
/*   Updated: 2026/02/02 11:31:59 by mtaranti         ###   ########.fr       */
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
	if (data_input->number_of_coders == 1)
		execute_single_thread(data_input);
	else
		execute_multithread(data_input);
	while (i < data_input->number_of_coders)
	{
		pthread_mutex_destroy(&(data_input->usb_array[i]));
		i++;
	}
	pthread_mutex_destroy(&data_input->print_mutex);
	pthread_mutex_destroy(&data_input->flag_mutex);
	pthread_mutex_destroy(&data_input->monitor_mutex);
	pthread_cond_destroy(&data_input->monitor_cond);
	free_all_one(data_input);
	free_all_two(data_input);
	return (0);
}
