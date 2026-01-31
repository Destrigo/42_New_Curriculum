/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   mutex_helpers.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/01/31 12:12:01 by mtaranti          #+#    #+#             */
/*   Updated: 2026/01/31 12:23:42 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

int	flag_check_mutex(t_struct_input *data_input)
{
    pthread_mutex_lock(&data_input->flag_mutex);
    if (data_input->flag_stop == 1)
    {
        pthread_mutex_unlock(&data_input->flag_mutex);
        return (1);
    }
    pthread_mutex_unlock(&data_input->flag_mutex);
    return (0);
}

void	flag_change_mutex(t_struct_input *data_input)
{
    pthread_mutex_lock(&data_input->flag_mutex);
    data_input->flag_stop = 1;
    pthread_mutex_unlock(&data_input->flag_mutex);
}
