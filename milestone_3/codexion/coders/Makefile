# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/12/05 12:06:34 by mtaranti          #+#    #+#              #
#    Updated: 2026/01/31 13:52:58 by mtaranti         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

NAME = codexion

CC = cc
CFLAGS = -Wall -Wextra -Werror -pthread
RM = rm -f
SRC = 	src/main.c				\
		src/parsing.c			\
		src/queue.c				\
		src/time_stuff.c		\
		src/helpers.c			\
		src/routine.c			\
		src/mutex_helpers.c		\
		src/queue_actions.c		\
		src/threads.c			\
		src/coders_actions.c
OBJ = $(SRC:.c=.o)

all: $(NAME)

$(NAME): $(OBJ)
	$(CC) $(CFLAGS) $(OBJ) -o $(NAME)

%.o: %.c coders.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	$(RM) $(OBJ)

fclean: clean
	$(RM) $(NAME)

run: ./$(NAME)
	./$(NAME)
	clear

test1: re
	./$(NAME) 1 1000 200 200 200 3 100 fifo
test2: re
	./$(NAME) 2 1000 300 200 200 3 100 fifo

test3: re
	./$(NAME) 2 1000 300 200 200 3 100 edf

test4: re
	./$(NAME) 5 1000 330 220 220 5 100 fifo

test5: re
	./$(NAME) 5 800 200 100 100 3 100 fifo

test6: re
	./$(NAME) 5 800 200 100 100 3 100 edf

test7: re
	./$(NAME) 20 1000 150 100 100 5 100 edf

test8: re
	./$(NAME) 200 1200 200 200 200 50 100 edf

test9: re
	./$(NAME) 200 1200 200 200 200 50 100 fifo

test10: re
	./$(NAME) 5 10000 100 100 100 200 500 fifo

re: fclean all

.PHONY: all clean fclean re