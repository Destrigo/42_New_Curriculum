/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   queue.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 21:44:04 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/04 19:51:58 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

void enqueue_coder(t_struct_input *data, t_struct_coder *coder)
{
    t_queue_node *node;

    node = malloc(sizeof(t_queue_node));
    if (!node)
        return ;
    node->coder = coder;
    // pthread_mutex_lock(&data->monitor_mutex);
    node->deadline = coder->last_action_time + data->time_to_burnout;
    node->next = NULL;
    if (!data->scheduler_queue) 
        data->scheduler_queue = node;
    else
    {
        if (data->scheduler == 1)
        { // FIFO
            t_queue_node *tmp = data->scheduler_queue;
            while (tmp->next) tmp = tmp->next;
            tmp->next = node;
        }
        else
        { // EDF
            t_queue_node *prev = NULL;
            t_queue_node *tmp = data->scheduler_queue;
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
    }
    // pthread_mutex_unlock(&data->monitor_mutex);
}

void dequeue_coder(t_struct_input *data, t_struct_coder *coder)
{
    // Note: monitor_mutex should already be locked by caller
    t_queue_node *prev;
    t_queue_node *tmp;

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
            break;
        }
        prev = tmp;
        tmp = tmp->next;
    }
    // Don't lock/unlock here - caller manages monitor_mutex
}

int can_take_dongles(t_struct_coder *coder)
{
    t_struct_input *data;
    data = coder->data_input;

    const long left = coder->id - 1;  // Fixed: 0-based indexing
    const long right = coder->id % data->number_of_coders;  // Fixed: 0-based
    const long now = timestamp();

    // Check if this coder is first in queue
    if (!data->scheduler_queue || data->scheduler_queue->coder != coder)
        return (0);
    
    // Check USB cooldown only
    if (now - data->usb_last_free_time[left] < data->dongle_cooldown ||
        now - data->usb_last_free_time[right] < data->dongle_cooldown)
        return (0);
    
    // Don't check mutex availability here - let routine() handle actual locking
    return (1);
}
