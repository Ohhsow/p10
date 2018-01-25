#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paramiko
import os, sys
import subprocess
from netmiko import ConnectHandler
from paramiko import client
import logging

logger = logging.getLogger(__name__)

progname = os.path.split(sys.argv[0])[-1]

if sys.version_info < (2, 7, 0):
    sys.exit(
        '''Error: %s is not supported on Python versions ''' % progname)


class System(object):
    """Update system"""

    def __init__(self, command):
        self.command = command
        self.ostype = "apt"
        if (os.path.isfile("/etc/redhat-release")):
            self.ostype = "rpm"

    def is_responsible(self):
        if (self.command == u"system-update"):
            return True
        else:
            return False

    def execute(self):
        if self.ostype == u"rpm":
            self.__yum("update", "-y")
        elif self.ostype == u"apt":
            self.__apt("update")
            self.__apt("upgrade", "-y")
        return (self.retval, self.output)

    def __yum(self, command, options=""):
        cmd = "yum %s %s" % (options, command)
        self.__exec(cmd)

    def __apt(self, command, options=""):
        cmd = "apt-get %s %s" % (options, command)
        self.__exec(cmd)

    def __exec(self, cmd):
        self.output = ""
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            self.output += line
        self.retval = p.wait()


class Connect(object):

    """New connection"""
    client = None


    def __init__(self, host=None, user_name=None, port=22):
        print("Connecting to server.")
        self.host = host
        self.user_name = user_name
        self.machine_port = port
        self.public_key_file = os.path.expanduser('~/.ssh/id_rsa.pub')
        self.client = client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.client.connect(hostname=self.host, username=self.user_name, key_filename=self.public_key_file,
                            port=self.port)

    @staticmethod
    def usage_msg():
        return '''
        This tool is designed to be used with SSH to add nodes
        to the configuration. It will generate a new SSH key. It can optionally add the
        new key to the node's authorized_keys folder.\n\n
        '''

    def exe_command(self, cmd):
        """Send command"""
        stdin, stdout, stderr = self.client.exe_command(cmd)
        if stderr.channel.recv_exit_status() != 0:
            return stderr.read()
        else:
            return stdout.read()



class KeysGen(object):
    def __init__(self):
        self.public_key_file = os.path.expanduser('~/.ssh/id_rsa.pub')

    def keys_generation(self):
        """Creates pair of keys for connection"""
        if os.path.exists(self.public_key_file) is False or os.stat(self.public_key_file).st_size == 0:
            process = subprocess.Popen('ssh-keygen')
            process.wait()
        else:
            print("The pair of keys is already created.")

class Sshpair(object):

    """Deploys new key on virtual machine"""

    def __init__(self, host=None, user_name=None, user_pass=None, port=22, public_key=None):
        """Constructor"""
        self.host = host
        self.user_name = user_name
        self.user_password = user_pass
        self.machine_port = port
        self.public_key = public_key
        self.public_key_file = os.path.expanduser('~/.ssh/id_rsa.pub')

    def key_push(self):
        """Deploys public key to remote machine"""
        with open(self.public_key_file) as key_file:
            self.public_key = key_file.readline()
        deploy_client = paramiko.SSHClient()
        deploy_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        deploy_client.connect(hostname=self.host, username=self.user_name, password=self.user_pass, port=self.port)
        deploy_client.exec_command('mkdir -p ~/.ssh/')
        deploy_client.exec_command('echo "%s" > ~/.ssh/authorized_keys' % self.public_key)
        deploy_client.exec_command('chmod 644 ~/.ssh/authorized_keys')
        deploy_client.exec_command('chmod 700 ~/.ssh/')
        deploy_client.close()
        # logger.debug(command)
        _, stdout, stderr = deploy_client.exec_command(com)
        stderr = stderr.read()
        if stderr != '':
            client.close()
            logger.error(stderr)
            return False
        deploy_client.close()
        return True

    def removing_created_keys(self):
        """Removes created keys"""
        removing_client = paramiko.SSHClient()
        removing_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        removing_client.connect(hostname=self.host, username=self.user_name, password=self.user_pass, port=self.port)
        removing_client.exec_command('rm ~/.ssh/authorized_keys')
        removing_client.close()
        # logger.debug(command)
        _, stdout, stderr = deploy_client.exec_command(com)
        stderr = stderr.read()
        if stderr != '':
            client.close()
            logger.error(stderr)
            return False
        deploy_client.close()
        return True

class Configurator(object):
    """Open configuration file"""

    def __init__(self,
                 host=None, user_name=None, user_pas=None, port=None, js=None):
        """Constructor """
        self.host = host
        self.user_name = user_name
        self.user_password = user_pas
        self.machine_port = port
        self.js = js

    def open_file(self):
        """Reads configuration file"""
        with open('config_file.txt') as configure:
            self.js = json.load(configure)
            for key in self.js:
                conf_file = self.js[key]
                self.extract_data(conf_file)

    def extract_data(self, dictionary):
        """Extracts results of json"""
        self.host = dictionary['host']
        self.user_name = dictionary['auth_data']['user']
        self.user_password = dictionary['auth_data']['secret']
        self.machine_port = dictionary['auth_data']['port']
        key_deploy = KeyDeploy(self.host, self.user_name, self.user_pass, self.port)
        key_deploy.deploy_key()


class BackUp(object):
    """Save keys"""

    def __init__(self,
                 rec_key=None,
                 pub_key=None):
        """Constructor"""
        self.recovered_key = rec_key
        self.pub_key_file = os.path.expanduser('~/.ssh/id_rsa.pub')
        self.pub_key = pub_key

    def back_up(self):
        """Back-up of removed keys"""
        with open(self.pub_key_file) as public:
            self.pub_key = public.readline()
        configuration_reset = Configurator()
        configuration_reset.opening_con_file()


if __name__ == '__main__':

    generator = KeysGen()
    generator.keys_generation()
    configuration = Configurator()
    configuration.open_file()
    ssh = Connect(configuration.host, configuration.user_name, configuration.port)
    ssh.exe_command("reboot")


