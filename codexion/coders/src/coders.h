/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   coders.h                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/03 14:05:05 by mtaranti          #+#    #+#             */
/*   Updated: 2025/12/04 21:47:00 by mtaranti         ###   ########.fr       */
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

typedef struct s_struct_input
{
	long	number_of_coders;
	long	time_to_burnout;
	int		flag_stop; //0 ok 1 stop
	long	time_to_compile;
	long	time_to_debug;
	long	time_to_refactor;
	long	number_of_compiles_required;
	long	dongle_cooldown;
	long	scheduler; //bool 1/2 based on input
	t_struct_coder	**arr;
	pthread_mutex_t print_mutex;
	pthread_mutex_t *usb_array;      // one per USB
	pthread_mutex_t monitor_mutex;   // protects the queue
	pthread_cond_t  monitor_cond;    // signals waiting coders
	t_queue_node *scheduler_queue;

}	t_struct_input;

typedef struct s_struct_coder
{
	t_struct_input *data_input;
	long	id;
	long	last_action_time;
	long	counter_compiled;
	int		flag_burnout; //0 ok, 1 is burnout
	long	flag_finished; //0 std, 1 is finished
	pthread_t	thread;
	
}	t_struct_coder;

//queue for FIFO or EDF
typedef struct s_queue_node {
    t_struct_coder *coder;
    long deadline;
    struct s_queue_node *next;

} t_queue_node;

void *routine(void *arg);
void execute_multithread(t_struct_input *data_input);
int	is_number(char *str);
int is_fifo_or_edf(char *str);
int	input_validation(int arg, char **argv);
t_struct_input *parse_input(int arg, char **argv);
void free_threads(pthread_t *arr, int i);
void compile(t_struct_input *data_input, int id, int timeshot, int sleepms);
void debug(t_struct_input *data_input, int id, int timeshot, int sleepms);
void refactor(t_struct_input *data_input, int id, int timeshot, int sleepms);
long timestamp(void);
long now_ms(t_struct_input *data);

#endif