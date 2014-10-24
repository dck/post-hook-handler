#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sh

REPOS_PATHS = {
    "repo": "~/work/repo"
}

class Error(Exception): pass
class SCMDoesntSupport(Error): pass

class SCMHandler(object):

    def __init__(self, *args, **kwargs):
        pass

    def pull(self):
        raise NotImplementedError

    def checkout(self):
        raise NotImplementedError


class HgHanlder(SCMHandler):

    def pull(self):
        sh.hg.pull("-u")

    def checkout(self, branchname):
        sh.hg.up(branchname)

class GitHanlder(SCMHandler):

    def pull(self):
        sh.git.pull()

    def checkout(self, branchname):
        sh.git.checkout(branchname)

def scm_factory(scm_name, *args, **kwargs):
    d = {
        "hg": HgHanlder,
        "git": GitHanlder
    }
    try:
        creator = d[scm_name]
    except KeyError:
        raise SCMDoesntSupport(scm_name)

    return creator(*args, **kwargs)



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