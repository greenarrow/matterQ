GCC = gcc -Wall

all: objdir matterq

objdir:
	mkdir -p build

matterq: queue.o src/matterq.c
	$(GCC) -o matterq build/queue.o src/matterq.c

queue.o: src/queue.c
	$(GCC) -c -o build/queue.o src/queue.c

clean:
	rm matterq build/*

