/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   queue.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 21:44:04 by mtaranti          #+#    #+#             */
/*   Updated: 2025/12/05 12:01:00 by mtaranti         ###   ########.fr       */
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
    pthread_mutex_lock(&data->monitor_mutex);
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
    pthread_mutex_unlock(&data->monitor_mutex);
}

void dequeue_coder(t_struct_input *data, t_struct_coder *coder)
{
    pthread_mutex_lock(&data->monitor_mutex);
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

    pthread_mutex_unlock(&data->monitor_mutex);
}

int can_take_dongles(t_struct_coder *coder)
{
    t_struct_input *data;
    data = coder->data_input;

    const long left = coder->id;
    const long right = (coder->id + 1) % data->number_of_coders;
    const long now = timestamp();

	// assume monitor_mutex is already locked when called
    if (!data->scheduler_queue || data->scheduler_queue->coder != coder)
        return (0);
    // check USB cooldown
    if (now - data->usb_last_free_time[left] < data->dongle_cooldown ||
        now - data->usb_last_free_time[right] < data->dongle_cooldown)
        return (0);
    // check if both USBs are available
    if (pthread_mutex_trylock(&data->usb_array[left]) != 0)
        return (0);
    if (pthread_mutex_trylock(&data->usb_array[right]) != 0)
        return (pthread_mutex_unlock(&data->usb_array[left]), 0);
    // both are available, unlock (actual lock happens later in routine)
    pthread_mutex_unlock(&data->usb_array[left]);
    pthread_mutex_unlock(&data->usb_array[right]);
    return (1);
}
