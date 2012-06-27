#ifndef FALSE
#define FALSE  0
#define TRUE  !FALSE
#endif

#define BUF_SIZE    1000


int spool(const char *queue, const char *filename);
int ignore(const char *path);
int list(const char *queue);
void print_usage(const char *program_name);

