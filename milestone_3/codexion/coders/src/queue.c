/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   queue.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 21:44:04 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/13 12:52:46 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

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
	int				i;
	t_queue_entry	*s;

	i = 0;
	while (i < data->scheduler_queue->size)
	{
		if (data->scheduler_queue->entries[i].coder == coder)
		{
			data->scheduler_queue->size--;
			if (i < data->scheduler_queue->size)
			{
				s = data->scheduler_queue->entries;
				s[i] = s[data->scheduler_queue->size];
				heap_down(data, i);
			}
			return ;
		}
		i++;
	}
}
