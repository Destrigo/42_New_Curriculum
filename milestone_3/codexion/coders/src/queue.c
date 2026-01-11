/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   queue.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 21:44:04 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/11 16:24:42 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

static void	helper_four(t_struct_input *data,
	t_queue_node *node, t_queue_node *prev, t_queue_node *tmp)
{
	if (data->scheduler == 1)
	{
		tmp = data->scheduler_queue;
		while (tmp->next)
			tmp = tmp->next;
		tmp->next = node;
		return ;
	}
	prev = NULL;
	tmp = data->scheduler_queue;
	while (tmp && tmp->deadline <= node->deadline)
	{
		prev = tmp;
		tmp = tmp->next;
	}
	if (!prev)
	{
		node->next = data->scheduler_queue;
		data->scheduler_queue = node;
	}
	else
	{
		node->next = tmp;
		prev->next = node;
	}
}

void	enqueue_coder(t_struct_input *data, t_struct_coder *coder)
{
	t_queue_node	*node;
	t_queue_node	*prev;
	t_queue_node	*tmp;

	node = malloc(sizeof(t_queue_node));
	if (!node)
		return ;
	tmp = NULL;
	prev = NULL;
	node->coder = coder;
	node->deadline = coder->last_action_time + data->time_to_burnout;
	node->next = NULL;
	if (!data->scheduler_queue)
		data->scheduler_queue = node;
	else
		helper_four(data, node, prev, tmp);
}

void	dequeue_coder(t_struct_input *data, t_struct_coder *coder)
{
	t_queue_node	*prev;
	t_queue_node	*tmp;

	prev = NULL;
	tmp = data->scheduler_queue;
	while (tmp)
	{
		if (tmp->coder == coder)
		{
			if (prev)
				prev->next = tmp->next;
			else
				data->scheduler_queue = tmp->next;
			free(tmp);
			break ;
		}
		prev = tmp;
		tmp = tmp->next;
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
	if (!data->scheduler_queue || data->scheduler_queue->coder != coder)
		return (0);
	if (now - data->usb_last_free_time[left] < data->dongle_cooldown)
		return (0);
	if (now - data->usb_last_free_time[right] < data->dongle_cooldown)
		return (0);
	return (1);
}
