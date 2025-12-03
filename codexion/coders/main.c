/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/03 13:18:40 by mtaranti          #+#    #+#             */
/*   Updated: 2025/12/03 20:28:47 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

/// @param argv 
// 	number_of_coders num of coders and dongles
// 	time_to_burnout(ms)  time to die
// 	time_to_compile time to compile
// 	time_to_debug time to debug
// 	time_to_refactor time to refactor - then it goest straight to compile
// 	number_of_compiles_required all coders have compiled, it stops. if not, go forever until one dies
// 	dongle_cooldown dongle cooldown between use
// 	scheduler fifo or edf
int main(int arg, char **argv)
{
	t_struct	*data_input;
	
	if (input_validation(arg, argv) != 0)
		return (write(2, "Invalid input", 13), 1);
	data_input = parse_input(arg, argv);
	if (!data_input)
		return (write(2, "Error allocating memory", 23), 1);	
	execute_multithread(data_input);
	free(data_input);
	return (0);
}

void *routine(void *arg)
{
	int life;

	life = gettimeofday();
	while (1)
	{
		//look at usb
		//wait until they are both free by scheduler logic
		//lock the usbs
		compile();
		//release usb and set cooldown
		debug();
		refactor();
		//if number of compiles is enough, break
		
		//at any point if life <= 0 die
	}
}

void execute_multithread(t_struct *data_input)
{
	int			i;
	int			k;

	i = -1;
	data_input->arr = malloc(sizeof(pthread_t) * data_input->number_of_coders);
	if (!data_input->arr)
		return ;
	while (++i < data_input->number_of_coders)
	{
		if (pthread_create(&(data_input->arr)[i], NULL, &routine, data_input) != 0)
			return (free_threads(data_input->arr, i));
	}
	k = -1;
	while (++k < data_input->number_of_coders)
	{
		if (pthread_join(data_input->arr[k], NULL) != 0)
			return (free_all(data_input->arr, i));
	}
	free_all(data_input->arr, i);
}

t_struct *parse_input(int arg, char **argv)
{
	t_struct *input;
	int i;

	i = -1;
	input = malloc(sizeof(t_struct));
	if (!input)
		return (-1);
	input->number_of_coders = atoi(argv[1]);
	input->usb_array = malloc(sizeof(int) * input->number_of_coders);
	while (++i < input->number_of_coders)
		input->usb_array[i] = 1;
	input->time_to_burnout = atoi(argv[2]);
	input->time_to_compile = atoi(argv[3]);
	input->time_to_debug = atoi(argv[4]);
	input->time_to_refactor = atoi(argv[5]);
	input->number_of_compiles_required = atoi(argv[6]);
	input->dongle_cooldown = atoi(argv[7]);
	input->scheduler = is_fifo_or_edf(argv[8]);
	return (input);
}
