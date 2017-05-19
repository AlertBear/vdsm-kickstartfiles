#!/usr/bin/python2.7

import re
import sys
import urllib2
import subprocess
from HTMLParser import HTMLParser


def execute(cmd, check=False):
    print "Executing [%s]..." % cmd 
    try:
        out = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        if check:
            raise e
        else:
            return e.output
    else:
        return out


class BuildHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
        self.a_texts = []
        self.a_text_flag = False

    def handle_starttag(self, tag, attrs):
        # print "Encountered the beginning of a %s tag" % tag
        if tag == "a":
            self.a_text_flag = True
            if len(attrs) == 0:
                pass
            else:
                for (variable, value) in attrs:
                    if variable == "href":
                        self.links.append(value)

    def handle_endtag(self, tag):
        if tag == "a":
            self.a_text_flag = False

    def handle_data(self, data):
        if self.a_text_flag:
            if data.startswith("redhat"):
                self.a_texts.append(data)


class DetailHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
        self.a_texts = []
        self.a_text_flag = False

    def handle_starttag(self, tag, attrs):
        # print "Encountered the beginning of a %s tag" % tag
        if tag == "a":
            self.a_text_flag = True
            if len(attrs) == 0:
                pass
            else:
                for (variable, value) in attrs:
                    if variable == "href":
                        self.links.append(value)

    def handle_endtag(self, tag):
        if tag == "a":
            self.a_text_flag = False

    def handle_data(self, data):
        if self.a_text_flag:
            if data.startswith("redhat"):
                self.a_texts.append(data)


def get_rhvh_squashfs_link(build):
    """
    Purpose:
        Get the latest rhvm appliance from appliance parent path
    """
    # Get the html page from 10.22
    build_url = "http://10.66.10.22:8090/rhvh_ngn/squashimg"
    req = urllib2.Request(build_url)
    response = urllib2.urlopen(req)
    build_html = response.read()

    # Parse the html
    mp = BuildHTMLParser()
    mp.feed(build_html)
    mp.close()

    # Get the build link
    for link in mp.links:
        if re.search(build, link):
            build_link = link

    build_link = build_url + '/' + build_link

    # Get the html page from build_link
    req = urllib2.Request(build_link)
    response = urllib2.urlopen(req)
    detail_html = response.read()

    dp = DetailHTMLParser()
    dp.feed(detail_html)
    dp.close()

    # Get the squashimg link
    for link in dp.links:
        if re.search(".*\.liveimg\.squashfs$", link):
            squashfs_link = link

    squashfs_link = build_link + squashfs_link
    return squashfs_link


if __name__ == "__main__":
    ks = sys.argv[1]
    build = sys.argv[2]

    squashfs_link = get_rhvh_squashfs_link(build)

    cmd = "sed -n '/liveimg --url=.*/=' %s" % ks
    line_num = int(execute(cmd))
    cmd = "sed -i '%sc liveimg --url=%s' %s" % (line_num, squashfs_link, ks) 
    execute(cmd)

