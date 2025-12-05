# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/12/05 12:06:34 by mtaranti          #+#    #+#              #
#    Updated: 2025/12/05 12:08:08 by mtaranti         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME = codexion

CC = cc
CFLAGS = -Wall -Wextra -Werror
RM = rm -f
SRC = 	src/main.c				\
		src/parsing.c			\
		src/queue.c				\
		src/time_stuff.c		\
		src/helpers.c			\
		src/coders_actions.c
OBJ = $(SRC:.c=.o)

# Default rule
all: $(NAME)

# Link object files into executable
$(NAME): $(OBJ)
	$(CC) $(CFLAGS) $(OBJ) -o $(NAME)

# Compile source files into object files
%.o: %.c coders.h
	$(CC) $(CFLAGS) -c $< -o $@

# Remove object files
clean:
	$(RM) $(OBJ)

# Remove object files and executable
fclean: clean
	$(RM) $(NAME)

# Recompile everything
re: fclean all

.PHONY: all clean fclean re