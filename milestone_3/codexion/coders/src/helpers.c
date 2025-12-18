/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   helpers.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/12/03 15:45:26 by mtaranti          #+#    #+#             */
/*   Updated: 2025/12/05 14:31:21 by mtaranti         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "coders.h"

int is_fifo_or_edf(char *str)
{
	const char *fifo = "fifo";
	const char *edf = "edf";
	int			i;

	i = 0;
	while (str[i] && fifo[i] && (str[i] == fifo[i]))
	{
		i++;
		if (str[i] == '\0' && fifo[i] == '\0')
			return (1);
	}
	i = 0;
	while (str[i] && edf[i] && (str[i] == fifo[i]))
	{
		i++;
		if (str[i] == '\0' && edf[i] == '\0')
			return (2);
	}
	return (0);
}

int	is_number(char *str)
{
	while(str)
	{
		if (*str < 48 || *str > 57)
			return (-1);
		str++;
	}
	return (0);
}

int	input_validation(int arg, char **argv)
{
	if (arg != 9)
		return (-1);
	if (is_number(argv[1]) != 0)
		return (-1);
	if (is_number(argv[2]) != 0)
		return (-1);
	if (is_number(argv[3]) != 0)
		return (-1);
	if (is_number(argv[4]) != 0)
		return (-1);
	if (is_number(argv[5]) != 0)
		return (-1);
	if (is_number(argv[6]) != 0)
		return (-1);
	if (is_number(argv[7]) != 0)
		return (-1);
	if (is_fifo_or_edf(argv[8]) == 0)
		return (-1);
	return (0);
}

void free_all(t_struct_input *data)
{
    int i;

    if (data->arr)
    {
        i = -1;
        while (++i < data->number_of_coders)
        {
            if (data->arr[i])
                free(data->arr[i]);
        }
        free(data->arr);
    }
    if (data->usb_array)
        free(data->usb_array);
    free(data);
}
