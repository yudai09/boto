# Copyright (c) 2010 Mitch Garnaat http://garnaat.org/
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
"""
Represents an Computing Placement Group
"""
from niftycloud.computing.computingobject import ComputingObject
from niftycloud.exception import NiftycloudClientError


class PlacementGroup(ComputingObject):

    def __init__(self, connection=None, name=None, strategy=None, state=None):
        super(PlacementGroup, self).__init__(connection)
        self.name = name
        self.strategy = strategy
        self.state = state

    def __repr__(self):
        return 'PlacementGroup:%s' % self.name

    def endElement(self, name, value, connection):
        if name == 'groupName':
            self.name = value
        elif name == 'strategy':
            self.strategy = value
        elif name == 'state':
            self.state = value
        else:
            setattr(self, name, value)

    def delete(self, dry_run=False):
        return self.connection.delete_placement_group(
            self.name,
            dry_run=dry_run
        )