# Copyright (c) 2006-2012 Mitch Garnaat http://garnaat.org/
# Copyright (c) 2010-2011, Eucalyptus Systems, Inc.
# Copyright (c) 2006-2012 Mitch Garnaat http://garnaat.org/
# Copyright (c) 2010-2011, Eucalyptus Systems, Inc.
# Copyright (c) 2011, Nexenta Systems Inc.
# Copyright (c) 2012 Amazon.com, Inc. or its affiliates.
# Copyright (c) 2010, Google, Inc.
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
from niftycloud.pyami.config import Config, NiftycloudConfigLocations
import niftycloud.plugin
import datetime
import os
import platform
import re
import sys
import logging
import logging.config

from niftycloud.compat import urlparse
from niftycloud.exception import InvalidUriError

__version__ = '0.0.1'
Version = __version__  # for backware compatibility

# http://bugs.python.org/issue7980
datetime.datetime.strptime('', '')

UserAgent = 'Niftycloud/%s Python/%s %s/%s' % (
    __version__,
    platform.python_version(),
    platform.system(),
    platform.release()
)
config = Config()

# Regex to disallow buckets violating charset or not [3..255] chars total.
BUCKET_NAME_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9\._-]{1,253}[a-zA-Z0-9]$')
# Regex to disallow buckets with individual DNS labels longer than 63.
TOO_LONG_DNS_NAME_COMP = re.compile(r'[-_a-z0-9]{64}')
GENERATION_RE = re.compile(r'(?P<versionless_uri_str>.+)'
                           r'#(?P<generation>[0-9]+)$')
VERSION_RE = re.compile('(?P<versionless_uri_str>.+)#(?P<version_id>.+)$')
ENDPOINTS_PATH = os.path.join(os.path.dirname(__file__), 'endpoints.json')


def init_logging():
    for file in NiftycloudConfigLocations:
        try:
            logging.config.fileConfig(os.path.expanduser(file))
        except:
            pass


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

log = logging.getLogger('niftycloud')
perflog = logging.getLogger('niftycloud.perf')
log.addHandler(NullHandler())
perflog.addHandler(NullHandler())
init_logging()

# convenience function to set logging to a particular file


def set_file_logger(name, filepath, level=logging.INFO, format_string=None):
    global log
    if not format_string:
        format_string = "%(asctime)s %(name)s [%(levelname)s]:%(message)s"
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fh = logging.FileHandler(filepath)
    fh.setLevel(level)
    formatter = logging.Formatter(format_string)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    log = logger
