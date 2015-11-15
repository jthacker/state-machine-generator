CC = gcc
CFLAGS = -Wall

.PHONY: all clean generate

all: generate run

generate:
	../../run vending_machine.h .

%.o : %.c
	@echo compiling: $<
	$(CC) $(CFLAGS) -g -c $^ -o $@

main: main.o smg_vending.o
	$(CC) $(CFLAGS) $^ -o $@

run: main
	./main

clean:
	rm -f main.o smg_vending.* main
