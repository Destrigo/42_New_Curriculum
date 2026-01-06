# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: mtaranti <mtaranti@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/12/05 12:06:34 by mtaranti          #+#    #+#              #
#    Updated: 2026/01/06 13:30:01 by mtaranti         ###   ########.fr        #
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
	./$(NAME) 1 1000 200 200 200 3 50 fifo
test2: re
	./$(NAME) 2 1000 300 200 200 3 50 edf

test3: re
	./$(NAME) 2 1000 300 200 200 3 50 edf

test4: re
	./$(NAME) 5 400 300 200 200 5 50 fifo

test5: re
	./$(NAME) 5 1000 200 100 100 3 50 fifo

test6: re
	./$(NAME) 10 1000 100 100 100 3 200 fifo

test7: re
	./$(NAME) 20 1000 150 100 100 5 50 edf

test 8: re
	./$(NAME) 8 500 400 100 100 4 50 edf

test9: re
	./$(NAME) 4 300 400 100 100 3 50 fifo

test10: re
	./$(NAME) 5 10000 10 10 10 200 50 fifo

re: fclean all

.PHONY: all clean fclean re