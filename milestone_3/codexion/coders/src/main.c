/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   main.c                                             :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/03 13:18:40 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/06 13:38:02 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

int main(int arg, char **argv)
{
	t_struct_input	*data_input;
	
	if (input_validation(arg, argv) != 0)
		return (write(2, "Invalid input\n", 14), 1);
	data_input = parse_input(argv);
	if (!data_input)
		return (write(2, "Error allocating memory", 23), 1);	
	execute_multithread(data_input);
	
	// Clean up mutexes and condition variables
	int i = 0;
	while (i < data_input->number_of_coders)
	{
		pthread_mutex_destroy(&(data_input->usb_array[i]));
		i++;
	}
	pthread_mutex_destroy(&data_input->print_mutex);
	pthread_mutex_destroy(&data_input->monitor_mutex);
	pthread_cond_destroy(&data_input->monitor_cond);
	
	free_all(data_input);
	return (0);
}

void *routine(void *arg)
{
    t_struct_coder *coder;
    
    coder = (t_struct_coder *)arg;
    const long left = coder->id - 1;
	const long right = (coder->id) % coder->data_input->number_of_coders;

    // Initialize with current timestamp (absolute time)
    if (coder->last_action_time == 0)
        coder->last_action_time = coder->data_input->start_time;    
    
    while (1)
    {
        // Check stop flag
		if (coder->data_input->flag_stop == 1)
            break;
            
        pthread_mutex_lock(&coder->data_input->monitor_mutex);
		if (coder->data_input->flag_stop == 1)
        {
            pthread_mutex_unlock(&coder->data_input->monitor_mutex);
            break;
        }
        
        enqueue_coder(coder->data_input, coder);
        
        while (!can_take_dongles(coder) && coder->data_input->flag_stop == 0)
        {
            struct timespec timeout;
            struct timeval now;
            gettimeofday(&now, NULL);
            timeout.tv_sec = now.tv_sec;
            timeout.tv_nsec = (now.tv_usec + 100000) * 1000; // 100ms timeout
            if (timeout.tv_nsec >= 1000000000)
            {
                timeout.tv_sec++;
                timeout.tv_nsec -= 1000000000;
            }
            pthread_cond_timedwait(&coder->data_input->monitor_cond, &coder->data_input->monitor_mutex, &timeout);
        }    
        if (coder->data_input->flag_stop == 1)
        {
            dequeue_coder(coder->data_input, coder);
            pthread_mutex_unlock(&coder->data_input->monitor_mutex);
            break;
        }
        
        dequeue_coder(coder->data_input, coder);
		pthread_mutex_unlock(&coder->data_input->monitor_mutex);
		// Lock both USB dongles
		pthread_mutex_lock(&coder->data_input->usb_array[left]);
        pthread_mutex_lock(&coder->data_input->usb_array[right]);
		safe_printf(coder->data_input, coder->id, get_timestamp(coder->data_input), "has taken a dongle\n");
        safe_printf(coder->data_input, coder->id, get_timestamp(coder->data_input), "has taken a dongle\n");
        // Compile (updates last_action_time inside to current timestamp)
        compile(coder->data_input, coder->id, get_timestamp(coder->data_input), coder->data_input->time_to_compile);
        
        // Release dongles and set cooldown
        coder->data_input->usb_last_free_time[left] = timestamp();
        coder->data_input->usb_last_free_time[right] = timestamp();
        pthread_mutex_unlock(&coder->data_input->usb_array[left]);
        pthread_mutex_unlock(&coder->data_input->usb_array[right]);
        
        pthread_cond_broadcast(&coder->data_input->monitor_cond); 
        
        // Check if finished
        if (++coder->counter_compiled == coder->data_input->number_of_compiles_required)
        {	
		    coder->flag_finished = 1;
			break;
		}
		
		// Check stop before continuing
		if (coder->data_input->flag_stop == 1)
            break;
            
        debug(coder->data_input, coder->id, get_timestamp(coder->data_input), coder->data_input->time_to_debug);
        
        if (coder->data_input->flag_stop == 1)
            break;
            
		refactor(coder->data_input, coder->id, get_timestamp(coder->data_input), coder->data_input->time_to_refactor);
    }
    return (NULL);
}

void *monitor_routine(void *arg)
{
	t_struct_input *data;
	int i;
	int counter;
	long time_since_last_compile;
	long current_time;

	data = (t_struct_input *)arg;
	usleep(10000); // Give threads time to initialize
	
	while (1)
	{
	    if (data->flag_stop == 1)
	        {break ;}
		counter = 0;
		i = -1;
		current_time = timestamp();
		while (++i < data->number_of_coders)
		{
		    // Check if finished first
		    if (data->arr[i]->flag_finished == 1)
		    {
				counter++;
				continue;
		    }
		    
		    // Check burnout - use absolute timestamp difference
		    time_since_last_compile = current_time - data->arr[i]->last_action_time;
		    
			if (time_since_last_compile >= data->time_to_burnout)
			{
			    if (data->flag_stop == 0)
			    {
    				data->flag_stop = 1;
    				
    				pthread_mutex_lock(&data->print_mutex);
    				printf("%ld %d burned out\n", get_timestamp(data), i + 1);
    				fflush(stdout);
    				pthread_mutex_unlock(&data->print_mutex);
    				
    				pthread_cond_broadcast(&data->monitor_cond);
			    }
				return (NULL);
			}
		}
		
		if (counter == data->number_of_coders)
		{
		    if (data->flag_stop == 0)
		    {
    			data->flag_stop = 1;
    			
    			pthread_mutex_lock(&data->print_mutex);
    			printf("%ld finished all compilations\n", get_timestamp(data));
    			fflush(stdout);
    			pthread_mutex_unlock(&data->print_mutex);
    			
    			pthread_cond_broadcast(&data->monitor_cond);
		    }
			return (NULL);
		}
		usleep(1000); // Check every 1ms
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
	// Wait for monitor to finish first
	// Wait for monitor to finish first
	pthread_join(monitor, NULL);
	
	// Ensure flag is set and broadcast repeatedly
	data_input->flag_stop = 1;
	pthread_cond_broadcast(&data_input->monitor_cond);
	usleep(50000); // Give threads 50ms to finish
	pthread_cond_broadcast(&data_input->monitor_cond);
	
	i = -1;
	while (++i < data_input->number_of_coders)
		pthread_join(data_input->arr[i]->thread, NULL);
}