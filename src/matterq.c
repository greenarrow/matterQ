#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <dirent.h>

#include "job.h"
#include "matterq.h"


int next_job_id(const char *queue) {
    DIR *dp = NULL;
    struct dirent *ep = NULL;

    unsigned int job = 0;
    int na = 0;

    unsigned int max = 0;

    if (chdir(getenv("OPSQUEUEDIR")) != 0) {
        fprintf(stderr, "bad queue path\n");
        return -1;
    }

    dp = opendir(queue);
    if (dp == NULL) {
        fprintf(stderr, "queue %s does not exist\n", queue);
        return -1;
    }

    while ((ep = readdir(dp))) {
        if (ignore(ep->d_name) == TRUE)
            continue;

        na = sscanf(ep->d_name, "%u:", &job);

        if (na != 1) {
            fprintf(stderr, "bad job: %s\n", ep->d_name);
            return -1;
        }

        if (job > max)
            max = job;
    }

    closedir(dp);

    return max + 1;
}


int spool(const char *queue, const char *filename) {
    FILE *stream = NULL;
    FILE *spool = NULL;

    char *buffer[BUF_SIZE];
    size_t nb;

    int job = 0;
    char *sfile = NULL;

    if (strcmp(filename, "-") == 0)
        stream = stdin;

    // TODO else open file

    job = next_job_id(queue);
    printf("job: %d\n", job);

    if (chdir(getenv("OPSQUEUEDIR")) != 0) {
        fprintf(stderr, "bad queue path\n");
        return -1;
    }

    if (chdir(queue) != 0) {
        fprintf(stderr, "bad queue path\n");
        return -1;
    }

    asprintf(&sfile, "%u:%u:%s", job, 1, "No Name");
    spool = fopen(sfile, "w");
    free(sfile);

    // TODO checks and flushes
    while ((nb = fread(buffer, sizeof(char), BUF_SIZE, stream)) > 0) {
        fwrite(buffer, sizeof(char), nb, spool);
    }

    fclose(spool);

    return 0;
}


int ignore(const char *path) {
    if (path[0] == '.' && path[1] == '\0')
        return TRUE;

    if (path[1] == '.' && path[2] == '\0')
        return TRUE;

    if (strcmp(path, "queue") == 0)
        return TRUE;

    return FALSE;
}


int list(const char *queue) {
    DIR *dp = NULL;
    struct dirent *ep = NULL;

    unsigned int job = 0;
    unsigned int priority = 0;
    char name[256];
    int na = 0;
    int nb = 0;

    if (chdir(getenv("OPSQUEUEDIR")) != 0) {
        fprintf(stderr, "bad queue path\n");
        return -1;
    }

    dp = opendir(queue);
    if (dp == NULL) {
        fprintf(stderr, "queue %s does not exist\n", queue);
        return -1;
    }

    while ((ep = readdir(dp))) {
        if (ignore(ep->d_name) == TRUE)
            continue;

        na = sscanf(ep->d_name, "%u:%u:%255[^\n]%n", &job, &priority, name, &nb);

        if (na != 3 || nb != strlen(ep->d_name)) {
            fprintf(stderr, "bad job: %s\n", ep->d_name);
            return -1;
        }

        printf("job:\t\t%u\npriority:\t%u\nname:\t\t%s\n\n", job, priority, name);
    }

    closedir(dp);

    return 0;
}


void print_usage(const char *program_name) {
}


int main(int argc, char *argv[]) {
    if (argc < 2) {
        print_usage(argv[0]);
        return 1;
    }

    int verbose = FALSE;
    char *queue = "default";
    char *command = NULL;

    int option_index = 0, c = 0;
    const char *short_options = "+hvq:";
    struct option const long_options[] = {
        {"help", 0, NULL, 'h'},
        {"queue", 1, NULL, 'q'},
        {"verbose", 0, NULL, 'v'},
        {NULL, 0, NULL, 0}
    };

    do {
        c = getopt_long(argc, argv, short_options, long_options, &option_index);

        switch (c) {
            case 'h':
                print_usage(argv[0]);
                return 1;
            case 'v':
                verbose = TRUE;
                break;
            case 'q':
                queue = optarg;
                break;
        }
    } while (c != -1);

    if (!(command = argc - optind >= 1 ? argv[optind] : NULL)) {
        print_usage(argv[0]);
        return 1;
    }

    /*
    commands:
    spool
    print
    list
    cancel
    status
    */

    // TODO check correct numbers of args

    if (strcmp(command, "spool") == 0) {
        spool(queue, argv[optind + 1]);
    } else if (strcmp(command, "list") == 0) {
        list(queue);
    } else {
        print_usage(argv[0]);
        return 1;
    }

    return 0;
}


