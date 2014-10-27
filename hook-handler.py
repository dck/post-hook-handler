#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import sh
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from urlparse import parse_qs

WORK_BRANCH = "default"
REPOS_PATHS = {
    "SOPT": "/tmp/aaa/sopt"
}

class Error(Exception): pass
class SCMDoesntSupport(Error): pass
class BadRequest(Error): pass
class NoPathForRepo(Error): pass

class SCMHandler(object):

    def __init__(self, *args, **kwargs):
        pass

    def pull(self):
        raise NotImplementedError

    def checkout(self):
        raise NotImplementedError


class HgHandler(SCMHandler):

    def pull(self):
        sh.hg.pull("-u")

    def checkout(self, branchname):
        sh.hg.up(branchname)

class GitHandler(SCMHandler):

    def pull(self):
        sh.git.pull()

    def checkout(self, branchname):
        sh.git.checkout(branchname)

class PushInfo(object):

    def __init__(self, json_payload):
        obj_payload = json.loads(json_payload)
        self.commits = obj_payload["commits"]
        self.repo_info = obj_payload["repository"]

    def scm(self):
        return self.repo_info["scm"]

    def name(self):
        return self.repo_info["name"]

    def is_branch_changed(self, branchname):
        res = any(c["branch"] == branchname for c in self.commits)
        return res



class Handler(BaseHTTPRequestHandler):

    def parse_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(
                    self.rfile.read(length),
                    keep_blank_values=1)
        else:
            postvars = {}
        return postvars

    def do_POST(self):
        postvars = self.parse_POST()
        try:
            payload = postvars["payload"][0]
        except KeyError:
            raise BadRequest

        go(payload)


def scm_factory(scm_name, *args, **kwargs):
    d = {
        "hg": HgHandler,
        "git": GitHandler
    }
    try:
        creator = d[scm_name]
    except KeyError:
        raise SCMDoesntSupport(scm_name)

    return creator(*args, **kwargs)


def go(payload):
    print "Got POST request"
    r = PushInfo(payload)
    if not r.is_branch_changed(WORK_BRANCH):
        print "There are no proper changes in {}".format(r.name())
        return

    try:
       path = REPOS_PATHS[r.name()]
       print "Path to work: {}".format(path)
    except KeyError:
        raise NoPathForRepo

    print "SCM: {}".format(r.scm())
    scm_handler = scm_factory(r.scm())
    old_path = os.getcwd()
    try:
        sh.cd(path)
        scm_handler.checkout(WORK_BRANCH)
        scm_handler.pull()
        print "Complete"
    finally:
        sh.cd(old_path)


server = HTTPServer(('', 4444), Handler)
print "Start serving"
server.serve_forever()



# {
#     "canon_url": "https://bitbucket.org",
#     "commits": [
#         {
#             "author": "marcus",
#             "branch": "featureA",
#             "files": [
#                 {
#                     "file": "somefile.py",
#                     "type": "modified"
#                 }
#             ],
#             "message": "Added some featureA things",
#             "node": "d14d26a93fd2",
#             "parents": [
#                 "1b458191f31a"
#             ],
#             "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
#             "raw_node": "d14d26a93fd28d3166fa81c0cd3b6f339bb95bfe",
#             "revision": 3,
#             "size": -1,
#             "timestamp": "2012-05-30 06:07:03",
#             "utctimestamp": "2012-05-30 04:07:03+00:00"
#         }
#     ],
#     "repository": {
#         "absolute_url": "/marcus/project-x/",
#         "fork": false,
#         "is_private": true,
#         "name": "Project X",
#         "owner": "marcus",
#         "scm": "hg",
#         "slug": "project-x",
#         "website": ""
#     },
#     "user": "marcus"
# }