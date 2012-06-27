GCC = gcc -Wall

all: objdir mattterq

objdir:
	mkdir -p build

matterq: src/matterq.c
	$(GCC) -c -o matterq src/matterq.c

clean:
	rm matterq build/*

