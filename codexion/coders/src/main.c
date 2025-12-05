/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/03 13:18:40 by mtaranti          #+#    #+#             */
/*   Updated: 2025/12/05 12:17:54 by mtaranti         ###   ########.fr       */
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
	t_struct_input	*data_input;
	
	if (input_validation(arg, argv) != 0)
		return (write(2, "Invalid input", 13), 1);
	data_input = parse_input(argv);
	if (!data_input)
		return (write(2, "Error allocating memory", 23), 1);	
	execute_multithread(data_input);
	pthread_mutex_unlock(&data_input->print_mutex);
	pthread_mutex_destroy(&data_input->print_mutex);
	while (0 <= data_input->number_of_coders--)
		pthread_mutex_destroy(&(data_input->usb_array[data_input->number_of_coders]));
	free_all(data_input);
	return (0);
}

void *routine(void *arg)
{
	t_struct_coder *coder;
	coder = (t_struct_coder *)arg;
	const long left = coder->id;
    const long right = (coder->id + 1) % coder->data_input->number_of_coders;

	coder->last_action_time = timestamp(); //create time to die
	while (coder->data_input->flag_stop != 1 && coder->flag_burnout != 1)
	{
		//queue
		enqueue_coder(coder->data_input, coder);
		pthread_mutex_lock(&coder->data_input->monitor_mutex);
        while (!can_take_dongles(coder))
            pthread_cond_wait(&coder->data_input->monitor_cond, &coder->data_input->monitor_mutex);
        //dequeue in its turn
		dequeue_coder(coder->data_input, coder);
        pthread_mutex_unlock(&coder->data_input->monitor_mutex);
		 // Lock actual USBs
        pthread_mutex_lock(&coder->data_input->usb_array[left]);
        pthread_mutex_lock(&coder->data_input->usb_array[right]);
		compile(coder->data_input, coder->id, timestamp(), coder->data_input->time_to_compile);
		//unlock usb
		coder->data_input->usb_last_free_time[left] = timestamp();
		coder->data_input->usb_last_free_time[right] = timestamp();
		pthread_mutex_unlock(&coder->data_input->usb_array[left]);
		pthread_mutex_unlock(&coder->data_input->usb_array[right]);
		pthread_cond_broadcast(&coder->data_input->monitor_cond); 
		//check if finished
		if (++coder->counter_compiled == coder->data_input->number_of_compiles_required)
			coder->flag_finished = 1;
		//set usb cooldown
		debug(coder->data_input, (coder)->id, timestamp(), coder->data_input->time_to_debug);
		refactor(coder->data_input, (coder)->id, timestamp(), coder->data_input->time_to_refactor);
	}
	return (NULL);
}

void *monitor_routine(void *arg)
{
	t_struct_input *data;
	int i;
	int counter;

	data = (t_struct_input *)arg;
	while (data->flag_stop == 0)
	{
		counter = 0;
		i = -1;
		while (++i < data->number_of_coders)
		{
			if (now_ms(data->arr[i]) >= data->time_to_burnout)
			{
				pthread_mutex_lock(&data->print_mutex);
				printf("%ld %d %s\n", timestamp(), i, "is bornout");
				data->flag_stop = 1;
				pthread_cond_broadcast(&data->monitor_cond); //need to understand
				return (NULL);
			}
			if (data->arr[i]->flag_finished == 1)
			{
				if (++counter == data->number_of_coders)
				{
					pthread_mutex_lock(&data->print_mutex);
					printf("%ld %d %s\n", timestamp(), i, "is bornout");
					data->flag_stop = 1;
					pthread_cond_broadcast(&data->monitor_cond); //need to understand
					return (NULL);
				}
			}
		}
		usleep(1000);
	}
	return (NULL);
}

void execute_multithread(t_struct_input *data_input)
{
	pthread_t	monitor;
	int			i;

	i = -1;
	while (++i < data_input->number_of_coders)
	{
		if (pthread_create(&(data_input->arr[i]->thread), NULL, &routine, data_input->arr[i]) != 0)
			return ;
	}
	if (pthread_create(&monitor, NULL, &monitor_routine, data_input) != 0)
			return ;
	i = -1;
	while (++i < data_input->number_of_coders)
	{
		if (pthread_join(data_input->arr[i]->thread, NULL) != 0)
			return ;
	}
	pthread_join(monitor, NULL);
}
