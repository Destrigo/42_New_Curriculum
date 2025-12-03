/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   coders.h                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/03 14:05:05 by mtaranti          #+#    #+#             */
/*   Updated: 2025/12/03 20:31:27 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CODERS_H
# define CODERS_H
# include <stdlib.h>
# include <unistd.h>
# include <limits.h>
# include <time.h>
# include <pthread.h>
# include <stdio.h>
# include <pthread.h>

typedef struct s_struct
{
	int	number_of_coders;
	int	*usb_array;
	int	time_to_burnout;
	int	time_to_compile;
	int time_to_debug;
	int time_to_refactor;
	int number_of_compiles_required;
	int dongle_cooldown;
	int scheduler; //bool 1/2 based on input
	pthread_t	*arr;
	
}	t_struct;

void *routine(void *arg);
void execute_multithread(t_struct *data_input);
int	is_number(char *str);
int is_fifo_or_edf(char *str);
int	input_validation(int arg, char **argv);
t_struct *parse_input(int arg, char **argv);
void free_threads(pthread_t *arr, int i);

#endif