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


def read_status(msg):
    status = None

    for line in msg.split("\n"):
        if line.startswith(" Status:"):
            match = re.match(r" Status: LP filter msg - '(.*?)' at ([0-9:.]+)",
                             line)
            if match:
                status = match.groups()[0]

    return status


def read_active_job(msg):
    active = False

    for line in msg.split("\n"):
        items = line.split()

        if line.startswith(" Rank   Owner/ID"):
            active = True
            job_index = items.index("Job")

        if not active or len(line) == 0:
            continue

        if items[0] == "active":
            return items[job_index]

    return None


def pretty_size(value):
    suffix = ("K", "M", "G", "T")

    if value < 1024.0:
        return str(value)

    for s in suffix:
        value = value / 1024.0
        if value < 1024.0:
            break

    return "%.1f%s" % (value, s)


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
    stream.write("\t\t\t<a href='http://matterq.org'>")
    stream.write("\t\t\t<img src='/media/images/logo64.png'></a>\n")
    stream.write("\t\t\t<h1>matterQ</h1>\n")
    stream.write("\t\t</div>\n")


def render_footer(stream):
    stream.write("\t\t<div id='footer'>\n")
    stream.write("\t\t\t<hr />\n")
    stream.write("\t\t\t<p><a href='http://matterq.org'>http://matterq.org</a></p>\n")
    stream.write("\t\t</div>\n")
    stream.write("\t</body>\n")
    stream.write("</html>\n")


def render_status(stream, out, indent=""):
    serial = os.environ.get("AG_SERIALPORT")
    if serial is None:
        stream.write("%s<p><img src='/media/images/stop32.png'> " % indent)
        stream.write("Printer is not configured.</p>\n")
    else:
        if os.path.exists(serial):
            stream.write("%s<p><img src='/media/images/tick32.png'>" % indent)
            stream.write(" Printer is connected.</p>\n")

            job = read_active_job(out)
            if job is None:
                status = "waiting"
            else:
                status = read_status(out)

            stream.write("%s<p>Status: %s</p>\n" % (indent, status))
        else:
            stream.write("%s<p><img src='/media/images/stop32.png'> " % indent)
            stream.write(" Printer is not connected.<br />\n")
            stream.write("%s<i>Device: %s</i></p>\n" % (indent, serial))


def render_queue(stream, out, indent=""):
    re_job = re.compile(r"^([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+(\d+)\s+(.+?)\s+(\d+)\s+([0-9:]+)$")

    active = False
    tally = 0

    jobs = []

    for line in out.split("\n"):
        if len(line) == 0:
            continue

        match = re_job.match(line)
        if match is None:
            continue

        jobs.append(match.groups())

    if len(jobs) == 0:
        stream.write("%s<p>No jobs found</p>\n" % indent)
        return

    stream.write("%s<table>\n" % indent)
    stream.write("%s\t<tr>\n" % indent)
    stream.write("%s\t\t<th>Rank</th>\n" % indent)
    stream.write("%s\t\t<th>Owner</th>\n" % indent)
    stream.write("%s\t\t<th>Class</th>\n" % indent)
    stream.write("%s\t\t<th>Job</th>\n" % indent)
    stream.write("%s\t\t<th>Files</th>\n" % indent)
    stream.write("%s\t\t<th>Size</th>\n" % indent)
    stream.write("%s\t\t<th>Time</th>\n" % indent)
    stream.write("%s\t\t<th><br /></th>\n" % indent)
    stream.write("%s\t</tr>\n" % indent)

    for items in jobs:
        stream.write("%s\t<tr>\n" % indent)
        items += ("<a href='/cancel/%s'>cancel</a>" % items[3],)

        for i, item in enumerate(items):
            if i == 5:
                item = pretty_size(float(item))

            stream.write("%s\t\t<td>%s</td>\n" % (indent, item))

        stream.write("%s\t</tr>\n" % indent)

    stream.write("%s</table>\n" % indent)



def index(stream):

    p = subprocess.Popen(["/usr/bin/lpq", "-lll"], stdout=subprocess.PIPE)
    assert p.wait() == 0
    out = p.communicate()[0]

    render_header(stream, autorefresh=True)

    stream.write("\t\t<div id='status'>\n")
    stream.write("\t\t\t<h2>Status</h2>\n")
    render_status(stream, out, "\t\t\t")
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

