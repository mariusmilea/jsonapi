#!/usr/bin/env python

import json
import logging
import os
import sys
import urllib
import urllib2
from StringIO import StringIO

target_url = 'https://api.host.com/api-v1/repositories/'
auth_url = 'https://api.host.com/auth'
post_url = 'https://api.host.com/do'

_auth = None


def authenticate():
    global _auth
    user = os.getenv('API_USER')
    pwd = os.getenv('API_PWD')
    errors = ''
    if user is None:
        errors = errors + 'API_USER not set. '
    if pwd is None:
        errors = errors + 'API_PWD not set. '

    if errors != '':
        logging.error(errors)
        sys.exit(1)

    try:
        token_req = urllib2.Request(
            auth_url,
            urllib.urlencode({'username': user, 'password': pwd})
        )
        token_response = urllib2.urlopen(token_req).read()
        token = json.load(StringIO(token_response))['token']
        logging.info('Authentication token: ' + token)
        _auth = {'Authorization': 'Token ' + token}
        return token
    except urllib2.HTTPError as e:
        logging.error('Could not authenticate: ' + e)
        raise
    except Exception as e:
        logging.error('Could not authenticate:' + e)
        raise


def get_data_for(url):
    global _auth
    if _auth is None:
        authenticate()

    try:
        req = urllib2.Request(url, None, _auth)
        data = urllib2.urlopen(req).read()
    except urllib2.HTTPError as e:
        logging.error('Cannot get {url}. Code {code}: {reason}'.format(
            url=url,
            code=e.code,
            reason=e.reason)
        )
        sys.exit(1)
    except:
        logging.error('Cannot get ' + url)
        raise
    return json.load(StringIO(data))


def post_data_for(url, key, val):
    """
    Post the data dict
    """
    global _auth
    if _auth is None:
        authenticate()

    data = {"key": "%s", "val": "%s", "env": "staging"} % (key, val)
    try:
        req = urllib2.Request(url, None, _auth)
        req.add_header('Content-Type', 'application/json')
        urllib2.urlopen(req, json.dumps(data))
        logging.info("Setting value  {val} for {key}".format(val=val, key=key))
    except urllib2.HTTPError as e:
        logging.error('Cannot get {url}. Code {code}: {reason}'.format(
            url=url,
            code=e.code,
            reason=e.reason)
        )
        sys.exit(1)
    except:
        logging.error('Cannot get ' + url)
        raise


repos = ['repo1', 'repo2']

for repo in repos:
    # get API data
    target = get_data_for(target_url + repo)
    logging.info("working on {repo} with {tag}".format(
        repo=target['repo'],
        tag=target['tag'])
    )
    # silly example for a POST
    if target['tag'] == "1.0.0":
        prefix = "prefix"
        post_data_for(post_url, target['repo'], prefix)
