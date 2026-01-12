/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   coders.h                                           :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: marco <marco@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/03 14:05:05 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/12 23:16:59 by marco            ###   ########.fr       */
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

struct	s_struct_coder;
struct	s_priority_queue;

typedef struct s_queue_entry
{
	struct s_struct_coder	*coder;
	long					deadline;
	long					enqueue_time;
}	t_queue_entry;

typedef struct s_priority_queue
{
	t_queue_entry	*entries;
	int				size;
	int				capacity;
}	t_priority_queue;

typedef struct s_struct_input
{
	long					number_of_coders;
	long					time_to_burnout;
	int						flag_stop;
	long					time_to_compile;
	long					time_to_debug;
	long					time_to_refactor;
	long					number_of_compiles_required;
	long					dongle_cooldown;
	long					scheduler;
	long					start_time;
	struct s_struct_coder	**arr;
	pthread_mutex_t			print_mutex;
	pthread_mutex_t			*usb_array;
	long					*usb_last_free_time;
	pthread_mutex_t			monitor_mutex;
	pthread_cond_t			monitor_cond;
	t_priority_queue		*scheduler_queue;
}	t_struct_input;

typedef struct s_struct_coder
{
	t_struct_input	*data_input;
	long			id;
	long			last_action_time;
	long			counter_compiled;
	int				flag_burnout;
	long			flag_finished;
	pthread_t		thread;
}	t_struct_coder;

long			timestamp(void);
long			now_ms(t_struct_coder *coder);
int				is_fifo_or_edf(char *str);
int				is_number(char *str);
int				input_validation(int arg, char **argv);
void			free_all_one(t_struct_input *data);
void			free_all_two(t_struct_input *data);
void			compile(t_struct_input *data,
					int id, long timeshot, int sleepms);
void			debug(t_struct_input *data, int id, long timeshot, int sleepms);
void			refactor(t_struct_input *data,
					int id, long timeshot, int sleepms);
void			safe_printf(t_struct_input *data,
					int id, long timeshot, char *str);
int				main(int arg, char **argv);
void			*routine(void *arg);
void			*monitor_routine(void *arg);
void			execute_multithread(t_struct_input *data_input);
int				can_take_dongles(t_struct_coder *coder);
void			dequeue_coder(t_struct_input *data, t_struct_coder *coder);
void			enqueue_coder(t_struct_input *data, t_struct_coder *coder);
t_struct_input	*parse_input(char **argv);
int				parse_datastruct(t_struct_input *data, char **argv);
int				parse_coders(t_struct_input *data);
long			get_timestamp(t_struct_input *data);

#endif
