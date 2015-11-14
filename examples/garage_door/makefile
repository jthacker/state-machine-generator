CC = gcc
CFLAGS = -Wall

.PHONY: all clean generate

all: main

generate:
	../../run garage_door.h .

smg_garage.c: generate
smg_garage.h: generate

%.o : %.c
	@echo compiling: $<
	$(CC) $(CFLAGS) -g -c $^ -o $@

main: main.o smg_garage.o
	$(CC) $(CFLAGS) $^ -o $@

run: main
	./main

clean:
	rm -f main.o smg_garage.* main
