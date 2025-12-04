/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   time_stuff.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/04 19:46:31 by mtaranti          #+#    #+#             */
/*   Updated: 2025/12/04 20:53:06 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

long timestamp(void)
{
    struct timeval *tv;

    gettimeofday(&tv, NULL);
    return (tv->tv_sec * 1000 + tv->tv_usec / 1000);
}

long now_ms(t_struct_coder *coder)
{
    return timestamp() - coder->last_action_time;
}