GCC = gcc -Wall

all: objdir matterq

objdir:
	mkdir -p build

matterq: src/matterq.c
	$(GCC) -o matterq src/matterq.c

clean:
	rm matterq build/*

