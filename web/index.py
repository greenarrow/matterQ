#!/usr/bin/python

import os
import sys
import subprocess
import re
import cgi
import cgitb


def load_config():
    for line in open("/etc/matterq.conf"):
        parts = line.split("=", 1)
        if len(parts) == 2:
            os.environ[parts[0]] = parts[1].strip()


def render_header(stream, autorefresh=False):
    stream.write("<html>\n")
    stream.write("\t<head>\n")
    stream.write("\t\t<title>matterQ</title>\n")
    stream.write("\t\t<link type='text/css' rel='stylesheet' href='/media/css/style.css' />\n")
    stream.write("\t\t<script type='text/javascript' src='/media/js/common.js'></script>\n")
    stream.write("\t</head>\n")

    if autorefresh:
        stream.write("\t<body onload='auto_refresh(5000);'>\n")
    else:
        stream.write("\t<body>\n")

    stream.write("\t\t<div id='header'>\n")
    stream.write("\t\t\t<img src='/media/images/logo64.png'>\n")
    stream.write("\t\t\t<h1>matterQ</h1>\n")
    stream.write("\t\t</div>\n")


def render_footer(stream):
    stream.write("\t\t<div id='footer'>\n")
    stream.write("\t\t\t<hr />\n")
    stream.write("\t\t\t<p><a href='http://matterq.org'>http://matterq.org</a></p>\n")
    stream.write("\t\t</div>\n")
    stream.write("\t</body>\n")
    stream.write("</html>\n")


def render_status(stream, indent=""):
    serial = os.environ.get("AG_SERIALPORT")
    if serial is None:
        stream.write("%s<p><img src='/media/images/stop32.png'> " % indent)
        stream.write("Printer is not configured.</p>\n")
    else:
        if os.path.exists(serial):
            stream.write("%s<p><img src='/media/images/tick32.png'>" % indent)
            stream.write(" Printer is connected.</p>\n")
        else:
            stream.write("%s<p><img src='/media/images/stop32.png'> " % indent)
            stream.write(" Printer is not connected.<br />\n")
            stream.write("%s<i>Device: %s</i></p>\n" % (indent, serial))


def render_queue(stream, out, indent=""):
    active = False
    tally = 0

    stream.write("%s<table>\n" % indent)

    for line in out.split("\n"):
        items = line.split()

        if line.startswith(" Rank   Owner/ID"):
            active = True
            job_index = items.index("Job")
            col = "th"
        else:
            col = "td"

        if not active or len(line) == 0:
            continue

        stream.write("%s\t<tr>\n" % indent)

        if col == "th":
            items.append("")
        else:
            items.append("<a href='/cancel/%s'>cancel</a>" % items[job_index])

        for item in items:
            stream.write("%s\t\t<%s>%s</%s>\n" % (indent, col, item, col))

        stream.write("%s\t</tr>\n" % indent)
        tally += 1

    stream.write("%s</table>\n" % indent)

    if tally == 0:
        stream.write("%s<p>No jobs found</p>\n" % indent)


def index(stream):

    p = subprocess.Popen(["/usr/bin/lpq", "-l"], stdout=subprocess.PIPE)
    assert p.wait() == 0
    out = p.communicate()[0]

    render_header(stream, autorefresh=True)

    stream.write("\t\t<div id='status'>\n")
    stream.write("\t\t\t<h2>Status</h2>\n")
    render_status(stream, "\t\t\t")
    stream.write("\t\t</div>\n")

    stream.write("\t\t<div id='queue'>\n")
    stream.write("\t\t\t<h2>Queue</h2>\n")
    render_queue(stream, out, "\t\t\t")
    stream.write("\t\t</div>\n")

    render_footer(stream)


def remove(stream, job):
    render_header(stream)

    p = subprocess.Popen(["/usr/bin/lprm", job])

    if p.wait() == 0:
        stream.write("\t\t<p>Job %s cancelled. " % job)
    else:
        stream.write("\t\t<p>Failed to cancel job %s." % job)

    stream.write("<a href='/'>Return to main page.</a></p>")
    render_footer(stream)


if __name__ == "__main__":
    load_config()

    cgitb.enable()

    form = cgi.FieldStorage() 
    cancel = form.getvalue('cancel')

    stream = sys.stdout

    stream.write("Content-type: text/html\n\n")

    if cancel is not None:
        remove(stream, cancel)
    else:
        index(stream)

