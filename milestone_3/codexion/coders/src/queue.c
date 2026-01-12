/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   queue.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: marco <marco@student.42.fr>                +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 21:44:04 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/12 23:18:14 by marco            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

static void	swap_entries(t_queue_entry *a, t_queue_entry *b)
{
	t_queue_entry	tmp;

	tmp = *a;
	*a = *b;
	*b = tmp;
}

/* Heap helper: get priority for comparison */
static long	get_priority(t_struct_input *data, t_queue_entry *entry)
{
	if (data->scheduler == 1)
		return (entry->enqueue_time);
	else
		return (entry->deadline);
}

/* Heap helper: compare entries (returns 1 if a has higher priority) */
static int	has_higher_priority(t_struct_input *data,
	t_queue_entry *a, t_queue_entry *b)
{
	long	prio_a;
	long	prio_b;

	prio_a = get_priority(data, a);
	prio_b = get_priority(data, b);
	return (prio_a < prio_b);
}

static void	heap_up(t_struct_input *data, int idx)
{
	int	parent;

	while (idx > 0)
	{
		parent = (idx - 1) / 2;
		if (!has_higher_priority(data,
			&data->scheduler_queue->entries[idx],
			&data->scheduler_queue->entries[parent]))
			break ;
		swap_entries(&data->scheduler_queue->entries[idx],
			&data->scheduler_queue->entries[parent]);
		idx = parent;
	}
}

static void	heap_down(t_struct_input *data, int idx)
{
	int	left;
	int	right;
	int	smallest;

	while (1)
	{
		left = 2 * idx + 1;
		right = 2 * idx + 2;
		smallest = idx;
		if (left < data->scheduler_queue->size
			&& has_higher_priority(data,
				&data->scheduler_queue->entries[left],
				&data->scheduler_queue->entries[smallest]))
			smallest = left;
		if (right < data->scheduler_queue->size
			&& has_higher_priority(data,
				&data->scheduler_queue->entries[right],
				&data->scheduler_queue->entries[smallest]))
			smallest = right;
		if (smallest == idx)
			break ;
		swap_entries(&data->scheduler_queue->entries[idx],
			&data->scheduler_queue->entries[smallest]);
		idx = smallest;
	}
}

void	enqueue_coder(t_struct_input *data, t_struct_coder *coder)
{
	int	idx;

	if (data->scheduler_queue->size >= data->scheduler_queue->capacity)
		return ;
	idx = data->scheduler_queue->size;
	data->scheduler_queue->entries[idx].coder = coder;
	data->scheduler_queue->entries[idx].deadline = coder->last_action_time
		+ data->time_to_burnout;
	data->scheduler_queue->entries[idx].enqueue_time = timestamp();
	data->scheduler_queue->size++;
	heap_up(data, idx);
}

void	dequeue_coder(t_struct_input *data, t_struct_coder *coder)
{
	int	i;

	i = 0;
	while (i < data->scheduler_queue->size)
	{
		if (data->scheduler_queue->entries[i].coder == coder)
		{
			data->scheduler_queue->size--;
			if (i < data->scheduler_queue->size)
			{
				data->scheduler_queue->entries[i] =
					data->scheduler_queue->entries[data->scheduler_queue->size];
				heap_down(data, i);
			}
			return ;
		}
		i++;
	}
}

int	can_take_dongles(t_struct_coder *coder)
{
	t_struct_input	*data;
	long			left;
	long			right;
	long			now;

	data = coder->data_input;
	left = coder->id - 1;
	right = coder->id % data->number_of_coders;
	now = timestamp();
	if (data->number_of_coders == 1)
		return (0);
	if (data->scheduler_queue->size == 0
		|| data->scheduler_queue->entries[0].coder != coder)
		return (0);
	if (now - data->usb_last_free_time[left] < data->dongle_cooldown)
		return (0);
	if (now - data->usb_last_free_time[right] < data->dongle_cooldown)
		return (0);
	return (1);
}
