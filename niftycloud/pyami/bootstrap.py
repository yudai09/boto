# Copyright (c) 2006,2007 Mitch Garnaat http://garnaat.org/
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
import os
import niftycloud
from niftycloud.utils import get_instance_metadata, get_instance_userdata
from niftycloud.pyami.config import Config, NiftycloudConfigPath
from niftycloud.pyami.scriptbase import ScriptBase
import time

class Bootstrap(ScriptBase):
    """
    The Bootstrap class is instantiated and run as part of the PyAMI
    instance initialization process.  The methods in this class will
    be run from the rc.local script of the instance and will be run
    as the root user.

    The main purpose of this class is to make sure the niftycloud distribution
    on the instance is the one required.
    """

    def __init__(self):
        self.working_dir = '/mnt/pyami'
        self.write_metadata()
        super(Bootstrap, self).__init__()

    def write_metadata(self):
        fp = open(os.path.expanduser(NiftycloudConfigPath), 'w')
        fp.write('[Instance]\n')
        inst_data = get_instance_metadata()
        for key in inst_data:
            fp.write('%s = %s\n' % (key, inst_data[key]))
        user_data = get_instance_userdata()
        fp.write('\n%s\n' % user_data)
        fp.write('[Pyami]\n')
        fp.write('working_dir = %s\n' % self.working_dir)
        fp.close()
        # This file has the AWS credentials, should we lock it down?
        # os.chmod(NiftycloudConfigPath, stat.S_IREAD | stat.S_IWRITE)
        # now that we have written the file, read it into a pyami Config object
        niftycloud.config = Config()
        niftycloud.init_logging()

    def create_working_dir(self):
        niftycloud.log.info('Working directory: %s' % self.working_dir)
        if not os.path.exists(self.working_dir):
            os.mkdir(self.working_dir)

    def load_niftycloud(self):
        update = niftycloud.config.get('Niftycloud', 'niftycloud_update', 'svn:HEAD')
        if update.startswith('svn'):
            if update.find(':') >= 0:
                method, version = update.split(':')
                version = '-r%s' % version
            else:
                version = '-rHEAD'
            location = niftycloud.config.get('Niftycloud', 'niftycloud_location', '/usr/local/niftycloud')
            self.run('svn update %s %s' % (version, location))
        elif update.startswith('git'):
            location = niftycloud.config.get('Niftycloud', 'niftycloud_location', '/usr/share/python-support/python-niftycloud/niftycloud')
            num_remaining_attempts = 10
            while num_remaining_attempts > 0:
                num_remaining_attempts -= 1
                try:
                    self.run('git pull', cwd=location)
                    num_remaining_attempts = 0
                except Exception as e:
                    niftycloud.log.info('git pull attempt failed with the following exception. Trying again in a bit. %s', e)
                    time.sleep(2)
            if update.find(':') >= 0:
                method, version = update.split(':')
            else:
                version = 'master'
            self.run('git checkout %s' % version, cwd=location)
        else:
            # first remove the symlink needed when running from subversion
            self.run('rm /usr/local/lib/python2.5/site-packages/niftycloud')
            self.run('easy_install %s' % update)

    def fetch_s3_file(self, s3_file):
        try:
            from niftycloud.utils import fetch_file
            f = fetch_file(s3_file)
            path = os.path.join(self.working_dir, s3_file.split("/")[-1])
            open(path, "w").write(f.read())
        except:
            niftycloud.log.exception('Problem Retrieving file: %s' % s3_file)
            path = None
        return path

    def load_packages(self):
        package_str = niftycloud.config.get('Pyami', 'packages')
        if package_str:
            packages = package_str.split(',')
            for package in packages:
                package = package.strip()
                if package.startswith('s3:'):
                    package = self.fetch_s3_file(package)
                if package:
                    # if the "package" is really a .py file, it doesn't have to
                    # be installed, just being in the working dir is enough
                    if not package.endswith('.py'):
                        self.run('easy_install -Z %s' % package, exit_on_error=False)

    def main(self):
        self.create_working_dir()
        self.load_niftycloud()
        self.load_packages()
        self.notify('Bootstrap Completed for %s' % niftycloud.config.get_instance('instance-id'))

if __name__ == "__main__":
    # because bootstrap starts before any logging configuration can be loaded from
    # the niftycloud config files, we will manually enable logging to /var/log/niftycloud.log
    niftycloud.set_file_logger('bootstrap', '/var/log/niftycloud.log')
    bs = Bootstrap()
    bs.main()
