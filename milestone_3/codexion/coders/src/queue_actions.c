/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   queue_actions.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/13 12:35:07 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/13 12:35:15 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

void	swap_entries(t_queue_entry *a, t_queue_entry *b)
{
	t_queue_entry	tmp;

	tmp = *a;
	*a = *b;
	*b = tmp;
}

long	get_priority(t_struct_input *data, t_queue_entry *entry)
{
	if (data->scheduler == 1)
		return (entry->enqueue_time);
	else
		return (entry->deadline);
}

int	has_higher_priority(t_struct_input *data,
	t_queue_entry *a, t_queue_entry *b)
{
	long	prio_a;
	long	prio_b;

	prio_a = get_priority(data, a);
	prio_b = get_priority(data, b);
	return (prio_a < prio_b);
}

void	heap_up(t_struct_input *data, int idx)
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

void	heap_down(t_struct_input *data, int idx)
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
