from __future__ import print_function
from __future__ import absolute_import
from future.utils import iteritems
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.error, urllib.parse
import http.client
from base64 import b64encode
from tempfile import mkstemp
from os import close

import requests
import signal

from .util import CCTError

from . import makemultipart as multi

"""
This file contains some utility functions for the content-copy-tool that relate
to http requests.
"""

timeout = 300

def http_post_request(url, headers={}, auth=(), data={}):
    """
    Sends a POST request to the specified url with the specified headers, data,
    and authentication tuple. Because we want to the post request to be successful
    in the widest variety of cases, all permanent redirects are treated as a 308
    would (i.e. POST is not converted to GET). Because we expect successful POSTs
    to redirect to the result of the request, temporary redirects are all treated
    as a 303 would (i.e. POST can be converted to GET) and then the following GET
    request redirects are followed.
    """

    MAX_REDIRECTS = 4
    redirects = 0

    def handle_timeout(signal, frame):
        print("Request: {} is taking an exceptionally long time, you might want to skip this task (Ctrl+z)".format(url))

    def follow_with_post(response):
        return requests.post(response.headers['Location'], headers=headers, auth=auth, data=data, allow_redirects=False)

    def follow_with_get(response):
        return requests.Session().send(response.next, allow_redirects=False)

    signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(timeout)
    response = requests.post(url, headers=headers, auth=auth, data=data, allow_redirects=False)
    while response.is_redirect and redirects < MAX_REDIRECTS:
        redirects += 1
        response = {
            True: follow_with_post,
            False: follow_with_get
        }[response.is_permanent_redirect and response.request.method == 'POST'](response)
    if response.is_redirect:
        raise CCTError("POST redirection failed after maximum number of requests")
    signal.alarm(0)
    return response

def http_get_request(url, headers={}, auth=(), data={}):
    """
    Sends a GET request to the specified url with the specified headers, data,
    and authentication tuple.
    """
    def handle_timeout(signal, frame):
        print("Request: {} is taking an exceptionally long time, you might want to skip this task (Ctrl+z)".format(url))

    signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(timeout)
    response = requests.get(url, headers=headers, auth=auth, data=data)
    signal.alarm(0)
    return response

def http_request(url, headers={}, data={}):
    """
    Sends an HTTP request to the specified url with the specified headers and
    data. If no data is provided, the request will be a GET, if data is provided
    the request will be a POST.
    """
    request = urllib.request.Request(url)
    if headers:
        for key, value in iteritems(headers):
            request.add_header(key, value)
    if data:
        request.data=urllib.parse.urlencode(data)
    try:
        response = urllib.request.urlopen(request)
        return response
    except urllib.error.HTTPError as e:
        print(e.message)

def http_download_file(url, filename, extension):
    """ Downloads the file at [url] and saves it as [filename.extension]. """
    def handle_timeout(signal, frame):
        print("Request: {} is taking an exceptionally long time, you might want to skip this task (Ctrl+z)".format(url))

    signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(timeout)
    try:
        urllib.request.urlretrieve(url, filename + extension)
    except Exception as e:
        print(e)
    signal.alarm(0)
    return filename + extension

def extract_boundary(message):
    """ Extracts the boundary line of a multipart file at filename. """
    boundary_start = 'boundary=\"'
    boundary_end = '\"'
    text = message.as_string(unixfrom=False)
    start = text.find(boundary_start) + len(boundary_start)
    end = text.find(boundary_end, start)
    return text[start:end]

def http_upload_file(xmlfile, zipfile, url, credentials, logger, mpartfilename='tmp'):
    """
    Uploads a multipart file made up of the given xml and zip files to the
    given url with the given credentials. The temporary multipartfile can be
    named with the mpartfilename parameter.
    """
    message = multi.makemultipart(open(xmlfile, 'r'), open(zipfile, 'rb'))
    boundary_code = extract_boundary(message)
    userAndPass = b64encode(credentials.encode()).decode("ascii")
    headers = {"Content-Type": "multipart/related;boundary=%s;type=application/atom + xml" % boundary_code,
               "In-Progress": "true", "Accept-Encoding": "zip", "Authorization": 'Basic %s' % userAndPass}
    req = urllib.request.Request(url)

    def handle_timeout(signal, frame):
        print("Request: {} is taking an exceptionally long time, you might want to skip this task (Ctrl+z)".format(url))

    signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(timeout)
    if url.startswith('https://'):
        connection = http.client.HTTPSConnection(req.host)
    else:
        connection = http.client.HTTPConnection(req.host)
    logger.debug('Multipart uploading documents')
    logger.debug('Url: {}'.format(url))
    logger.debug('Host: {}'.format(req.host))
    logger.debug('Selector: {}'.format(req.selector))
    logger.debug('Headers: {}'.format(headers))
    logger.debug('Boundary: {}'.format(boundary_code))
    logger.debugv('Content:')
    logger.debugv(message.as_string(unixfrom=False))
    connection.request('POST', req.selector, message.as_string(unixfrom=False), headers)
    response = connection.getresponse()
    signal.alarm(0)
    return response, url

def verify(response, logger):
    """ Returns True if the response code is < 400, False otherwise. """
    if response.status_code < 400:
        return True
    else:
        error = "Failed response: %s %s when sending to %s with data %s" % \
                (response.status_code, response.reason, response.request.url, response.request.body)
        if logger is None:
            print(error)
        else:
            logger.debug(error)
        return False
