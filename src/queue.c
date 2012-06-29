#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <dirent.h>

#include "common.h"
#include "queue.h"


int chqueue(const char *queue) {
    int rc = 0;

    rc = chdir(getenv("OPSQUEUEDIR"));
    if (rc != 0) {
        fprintf(stderr, "bad queue path\n");
        return rc;
    }

    if (queue == NULL)
        return rc;

    rc = chdir(queue);
    if (rc != 0) {
        fprintf(stderr, "queue %s does not exist\n", queue);
        return rc;
    }

    return rc;
}


int next_job_id(const char *queue) {
    DIR *dp = NULL;
    struct dirent *ep = NULL;

    unsigned int job = 0;
    int na = 0;

    unsigned int max = 0;

    if (chqueue(NULL) != 0)
        return -1;

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


int ignore(const char *path) {
    if (path[0] == '.' && path[1] == '\0')
        return TRUE;

    if (path[1] == '.' && path[2] == '\0')
        return TRUE;

    if (strcmp(path, "queue") == 0)
        return TRUE;

    return FALSE;
}


