#!/usr/local/bin/nice-python

import os
import sys
import subprocess
import re
import web
import cStringIO


re_job = re.compile(r"^([^\s]+)\s+([^\s]+)\s+([^\s]+)\s+(\d+)\s*(.+?)?\s*(\d+)?\s*([0-9:]+)?$")
re_status = re.compile(r" Status: LP filter msg - '(.*?)' at ([0-9:.]+)")


def load_config():
    for line in open("/etc/matterq.conf"):
        parts = line.split("=", 1)
        if len(parts) == 2:
            os.environ[parts[0]] = parts[1].strip()


def read_status(msg):
    status = None

    for line in msg.split("\n"):
        if line.startswith(" Status:"):
            match = re_status.match(line)
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


def render_status(stream, form):
    p = subprocess.Popen(["/usr/bin/lpq", "-lll"], stdout=subprocess.PIPE)
    assert p.wait() == 0
    out = p.communicate()[0]

    serial = os.environ.get("AG_SERIALPORT")
    if serial is None:
        stream.write("<p><img src='/media/images/stop32.png' /> ")
        stream.write("Printer is not configured.</p>\n")
    else:
        if os.path.exists(serial):
            stream.write("<p><img src='/media/images/tick32.png' />")
            stream.write(" Printer is connected.</p>\n")

            job = read_active_job(out)
            if job is None:
                status = "waiting"
            else:
                status = read_status(out)

            stream.write("<p>Status: %s</p>\n" % status)
        else:
            stream.write("<p><img src='/media/images/stop32.png' /> ")
            stream.write(" Printer is not connected.<br />\n")
            stream.write("<i>Device: %s</i></p>\n" % serial)


def render_queue(stream, form):
    queue = form.get("queue")
    if queue is None:
        stream.write("queue required")
        return

    p = subprocess.Popen(["/usr/bin/lpq", "-lll"], stdout=subprocess.PIPE)
    assert p.wait() == 0
    out = p.communicate()[0]


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
        stream.write("<p>No jobs found</p>\n")
        return

    stream.write("<table>\n")
    stream.write("\t<tr>\n")
    stream.write("\t\t<th>Job</th>\n")
    stream.write("\t\t<th>State</th>\n")
    stream.write("\t\t<th>Files</th>\n")
    stream.write("\t\t<th><br /></th>\n")
    stream.write("\t\t<th><br /></th>\n")
    stream.write("\t</tr>\n")

    for items in jobs:
        stream.write("\t<tr>\n")

        for i in (3, 0, 4):
            stream.write("\t\t<td>%s</td>\n" % items[i])

        stream.write("\t\t<td><a class='detail' "
                     "href='/ajax/%s/detail/%s'>detail</a></td>" % \
                     (queue, items[3]))

        stream.write("\t\t<td><a class='cancel' "
                     "href='/ajax/%s/cancel/%s'>cancel</a></td>" % \
                     (queue, items[3]))

        stream.write("\t</tr>\n")

    stream.write("</table>\n")


def render_detail(stream, form):
    queue = form.get("queue")
    job = form.get("job")

    if queue is None:
        stream.write("queue required")
        return

    if job is None:
        stream.write("job required")
        return

    p = subprocess.Popen(["/usr/bin/lpq", job], stdout=subprocess.PIPE)
    assert p.wait() == 0
    out = p.communicate()[0]

    items = None

    for line in out.split("\n"):
        if len(line) == 0:
            continue

        match = re_job.match(line)
        if match is None:
            continue

        items = match.groups()

    if items is None:
        stream.write("no such job")
        return

    titles = ("Rank", "Owner", "Class", "Job", "Files", "Size", "Time")

    assert len(items) == len(titles)

    for i in range(len(titles)):
        stream.write("%s: %s\n" % (titles[i], items[i]))


def render_log(stream, form):
    p = subprocess.Popen(["/usr/local/bin/matterq-log"],
                         stdout=subprocess.PIPE)
    assert p.wait() == 0
    out = p.communicate()[0]

    for line in out.split("\n"):
        stream.write(line)
        stream.write("<br />")


def remove(stream, form):
    job = form.get("job")

    if job is None:
        stream.write("false")
        return

    p = subprocess.Popen(["/usr/bin/lprm", job])

    if p.wait() == 0:
        stream.write("true")
    else:
        stream.write("false")


def clear_bed(stream, form):
    path = os.path.join(os.environ["MQ_SPOOLDIR"], "depositions")
    cleared = False

    for name in os.listdir(path):
        os.remove(os.path.join(path, name))

    subprocess.Popen(["/usr/local/bin/matterq-plate-render"]).wait()
    subprocess.Popen(["/usr/sbin/lpc", "release", "lp", "all"]).wait()

    stream.write("true")


def upload(stream, form):
    data = web.input(gcode = {})

    queue = form.get("queue")
    input = data.get("gcode")

    if input is None:
        stream.write("Upload Error")
        return

    if queue is None:
        stream.write("queue required")
        return

    p = subprocess.Popen(["lp", "-d", queue, "-t", input.filename, "-"],
                         stdin = input.file)

    if p.wait() != 0:
        stream.write("Upload Error")
        return

    stream.write("Upload Complete")


class Index(object):
    mapper = {
        "status" : render_status,
        "queue" : render_queue,
        "detail" : render_detail,
        "log" : render_log,
        "cancel" : remove,
        "clear" : clear_bed,
        "upload" : upload,
    }

    def GET(self):
        form = web.input()
        stream = cStringIO.StringIO()

        try:
            handler = self.mapper.get(form.get("ajax"))

            if handler is None:
                stream.write("invalid ajax call")
            else:
                handler(stream, form)

            return stream.getvalue()

        finally:
            stream.close()

    POST = GET


if __name__ == "__main__":
    load_config()

    urls = (
        "/.*", "Index"
    )

    app = web.application(urls, {"Index" : Index})
    app.run()
