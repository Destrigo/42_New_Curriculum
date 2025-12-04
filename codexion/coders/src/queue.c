/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   queue.c                                            :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 21:44:04 by mtaranti          #+#    #+#             */
/*   Updated: 2025/12/04 21:50:12 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

void enqueue_coder(t_struct_input *data, t_struct_coder *coder)
{
    t_queue_node *node = malloc(sizeof(t_queue_node));
    node->coder = coder;
    node->deadline = coder->last_action_time + data->time_to_burnout;
    node->next = NULL;
    pthread_mutex_lock(&data->monitor_mutex);
    if (!data->scheduler_queue) {
        data->scheduler_queue = node;
    } else {
        if (data->scheduler == 1) { // FIFO
            t_queue_node *tmp = data->scheduler_queue;
            while (tmp->next) tmp = tmp->next;
            tmp->next = node;
        } else { // EDF
            // Insert sorted by deadline
            t_queue_node **curr = &data->scheduler_queue;
            while (*curr && (*curr)->deadline <= node->deadline)
                curr = &(*curr)->next;
            node->next = *curr;
            *curr = node;
        }
    }
    pthread_mutex_unlock(&data->monitor_mutex);
}

void dequeue_coder(t_struct_input *data, t_struct_coder *coder)
{
    pthread_mutex_lock(&data->monitor_mutex);
    t_queue_node **curr = &data->scheduler_queue;

    while (*curr) {
        if ((*curr)->coder == coder) {
            t_queue_node *tmp = *curr;
            *curr = (*curr)->next;
            free(tmp);
            break;
        }
        curr = &(*curr)->next;
    }
    pthread_mutex_unlock(&data->monitor_mutex);
}

int can_take_dongles(t_struct_coder *coder)
{
    t_struct_input *data = coder->data_input;
    long id;
    long left;
    long right;

	data = coder->data_input;
	id = coder->id;
	left = id;
	right = (id + 1) % data->number_of_coders;
    pthread_mutex_lock(&data->monitor_mutex);
	if (data->scheduler_queue->coder != coder) {
        pthread_mutex_unlock(&data->monitor_mutex);
        return (1);
    }
	if (pthread_mutex_trylock(&data->usb_array[left]) != 0 ||
        pthread_mutex_trylock(&data->usb_array[right]) != 0) {
        if (pthread_mutex_trylock(&data->usb_array[left]) == 0) pthread_mutex_unlock(&data->usb_array[left]);
        if (pthread_mutex_trylock(&data->usb_array[right]) == 0) pthread_mutex_unlock(&data->usb_array[right]);
        pthread_mutex_unlock(&data->monitor_mutex);
        return (1);
    }
    pthread_mutex_unlock(&data->usb_array[left]);
    pthread_mutex_unlock(&data->usb_array[right]);
    pthread_mutex_unlock(&data->monitor_mutex);
    return (0);
}
