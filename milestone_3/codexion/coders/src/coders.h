/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   coders.h                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/03 14:05:05 by mtaranti          #+#    #+#             */
/*   Updated: 2025/12/05 12:20:18 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CODERS_H
# define CODERS_H
# include <stdlib.h>
# include <unistd.h>
# include <limits.h>
# include <sys/time.h>
# include <pthread.h>
# include <stdio.h>
# include <pthread.h>

struct s_struct_coder;
struct s_queue_node;

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
	struct s_struct_coder	**arr;
	pthread_mutex_t print_mutex;
	pthread_mutex_t *usb_array;      // one per USB
	long	*usb_last_free_time;
	pthread_mutex_t monitor_mutex;   // protects the queue
	pthread_cond_t  monitor_cond;    // signals waiting coders
	struct s_queue_node *scheduler_queue;

}	t_struct_input;

//queue for FIFO or EDF
typedef struct s_queue_node {
    struct s_struct_coder *coder;
    long deadline;
    struct s_queue_node *next;

} t_queue_node;

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


long timestamp(void);
long now_ms(t_struct_coder *coder);
int is_fifo_or_edf(char *str);
int	is_number(char *str);
int	input_validation(int arg, char **argv);
void free_all(t_struct_input *data);
void compile(t_struct_input *data, int id, long timeshot, int sleepms);
void debug(t_struct_input *data, int id, long timeshot, int sleepms);
void refactor(t_struct_input *data, int id, long timeshot, int sleepms);
void safe_printf(t_struct_input *data, int id, long timeshot, char *str);
int main(int arg, char **argv);
void *routine(void *arg);
void *monitor_routine(void *arg);
void execute_multithread(t_struct_input *data_input);
int can_take_dongles(t_struct_coder *coder);
void dequeue_coder(t_struct_input *data, t_struct_coder *coder);
void enqueue_coder(t_struct_input *data, t_struct_coder *coder);
t_struct_input *parse_input(char **argv);
int parse_datastruct(t_struct_input *data, char **argv);
int parse_coders(t_struct_input *data);

#endif